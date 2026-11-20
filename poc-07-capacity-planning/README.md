# POC 07: Capacity planning on AWS

**Book chapter:** 15 (Capacity Planning), plus 13 (two layers of capacity automation) and 20 (utilisation-loss framework)

| Path | What |
|---|---|
| `capacity.py` | Organic trend forecast + inorganic events + an uncertainty band from **backtesting**; N+1 supply plan across AZs; redundancy overhead (1/N); **peak of sums vs sum of peaks**; stranded capacity |
| `terraform/` | ASG with a **static-stability floor** (N+1 per AZ, on-demand), Spot burst with several instance types (fungibility), **target tracking** on requests per target (business demand, not CPU), **predictive scaling**, a scheduled pre-scale for a known peak, optional **capacity reservations** for supply risk |

```bash
python -m pytest -q
python -c "from capacity import plan_supply; print(plan_supply(9000, 100, 3, 0.7))"
```

## Concept map
| Book | AWS |
|---|---|
| Demand forecasting (organic + inorganic, planned/unplanned) | CloudWatch metrics history, Predictive Scaling, scheduled actions for launches |
| Business-driven demand (resources per unit of product demand) | `ALBRequestCountPerTarget`; track *instances per 1k QPS* over time as an efficiency SLI |
| Supply: fungibility, lead time, elasticity | Multiple instance types/families, Spot vs On-Demand vs Savings Plans/RIs, capacity reservations, service quotas (request increases **before** you need them) |
| Failure domains & N+1 | 3 AZs, floor sized so 2 carry peak; cells for blast radius |
| Overload & crumple zones | Shed by criticality (POC 04), SQS buffers, degrade features (POC 05 flags) |
| Peak of sums (Flex) | Shared clusters (EKS/ECS capacity providers) across services in different time zones |
| FinOps | Cost Explorer, tags for chargeback, Compute Optimizer for right-sizing |

## Interview talking points
* Ask first whether you need rigorous planning at all. If autoscaling and a fault-tolerant design absorb shortfalls, spend the effort elsewhere.
* Express SLO-relevant capacity as **"how much can we lose and still meet the SLO at peak?"**
* Quantify uncertainty: backtest the forecaster, choose a confidence level, and put capacity into your postmortems.
* Google Meet during COVID grew 400× regionally in three months. That kind of growth is why you need control knobs (quality reduction, load shedding), pooled capacity and adaptive incident response, not only better forecasts.
