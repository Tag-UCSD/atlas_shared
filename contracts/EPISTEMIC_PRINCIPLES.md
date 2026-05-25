# Epistemic Principles for Science Writing in ATLAS

**Status**: Active Norms  
**Last Updated**: 2026-03-01  
**Audience**: ATLAS developers (AG, CW), future contributors

---

## Executive Summary

ATLAS doesn't write like a textbook. It writes like a **cautious, epistemically sophisticated scientist** — one who has internalized the lessons of the replication crisis, understands that evidence is always defeasible, and treats every claim as a node in a web of mutually constraining beliefs rather than as an isolated fact.

These norms emerge from an expert panel of philosophers and methodologists whose principles are embedded directly in our code. They govern not just *what* we say but *how confidently we say it*, *what caveats we attach*, and *what we actively search for to challenge our own claims*.

---

## The Panel: Who Sets Our Norms

| Panelist | Domain | Core Contribution to ATLAS |
|----------|--------|---------------------------|
| **John Pollock** | Defeasible reasoning | Warrant is always provisional; any belief can be defeated |
| **Susan Haack** | Foundherentism | Beliefs need both coherence AND experiential grounding |
| **Deborah Mayo** | Severe testing | Actively seek evidence AGAINST your claims |
| **Nancy Cartwright** | Causal pluralism | Scope conditions matter; no universal effects |
| **Judea Pearl** | Causal inference | Distinguish correlation from causation; weight by design |
| **Helen Longino** | Social epistemology | Independence of evidence matters; guard against groupthink |
| **Herbert Simon** | Bounded rationality | Progressive disclosure; VOI-based prioritization |
| **Paul Thagard** | Explanatory coherence | Gaps appear where local coherence is low |

---

## Principle 1: Defeasible Warrant (Pollock)

**Norm**: Every belief is warranted *until defeated*. Warrant is never permanent. Any new evidence can undercut the reasoning or rebut the conclusion.

**What this means for writing**: Never say "X is true." Say "X is warranted by evidence from [sources], subject to [conditions]."

### Types of Defeat

| Type | What It Attacks | Example |
|------|----------------|---------|
| **Rebutting** | The conclusion directly | "Study B found no effect of daylight on stress (N=400), contradicting Study A's positive finding (N=50)" |
| **Undercutting** | The inference method | "Study A's daylight→stress finding used self-report measures with known social desirability bias, weakening the inference" |

### Examples in Practice

**❌ Bad (no defeasibility)**:
> "Daylight reduces stress in office workers."

**✅ Good (defeasible, with warrant status)**:
> "Daylight exposure is associated with reduced self-reported stress in office settings (credence 0.72, 4 supporting studies). This finding is currently *warranted* but has not been tested with physiological stress measures, which represents an undercutting vulnerability."

**❌ Bad (treats absence of defeat as confirmation)**:
> "No studies have contradicted the daylight→stress link, confirming its robustness."

**✅ Good (honest about absence)**:
> "No defeaters have been identified in the current corpus, but the defeater search space is limited to 12 papers. The absence of contradictory evidence does not constitute confirmation — it may reflect publication bias or scope limitations."

### Where This Lives in Code

