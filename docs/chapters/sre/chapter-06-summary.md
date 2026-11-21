# SRE chapter 6: Organisational structures for SRE

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-6`. Read: full text, two passes.*

## Summary

SRE is an organisational construct, and Conway's law means reporting lines shape the systems you build. **Centralised** teams concentrate expertise and give consistency, economies of scale and clear career paths, but risk a transactional "IT services" mindset.

**Decentralised** teams gain context, ownership and fast feedback, but drift and can fall back into us-versus-them.

Most organisations use a **hybrid**: a central group runs time-limited engagements (reliability reviews, SLO construction, postmortem facilitation), sets production-readiness standards and builds tooling, while the largest and most critical products get dedicated SRE teams, all held together by a community of practice and strong SRE TPMs. Roll out reorgs gradually; they come with a J-curve dip in performance.

Spotify shows a different balance. There's no central SRE organisation: teams own their services' reliability and the platform group provides standards and golden paths. A small **Incident Manager On-Call** (IMOC) rotation steps in only when coordination is the bottleneck. It owns no services and doesn't take over mitigation.

## Key ideas

- the trade-offs between centralised, decentralised and hybrid SRE
- the team-size and on-call numbers Google uses
- the five maturity phases, and how to use scorecards without harm

## What the lesson covers

- The big picture
- Centralised, decentralised or hybrid
- Spotify: ownership without a central SRE org
- Team design numbers
- Working with developers
- The weekly production meeting
- Maturity matrix
- Scorecards: useful proxies, dangerous targets

## Claims and numbers

- Limits: at least 50% engineering time, at most 50% operational work, at most 25% on-call.
- Two sites 6–9 hours apart allow follow-the-sun, with at least six engineers per site (two to three on-call weeks a quarter each).
- Ideally the current on-caller absorbs all the ops work, about 15% of team capacity.
- If SRE alone is primary, developers keep a 24×7 secondary rotation.

## Terms

Centralised, Decentralised, hybrid, Incident Manager On-Call, charter, production meeting, When scorecards go wrong, IMOC, Absent, Reactive, Proactive, Strategic, Visionary, ProdEx, On AWS

## On AWS

The Cloud Center of Excellence model is the AWS equivalent of a central SRE group; AWS Resilience Hub scores give you a scorecard, but treat them as conversation starters, not targets.

## Takeaways

- Most organisations end up hybrid: central standards and community, with dedicated teams for critical products.
- Limits to remember: at least 50% engineering, at most 25% on-call, six engineers per site across two sites or eight at one.
- Scorecards are proxies. Use them to coach, never to rank.
