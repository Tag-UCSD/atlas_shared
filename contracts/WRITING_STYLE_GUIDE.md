# ATLAS Writing Style Guide

*Canonical reference for all prose produced by ATLAS — papers, reports, QA responses, documentation.*
*Last updated: 2026-05-06 (added MANDATES PROVENANCE header per CONTRACT_PROCESS_PROVENANCE_AUDIT recommendation #2)*

**Companion documents**: For article-level architecture, revision methodology, and science-writer theoretical grounding, see `SCIENCE_COMMUNICATION_NORMS.md`. For math exposition, see `MATH_EXPLANATION_NORMS.md`. For figures, see `VISUALIZATION_NORMS.md`. For QA answer epistemic content, see `docs/EPISTEMIC_PRINCIPLES.md` (Principles 11-17).

```
═══ MANDATES PROVENANCE ═══
docs_read:        [contracts/PROSE_PROCESS_PROVENANCE_ADDENDUM_2026-05-06.md,
                  contracts/SCIENCE_COMMUNICATION_NORMS.md (header survey),
                  contracts/WRITING_STYLE_GUIDE.md (this file, surveyed),
                  data/construct_lexicon.json]
docs_read_at:     2026-05-06 (header back-fill session)
protocol_applied: Header added retrospectively per the
                  PROSE_PROCESS_PROVENANCE_ADDENDUM contract. The body
                  is a sentence/paragraph/section mechanics reference,
                  not a sc-summary, and pre-dates the lex-aware
                  metric. The header records honest accounting of
                  scope, not a fresh rewrite.
gates_target:     This document is a style-mechanics reference, so
                  the strict 750-1250 sc-summary gate does not apply.
                  The relevant gates are structural compliance,
                  internal consistency, and the presence of this
                  header. The norms in the document are themselves
                  the gates that other deliverables are held to.
gates_measured:   measured by prose_provenance_ingester on ingest;
                  body word count exceeds 2500, so the wc_750-1250
                  gate is out of scope by design
gates_passed:     trigger satisfied, header present (this block),
                  references documented, ingester wired
gates_failed:     full sc-summary gate compliance is out of scope for
                  a style-guide document
═══════════════════════════
```

---

## The Target Voice

Our target reader is a **smart 3rd-year undergraduate** in cognitive science, psychology, or architecture — someone who has taken intro stats, one or two lab methods courses, and reads widely but is not yet a specialist. They are curious, competent, and impatient. They will not tolerate being talked down to, but they also will not tolerate impenetrable jargon. They want to understand why something matters before they invest effort in how it works.

The voice we aim for sits between two poles:

| Popular Science | **ATLAS Voice** | Expert Journal |
|---|---|---|
| "The brain likes medium complexity" | "The brain optimizes its response to intermediate prediction error — not too simple (nothing to learn) and not too chaotic (impossible to learn)" | "Hierarchical Bayesian inference under precision-weighted prediction error minimization produces a non-monotonic free energy landscape with a local minimum at intermediate stimulus complexity" |
| Avoids equations | Uses equations but always explains them in words first | Assumes the reader can parse equations without verbal scaffolding |
| No citations in text | Key citations woven into prose naturally | Dense (Author, Year) clusters that interrupt flow |
| Metaphors everywhere | Metaphors to open, then precise language to close | No metaphors — considered imprecise |
| Short paragraphs (2-3 sentences) | Medium paragraphs (4-7 sentences) | Long paragraphs (8-15 sentences) |
| Present tense, active voice | Present tense for claims, past tense for methods, active voice strongly preferred | Past tense throughout, passive voice common |

**The bias is toward the popular end.** When in doubt, write it so the smart undergrad gets it. You can always add precision; you cannot easily add clarity after the fact.

---

## 1. Sentence-Level Norms

### 1.1 Lead with the Point

Every paragraph should open with its conclusion, not build to it. The reader should know what you're arguing before you present the evidence.

**Good**: "The Goldilocks Principle operates across all five sensory modalities studied. Visual complexity peaks at fractal dimension D ≈ 1.3, thermal comfort at adaptive neutral, and acoustic preference at 50-60 dB. This cross-modal consistency is the theory's distinctive claim."

**Bad**: "We examined visual complexity, thermal comfort, acoustic preference, temporal variation, and social density. In each case, we found an inverted-U function. The peaks occurred at domain-specific optima. These results suggest that the Goldilocks Principle may operate across sensory modalities."

The good version tells you what to think, then gives you the evidence. The bad version makes you hold five facts in working memory before revealing the punchline.

### 1.2 One Idea Per Sentence

Complex ideas need simple containers. If a sentence has two independent claims, split it. If a sentence has a dependent clause longer than 15 words, promote the clause to its own sentence.

**Good**: "Prediction error drives learning. When error is too low, the brain has nothing new to encode. When error is too high, the signal overwhelms working memory. The optimum lies between these extremes."

**Bad**: "Prediction error drives learning, and when error is too low the brain has nothing new to encode, but when error is too high the signal overwhelms working memory, so the optimum lies between these extremes where the brain can successfully resolve prediction errors without exceeding metabolic or computational capacity."

### 1.3 Active Voice (Almost Always)

Active voice is shorter, clearer, and more engaging. Use passive voice only when the agent is unknown, irrelevant, or deliberately de-emphasized.

**Good**: "Taylor et al. (1999) measured aesthetic preference for fractal patterns across 220 participants."

**Bad**: "Aesthetic preference for fractal patterns was measured across 220 participants by Taylor et al. (1999)."

**Exception (passive OK)**: "The participants were recruited from undergraduate psychology courses." (The recruiter is irrelevant.)

### 1.4 Concrete Before Abstract

Always give the concrete example or specific case before the abstract principle. The brain anchors on examples and generalizes from them.

**Good**: "A Gothic cathedral has a fractal dimension of about 1.3 — the same as a coastline or a forest edge. This is no coincidence. Human visual preference peaks at exactly this level of complexity, where the brain's prediction machinery operates most efficiently."

**Bad**: "Human visual preference follows an inverted-U function of fractal dimension, peaking at approximately 1.3, which corresponds to the fractal statistics of natural environments. Gothic cathedrals happen to fall at this optimum."

### 1.5 Use "You" and "We" Deliberately

- **"We"** = the authors and the reader together, reasoning through the argument: "We can now see why the inverted-U appears across modalities."
- **"You"** = addressing the reader directly for engagement: "Imagine you walk into a room with bare concrete walls, fluorescent lighting, and no windows. You feel something is wrong — this is the Goldilocks Principle in action."
- **"One"** = never use. It sounds Victorian.
- **"The authors"** = never in ATLAS prose. This is third-person journal convention that creates distance.

---

## 2. Paragraph-Level Norms

### 2.1 The SCQA Structure

For explanatory paragraphs, use Situation-Complication-Question-Answer:

1. **Situation**: What everyone agrees on (1-2 sentences)
2. **Complication**: What's surprising, missing, or problematic (1-2 sentences)
3. **Question**: What this raises (explicit or implied, 0-1 sentence)
4. **Answer**: Your claim (1-2 sentences, then supporting evidence)

**Example**:
"The inverted-U function has been documented in visual, thermal, and acoustic domains for decades (**Situation**). What has not been shown is whether these domain-specific curves reflect a single underlying mechanism or are merely coincidental parallels (**Complication**). If they share a mechanism, we should be able to predict one domain's optimum from another's (**Question implies**). The Goldilocks Principle proposes exactly this: all modalities optimize under the same prediction-error efficiency constraint, differing only in the units of the complexity measure C(x) (**Answer**)."

### 2.2 Paragraph Length

Target 4-7 sentences. Shorter than 3 feels choppy (blog style). Longer than 8 loses the reader (textbook style). A paragraph is a unit of argument — it should contain exactly one move in the reasoning chain.

### 2.3 Transitions

Use explicit logical connectives, but vary them. Avoid starting three paragraphs in a row with "However." Good transition inventory:

- **Addition**: "Moreover," "Furthermore," "In addition,"
- **Contrast**: "However," "Yet," "On the other hand," "Despite this,"
- **Consequence**: "As a result," "This implies," "Consequently,"
- **Evidence**: "Consistent with this," "Supporting this claim," "For example,"
- **Concession**: "While X is true," "Granted," "Although,"
- **Summary**: "In short," "The upshot is," "To summarize,"

But the best transition is no connective at all — just a sentence that picks up where the previous paragraph ended: "This cross-modal consistency raises an obvious question: what is the mechanism?"

---

## 3. Section-Level Norms

### 3.1 Section Openings

Every section should open with a 2-3 sentence orientation that tells the reader: (a) what this section covers, (b) why it matters, and (c) what the punchline will be.

**Good**: "This section reviews the empirical evidence for inverted-U curves across five sensory modalities. The evidence is strongest for visual complexity and thermal comfort, moderate for acoustics and temporal variation, and weak for social density. We flag specific gaps — particularly the absence of olfactory data and the WEIRD bias in all published studies."

**Bad**: "We now turn to the empirical evidence." (Tells the reader nothing.)

### 3.2 Section Closings

Every section should end with a forward-pointing sentence that connects to the next section.

**Good**: "The empirical pattern is clear: inverted-U curves are robust across modalities. What remains is to explain *why* — which requires the neural and computational mechanisms discussed in Section 6."

**Bad**: "In conclusion, the evidence supports the Goldilocks Principle across modalities." (Dead end — reader doesn't know where to go next.)

### 3.3 Headings

Headings should be informative, not just topical. A heading should tell the reader the section's conclusion.

**Good heading**: "Fractal Dimension Peaks at D ≈ 1.3 Because Natural Scenes Do"
**Bad heading**: "Fractal Dimension Results"

**Good heading**: "Cultural Calibration: The Optimum Shifts, the Shape Doesn't"
**Bad heading**: "Cross-Cultural Considerations"

---

## 4. Handling Technical Content

### 4.1 Equations

Always introduce an equation in words before presenting it formally. The words should convey the intuition; the equation should convey the precision.

**Good**: "Preference follows a Gaussian curve around the optimal complexity. When complexity matches the optimum exactly, preference is maximal. As complexity deviates in either direction, preference falls off symmetrically. The rate of fall-off depends on the individual's tolerance bandwidth. Formally:

P(x) = exp(−(C(x) − C*)² / (2σ²))

where C(x) is the complexity of stimulus x, C* is the individual's optimum, and σ is their tolerance."

**Bad**: "We model preference as P(x) = exp(−(C(x) − C*)² / (2σ²))."

After presenting an equation, always walk through what happens at key values: "When C(x) = C* (stimulus matches the optimum), P = 1 — maximal preference. When C(x) deviates by one σ in either direction, P drops to about 0.6."

### 4.2 Statistics

Report effect sizes, not just p-values. Use the format: "effect description (d = 0.45, 95% CI [0.32, 0.58])."

Translate effect sizes into everyday language: "a medium effect size of d = 0.45, meaning that roughly 67% of participants in the optimal-complexity condition preferred their environment over the baseline."

### 4.3 Jargon Rules

- **Introduce every technical term on first use** with a plain-English definition in the same sentence
- **Never use a technical term when a plain one works**: "brain regions" not "neural substrates"; "falls off" not "attenuates"; "brain's prediction system" not "hierarchical generative model" (unless specifically discussing the model)
- **Acronyms**: Spell out on first use. Use the acronym only if it appears 5+ times. Otherwise, just use the full term.
- **Latin**: Avoid. "For example" not "e.g."; "that is" not "i.e."; "and others" not "et al." (except in citations)

### 4.4 Citation Style

Weave citations into the prose rather than stacking them:

**Good**: "Berlyne (1971) showed that collative variables — complexity, novelty, ambiguity — all follow inverted-U curves. This was replicated by Martindale and Moore (1988) for literary texts and by Taylor, Spehar, and colleagues (1999, 2005, 2011) for fractal visual patterns."

**Bad**: "Collative variables follow inverted-U curves (Berlyne, 1971; Martindale & Moore, 1988; Taylor et al., 1999, 2005, 2011; Spehar et al., 2003; Hagerhall et al., 2004)."

The good version gives the reader a narrative. The bad version gives them a bibliography.

---

## 5. Rhetorical Devices

These devices, used sparingly, make academic prose come alive. Use each no more than once per section.

### 5.1 The Concrete Opening
Start a section or paper with a specific, vivid scenario that the reader can picture.

"Imagine you walk into a hotel lobby. The ceiling is 12 meters high. The floor is polished marble. Every surface is a uniform off-white. There is no art, no texture, no variation. You feel uneasy — something is missing. Now imagine the same lobby with a climbing wall of plants along one wall, natural stone floors with visible grain, pendant lights at varying heights, and a view of trees through floor-to-ceiling windows. The space feels alive. What changed? Not the function — both lobbies serve the same purpose. What changed is the complexity."

### 5.2 The Surprising Statistic
Deploy a single striking number to anchor a claim.

"Gothic cathedrals have a fractal dimension of approximately 1.3 — exactly the same as a coastline. This is not a coincidence."

### 5.3 The Reversal
State the conventional wisdom, then overturn it.

"The obvious explanation is that people simply prefer what they grew up with. But this cannot be right, because the inverted-U shape is universal across cultures — only the location of the peak shifts."

### 5.4 The Honest Concession
Acknowledge limitations directly, without hedging.

"We do not yet have olfactory data. No published study has measured the Goldilocks curve for scent. This is a genuine gap, not a minor footnote — if the principle truly generalizes across modalities, it should hold for smell."

---

## 6. Tone Calibration

### 6.1 Confidence Spectrum

Match your phrasing to your evidence:

| Evidence Level | Phrasing |
|---|---|
| **Strong** (replicated, meta-analyzed, d > 0.5) | "X is the case." / "X reliably produces Y." |
| **Moderate** (several studies, consistent direction) | "X appears to produce Y." / "The evidence suggests X." |
| **Preliminary** (one or two studies, small samples) | "Initial evidence points toward X." / "X has been reported but not yet replicated." |
| **Speculative** (theoretical argument, no data) | "We hypothesize that X." / "It is plausible that X, though no direct evidence exists." |
| **Gap** (no data at all) | "This remains untested." / "No published data address X." |

Never use "clearly" or "obviously" — if it were clear or obvious, you wouldn't need to say so. Never use "interestingly" — let the reader decide what's interesting.

### 6.2 Warmth Without Informality

The ATLAS voice is warm and direct but not casual. Think of a professor who genuinely enjoys explaining something to a student who has just asked a smart question.

- **Good**: "This is where the story gets interesting." (Warm, conversational, creates anticipation)
- **Bad**: "This is super cool." (Too informal)
- **Also bad**: "It is of considerable interest to note that..." (Stuffy, creates distance)

---

## 7. Document-Specific Calibrations

### 7.1 Papers (Psychological Review, BBS, etc.)
- Bias: 60% toward popular, 40% toward expert
- Equations: include and explain
- Paragraphs: 5-7 sentences
- Citations: woven into prose (see §4.4)
- First person: "we" throughout
- Figures: captioned per Scientific American standard (see VISUALIZATION_NORMS.md)

### 7.2 QA System Responses
- Bias: 80% toward popular, 20% toward expert
- Equations: only if the user asks
- Paragraphs: 3-5 sentences
- Citations: mention key researchers by name, link if available
- First person: "the system finds..." or direct address "you asked about..."
- Figures: optional, inline

### 7.3 Technical Documentation (TASKS.md, Architecture docs)
- Bias: 50/50
- Equations: include without verbal scaffolding
- Paragraphs: short (2-4 sentences)
- Citations: APA format, brief
- First person: minimal
- Figures: diagrams and tables with brief captions

### 7.4 Master Document
- Bias: 55% popular, 45% expert
- Equations: include, explain key terms, worked examples
- Paragraphs: 5-8 sentences (denser than papers — this is a reference)
- Citations: full APA in body + reference lists
- First person: "we" for shared reasoning
- Figures: all figures captioned per Scientific American standard

---

## 8. Common Mistakes to Avoid

1. **Hedging stacks**: "It might perhaps be the case that X could potentially..." — Pick one hedge or none.
2. **Nominalization**: "The optimization of prediction error" → "Optimizing prediction error." Verbs are stronger than nouns.
3. **Throat-clearing**: "It is important to note that..." — Just state the note.
4. **Elegant variation**: Don't cycle between "the brain," "the neural system," "the cognitive apparatus" for the same referent. Pick one term and stick with it. Clarity beats style.
5. **Citation clustering**: "(Smith, 2020; Jones, 2019; Brown, 2018; Garcia, 2017; Kim, 2016)" — This is a bibliography, not prose. Name the 1-2 most important, cite the rest in a footnote.
6. **False balance**: Don't present a fringe view as equally weighted to a mainstream consensus. Report the consensus, then acknowledge the dissent.
7. **Passive hedging**: "It has been suggested that..." — By whom? Say so.
8. **Missing "so what"**: Every paragraph should leave the reader knowing why they just read it.

---

## 9. Quick Reference Card

When writing any ATLAS prose, ask:

1. **Who is my reader?** (Smart 3rd-year undergrad unless otherwise specified)
2. **What is the one thing they should take away?** (State it in the first sentence)
3. **Am I leading with the point or building to it?** (Lead with it)
4. **Would I say this out loud to a student?** (If not, rewrite)
5. **Is every technical term defined on first use?** (Must be)
6. **Does every paragraph have a "so what"?** (Must have)
7. **Am I being honest about what I know vs. don't?** (See confidence spectrum)
8. **Is this the simplest way to say this?** (Probably not — simplify again)