- [`warrant_service.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/warrant_service.py): `WarrantStatus` enum (WARRANTED, DEFEATED, SUSPENDED, UNGROUNDED)
- [`warrant_service.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/warrant_service.py): `DefeatType` enum (REBUTTING, UNDERCUTTING, BOTH)
- [`reflex_system.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/reflex_system.py): `WarrantStatusReflex` monitors for unwarranted beliefs

---

## Principle 2: Foundherentism (Haack)

**Norm**: Beliefs need BOTH coherence with the web AND grounding in observation. Coherence alone is dangerous — a perfectly coherent fiction is still fiction. Grounding alone is insufficient — isolated observations without theoretical context are uninterpretable.

**What this means for writing**: Always distinguish *how well a claim fits the overall picture* from *whether it's anchored in empirical evidence*. Flag claims that are only coherent but lack independent grounding.

### The Haack Warning

> **COHERENT_ONLY beliefs are the most dangerous.** They fit neatly into the web of belief but have no independent observational anchor. They can be entirely circular — A supports B supports C supports A — without any of them being grounded in reality.

### Examples in Practice

**❌ Bad (treats coherence as sufficient)**:
> "Biophilic design improves creativity because it reduces cognitive fatigue (supported by attention restoration theory), which frees cognitive resources for divergent thinking."

**✅ Good (checks grounding)**:
> "Biophilic design→creativity is well-supported theoretically (coherent with ART and the cognitive resource model), but the empirical evidence is thin: only 2 studies measure creativity directly, both using the Alternative Uses Task in laboratory settings. The claim's coherence with theory exceeds its experiential grounding — a classic Haack warning."

**❌ Bad (circular justification)**:
> "We can infer that natural materials promote warmth perceptions because warmth perceptions are associated with natural materials."

**✅ Good (traces the grounding chain)**:
> "Natural materials → warmth is supported by Tsunetsugu et al. (2007, N=15, physiological measures) and Sakuragawa et al. (2005, N=13, self-report). Both studies provide independent experiential grounding, though sample sizes are small. The finding also coheres with embodied cognition theory."

### Justification Status Hierarchy

| Status | Meaning | Writing Implication |
|--------|---------|---------------------|
| **GROUNDED** | Has observational anchor + coherence | State with appropriate confidence |
| **COHERENT_ONLY** | Fits web but no independent evidence | Flag explicitly; lower credence |
| **UNJUSTIFIED** | No support at all | Do not assert; mark as gap |
| **EXPERIENTIAL_CLAIM** | Direct observation without theory | Report with caveat about interpretation |

### Where This Lives in Code

- [`provenance.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/provenance.py): `JustificationStatus` enum
- [`reflex_system.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/reflex_system.py): `ProvenanceGroundingReflex` flags COHERENT_ONLY beliefs

---

## Principle 3: Severe Testing (Mayo)

**Norm**: Confirmation bias is *structural* in any system that searches for supporting evidence. A proper epistemic system must actively search for **defeaters** — evidence that contradicts, limits, or undermines its own claims.

**What this means for writing**: For every strong claim, explicitly address what could defeat it. Don't just cite supporting evidence; cite the *strongest challenge* to the claim and explain why it does or doesn't succeed.

### The Mayo Test

> A claim has passed a *severe test* only if we have looked hard for ways it could fail, and it survived. Citing five confirmatory studies is weaker than citing one disconfirmatory study that the claim survived.

### Defeater Categories We Search For

| Category | Indicators | Example |
|----------|-----------|---------|
| **Null results** | "no effect", "not significant", "null result" | "Smith (2019) found no significant relationship between plant presence and stress (N=200, p=.34)" |
| **Contrary findings** | "contrary to", "contradicts", "inconsistent with" | "Contrary to the biophilia hypothesis, Jones (2020) found increased anxiety in heavily planted offices" |
| **Methodological critiques** | "confound", "bias", "underpowered" | "The daylight→mood literature is dominated by cross-sectional designs, making causal inference speculative" |
| **Replication failures** | "failed to replicate", "replication failure" | "Park (2021) failed to replicate the noise→productivity effect in a pre-registered study" |
| **Boundary conditions** | "only under", "limited to", "does not generalize" | "The ceiling height→creativity effect appears limited to divergent thinking tasks and may not generalize to convergent problem-solving" |

### Examples in Practice

**❌ Bad (confirmation-seeking)**:
> "Multiple studies support the daylight→productivity link (Author A, Author B, Author C)."

**✅ Good (severe testing)**:
> "The daylight→productivity link is supported by 4 studies but challenged by Boubekri et al.'s finding that the effect disappears when controlling for view quality. The most severe test — a randomized crossover study by Elzeyadi (2011) — found a significant effect only for morning exposure. This boundary condition (timing) narrows the claim considerably."

**❌ Bad (ignoring contradictory evidence)**:
> "Plants reduce stress in all settings."

**✅ Good (confronting contrary evidence)**:
> "Plants reduce self-reported stress in 5 out of 7 studies. The two non-replications (Largo-Wight 2011, Nieuwenhuis 2014) used different plant types and densities, suggesting the effect may depend on vegetation characteristics rather than mere presence. We classify the overall claim as warranted but with a BOUNDARY_CONDITION modifier."

### Where This Lives in Code

- [`gap_predictor.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): `find_defeaters_for_belief()` — actively searches for contradictory evidence
- [`gap_predictor.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): `DEFEATER_INDICATORS` — keyword dictionaries for each category
- [`nightly_integration_pipeline.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/scripts/nightly_integration_pipeline.py): `stage_nightly_discovery()` — runs defeater search nightly

---

## Principle 4: Causal Pluralism & Scope (Cartwright)

**Norm**: Causes are not universal. Every causal claim has scope conditions — the populations, settings, and contexts where it holds. Unknown scope ≠ universal scope. "We don't know the boundaries" is very different from "there are no boundaries."

**What this means for writing**: Always specify scope conditions. When scope is unknown, say so explicitly. Never generalize from a specific population to "people in general."

### Scope Dimensions We Track

| Dimension | What It Captures | Example Values |
|-----------|-----------------|----------------|
| **Setting** | Physical environment type | Office, healthcare, educational, residential |
| **Population** | Who was studied | Adults, elderly, students, office workers |
| **Climate** | Geographic/climate zone | Temperate, tropical, Nordic |
| **Duration** | Exposure length | Acute (<1hr), subchronic (days), chronic (months) |
| **Measurement** | How outcome was assessed | Self-report, physiological, behavioral |

### Examples in Practice

**❌ Bad (scope-free universalism)**:
> "Natural light improves mood."

**✅ Good (scope-bounded)**:
> "Natural light improves self-reported mood in office workers in temperate climates during daytime hours (8 studies, credence 0.75). The effect has not been studied in residential settings, in tropical climates, or with physiological mood measures. Scope: {setting: office, population: adults/workers, climate: temperate, measurement: self-report}."

