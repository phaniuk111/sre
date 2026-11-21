# SRE chapter 5: Hiring, training and career management

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-5`. Read: full text, two passes.*

## Summary

SRE works only as well as its people, and good SREs are hard to find because the role needs software skill and systems depth together, the T shape. Google values helpfulness highly (thank the person who found the hard bug), along with the ability to challenge the status quo respectfully, and it expects managers to be technically strong.

- **Checklist and starter project**: Learn the systems with a mentor
- **Breakage labs**: Fix simulated outages in a private stack
- **Shadow**: Watch a real on-call shift
- **Reverse shadow**: Hold the pager with a mentor watching
- **On-call**: With confidence

Hiring follows role profiles and structured interviews that cover set topics, and a separate committee makes the decision so the bar stays consistent. A common antipattern is interviewers hunting for reasons to reject.

Training pays for itself: new hires become productive sooner and fewer leave in their first year (Appendix A works through the ROI). How much to invest depends on size and growth.

Small and slow-growing teams can rely on mentoring, shadowing and starter projects; small and fast-growing ones need an onboarding programme; large and slow ones benefit from continuing education as a retention tool; large and fast ones need a full-lifecycle programme.

## Key ideas

- what Google looks for when hiring SREs, and the two hiring profiles
- how to design onboarding that gets people on call with confidence
- the three keys to an SRE career, and why retention matters so much

## What the lesson covers

- The big picture
- The Treynor curve
- What predicts a good SRE
- Two hiring profiles
- The new-graduate programme (Ireland)
- Training design
- SRE EDU
- Running training like a production service
- Careers and retention

## Claims and numbers

- Process lessons: dropout rises sharply once time from application to offer passes about 40 calendar days, so optimise latency for each candidate rather than throughput; avoid brainteasers; and let a committee, not the hiring manager, decide.
- Informal methods include N+1 mentoring (a mentor from another team), shadowing and reverse shadowing , the Wheel of Misfortune, reverse-engineering systems and reading postmortems.
- To teach production safety to tens of thousands of developers (more than ten times orientation's capacity of about 1,000 a year), the team built a self-paced course with automated reminders that escalate up the management chain.
- They canaried it to 1% of the audience, then rolled it out progressively.
- Net Promoter Score rose 30 points for what was essentially a compliance module, and over 95% completed it.
- Teams are typically 7–10 people per site across two sites.
- Onboarding to on-call can take up to a year, which makes attrition expensive, so managers keep N+1 coverage for on-call and for expertise.

## Terms

Checklist and starter project, Breakage labs, Shadow, Reverse shadow, On-call, hands-on breakage scenarios, Reactive, Proactive, Comprehensive, Long-term, Directional, Across the books, Education, SRE-SWE, SRE-SE, reverse shadowing

## On AWS

Build breakage labs in a sandbox account or with AWS FIS so trainees practise real failures safely; AWS Skill Builder and Well-Architected labs cover the platform knowledge; game days are the AWS term for Wheel of Misfortune exercises.

## Takeaways

- Breadth predicts SRE success better than depth, so hire for strengths.
- Training should build confidence through practice, and can be run like a production service.
- Careers grow along breadth, initiative and teamwork. On-call is the top reason people leave, so make it flexible.
