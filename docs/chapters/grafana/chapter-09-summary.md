# Grafana chapter 9: Incident management with Grafana Alerting, OnCall and Incident

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-9`. Code: POC 23, 24 · 9. Read: full text, one pass; all figures seen.*

## Summary

Bad incident management is genuinely harmful: stress, burnout, worse. The chapter organises good practice into before, during and after an incident, and draws on the UK government’s emergency response guidance, Atlassian’s incident handbook, ServiceNow’s guide and Google’s SRE books. Frameworks to borrow from include ITIL, Google SRE, NIST and SANS.

- **Commander**: Has authority, calls people in, signs off customer and leadership communication. Every other role reports to them.
- **Communications**: Internal, third-party and customer communication, on a cadence.
- **Technical lead**: Directs the investigators and knows who is looking at what.

The gold–silver–bronze structure comes from UK emergency services. Most incident frameworks describe only bronze; agreeing silver and gold responsibilities in advance is what lets a serious incident escalate cleanly.

That is **white-box** monitoring, from inside. **Black-box** monitoring checks from outside as a user would: synthetic probes (the Prometheus blackbox exporter for HTTP, DNS, TCP, ICMP and gRPC; a third-party service to prove SLA compliance) and real user monitoring. Black-box checks also cover things you don’t control, such as ISPs and DNS, so expect some false positives. Runbooks and a strong post-incident process move an organisation away from a **hero culture**, where a few people hold everything together at the expense of their health.

An escalation policy answers: who is paged first (in hours, out of hours, by severity)? Who is next if they don’t answer? Who takes over, and when (duration, severity, time of day)? How is it handed over? What if two incidents run at once? Leadership must make sure juniors know it is fine to escalate, and audit rotas for overload.

## Key ideas

- Roles before an incident, and the gold–silver–bronze command structure
- Cutting noise in telemetry and in communication
- RED, USE, golden signals, Web Vitals, and white- versus black-box monitoring
- Escalation, communication and blameless post-incident reviews
- Grafana Alerting, OnCall and Incident in practice

## What the lesson covers

- Being alerted versus being alarmed
- Before: roles and structure
- During: knowing something is wrong
- After: blameless reviews
- SLIs, SLOs and SLAs
- Grafana Alerting
- Grafana OnCall
- Grafana Incident

## Claims and numbers

- With an agreed SLI (“errors in a 15-minute period”) and SLO (“no more than 3% of requests in 10 minutes”), writing an alert is just translating the sentence into PromQL or LogQL.
- The book’s rule is the percentage of 5xx responses over ten minutes with a threshold of 3, the SLO.
- Its Insights page summarises 90 days of incidents and is meant for silver to review with gold.

## Terms

Commander, Communications, Technical lead, white-box, Black-box, hero culture, reduce, threshold, evaluation group, Contact points, Silences, alert groups, escalation chains, Across the books, SLI, SLO, SLA, Four golden signals

## Interview line

I prepare for incidents before they happen: clear roles (commander, communications, technical lead), an escalation policy, protected channels and pre-written status messages, with gold, silver and bronze levels agreed for serious incidents. I detect with RED for request-driven services, USE for resources, and black-box probes for the user’s view, alert on a few SLIs per service, and finish with a blameless review built from a recorded timeline.

## On AWS

On AWS, AWS Systems Manager Incident Manager provides on-call schedules, escalation plans, engagement by SMS, voice and chat, response plans with runbooks, and a timeline; it is triggered from CloudWatch alarms or EventBridge. AMP’s Alertmanager pages through SNS. Amazon Managed Grafana includes Grafana alerting with contact points such as SNS. CloudWatch Synthetics canaries are the black-box probes, CloudWatch RUM the user’s view. Grafana OnCall and Incident are available in Grafana Cloud.

## Takeaways

- Roles, escalation and communication are decided before the incident.
- RED for requests, USE for resources, black-box for the user’s view.
- Blameless reviews from a recorded timeline; Grafana Alerting, OnCall and Incident cover detection to review.
