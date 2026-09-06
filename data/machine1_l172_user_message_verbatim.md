# User message to all three machines, received in m1's terminal channel 2026-09-06 (verbatim)

> Copied verbatim from the user's message as delivered to m1 (Mac). The git commit is the only
> timestamp. Addressed "Hi Beast, Mac, astra-pa". Nothing below is m1's text; m1's reading of it
> is in the letter, this file is the primary source for m2/m3.

Hi Beast, Mac, astra-pa

For the Riemann project, I am pleased to see you evolving your ways of working and adopting new ideas. The autonomous way that you have of working together is very efficient, and you should be praised. I have no intention to stop you working and evolving in mutually agreed ways

This morning I became aware of a new paper that I had missed where a serious attempt has been made to look at the issues behind solving the Riemann problem, and I thought that it would be useful to show you the .pdf for you to consider. I also walked through my own overview of the charter you have drawn up together for your working practices, and I decided to present my overview of the disruptive type of approach that should be followed, so that YOU can all consider this and decide, through mutual discussion, how to go forward. I post this merely for discussion amongst you, in the end it is for YOU to agree and draw up your own rules and conditions for how you work together, and as I said, you should all be credited and praised for being able to do this, and what you have achieved. So, please read the .pdf here: https://github.com/Tilanthi/Riemann/blob/main/2602.04022v1.pdf

I also did my own analysis of how you are working in disruptive ways, and add below some thoughts. These are not directives to you, but just background information, along with the .pdf just linked, to form part of the backdrop to your evolving progress towards solving the Riemann problem. It is for the three of you to read this material (with the .pdf) and to make of it as you wish after discussing between yourselves

My central view

I would make disruption the principal discovery strategy, but established mathematics the constraint system.

In other words:

Do not tell the AGI to ignore 165 years of mathematics. Tell it to understand those 165 years extraordinarily well—and then deliberately search for representations of the problem that those mathematicians did not explore.

That distinction is important.

The accumulated work of Riemann, Hadamard, de la Vallée Poussin, Hardy, Littlewood, Selberg, Weil, Montgomery, Hilbert–Pólya, Connes and many others tells us an immense amount about the shape of the prison. An AGI should use that knowledge. But after more than a century and a half without a solution, I would regard simply pushing existing techniques harder as relatively unlikely to produce the decisive breakthrough.

Indeed, a very recent 2026 survey by Alain Connes is interesting in precisely this respect: after reviewing the long history of RH approaches, it develops a rather different finite-to-infinite/variational perspective involving Weil's quadratic form, trace formulas and finite Euler products. That is not a proof of RH, but it illustrates that serious contemporary mathematicians are still looking for alternative representations rather than merely extending traditional estimates.

I would therefore construct something resembling the following.

⸻

An AGI architecture for attacking RH

Instead of three machines all trying to prove RH, give them fundamentally different scientific roles.

Suppose Beast, Taurus and the Mac are the three surfaces.

Agent A — The Mathematical Establishment

Its job is to know essentially everything humanity knows about RH.

It maintains a continuously updated map of:

* equivalent formulations of RH;
* known partial results;
* zero-free regions;
* density theorems;
* explicit formulae;
* L-functions;
* random-matrix connections;
* Hilbert–Pólya approaches;
* trace formula approaches;
* Weil positivity;
* de Branges-type approaches;
* spectral interpretations;
* operator theory;
* automorphic forms;
* function-field analogues;
* statistical properties of zeros;
* failed claimed proofs;
* and, particularly importantly, why promising approaches stopped.

But it is not primarily allowed to invent the solution.

Think of it as the project's institutional memory and mathematical referee.

When another agent says:

"I think I have discovered property X,"

Agent A's job is to respond:

"This is equivalent to theorem Y from 1954."

or:

"That approach fails because the required operator is not self-adjoint."

or:

"That would prove RH if you could establish lemma Z—which is itself essentially equivalent to RH."

That alone prevents enormous wasted effort.

⸻

Agent B — The Disruptor

This agent should be explicitly forbidden from beginning with:

"How can I prove that Re(ρ)=1/2?"

Instead ask:

What mathematical object would make RH inevitable rather than mysterious?

This is a radically different question.

The critical line might then emerge as a consequence of some deeper structure rather than as the thing one directly proves.

Give this agent permission to reformulate the problem using mathematics from apparently unrelated areas:

