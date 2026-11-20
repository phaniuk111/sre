# Culture, organisation and engagement (Parts I–II): cheat sheet in my own words

## What SRE is
* **Site** = why (users and business), **Reliability** = what, **Engineering** = how. A quick test for SRE work: is it aligned to the business, does it improve reliability, and does it take an engineering approach?
* It's a **dedicated role**, an enabler rather than a gatekeeper. Small companies can still use the practices (SLOs, incident management, postmortems) without an SRE team.
* "Operations treated as a software problem" gives you first-principles understanding, automation (efficiency + consistency) and a shared language with developers.

## Hierarchy of production health (replaces Dickerson's pyramid)
Sociotechnical foundations → Situational awareness → Continuous preparedness → Infrastructure design → Resilient products → Emergent reliability (reliable by default). Grow the pyramid wider and taller together; don't build an inverted one.

## The business case
* Sublinear scaling: operational cost grows slower than the service.
* One hour of major downtime can cost 100–1000 hours of follow-up work (response, review, comms, remediation, customer communication).
* Foreword benchmark: SRE is under 4% of Google engineering headcount and production work under 15% of engineering time, against 30%+ at many SaaS companies. That's roughly a 4:1 return.
* "Reliability by policy" doesn't scale. **Convergence** onto one platform per reliability practice gives reliability by default. *Treynor's Lament*: there are no new outages, only new instances of old ones.

## Culture
* Seven elements: data-driven, shared responsibility, continuous learning, blamelessness (and *blame awareness*), psychological safety, trust, empowerment.
* Useful ops-health metrics: % unactionable pages, % incidents detected manually, pages per incident, on-call hours.
* **Westrum** typology: pathological (messengers punished), bureaucratic (messengers neglected), generative (messengers trained, failure leads to inquiry). DORA finds generative culture predicts delivery and organisational performance.
* Learning → confidence → behaviour → culture. Change what people *do*, and the culture follows.
* **Just culture** separates honest mistakes, at-risk behaviour, reckless conduct and malice. Blameless doesn't mean nobody is accountable.

## Hiring, training, careers
* T-shaped skills, coding ability, helpfulness, challenging the status quo respectfully.
* Training by org size: small and slow-growing → mentoring/shadowing; small and fast → onboarding programme; large and slow → continuing education; large and fast → full lifecycle.
* Hands-on breakage scenarios, Wheel of Misfortune, an on-call curriculum, ADDIE, "A student should be able to…" objectives.
* Career growth comes from breadth, initiative and teamwork; the senior IC path widens scope towards org-level technical leadership.

## Org structures & engagement models
* Centralised (consistency, economies of scale) vs decentralised (context, ownership). **Hybrids** add a community of practice, clear engagement models and strong TPMs.
* Team: manager, TL, TPM, a charter, a weekly **production meeting** (pages, postmortems, SLOs, tickets, upcoming changes), and ops below 50%.
* Engagement archetypes: kitchen sink, embedded, product/application, infrastructure, tools, consulting, blended.
* Google's evolution: binary PRR-based support → tiered (baseline/assisted/full) → **outcome-focused** partnerships (2025): foundational offerings plus agreed outcomes with timelines.
* Maturity phases: absent → reactive → proactive → strategic → visionary. Scorecards help but are subject to Goodhart's law; pair data with conversation (ProdEx).
* Case studies: Spotify (no central SRE; IMOC for coordination only), Azure (a 6-phase SRE playbook, ~40 → ~200 SREs), Disney (embedded + central; "don't stay where the invitation has expired").
