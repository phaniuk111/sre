# SRE chapter 19: SRE at the tipping point

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-19`. Read: full text, two passes.*

## Summary

AI-driven development is pushing the cost of writing plausible code towards zero and the rate of change beyond human timescales. The SDLC still holds (work is roughly serial, and it loops), but non-functional properties such as reliability can be destroyed by a single line, and the SDLC is social as well as technical (Conway's law).

- **Plan**
- **Analyse**
- **Design**
- **Build**
- **Test**
- **Deploy**: The hard boundary stays
- **Maintain**

If you ship ten times faster and change nothing else, expect roughly ten times the incidents, odd interactions and resource exhaustion. Cherry-picking fixes gets harder, versioning stops partitioning risk well, staging environments drift further from production, and manual production debugging won't keep up.

Humans stay essential until AGI, because models hallucinate and outages need accountability. Expect longer causal chains, skill erosion and the risk that prevention gets under-funded because response becomes so good. The bright spots: observability gets cheaper and formal methods become more practical.

## Key ideas

- what changes when writing code becomes nearly free
- the chapter’s predictions for rollouts, debugging and incidents
- what “strategic incoherence” means and how to counter it

## What the lesson covers

- The big picture
- More from the chapter

## Terms

Plan, Analyse, Design, Build, Test, Deploy, Maintain, roll-forward may become primary, Strategic incoherence

## Takeaways

- Faster delivery without other changes means proportionally more incidents.
- Agents generate technical debt tirelessly unless specifications keep the design coherent.
- Humans stay the understanders of last resort, so keep skills sharp.
