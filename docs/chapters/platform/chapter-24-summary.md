# Platform chapter 24: Education: why teaching belongs to the platform team

*Platform Engineering at Google (early release). Course lesson: `#pe-10`. Read: full text, one pass; all figures seen.*

## Summary

The chapter opens with a rule from its author that is worth memorising: if something is accidentally complex, simplify it; if it is inherently complex, educate.

Its argument has three steps. Engineering performance comes from culture. The root of good culture is learning and growth. And somebody has to be responsible for the learning that can’t be left to chance, which is most naturally the platform organisation.

Management thinkers, academic researchers, Google’s own team studies and the DORA research all point the same way: culture is at the root of performance. The culture they describe is **psychological safety**, where it is safe to be wrong, safe not to know, and safe to make an honest mistake.

The chapter makes a sharper point than “people work better when they aren’t afraid”. Safety is what lets information move and makes learning valued.

## Key ideas

- Why a culture of learning is the root of engineering performance
- What a computer science degree can’t cover
- Why education fits the platform organisation, and how to staff it
- What AI changes: documentation, specification and verification

## What the lesson covers

- The big picture
- A culture of learning
- Why universities can’t do it for us
- Why education belongs with the platform
- Education and AI

## Claims and numbers

- An old model from the 1970s, the “surgical team”, gives the critical work to the best engineer and has everyone else support them.
- All the lectures, labs and homework in a computing degree add up to less than 18 months of full-time work, and less than a third of the popular “10,000 hours to mastery” figure.
- Enrolment in the US grew about fivefold in 15 years and teaching staff didn’t, so early courses are graded automatically on whether the output is right.
- Being the person 10,000 Java engineers bring their questions to is another.

## Terms

psychological safety, Single game, Endless game, learning debt, brittle productivity, A thought experiment, The field is young, There aren’t enough hours, The content is skewed, Student teams aren’t teams, Expertise accumulates there, The missions match, curate, amplifier, Clean up your documentation, Teach specification

## Interview line

I think of education as part of the platform’s job. The platform team sees every team’s problems and decides what the standard way is, so it should also explain that way. I’d give a few engineers on each platform component real time for support, writing and teaching, and I’d treat repeated questions as toil to automate with documentation. With AI in the picture it matters more: assistants answer from our docs, and the scarce skills are now specifying what we want and verifying what we got.

## On AWS

Make documentation part of the golden path: every template ships a README, a runbook and architecture notes in the repository, rendered in the developer portal. Keep them current with ownership metadata and a staleness check in CI, because that corpus is what an internal assistant (Amazon Q Business or a Bedrock knowledge base) will answer from. Scope training to what the platform supports, and curate AWS Skill Builder paths instead of writing general cloud courses yourself. Use game days and Well-Architected reviews as teaching moments, not audits.

## Takeaways

- If it is accidentally complex, simplify. If it is inherently complex, educate.
- Give the next task to the most junior engineer who can do it with guidance.
- Education fits the platform team: it sees everything and sets the standard way.
- AI answers from your docs, and makes specification and verification the scarce skills.