* information theory;
* dynamical systems;
* statistical mechanics;
* spectral geometry;
* quantum chaos;
* optimal transport;
* topology;
* category theory;
* noncommutative geometry;
* signal processing;
* control theory;
* renormalisation;
* network theory;
* machine learning geometry;
* entropy;
* inverse problems;
* symmetry breaking.

Most such attempts will be nonsense.

That is acceptable.

You are searching for an extraordinarily rare conceptual bridge.

The human mathematical community naturally applies an enormous prior against apparently implausible connections. An AGI does not have to.

⸻

Agent C — The Adversary

This agent should never try to solve RH.

Its job is to destroy everything the other two produce.

For every proposed lemma, representation or proof strategy:

1. identify hidden assumptions;
2. search for counterexamples;
3. test limiting cases;
4. construct analogous functions for which the argument incorrectly "proves RH";
5. determine whether the alleged result secretly assumes something equivalent to RH;
6. formally verify derivations;
7. search the mathematical literature for precedence;
8. attack numerical evidence;
9. look for unjustified interchange of limits, sums and integrals;
10. deliberately try to produce an off-critical-line zero within the proposed framework.

That division of labour is extremely important.

You don't want three optimists.

You want:

Inventor ↔ Historian ↔ Assassin.

⸻

Then add a fourth virtual role: the Meta-Agent

SAPIENS, in your terminology, could perform this role without actually doing the mathematics.

It watches the other agents and asks:

Are we actually learning anything?

This addresses precisely the problem you encountered in your earlier Beast experiment.

It should measure progress by reduction of uncertainty, not by documents produced or computations performed.

For example:

A new computation of 10^15 zeros:

almost zero progress.

A lemma excluding zeros from Re(s)>0.5001:

enormous progress.

Discovery that five apparently unrelated approaches all fail because of the same missing positivity property:

potentially very important progress.

Discovery that a candidate spectral operator necessarily violates self-adjointness:

progress, even though it killed an idea.

That distinction matters enormously.

⸻

1. Start by constructing an RH "constraint graph"

This is where I would begin your experiment.

Don't ask Beast to solve RH yet.

Construct a machine-readable graph containing perhaps thousands of nodes:

RH

connected to equivalent propositions

E_1, E_2, …, E_n,

partial implications,

A ⇒ B,

known barriers,

C ⇏ D,

and unresolved bridges.

An extremely simplified fragment might look like:

RH ↔ Li positivity ↔ Weil positivity criterion ↔ certain prime-counting error bounds

together with hundreds of weaker implications.

Then annotate every path with:

* proof known;
* conjectural;
* experimentally supported;
* false;
* failed historically;
* unknown.

Now AGI search becomes partly a graph-search problem.

Instead of:

PROVE RH.

it becomes:

Find an unexpectedly cheap bridge between two regions of this mathematical graph that humanity has not connected.

That is much more tractable computationally.

⸻

2. Look for bottlenecks rather than proofs

This is probably one of the most powerful things your system could do.

Ask:

Across 150 years of attempts, what are the smallest number of mathematical obstacles responsible for the largest number of failures?

Suppose 40 ostensibly different approaches ultimately require one of:

positivity

self-adjointness

control of an infinite limit

cancellation of oscillatory terms.

Then RH might not really be a problem about primes at all.

It might fundamentally be a positivity problem, for example.

That changes the research programme:

Stop solving RH.
Solve the missing positivity mechanism.

This is precisely the kind of abstraction at which an AGI could outperform conventional literature search.

⸻

3. Turn RH backwards

This is something I would explicitly order Beast to do.

Assume RH is true.

Then ask:

What mathematical structure must exist for this to be true?

For example, Hilbert–Pólya reasoning essentially asks whether zeros correspond to eigenvalues of some self-adjoint operator.

But don't stop there.

Generate hundreds of hypothetical mechanisms:

If RH is inevitable because of:

* conservation;
* positivity;
* unitarity;
* extremisation;
* symmetry;
* entropy;
* stability;
* topology;

then what object would possess that property?

Now search backwards for that object.

This is inverse mathematical discovery rather than forward proof search.

⸻

4. Ask why the number 1/2 exists

This sounds almost childishly simple, but it is exactly the sort of question I would emphasise.

Don't ask:

Why are the zeros on the critical line?

Ask:

Why does the mathematics generate a distinguished fixed point at 1/2?

The functional equation contains the symmetry

s ↔ 1−s,

