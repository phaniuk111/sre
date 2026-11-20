# Capacity on AWS: two layers of automation, as in book ch. 13/15.
#   short timescale (minutes): target-tracking autoscaling on a demand metric
#   longer timescale (days):   predictive scaling from learned daily/weekly cycles
# plus a static-stability floor: min size = N+1 per AZ so one AZ can be lost
# without needing the control plane to scale.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.40" }
  }
}

provider "aws" {
  region = var.region
}

locals {
  # From capacity.plan_supply(): instances needed per AZ so that (AZs - 1) carry the peak
  per_az_floor = ceil(var.peak_qps / (var.qps_per_instance * var.target_utilisation) / (length(var.subnet_ids) - 1))
}

resource "aws_autoscaling_group" "checkout" {
  name                      = "checkout"
  vpc_zone_identifier       = var.subnet_ids
  min_size                  = local.per_az_floor * length(var.subnet_ids)
  max_size                  = local.per_az_floor * length(var.subnet_ids) * 4
  health_check_type         = "ELB"
  health_check_grace_period = 120
  target_group_arns         = [var.target_group_arn]
  capacity_rebalance        = true

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = local.per_az_floor * length(var.subnet_ids) # floor never on Spot
      on_demand_percentage_above_base_capacity = 0                                           # burst on Spot (FinOps trade-off)
      spot_allocation_strategy                 = "price-capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = var.launch_template_id
        version            = "$Latest"
      }
      override { instance_type = "m7g.large" }
      override { instance_type = "m6g.large" } # fungibility: more pools = fewer stockouts
    }
  }

  tag {
    key                 = "service"
    value               = "checkout"
    propagate_at_launch = true
  }
}

# Scale on the business-driven demand signal (requests per target), not on CPU.
resource "aws_autoscaling_policy" "target_tracking" {
  name                   = "checkout-requests-per-target"
  autoscaling_group_name = aws_autoscaling_group.checkout.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = var.alb_resource_label
    }
    target_value = var.qps_per_instance * var.target_utilisation * 60 # per-minute metric
  }
}

resource "aws_autoscaling_policy" "predictive" {
  name                   = "checkout-predictive"
  autoscaling_group_name = aws_autoscaling_group.checkout.name
  policy_type            = "PredictiveScaling"
  predictive_scaling_configuration {
    mode                         = "ForecastAndScale"
    scheduling_buffer_time       = 300 # launch 5 min before forecast demand
    max_capacity_breach_behavior = "IncreaseMaxCapacity"
    max_capacity_buffer          = 20
    metric_specification {
      target_value = var.qps_per_instance * var.target_utilisation * 60
      predefined_load_metric_specification {
        predefined_metric_type = "ALBTargetGroupRequestCount"
        resource_label         = var.alb_resource_label
      }
      predefined_scaling_metric_specification {
        predefined_metric_type = "ALBRequestCountPerTarget"
        resource_label         = var.alb_resource_label
      }
    }
  }
}

# Inorganic, PLANNED demand (launch, Black Friday): book it in advance.
resource "aws_autoscaling_schedule" "black_friday" {
  scheduled_action_name  = "black-friday-prescale"
  autoscaling_group_name = aws_autoscaling_group.checkout.name
  start_time             = var.peak_event_start
  end_time               = var.peak_event_end
  min_size               = local.per_az_floor * length(var.subnet_ids) * 2
  max_size               = local.per_az_floor * length(var.subnet_ids) * 6
  desired_capacity       = local.per_az_floor * length(var.subnet_ids) * 2
}

# Supply risk: on-demand capacity can run out for an instance type/AZ.
# For must-have peaks, reserve it (an On-Demand Capacity Reservation) ahead of time.
resource "aws_ec2_capacity_reservation" "peak" {
  count             = var.reserve_peak_capacity ? length(var.availability_zones) : 0
  instance_type     = "m7g.large"
  instance_platform = "Linux/UNIX"
  availability_zone = var.availability_zones[count.index]
  instance_count    = local.per_az_floor
  end_date_type     = "limited"
  end_date          = var.peak_event_end
}