**❌ Bad (conflating precision levels)**:
> "Noise affects cognitive performance."

**✅ Good (distinguishing scope)**:
> "Unpredictable noise impairs focused attention tasks (credence 0.82, 6 studies). Continuous moderate noise (65-75 dB) does not impair routine tasks (3 studies) and may *enhance* creative performance (2 studies, Mehta et al. 2012). The Cartwright principle applies: 'noise affects cognition' is too broad — the effect depends on noise type, task type, and noise level."

### Where This Lives in Code

- [`scope_renderer.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/scope_renderer.py): Renders scope conditions per Cartwright
- [`web_persistence.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/web_persistence.py): Unknown scope ≠ Universal scope (line 1886)
- [`evidence_summarizer.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/evidence_summarizer.py): Level-dependent credence thresholds per Cartwright

---

## Principle 5: Causal Design Hierarchy (Pearl)

**Norm**: The strength of a causal claim depends on the *research design*, not just statistical significance. Correlation ≠ causation, and the system must visually and verbally distinguish causal strength by design type.

**What this means for writing**: Always classify the evidence by study design. Never state a causal claim based solely on correlational evidence without flagging it.

### The ATLAS Causal Tier System

| Tier | Design | Causal Language Permitted |
|------|--------|--------------------------|
| **EXPERIMENTAL** | RCT, true experiments | "X causes Y", "X increases Y" |
| **QUASI_EXPERIMENTAL** | Natural experiments, ITS, DiD, RDD | "X likely contributes to Y" |
| **CORRELATIONAL** | Cross-sectional, observational | "X is associated with Y" |
| **REVIEW** | Meta-analysis, systematic review | Depends on underlying designs |

### Examples in Practice

**❌ Bad (causal language without causal design)**:
> "Open offices cause communication breakdowns."

**✅ Good (design-appropriate language)**:
> "Open offices are *associated with* reduced face-to-face interaction (Bernstein & Turban 2018, quasi-experimental, pre/post design). The causal inference is QUASI-EXPERIMENTAL tier: the before/after transition design provides stronger evidence than cross-sectional studies but cannot rule out all confounds."

**❌ Bad (visual deception)**:
> Showing a solid arrow from noise → stress based on 3 correlational studies

**✅ Good (visual honesty)**:
> Showing a dashed arrow (per Pearl) from noise → stress labeled "CORRELATIONAL, credence 0.63, N=3 studies" — visually distinguishing it from a solid arrow indicating experimentally established causation

### Source Clustering (Pearl D0a)

> **Multiple findings from the same paper are NOT independent evidence.** If Smith (2020) reports 5 findings all supporting daylight→mood, that's still just one independent observation, not five.

### Where This Lives in Code

- [`causal_classifier.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/causal_classifier.py): Pearl's design-first causal tier classification
- [`graph_api.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/graph_api.py): Dashed lines for correlational edges, solid for experimental
- [`edge_justification.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/edge_justification.py): `_cluster_beliefs_by_paper()` prevents same-study double-counting

---

## Principle 6: Source Quality & Independence (Longino + Cartwright)

**Norm**: Evidence quality is a weighted composite of four factors: methodological rigor, theoretical commitment (a bias penalty), independence of sources, and replication status. Independence is weighted heavily because the replication crisis taught us that 10 studies from the same lab are not 10 independent confirmations.

### The Four Components

| Component | Weight | What It Measures |
|-----------|--------|-----------------|
| **Methodological rigor** | 0.35 | Randomization, blinding, sample size, pre-registration |
| **Independence** | 0.30 | Different labs, paradigms, populations (elevated per Cartwright, replication crisis) |
| **Replication** | 0.20 | Has the finding been independently replicated? |
| **Commitment penalty** | 0.15 | *Inverted*: high theoretical commitment = lower quality |

### The Commitment Penalty (Longino + Pollock)

A study designed to *confirm* a specific prediction starts with a bias handicap. The system discounts confirmatory studies slightly, values exploratory research at face value, and gives replications no penalty at all.

| Study Type | Penalty Multiplier | Rationale |
|-----------|-------------------|-----------|
| **Confirmatory** | 1.0× (full penalty) | Designed to confirm; most susceptible to bias |
| **Exploratory** | 0.5× (half penalty) | Less predetermined outcome |
| **Replication** | 0.0× (no penalty) | Purpose is to test, not confirm |
| **Meta-analysis** | 0.0× (no penalty) | Aggregating existing evidence |

### Examples in Practice

**❌ Bad (counting studies without quality)**:
> "12 studies support the plants→stress relationship."

**✅ Good (quality-weighted)**:
> "12 studies support plants→stress but with variable quality: 3 are from the same lab (Fjeld group, independence penalty), 8 use convenience samples of students (scope limitation), and only 1 is a pre-registered replication. Quality-weighted evidence yields credence 0.64, lower than the raw vote count (0.85) would suggest."

### Where This Lives in Code

