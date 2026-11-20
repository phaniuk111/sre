output "page_topic_arn" {
  value = aws_sns_topic.page.arn
}

output "ticket_topic_arn" {
  value = aws_sns_topic.ticket.arn
}

output "error_budget_minutes_per_30d" {
  value = (1 - var.slo_target) * 30 * 24 * 60
}