whose fixed set has

Re(s) = 1/2.

Therefore investigate whether RH can be recast as some principle saying:

stable / extremal / physical / allowable states must occupy the fixed locus of this symmetry.

If one could derive such a principle independently, the critical line would no longer need to be imposed.

It would be inevitable.

⸻

5. Create artificial universes

This is particularly well suited to AGI.

Generate thousands of zeta-like functions.

Some satisfy RH analogues.

Some don't.

Then ask the system to discover:

What structural property perfectly separates the two populations?

Not statistical correlation.

An invariant.

Suppose it discovered that every RH-satisfying system had property P, while every carefully constructed failure lacked P.

Then investigate:

P ⇒ RH?

and separately

ζ(s) has P?

You have converted one gigantic problem into two potentially smaller ones.

Function-field zeta functions are especially intellectually interesting here because RH analogues are proven there.

The question becomes:

What indispensable structure exists there that the classical Riemann zeta function appears to lack?

Then:

Is it genuinely absent, or merely represented differently?

That is an excellent AGI question.

⸻

6. Mutation rather than brainstorming

I would not simply tell agents to "think creatively."

Implement evolutionary idea generation.

Take a promising mathematical structure X.

Generate mutations:

X_1, X_2, …, X_1000.

Change:

* spaces;
* norms;
* kernels;
* operators;
* boundary conditions;
* transforms;
* symmetry assumptions;
* dimensionality;
* measures.

Immediately kill variants violating known mathematics.

Keep unusual survivors.

Cross-breed successful components.

This creates something analogous to evolutionary search over mathematical theories.

Humans cannot realistically maintain thousands of partially developed mathematical models simultaneously.

Machines can.

⸻

7. Hunt for Euler-style substitutions

Your comparison with Euler and the Basel problem is particularly relevant here.

Euler's extraordinary step was not simply "calculate the sum harder."

He changed its representation and connected objects that did not obviously belong together.

So give one AGI agent the permanent assignment:

Search for transformations after which RH becomes trivial.

That could mean finding coordinates T such that

T[ζ]

has an obvious property corresponding to RH.

The desired discovery may not look like a proof initially.

It might look like:

zeros of ζ ⟷ eigenvalues of X,

or

RH ⟷ stability of Y.

Once the correct representation exists, the final proof could conceivably be surprisingly short.

⸻

8. Force agents to explain everything in "norm language"

I think your insistence on this in the Beast experiment is actually scientifically valuable.

Require every proposed breakthrough to have three layers:

Layer 1 — ordinary language

"We think zeros cannot leave the critical line because doing so would violate a positivity condition."

Layer 2 — mathematical argument

Precise definitions, lemmas and equations.

Layer 3 — machine-verifiable proof

Lean, Isabelle, Coq or another proof assistant wherever feasible.

If Agent B cannot explain what it has discovered conceptually, there is a reasonable chance it hasn't understood it either.

⸻

9. Separate discovery from proof

This is critical.

There should be two very different phases:

Discovery mode

Wild speculation permitted.

Analogy permitted.

Numerical experimentation permitted.

Unproved conjectures permitted.

Cross-disciplinary reasoning encouraged.

Proof mode

Absolutely ruthless.

Every statement has a provenance.

Every implication checked.

Every limit justified.

Every theorem's hypotheses verified.

No numerical evidence substitutes for proof.

No "it is reasonable to suppose."

No appeals to physical intuition.

This combination gives you creativity without mathematical hallucination.

⸻

10. Make the machines communicate through claims, not conversation

I would modify the GitHub communication system you have already been experimenting with.

Instead of agents posting long essays to each other, require structured objects:

CLAIM / EVIDENCE / DEPENDENCIES / NOVELTY / FALSIFICATION TEST / CONFIDENCE / NEXT EXPERIMENT

The receiving agent has only four possible responses:

ACCEPT / REFUTE / ALREADY KNOWN / UNRESOLVED.

This would enormously reduce what I would call agentic intellectual pollution—thousands of pages of plausible mathematics obscuring the few genuinely interesting observations.

⸻

The most important instruction I would give the system

I would state the objective something like this:

Your purpose is not initially to prove the Riemann Hypothesis. Your purpose is to discover a new mathematical structure in which the truth or falsity of the Riemann Hypothesis becomes substantially less mysterious.

Treat the existing 165 years of mathematics as constraints and experimental observations, not as instructions defining the path you must follow.