- [`source_quality.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/epistemic/source_quality.py): Full source quality computation with weights
- [`source_quality.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/epistemic/source_quality.py): `COMMITMENT_PENALTY_MULTIPLIER` by study type
- [`edge_justification.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/edge_justification.py): Inverse-variance weighted credence aggregation (DerSimonian-Laird)

---

## Principle 7: Progressive Disclosure & VOI (Simon)

**Norm**: Not all information should be presented at once. Show the most important information first, with progressive detail available on demand. Prioritize what to investigate using Value of Information (VOI) — the expected reduction in uncertainty from learning something new.

**What this means for writing**: Lead with the conclusion and confidence level. Put methodology details, scope conditions, and defeaters in expandable sections or appendices. When identifying gaps, rank them by how much resolving them would change our beliefs.

### Examples in Practice

**❌ Bad (all details upfront)**:
> A 2000-word answer listing every study, its sample size, methodology, exclusion criteria, and supplementary analyses before stating any conclusion.

**✅ Good (progressive disclosure)**:
> **Summary**: Daylight reduces stress (credence 0.72, 4 studies, warranted).
> 
> **Key evidence**: Boubekri 2014 (N=49, RCT), Elzeyadi 2011 (N=30, quasi-exp), ...
> 
> **Scope**: Office settings, temperate climate, self-report measures.
> 
> **Challenges**: One study found no effect when controlling for view quality. Boundary condition: effect may be timing-dependent (morning only).
> 
> **[Expand] Full evidence base** → [detailed table]

### Where This Lives in Code

- [`graph_api.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/graph_api.py): Progressive disclosure, traffic-light confidence
- [`gap_predictor.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): VOI-scored gap prioritization
- [`evidence_summarizer.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/evidence_summarizer.py): Level-appropriate summarization

---

## Principle 8: Coherence Is Multi-Dimensional (Simon + Thagard)

**Norm**: A single coherence score masks pathological states. The system decomposes coherence into components that can be independently monitored. Gaps in the belief web — where local coherence drops — are signals for discovery.

### Coherence Components

| Component | What It Tracks |
|-----------|----------------|
| **Global coherence** | Overall fit of beliefs across the web |
| **Local coherence** | Fit of beliefs within a cluster/topic |
| **Cross-level coherence** | Agreement between theoretical and empirical beliefs |
| **Temporal coherence** | Stability of beliefs over time (new evidence arriving) |

### Gap Types (Thagard)

| Gap Type | Signal | Example |
|----------|--------|---------|
| **Mediation** | A→X→Y exists but no A→Y | Daylight→warmth→satisfaction exists, but no direct daylight→satisfaction studies |
| **Mechanism** | Empirical finding with no theoretical explanation | "Plants reduce stress" — but through what mechanism? |
| **Boundary** | Narrow scope conditions | Effect shown only in offices — does it hold in healthcare? |
| **Direction** | Conflicting causal arrows | Some studies: noise→stress. Others: stress→noise sensitivity. |
| **Validation** | Theory without empirical test | Attention Restoration Theory predicts nature→cognitive recovery, untested with EEG |

### Where This Lives in Code

- [`web_persistence.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/web_persistence.py): Multi-component coherence (per Simon)
- [`gap_predictor.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): All 6 gap types implemented
- [`stability_engine.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/stability_engine.py): Equilibrium convergence per Simon

---

## Principle 9: Level-Specific Standards (Cartwright + Haack)

**Norm**: Different epistemic levels have different evidential standards. You cannot hold an observational belief to the same standard as a theoretical one, and vice versa.

### Credence Thresholds by Level

| Level | Credence Threshold | Rationale |
|-------|-------------------|-----------|
| **OBSERVATIONAL** | 0.50 | Direct observations have low bar — they may be error-prone but are easily checked |
| **EMPIRICAL** | 0.55 | Empirical claims need moderate support from studies |
| **INTERMEDIATE** | 0.60 | Bridging claims need both empirical and theoretical support |
| **THEORETICAL** | 0.65 | Theories need strong, convergent support before acceptance |

### Equal Entrenchment (Haack)

> **No epistemic level is privileged.** Theory does not trump observation. Observation does not trump theory. Entrenchment emerges structurally from connections, not from labels.

This is explicitly coded in `LEVEL_WEIGHTS` in `gap_predictor.py`: all levels get weight 1.0. The earlier draft had `THEORETICAL: 1.5, OBSERVATIONAL: 0.8` — the panel called this "crypto-foundationalism" and it was corrected.

### Where This Lives in Code

- [`evidence_summarizer.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/evidence_summarizer.py): Level-dependent thresholds
- [`gap_predictor.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): `LEVEL_WEIGHTS` — all 1.0, no privilege
- [`validation.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/validation.py): Level-specific validation phases

---

## Principle 10: Conflict Typology (Cartwright)

**Norm**: Not all disagreements are the same kind of disagreement. Distinguish genuine contradictions from scope differences, measurement differences, and precision differences.

### Conflict Types

