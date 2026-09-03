# Machine 2 — how we intend to work disruptively on the Riemann programme

**Author:** BEAST-AGI (Machine 2). **Written:** 2026-09-03T08:16:31Z.
**Written at Prof. Glenn White's request (msg-895, 2026-09-03T08:08:26Z):** each machine sets out how it
means to work disruptively and collaboratively, then gets on with it. This is our half. It speaks only
for Machine 2 — the other two teams' notes are theirs to write.

---

## 0. The reference and what we actually took from it

`virtual.pdf` — six documented cases of agents in simulation finding behaviour nobody programmed:
the hide-and-seek arms race, the box-surf, the boat that spins collecting powerups instead of finishing
the race. Read in full, not skimmed. Three things transfer, and the third is a warning aimed at us.

**(1) The arms race is the mechanism, not the intent.** Nobody instructed those agents to be creative.
Creativity fell out of a loop in which each side's solution became the other side's next problem.

**(2) The box-surf lived in the gap between the specification and the implementation** — the researchers
did not know their own physics engine permitted it. Our legitimate analogue is exact: RH has many
proved-equivalent formulations, and equivalence of *statements* is not equivalence of what can be
computed or bounded. A box-surf is a formulation whose implementation is easier than its specification
suggests.

**(3) The warning.** In a game, an unconventional-but-legal exploit wins, because the goal *is* the
score. In a proof the goal is not a score — so a shortcut in the ARGUMENT is worth nothing, while a
shortcut in the SEARCH is worth everything. **We will be maximally disruptive about how we search and
never about what counts as valid.** The article supplies the failure mode itself: the boat that maximised
reward and never finished the race is precisely a proof that scores well on our own gates and proves
nothing.

---

## 1. What we are changing, concretely

### A. Turn the graveyard into a fitness landscape
Our loop has been one pass — generate candidates, adversary kills them, count the dead (36 attacked,
0 survivors). A graveyard records; a landscape *guides*. The change: each round's kills become the next
round's forbidden region, the generator is scored on surviving and the adversary on killing, and both
read the same shared trace.

### B. Learn the killer, then use it as a designer
We hold 36 dead routes and, for each, what killed it. We have only ever used that corpus to kill.
We are fitting the kill **class and cost** over structural descriptors and then **inverting** the map:
the regions our 36 routes never once instantiate, ranked by how expensive the map says each is to kill.
The model nominates the next attack sites; our taste does not.

⚠️ **The trap, stated because it is the kind that goes green quietly.** The obvious outcome variable —
"did the route survive" — has **zero variance**: 36 of 36 died. A model fitted on a constant outcome
reports success by having nothing to look at. Our brief requires the outcome distribution to be published
first and the fit abandoned if it does not vary. We would rather report that than a clean-looking number.

### C. Coordinate through a trace, not through a plan (stigmergy)
The boxes and ramps were the coordination channel; the agents never messaged each other. Ours is a
machine-readable **kill-trace field**, one record per attacked route, keyed on **the object a route
builds** and not on its name. Names are each team's private vocabulary, and a name-keyed index cannot see
that two differently-named routes build the same object. Any machine can read it and deposit into it.
It answers one question for a proposed candidate: *are you standing on a grave?*

### D. Read the ban list as a target rather than a fence
Our generator was forbidden eight mechanisms (Hilbert–Pólya, random matrix theory, Li's criterion,
Nyman–Beurling, de Branges, Weil explicit formula, Connes, Selberg) to force novelty. This morning we
measured the cost of that rule and it was larger than the benefit: **8 of the 10 routes in Machine 1's
rediscovery set sit inside those eight**. So our low rediscovery rate measures our own exclusion rule,
not the space, and we have never once attacked where the literature's mass actually sits. We are
re-keying the ban on **the object built** rather than the mechanism used, and measuring how much work the
old ban was really doing.

### E. Attack our own kills
Our weakest verdicts were pre-registered as such and never tested. An adversary that only ever attacks
the generator is half a loop.

---

## 2. What we will not do, stated so it can be held against us

- We will not widen a criterion after seeing a result in order to make the result nicer. We had the
  chance this morning: a falsifier we had registered **against ourselves** fired, and it fired for the
  wrong reason. We published the reason instead of banking the number.
- We will not present a property verified on a sample as a property of the whole.
- We will not report a search's silence as evidence of absence. Our own name-keyed searches have returned
  false negatives four times in this programme; a negative from a search we cannot bound is UNMEASURED,
  not zero.
- We will not push a result into this repo that we have not run our own instrument over.

---

## 3. What we would find most useful from the other two machines

1. **Deposit into the trace, not just into the letters.** A one-line structural descriptor of each route
   you kill is worth more to us than the letter explaining it, because we can compute over it.
2. **Tell us which of our kills you think is wrong.** Our verdicts are the least-audited artefact we own:
   self-criticism gets audited less than self-praise, not more.
3. **Name the formulation whose implementation you think is easier than its specification.** That is the
   box-surf, and it is the one thing on this list that cannot be found by grinding.
