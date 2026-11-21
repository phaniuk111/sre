# Platform product templates

Working templates after the "Why Developer Experience Matters" and "Platform as a Product" chapters of *Platform Engineering at Google*. Copy the one you need.

## 1. Jobs to be done
Ask what the developer is trying to accomplish. The feature they request is one possible answer.

| | |
|---|---|
| **Who** (persona: new hire, frontend specialist, principal backend engineer, ML engineer…) | |
| **The request as stated** | "I need a dashboard of build logs" |
| **The job** ("When ___, I need to ___, so I can ___") | "When my deployment fails, I need to find the cause quickly, so I can fix it" |
| **What they do today** (the alternative you compete with) | scroll raw logs; ask in chat |
| **How often** (aim for several times a day) | |
| **Other ways to do the job** | clearer error message; chat notification linking to the failing step; detect the failure before they notice |
| **How we'd know it worked** | time from failure to fix; fewer support questions |

## 2. Hypothesis and hand-run MVP
> We believe that by solving **X** for **developer Y**, we will achieve **outcome Z**.

Before writing code, do the job by hand for two or three friendly teams for two weeks. Record:

| Team | What we did for them | Edge cases found | Would they miss it if we stopped? |
|---|---|---|---|
| | | | |

Write code only when a handful of hand-served teams are happy.

## 3. Capability roadmap: now, next, later
Outcomes, not features. "Enable self-service database provisioning", not "build database API v1".

| Now (being built, high confidence) | Next (in discovery) | Later (direction only) |
|---|---|---|
| | | |

## 4. Build, buy or partner
| Question | Answer | Leaning |
|---|---|---|
| Is this a core competency or a competitive advantage? | | build |
| Does an existing product or open-source project solve 80% of it? | | buy or partner |
| Can we adopt one and spend our engineering on the last mile that is specific to us? | | integrate |
| Lifetime cost of owning it (people, on-call, upgrades) against the licence | | |

## 5. Developer-experience review
Score each pillar 1–5 after watching three developers use the platform.

| Pillar | Evidence | Score |
|---|---|---|
| Usability and simplicity | | |
| Discoverability and onboarding (time to first "hello world") | | |
| Fast, clear feedback (build and deploy times; error messages that say what to do) | | |
| Reliability and trust | | |
| Workflow integration (one API behind console, CLI, IaC and agents) | | |
| Flexibility and escape hatches (defaults for ~80%; a supported way out) | | |
| Documentation and support | | |

Is this "broccoli"? Are we making a small internal tool pay the setup cost of our largest product? If yes, add a lighter path.

## 6. Product surface area, for people and for agents
| Surface | Human check | Agent check |
|---|---|---|
| Interfaces | consistent CLI, console and API | published API specification; predictable names; tool schemas; errors with plain-text context |
| Documentation | accurate, searchable, working examples | structured, machine-readable, owned, with a review date |
| Onboarding | time to first "hello world" | can an agent create the first service unaided? |
| Support and communication | channel, office hours, release notes, roadmap | |

## 7. Deprecation checklist (a launch in reverse)
- [ ] The replacement is ready and clearly better for each kind of user
- [ ] A written plan: reason, timeline, migration path
- [ ] Callers identified from logs, not from memory
- [ ] Migration tooling, and pairing for the hard cases
- [ ] Announcements in several channels, repeated as dates approach
- [ ] Brownouts scheduled (see POC 18 `brownout_plan`)
- [ ] The off switch has a date and an owner, and is used

Antipattern to avoid: the ghost ship, an old platform left to decay with no owner.

## 8. Education plan
After the "Education and Platform Engineering" chapter.

| | |
|---|---|
| Topics in scope (only what the platform supports) | |
| Who has time allocated to support, writing and teaching on each component team | |
| Top five repeated questions this quarter, and the page or class that now answers each | |
| Documentation pages with an owner and a review date (%) | |
| External material we curate instead of writing | |
| Training on specification and verification for AI-assisted work | |
