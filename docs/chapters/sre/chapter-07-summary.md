# SRE chapter 7: SRE engagement models

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-7`. Read: full text, two passes.*

## Summary

An engagement model is the written contract between SRE and product teams: how they work together, what SRE offers and how SRE chooses its work. Org structure answers "who reports to whom"; the engagement model answers "what work do we do together".

- **1 · PRR gate**: Supported or not. Thorough, but sticky and late
- **2 · Tiers**: Baseline, assisted, full. Still about who holds the pager
- **3 · Outcomes (2025)**: Foundational offerings for all, plus time-boxed engineering efforts

Archetypes: kitchen sink (often a renamed ops team, reactive), embedded, product/application (easy to show value), infrastructure (effectively platform engineering), tools, consulting, and blended.

Google moved through three models. First, a binary "SRE-supported or not" gated by **production readiness reviews**: SLOs, less paging, docs, progressive rollouts, backups, capacity plans, failure domains. That was thorough but slow and "sticky".

Next came baseline / assisted / full **tiers**, which were still centred on who held the pager. Since 2025 it has been **outcome-focused**: every service in a partnership gets foundational offerings, and SRE and dev agree concrete outcomes with rough timelines, such as faster detection and mitigation, an exercised DR plan, lower operational cost, or faster releases and rollbacks. Then they split the work.

## Key ideas

- the difference between an org structure and an engagement model
- the scoping archetypes, and how consumer and enterprise SRE differ
- why Google moved from launch reviews, to tiers, to outcomes

## What the lesson covers

- The big picture
- A second worked example: the Azure playbook
- Organisation structure vs engagement model
- Scoping archetypes
- Consumer vs enterprise
- Google's three engagement models
- Case studies
- Beyond PRRs

## Claims and numbers

- An SLO of 99.99% under 10 ms needs a very different design from 99% under 250 ms.

## Terms

production readiness reviews, tiers, outcome-focused, contract of work, Kitchen sink, Embedded, Product or application, Infrastructure, Tools, Consulting, Blended, communicate first, mitigate second, Foundational offerings, outcome, efforts, Persistent Disk

## On AWS

Enterprise Support's Well-Architected and Countdown (launch readiness) engagements resemble PRRs; AWS's own Operational Readiness Reviews are a public example of the checklist style.

## Takeaways

- The engagement model is the contract of work, separate from who reports to whom.
- Building an engagement around on-call is an antipattern. On-call exists to inform engineering.
- Consumer SRE mitigates first. Enterprise SRE communicates first.