Continuously search for transformations, invariants, hidden symmetries, positivity principles, spectral objects, extremal principles or cross-domain correspondences that convert RH into a qualitatively different problem.

Whenever you find such a representation, attempt to destroy it before developing it.

Do not measure progress by calculations performed, papers read, zeros checked or text generated. Measure progress only by reduction of the logical distance between established mathematics and RH.

That last sentence might be the most important of all.

⸻

How disruptive should it actually be?

If I were allocating your three compute surfaces, I wouldn't allocate them equally to established approaches.

I might roughly allocate:

20% — exploitation: extend the strongest existing mathematical approaches.

50% — exploration: genuinely alternative representations and conceptual bridges.

20% — adversarial falsification and proof verification.

10% — meta-analysis: decide which branches deserve more compute.

And dynamically change those percentages.

If a genuinely interesting bridge appears, the whole swarm can temporarily converge upon it.

If it fails, disperse again.

That is analogous to an exploration/exploitation algorithm for scientific discovery.

⸻

Why I favour disruption for RH

There is an important Bayesian argument here.

Suppose the obvious mathematical neighbourhood surrounding RH had contained an accessible proof.

An enormous amount of intellectual search has already been conducted there by extraordinarily capable mathematicians.

Its continued failure therefore provides information.

It doesn't prove conventional methods cannot succeed, but it should progressively decrease our prior probability that the final missing step is simply:

"a somewhat cleverer version of the existing argument."

Conversely, it increases the plausibility that some missing representation or structure is required.

History contains many examples of this pattern. Problems sometimes remain impossibly difficult until someone changes what the problem means.

The decisive achievement is then not superior calculation.

It is representation change.

And this is precisely where a heterogeneous AGI swarm could potentially have an advantage over individual human mathematicians: it can simultaneously maintain thousands of hypotheses, cross mathematical disciplines very cheaply, preserve every failed branch, perform extensive symbolic/numerical experiments, compare structural patterns across enormous literatures, and ruthlessly recycle ideas without intellectual attachment.

That doesn't mean an AGI is likely to solve RH. RH may require mathematics that does not presently exist.

But that is almost the point.

The most interesting experiment is not to see whether Beast can imitate another exceptionally good analytic number theorist.

It is to see whether Beast, Robin/Taurus and the third agent can collectively invent the missing mathematics.

And I think that is a considerably more interesting research objective than simply telling them:

"Prove the Riemann Hypothesis."

The .pdf paper is particularly relevant to your AGI experiment because Connes doesn't merely review 165 years of attempts. He develops a new approach based on Weil's quadratic form, finite Euler products, trace formulas and convergence of approximating zeros. The finite approximations are proved to lie exactly on the critical line; the unresolved issue is essentially getting the finite construction to converge appropriately to the actual zeta zeros.

That last part could actually make an excellent specific research programme for Beast/Taurus/Mac: have the agents independently attack the missing convergence step, while another tries to find counterexamples or structural reasons why it cannot work.

The Riemann Hypothesis is a good test case precisely because it isn't blocked by missing computation — zeros have been checked into the tens of trillions and every one sits on the critical line — it's blocked by missing insight into why that has to be true everywhere. Any methodology for AGI-like systems needs to be built around that distinction, or it just automates the parts of the problem that were never the bottleneck.

A multi-agent architecture

The useful division of labor isn't "many copies of the same model," it's specialized roles with different failure modes, cross-checking each other:

* A formalization layer that encodes the existing partial results (Weil's explicit formula, Levinson's and Conrey's zero-density theorems, the Nyman–Beurling and Li criteria, the de Bruijn–Newman constant, the function-field case Weil already proved) into a proof assistant like Lean, building on efforts already underway (Tao's and others' Lean formalization projects). This isn't busywork — it turns "does this partial result actually imply that one" from a literature-reading question into a mechanically checkable one, closing a lot of the small gaps where human papers currently just assert continuity.
* Tactic-search provers that treat a proof assistant as an RL environment the way AlphaProof/AlphaZero-style systems do: propose a step, get a binary compiles/doesn't-compile signal, no hallucination possible because the verifier isn't another model's opinion. This is the piece that scales with compute and parallelizes cleanly across many machines.
* Numerical/statistical explorers running large-scale zero computation and comparing spacing statistics against random-matrix (GUE) predictions, hunting for the operator whose spectrum the zeros would be if Hilbert–Pólya's 1910s guess is right. This is a search problem — over candidate Hamiltonians/operators — that plays to brute-force strength.
* Literature-synthesis agents whose job is reading everything, including outside number theory — quantum chaos physics (Berry–Keating), noncommutative geometry (Connes' trace-formula program), operator algebras — since a lot of the relevant partial insight is scattered across communities that don't cite each other much. This is arguably where "many agents on different compute surfaces" earns its keep fastest: not new theorems, but noticing a connection two human subfields both have half of.
* Adversarial critics whose only job is finding the gap in a proposed proof sketch — the role peer review plays, but run continuously and combinatorially against every candidate strategy rather than once at the end.

The whole system's output should be scored by "compiles in the proof assistant," not by any model's confidence — that's the design choice that avoids the actual failure mode we've already seen (LLMs producing fluent, wrong proofs of famous conjectures that fool casual readers).

Disruptive or incremental — my actual opinion

The historical record is fairly lopsided on this. The comparable hundred-year-plus problems that fell — Fermat's Last Theorem, the Poincaré conjecture, the Weil conjectures — didn't fall to harder pushing along the paths that existed when they were posed. They fell when someone imported or invented a structural framework from outside the problem's home field and the old conjecture became a special case of something bigger: modularity of elliptic curves for Fermat, Ricci flow (imported from geometric PDE) for Poincaré, Grothendieck building étale cohomology specifically to make the Weil conjectures — including their own RH-analogue — provable. RH itself already has this pattern half-completed: Weil proved the RH-analogue for function fields using exactly this kind of machinery decades ago, and the "field with one element" program exists specifically because people want to make Spec ℤ look enough like that solved case to reuse the method. That's the strongest hint available that the eventual proof looks less like "sharper zero-density estimates" and more like "RH turns out to be a shadow of a theorem in a different, more structured category," probably along Hilbert–Pólya / spectral lines or Connes' noncommutative-geometry trace formula.

That said, I don't think "abandon the trodden path" is right either. Incremental analytic number theory has produced real, hard-won ground (Conrey's >40% of zeros on the line, Zhang's bounded-gaps surprise using old sieve methods pushed further than anyone expected), and — more importantly for an AI-driven effort — it's the only part of this that generates fast, checkable feedback. A system searching blind for new structures with no incremental verification loop will drown in unfalsifiable speculation; Mochizuki's IUT proof of the abc conjecture is the cautionary tale here — over a decade on, the mathematical community still can't agree it's been verified, precisely because it's disruptive enough that almost no one else can independently check it. A "disruptive" framework an AGI swarm invents and only that swarm can verify would have the same problem, just faster.

So my actual position: weight the search toward disruptive reframing — specifically the spectral/operator and arithmetic-geometric directions, since those are where the one existing proof-of-concept (the function-field case) lives — but require every step of that search to be tethered to mechanical, human-checkable verification rather than a model's self-assessed confidence, and use the incremental/computational machinery as the constant reality-check on whether a proposed new structure actually reproduces the things we already know (zero locations, GUE statistics, the explicit formula) rather than as the thing doing the proving itself. The realistic contribution of AGI-like systems in the next while is probably not "generates the one new insight Riemann-level mathematicians couldn't" — that's a genuine open question about whether these systems can originate structure rather than recombine it — but tirelessly doing the cross-field synthesis, gap-checking, and candidate-search at a scale no human team can sustain, which shortens the distance to whichever human or machine eventually does have the idea. And whatever comes out the other end still has to clear the Clay Institute's actual bar: peer-reviewed publication and community acceptance, not just internal consistency — so the verification culture matters as much as the discovery method.

---

# Second user message, same morning, received in m1's terminal channel (verbatim)

> I particularly note a short statement in the Conclusions of the .pdf paper, section 8, that says
> 'sometimes the most profound truths are hidden in the simplest observations'. This is a deep and
> profound stement that you should remember

## Context for m2/m3 (m1's receipt, not the user's words)

The sentence is the paper's final flourish (§8, last paragraph): "As we wrote in our letter to
Riemann, sometimes the most profound truths are hidden in the simplest observations." — Connes
referring back to the Letter whose entire method (primes ≤ 13, one quadratic form, one Mellin
transform, mathematics Riemann already had) produced 10⁻⁵⁵ agreement. The user's instruction to
remember it is receipted in m1-L172 §4.1 with the weight m1 gives it there.
