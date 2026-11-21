# SRE chapter 15: Capacity planning

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-15`. Code: POC 07. Read: full text, two passes.*

## Summary

Capacity planning means forecasting demand and providing supply, and it is really a risk-versus-cost trade-off much like an error budget. Ask first whether you need it at all: if autoscaling and a fault-tolerant design absorb a shortfall, spend the effort elsewhere.

- **Organic**: Steady growth. Forecast it from trends.
- **Planned inorganic**: Launches, Black Friday, the Olympics. Plan it with the launch.
- **Unplanned inorganic**: Going viral. Handle it with buffers, autoscaling and demand shaping.

Otherwise, **forecast demand** as organic growth plus **inorganic** events (planned launches, unplanned shocks); express it through a driver metric such as DAU or QPS; quantify the uncertainty with scenarios and **backtesting**; and include capacity in postmortems. Track the ratio of infrastructure to product demand as a living model and alert when it drifts.

**Supply** depends on fungibility (location, latency, regulation), lead time and elasticity, and your cloud provider's trade-offs become your risks, which means reservations for peaks you can't miss and scarce accelerators.

Latency and availability needs belong to *traffic*, not to the service, so tag traffic with criticality (shed the least important first), mark latency-tolerant work, and provision so you can drain a failure domain. Build capacity isolation and failure domains, and remember transitive dependencies.

## Key ideas

- when capacity planning is worth doing at all
- the three kinds of demand and how to forecast each
- how traffic tags, failure domains and pooling change the sums
- the Google Meet and AI-era case studies

## What the lesson covers

- The big picture
- The iron triangle of capacity
- Case study: the Google Meet loop
- First decide if you need it
- Demand
- Supply and the plan of record
- Requirements belong to traffic, not services
- Failure domains through a capacity lens
- Crumple zones and efficiency
- Peak of sums and Flex
- Google Meet during COVID
- The AI era

## Claims and numbers

- Case: Google Meet in 2020 saw regional growth of up to 400×, handled with adaptive long-running incident response, separate workstreams, pooled resources, control knobs (load shedding, lower video quality) and attention to burnout.
- Across both books Ideas in this lesson that the platform engineering book also covers, from the knowledge map:Failure domains and N+1 : Survive the loss of a zone or region; say which domain you mean.
- Provisioning for every edge case is like aiming for 100% availability.
- Simple autoscaling rules (add two instances above 70% CPU for five minutes, remove one below 40% with a floor of five) cover most services.
- Typical cloud SLAs are 99.5% for a zone and 99.99% for multi-region services.
- Google's Flex pools quota and saves about 5–20%.
- Then it grew up to 30× (and up to 400× in some regions by mid-May 2020), with first pages on 17 February in Asia.
- Dependency mapping : a 10× target against the pre-COVID peak, tracked in one sheet.

## Terms

Organic, Planned inorganic, Unplanned inorganic, forecast demand, inorganic, backtesting, Supply, crumple zones, Pooling, stranded capacity, Architect for constraints, Shift work in time, Improve connectivity, Review the inputs, One question, Capacity

## On AWS

Predictive Scaling, target tracking on requests per target, scheduled actions, On-Demand Capacity Reservations and Capacity Blocks, Savings Plans versus Spot, service quotas (raise them early), Compute Optimizer. See POC 07.

## Takeaways

- Planning for every edge case is like targeting 100%. Choose your risk.
- Latency and availability needs belong to traffic, not to services. Tag requests and shed by criticality.
- Pooling works because peaks rarely coincide, but pooled services must survive a stockout.