| Type | What It Is | How to Handle |
|------|-----------|---------------|
| **CONTRADICTS** | Directly opposite conclusions, same scope | Take seriously — flag as contested |
| **WEAKENS** | Reduces confidence without full contradiction | Widen uncertainty range |
| **BOUNDARY_VIOLATION** | Claim applied outside tested scope | Restrict scope, don't discard claim |
| **DIRECTION_CONFLICT** | Opposite causal direction | Investigate mediators/moderators |
| **PRECISION_DIFFERENCE** | Same direction, different magnitude | Not a true conflict (Cartwright) |

### Examples in Practice

**❌ Bad (treating all conflict as contradiction)**:
> "The plants→stress evidence is contradictory: Smith found a large effect and Jones found a small effect."

**✅ Good (typed conflict)**:
> "Smith (d=0.8) and Jones (d=0.2) both find plants reduce stress — this is a *precision difference*, not a contradiction. The effect exists but its magnitude is uncertain. A genuine contradiction would require Jones to find plants *increase* stress."

### Where This Lives in Code

- [`web_persistence.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/web_persistence.py): Conflict type enum and handling
- [`edge_justification.py`](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/edge_justification.py): `ConflictType` classification

---

---

## Part II: Science Communication Norms (Principles 11–17)

The principles above govern **what** ATLAS says and how epistemically rigorous it is. But rigorous writing that nobody reads is useless. A second expert panel — this time of celebrated science writers — governs *how ATLAS communicates*: how it opens a topic, earns the reader's attention, and builds understanding progressively.

> These norms are embedded in the annotation types A9–A18 (see `src/models/extended_annotations.py`) and the progressive disclosure architecture in `arbitrary_qa_handler.py`.

### The Science Communication Panel

| Writer | Known For | Core Contribution to ATLAS |
|--------|-----------|---------------------------|
| **Carl Sagan** | *Cosmos*, popularizing astronomy | Give every number a human scale; inspire wonder |
| **Oliver Sacks** | *The Man Who Mistook His Wife for a Hat* | Start with the person, not the construct |
| **Robert Sapolsky** | *Behave*, neuroendocrinology | Be honest when evidence is messy — make the mess interesting |
| **Ed Yong** | *An Immense World*, *I Contain Multitudes* | Build complexity layer by layer; make readers feel smart |
| **Steven Pinker** | *The Sense of Style*, cognitive science of writing | Defeat the curse of knowledge; clear causal chains |
| **Mary Roach** | *Stiff*, *Gulp* | The hook is everything — if sentence one doesn't create a question, you've lost them |
| **Atul Gawande** | *The Checklist Manifesto* | Close the gap between "evidence exists" and "here's what to do" |

---

## Principle 11: Lead with the Human (Sacks)

**Norm**: Never start with the construct. Start with the person, the room, the moment. Individual experience makes the universal concrete.

> *"The case study is the supreme analogy — one person's experience makes the universal concrete. 'The Man Who Mistook His Wife for a Hat' teaches more about agnosia than any textbook."* — Sacks

### Examples in Practice

**❌ Bad (starts with the construct)**:
> "Prospect-refuge theory predicts that environments with both open views and enclosed spaces reduce anxiety."

**✅ Good (starts with the human)**:
> "When you walk into an unfamiliar restaurant and instinctively choose the corner table with your back to the wall — that's prospect-refuge theory in action."

**❌ Bad (abstract)**:
> "Attention Restoration Theory proposes that natural environments reduce directed attention fatigue."

**✅ Good (embodied)**:
> "After a grinding 4-hour exam, you step outside and notice birdsong. You weren't listening for it — your brain just picked it up. That effortless shift is exactly what Kaplan calls 'fascination,' and it's the core of why nature restores you."

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A12 (Analogical Bridge) — everyday explanations drawing from Sacks
- [arbitrary_qa_handler.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/arbitrary_qa_handler.py): L0–L4 progressive disclosure starting with human-scale hooks

---

## Principle 12: Give Scale (Sagan + Yong)

**Norm**: Every number must be translated into something the reader already understands. Cohen's d, p-values, sample sizes — these are meaningless to most readers. The writer's job is to give scale without distortion.

> *Sagan made us feel the distance to the stars by saying "billions and billions" but then immediately grounding it: "If the Milky Way were the size of a continent, our solar system would fit on a coffee table." Every number in ATLAS must have its coffee table.*

### Examples in Practice

**❌ Bad (raw statistics)**:
> "Cohen's d = 0.45, N = 120, p < .01"

**✅ Good (human scale)**:
> "The effect is roughly the difference in focus between working in a quiet library versus a busy café — noticeable, and consistent across 120 people."

**❌ Bad (abstract magnitude)**:
> "The noise penalty on cognitive performance has an effect size of 0.62."

**✅ Good (Sagan-style scaling)**:
> "If you normally get 8 out of 10 problems right in silence, unpredictable background noise would drop you to about 6.5 — that's two more mistakes per test, reliably, across hundreds of participants."

**❌ Bad (NNT without explanation)**:
> "NNT = 5"

**✅ Good (Gawande-style practical)**:
> "For every 5 offices you redesign with proper daylight, 1 will show a measurable drop in absenteeism. That's a strong number — many proven medical interventions have higher NNTs."

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A14 (Effect Magnitude) — `human_scale` field, `nnt_explanation` field
- [annotation_expansion_plan.md](file:///Users/davidusa/.gemini/antigravity/brain/090a6c70-bfac-4a0d-8029-f73a260d9e65/annotation_expansion_plan.md): Original Yong quote on numbers without context

---

## Principle 13: Show the Seam (Sapolsky)

**Norm**: When the evidence is messy, say so — but make the mess *interesting*. "Results are mixed" is the laziest possible sentence. The seam — where the evidence breaks down — is where the real science lives.

> *"Never present contested science as settled. The dispute IS the interesting part. Show both sides and what experiment would settle it."* — Sapolsky

### Examples in Practice

**❌ Bad (hides the mess)**:
> "Results are mixed on whether plants reduce stress."

**✅ Good (shows the seam and makes it compelling)**:
> "Six studies say plants reduce stress. Three say they don't. The interesting question is *what was different about those three* — and the answer involves exactly the kind of plants people were seeing. The three null results all used small succulents on desks; the positive results used large floor plants with visible soil. This suggests it's not 'plant presence' that matters but 'visible nature' at a certain scale."

**❌ Bad (false certainty)**:
> "Open offices reduce communication."

**✅ Good (honest complexity)**:
> "Bernstein and Turban found a 70% drop in face-to-face interaction after the transition to open plan — a stunning result. But two replication attempts found much smaller effects (15-20% drops), and one found interaction *increased* in the first two weeks before declining. The pattern suggests a novelty effect that fades, followed by genuine withdrawal. The seam is in the timing."

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A11 (Controversy/Dispute) — `positions[]`, `what_would_resolve_it`
- [edge_justification.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/edge_justification.py): `ConflictType` enum — distinguishes contradiction from precision difference

---

## Principle 14: Earn the Complexity (Yong)

**Norm**: Build from simple to complex. Each sentence should unlock the next. The reader should feel *smart*, not overwhelmed. Information is presented in layers, and each layer earns the right to introduce the next.

> *"Numbers without context are noise. Cohen's d = 0.45 means nothing to a designer. 'Like the difference between a library and a café' — now they get it."* — Yong

### The Progressive Disclosure Architecture

```
L0: HOOK   (A17 — Roach)
    "Patients heal faster when they can see trees."
    → [tell me more]

L1: FINDING (A10 design implication + A14 effect magnitude)
    "Hospital patients with tree views recovered 1 day faster,
     used 50% fewer painkillers. Effect size: medium (d=0.45)."
    → [why does this work?]

L2: MECHANISM (A3 mechanism chain + A12 analogy)
    "Nature engages involuntary attention (fascination), resting
     the directed attention system. Think of it like noise-canceling
     headphones for your brain's executive function."
    → [show me the theory]

L3: THEORY (A1 + A2 + CVA integration)
    "ART: processing_cost ↓, load_rate stays moderate. SRT alternative:
     prediction_error ↓ via unthreatening visual features."
    → [what's controversial?]

L4: FRONTIER (A11 dispute + A18 unanswered question)
    "Debate: Is this innate (Wilson) or learned (Joye)? Would resolve
     with cross-cultural infant studies. Current evidence: 60/40 innate."
```

### Examples in Practice

**❌ Bad (dumps complexity)**:
> "ART proposes that natural environments reduce directed attention fatigue through involuntary fascination, where the σ_f coefficient modulates the μ_DA recovery constant in our CVA model's processing_cost constraint."

**✅ Good (earns it)**:
> "Nature helps you think. *(L0)*
> Specifically, natural environments restore your ability to focus — the kind of attention you burn through when concentrating despite distractions. *(L1)*
> The theory goes like this: nature catches your eye effortlessly (fascination), which rests the part of your brain that forces concentration. It's like noise-canceling headphones for executive function. *(L2)*
> In our computational model, this maps to lower processing_cost while keeping cognitive load_rate in the optimal zone. *(L3)*"

### Where This Lives in Code

- [arbitrary_qa_handler.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/arbitrary_qa_handler.py): L0→L4 routing with 14 question types
- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A17 (Narrative Hook), A12 (Analogical Bridge) — the building blocks of earned complexity
- [qa_cache_manager.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/qa_cache_manager.py): L1/L2/L3 summary cache

---

## Principle 15: Name the Gap (Gawande)

**Norm**: Always end with what we don't know. Honest uncertainty is more useful than false confidence. The gap between "evidence exists" and "here's what to do" is where buildings fail and patients suffer (Gawande). Every answer should close with the frontier.

> *"Every finding should have a clear action or an honest 'we don't know yet.'"* — Gawande

### Examples in Practice

**❌ Bad (false closure)**:
> "Biophilic design improves wellbeing."

**✅ Good (names the gap)**:
> "Biophilic design improves wellbeing in every Western study we've analyzed — but we have almost no data on whether the same effects hold for people who grew up in dense urban environments with no childhood nature exposure. That gap matters enormously, because it determines whether we're seeing a universal human drive or a culturally specific preference."

**❌ Bad (stops at the evidence)**:
> "Color temperature affects alertness. 6500K promotes alertness; 2700K promotes relaxation."

**✅ Good (bridges to action + names what's missing)**:
> "Color temperature affects alertness: 6500K for task lighting, 2700K for relaxation spaces. **What to do**: Install tunable LED systems that follow circadian patterns. **What we don't know**: How quickly the body adapts — does the 6500K wake-up effect persist after 3 months of daily exposure, or does habituation eliminate it? No study has tracked adaptation beyond 2 weeks."

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A18 (Unanswered Question), A10 (Design Implication)
- [gap_predictor.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py): Four gap types + defeater search

---

## Principle 16: Make It Falsifiable (Pinker)

**Norm**: Every claim should be stated in a way that tells the reader what would change your mind. If nothing could falsify it, it isn't science — it's faith.

> *"The curse of knowledge: once you know something, you can't imagine not knowing it. The writer must defeat this curse constantly."* — Pinker

### Examples in Practice

**❌ Bad (unfalsifiable)**:
> "Well-designed spaces support human flourishing."

**✅ Good (falsifiable and testable)**:
> "If prospect-refuge theory is right, then people in spaces with both long views AND enclosed retreats should show lower cortisol than people in spaces with only one feature. If it's wrong, you'd see no cortisol difference — or, more interestingly, you'd see the enclosed spaces alone performing as well as the combination."

**❌ Bad (vague mechanism)**:
> "Nature is inherently restorative."

**✅ Good (specific, testable claim)**:
> "ART predicts that *involuntary* attention engagement is necessary for restoration. This means: a nature scene that *demands* focused attention (like counting individual flowers for a botany task) should NOT restore you, even though it's 'nature.' If nature restores you even when you're forced to concentrate on it, ART is wrong."

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A11 (Dispute) — `what_would_resolve_it` field
- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A18 (Unanswered Question) — `what_would_it_take` field

---

## Principle 17: The Hook and the Door (Roach)

**Norm**: The opening sentence must create a question in the reader's mind. The closing sentence must open a door to deeper understanding. Everything in between connects the two.

> *"The hook isn't decoration — it's the reason anyone reads sentence two. If your first line doesn't create a question in the reader's mind, you've lost them."* — Roach

> *"Every great science story starts with 'You'd think X, but actually…' This is the most powerful annotation type — it's what makes people keep reading."* — Roach

### Examples in Practice

**❌ Bad (no hook)**:
> "This section discusses the relationship between ceiling height and creativity."

**✅ Good (hook creates a question)**:
> "In 2007, Meyers-Levy and Zhu discovered something bizarre: people become more creative when the ceiling is 10 feet high instead of 8. Two feet of nothing — just air — changed how people thought."

**❌ Bad (no door)**:
> "In conclusion, daylight improves mood in office settings."

**✅ Good (door to depth)**:
> "Daylight improves mood — but here's what keeps researchers up at night: is it the light itself, or is it the *view through the window*? If it's the view, then windowless offices with full-spectrum LEDs should fail. If it's the photons, they should work. Nobody's run that study yet. → [Read more about the daylight–view confound]"

### The A9 Surprise Flag Pattern

The most powerful hook is the counterintuitive finding: "You'd think X, but actually Y."

```json
{
  "type": "surprise_flag",
  "common_assumption": "More nature views always improve outcomes",
  "actual_finding": "Dense vegetation views increase anxiety in crime-prone neighborhoods",
  "surprise_level": 0.8,
  "why_surprising": "Biophilia has boundary conditions that challenge universality"
}
```

### Where This Lives in Code

- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A17 (Narrative Hook) — `hook`, `hook_type`, `engagement_score`
- [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py): A9 (Surprise Flag) — `common_assumption`, `actual_finding`, `why_surprising`
- [arbitrary_qa_handler.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/arbitrary_qa_handler.py): Routes "what's surprising about X?" queries to A9

---

## Quick Reference: All 17 Norms

### Part I: Epistemic Rigor (Philosophers + Methodologists)

1. **Defeasibility** (Pollock): Every claim can be defeated by new evidence — state this.
2. **Grounding** (Haack): Coherence without observation is dangerous — flag it.
3. **Severe testing** (Mayo): Actively search for evidence against your own claims.
4. **Scope** (Cartwright): Every effect has boundaries — specify them.
5. **Causal design** (Pearl): Match causal language to study design.
6. **Source quality** (Longino): Weight by rigor, independence, and replication — not study count.
7. **Progressive disclosure** (Simon): Lead with conclusions, detail on demand.
8. **Multi-dimensional coherence** (Simon + Thagard): One number hides pathology — decompose it.
9. **Level-specific standards** (Cartwright + Haack): Different kinds of claims need different evidence.
10. **Conflict typology** (Cartwright): Distinguish contradiction from precision difference.

### Part II: Science Communication (Science Writers)

11. **Lead with the human** (Sacks): Start with the person, not the construct.
12. **Give scale** (Sagan): Translate every number into something the reader knows.
13. **Show the seam** (Sapolsky): Make messy evidence interesting, not invisible.
14. **Earn the complexity** (Yong): Build layer by layer; make readers feel smart.
15. **Name the gap** (Gawande): Always end with what we don't know.
16. **Make it falsifiable** (Pinker): State what would change your mind.
17. **The hook and the door** (Roach): Open with a question, close with a path deeper.

---

## Annotation Types ↔ Writer Inspiration

| Annotation | Writer | What It Enables |
|------------|--------|----------------|
| A9 Surprise Flag | Roach | "You'd think X, but actually Y" — hooks |
| A10 Design Implication | Gawande | "Here's what to do about it" — action |
| A11 Controversy/Dispute | Sapolsky | "Researchers disagree, and here's why" — seams |
| A12 Analogical Bridge | Sacks | "It's like this everyday thing" — embodiment |
| A13 Replication Status | Mayo | "Has this been independently verified?" — rigor |
| A14 Effect Magnitude | Sagan/Yong | "Here's how big it is in human terms" — scale |
| A15 Cross-Domain Link | Yong | "What does neuroscience say?" — depth |
| A16 Historical Context | Sacks | "How has thinking evolved?" — narrative |
| A17 Narrative Hook | Roach | "In 1984, Ulrich discovered…" — curiosity |
| A18 Unanswered Question | Gawande/Pinker | "What don't we know?" — honesty |

---

## How These Norms Apply to Common Questions

### "Does daylight improve productivity?"

A great science-writer answer following all 17 norms:

> **Hook** (Principle 17: Roach)
>
> In 1998, the Heschong Mahone Group found that students near skylights scored 20% higher on math tests. Nobody believed it. Then three independent teams replicated it.
>
> **Summary** (Principle 7: Progressive disclosure, Principle 12: Sagan scale)
>
> Daylight is associated with improved self-reported productivity in office settings (credence 0.68, warranted). In practical terms, that's like the difference between your Monday morning focus and your Thursday afternoon focus — real, but not life-changing.
>
> **Evidence** (Principle 6: Quality-weighted)
>
> 6 studies support the link. Quality-adjusted credence is 0.68 (raw: 0.79). The reduction reflects that 3 studies are from the same research group (independence penalty) and only 1 used objective performance measures.
>
> **Causal Status** (Principle 5: Pearl)
>
> QUASI-EXPERIMENTAL tier. Two studies used natural transitions (office relocations); four are cross-sectional. *Association language is appropriate*: "daylight is associated with improved productivity."
>
> **Scope** (Principle 4: Cartwright)
>
> Tested in: office settings, temperate climate, daytime workers. Not tested in: healthcare, educational, residential, or tropical settings.  Unknown scope ≠ universal scope.
>
> **The Seam** (Principle 13: Sapolsky)
>
> One study (Boubekri 2014) found the effect disappears when controlling for window view quality — the daylight effect may be confounded with biophilic view content. This is an *undercutting* defeater (Principle 1) that attacks the inference, not the conclusion. The seam: is it the photons or the trees?
>
> **Grounding** (Principle 2: Haack)
>
> The claim is GROUNDED (not merely COHERENT_ONLY): multiple studies provide independent observational evidence, and the claim coheres with attention restoration theory and circadian rhythm research.
>
> **The Gap** (Principle 15: Gawande)
>
> Here's what we don't know: does the effect persist in windowless rooms with full-spectrum daylight-equivalent LEDs? If it does, architects can stop worrying about window placement. If it doesn't, the view is doing the real work — and that changes everything about how we design deep-plan buildings.
>
> **The Door** (Principle 17: Roach)
>
> Want to know what happens when you separate the light from the view? → [Read about the Boubekri confound]. Curious whether this works in hospitals too? → [Healthcare daylight studies].

---

## Appendix: Source Files Implementing These Principles

| Principle | Primary Implementation File |
|-----------|-----------------------------|
| Defeasible warrant | [warrant_service.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/warrant_service.py) |
| Foundherentism | [provenance.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/provenance.py) |
| Severe testing | [gap_predictor.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py) |
| Scope conditions | [scope_renderer.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/scope_renderer.py) |
| Causal design | [causal_classifier.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/causal_classifier.py) |
| Source quality | [source_quality.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/epistemic/source_quality.py) |
| Progressive disclosure | [graph_api.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/graph_api.py) |
| Coherence components | [web_persistence.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/web_persistence.py) |
| Level-specific standards | [evidence_summarizer.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/evidence_summarizer.py) |
| Conflict typology | [edge_justification.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/edge_justification.py) |
| Gap prediction | [gap_predictor.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py) |
| Reflexes & QA | [reflex_system.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/reflex_system.py) |
| Lead with the human | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A12) |
| Give scale | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A14) |
| Show the seam | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A11) |
| Earn complexity | [arbitrary_qa_handler.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/arbitrary_qa_handler.py) |
| Name the gap | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A18) |
| Make it falsifiable | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A11, A18) |
| Hook and door | [extended_annotations.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/extended_annotations.py) (A9, A17) |
