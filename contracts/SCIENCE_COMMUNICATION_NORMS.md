# Science Communication Writing Norms

*Canonical reference for article-level prose, reports, and extended documents produced by ATLAS.*
*Companion to `WRITING_STYLE_GUIDE.md` (sentence/paragraph/section mechanics) and `MATH_EXPLANATION_NORMS.md` (formula presentation).*
*Last updated: 2026-05-06 (added MANDATES PROVENANCE header per CONTRACT_PROCESS_PROVENANCE_AUDIT recommendation #1)*

```
═══ MANDATES PROVENANCE ═══
docs_read:        [contracts/PROSE_PROCESS_PROVENANCE_ADDENDUM_2026-05-06.md,
                  contracts/SCIENCE_COMMUNICATION_NORMS.md (this file, surveyed),
                  contracts/WRITING_STYLE_GUIDE.md (header survey),
                  data/construct_lexicon.json]
docs_read_at:     2026-05-06 (header back-fill session)
protocol_applied: Header added retrospectively per the
                  PROSE_PROCESS_PROVENANCE_ADDENDUM contract. The body
                  of this document was authored prior to the addendum
                  and pre-dates the lex-aware metric. The header
                  records honest measurement against current gates,
                  not a freshly rewritten body. A second-pass rewrite
                  to bring this norm document into compliance with its
                  own gates is queued as future work.
gates_target:     This document is itself a norms reference, so the
                  strict 750-1250 sc-summary gate does not apply. The
                  relevant gates are structural compliance, internal
                  consistency, and the presence of this header.
gates_measured:   measured by prose_provenance_ingester on ingest;
                  body word count exceeds 5000 (norms reference, not
                  a sc-summary), so the wc_750-1250 gate is out of
                  scope by design
gates_passed:     trigger satisfied, header present (this block),
                  references documented, ingester wired
gates_failed:     full sc-summary gate compliance is out of scope for
                  a norms reference document; the strict gates apply
                  to deliverables produced *under* these norms, not to
                  the norms document itself
═══════════════════════════
```

---

## Purpose

The `WRITING_STYLE_GUIDE.md` tells you *what* to do at the sentence, paragraph, and section level. This document tells you *why* those techniques work and extends them to article-level architecture, revision methodology, and genre-specific guidance. It is grounded in the practices of named science writers and writing researchers, just as `MATH_EXPLANATION_NORMS.md` is grounded in named mathematical communicators.

These norms apply whenever we write extended prose — papers, articles, reports, master document sections, perspective pieces, or any document exceeding ~2,000 words. They are David Kirsh's style preferences for all ATLAS writing output and should be treated as binding constraints, not optional suggestions.

---

## Reference Group

The norms below are synthesized from the following science writers and writing researchers, each selected because they have articulated *why* their techniques work, not merely demonstrated them:

**Steven Pinker** (Harvard) — *The Sense of Style: The Thinking Person's Guide to Writing in the 21st Century* (2014). Pinker brings cognitive science to bear on prose style. His three central contributions are: (a) *classic style* — the writer as a guide showing the reader something, not as an authority pronouncing truths; (b) the *curse of knowledge* — the systematic failure to realize that your reader does not share your mental model; and (c) *coherence through arcs of reasoning* — the reader needs to track which thread they're on and why each sentence advances it. Pinker's key insight is that bad academic writing is not a character flaw but a cognitive bias: experts literally cannot imagine what it is like not to know what they know, and this produces prose that assumes too much and explains too little (Pinker, 2014, ~3,200 Google Scholar citations).

**Joseph Williams** (University of Chicago) — *Style: Lessons in Clarity and Grace* (12th ed., 2016, with Joseph Bizup). Williams's contribution is the most empirically grounded sentence-level writing guide ever written. His two foundational principles are: (a) the *Given-New contract* — begin each sentence with information the reader already possesses, end with the new information you want to convey; and (b) the *stress position* — readers treat the end of a sentence as the point of emphasis, so put your most important content there. These are not stylistic preferences; they are grounded in psycholinguistic research on how readers process syntax (Williams & Bizup, 2016, ~6,500 citations across editions).

**Richard Lanham** (UCLA) — *Revising Prose* (5th ed., 2006) and the Paramedic Method. Lanham provides the most actionable *revision* technique in existence: the Paramedic Method, an eight-step diagnostic that transforms bloated, nominalized academic prose into clear, active sentences. His key concept is the *lard factor* — the percentage of words in a passage that carry no information. Typical academic writing has a lard factor of 50-70%. Lanham's method systematically identifies and removes it. The Paramedic Method is taught in more than 500 university writing programs because it works consistently on any prose, by any writer (Lanham, 2006, ~1,800 citations).

**Helen Sword** (University of Auckland) — *Stylish Academic Writing* (2012) and the Writer's Diet diagnostic. Sword conducted the largest empirical study of academic writing style ever attempted: she analyzed 1,000 articles across 10 disciplines and showed that the best-cited papers in every field use concrete subjects, active verbs, and first person more frequently than poorly cited papers. Her *Writer's Diet* test diagnoses prose health by counting five word categories: "be" verbs, abstract nouns, prepositions, adjectives/adverbs, and "it"/"this"/"there" openers. High concentrations of any category signal sick prose (Sword, 2012, ~2,100 citations).

**Oliver Sacks** (Columbia) — *The Man Who Mistook His Wife for a Hat*, *Awakenings*, *Musicophilia*. Sacks demonstrated that clinical neurological observations become comprehensible and memorable when embedded in the full texture of a patient's lived experience. His technique: every scientific claim is encountered first as a human story, and the theoretical framework emerges from the story rather than preceding it. Sacks never asks the reader to understand a mechanism in the abstract — the mechanism is always already doing something to someone specific (Sacks, 1985, 1973, ~12,000+ citations across works).

**Carl Sagan** (Cornell) — *The Cosmic Connection*, *The Dragons of Eden*, *Cosmos*. Sagan's distinctive contribution to science writing is *scale bridging*: he moves fluently between the very large and the very small, the very old and the very recent, by using concrete analogies that translate unfamiliar magnitudes into human-scale experience. "If you wish to make an apple pie from scratch, you must first invent the universe" is not just a quip — it is a pedagogical technique that makes cosmological timescales experientially accessible. Sagan also demonstrated that intellectual humility and wonder are not rhetorical weaknesses but strengths: admitting what science does not know is more compelling than pretending it knows everything (Sagan, 1973, 1977, 1980, ~5,000+ citations across works).

**Ed Yong** (The Atlantic) — *An Immense World*, *I Contain Multitudes*. Yong represents the current state of the art in long-form science journalism. His technique involves (a) *slow complexity building* — introducing one new concept at a time, never more, and always through a concrete example; (b) *dialogue with researchers* — quoting scientists in their own words so the reader hears the genuine voice of discovery; and (c) *defamiliarization* — taking something the reader thinks they understand (their own senses, their microbiome) and systematically showing that their understanding is wrong in interesting ways (Yong, 2016, 2022, Pulitzer Prize for Explanatory Reporting 2021).

**Atul Gawande** (Harvard Medical School) — *Complications*, *Better*, *The Checklist Manifesto*, *Being Mortal*. Gawande's contribution is the *narrative of systematic improvement*: he takes the reader through a problem, shows why the obvious solution fails, introduces the actual solution, and then shows its consequences — including the ways it falls short. Every essay follows a dramatic arc borrowed from fiction: setup, complication, crisis, resolution. His technique makes medical and public health evidence not just intelligible but narratively compelling (Gawande, 2002, 2007, 2009, 2014, ~8,000+ citations across works).

**Rachel Carson** (formerly US Fish and Wildlife Service) — *Silent Spring*, *The Sea Around Us*. Carson demonstrated that scientific evidence about invisible processes (pesticide bioaccumulation, marine ecology) becomes actionable when the reader can feel its consequences. Her technique: *sensory immersion* in the described environment, so that the scientific claim is experienced before it is stated. She also pioneered what we might call *ethical embedding* — making the reader understand that a scientific finding has moral implications without sermonizing about those implications (Carson, 1962, 1951, ~12,000+ citations for *Silent Spring* alone).

**Jean-Luc Doumont** (Principiae) — *Trees, Maps, and Theorems* (2009). Doumont brings engineering discipline to science communication. His central principle is *signal-to-noise*: every element of a document (word, sentence, figure, heading) either advances the reader's understanding or impedes it, and the writer's job is to maximize the signal. His most actionable contribution is the principle that *structure is communication*: how content is organized conveys meaning as strongly as the content itself. A well-structured document with mediocre prose is more useful than a poorly structured document with brilliant prose (Doumont, 2009, ~500 citations).

---

## The Twelve Norms

### Norm 1: Classic Style — The Writer as Guide (Pinker)

**The norm**: Write as if you are showing the reader something interesting that you have noticed. You are not lecturing, not summarizing, not performing expertise. You are a competent equal who happens to have seen something the reader has not yet seen, and you are pointing it out.

**Why it matters**: Pinker identifies two dysfunctional academic styles: (a) *self-conscious style*, where the writer constantly qualifies, hedges, and meta-comments on the difficulty of what they're doing ("It is important to note that the complexity of the issue makes definitive claims difficult..."); and (b) *oracular style*, where the writer issues pronouncements from authority without showing the reasoning ("The data unambiguously demonstrate that..."). Classic style avoids both. The writer is confident but not dogmatic, clear but not simplistic.

**Implementation**: When revising, ask of each paragraph: "Am I showing the reader something, or am I telling them about myself showing them something?" If the latter, cut the meta-commentary and just show.

**Diagnostic sentence types to eliminate**:
- "In this section, we will discuss..." (meta-commentary — just discuss)
- "As noted above..." (self-referential — the reader can see what's above)
- "It is worth pointing out that..." (throat-clearing — just point it out)
- "The author would like to argue that..." (self-conscious — just argue)

---

### Norm 2: The Given-New Contract (Williams)

**The norm**: Begin every sentence with information the reader already possesses (the Given), and end with the information you want to convey (the New). This mirrors the structure of working memory: the reader's attention activates the topic, and the new information attaches to it.

**Why it matters**: Violations of the Given-New contract are the single most common cause of "hard to follow" prose. When a sentence begins with new information, the reader has no schema to attach it to and must hold it in suspension until the sentence ends — consuming working memory that should be available for comprehension. Williams showed that reordering sentences to respect Given-New produces immediate, measurable improvements in reading comprehension, even for expert readers (Williams & Bizup, 2016, Chapter 5).

**Example**:

Bad (New-Given): "A non-monotonic free energy landscape with a local minimum at intermediate stimulus complexity is produced by hierarchical Bayesian inference under precision-weighted prediction error minimization."

Good (Given-New): "Hierarchical Bayesian inference under precision-weighted prediction error minimization [Given — the mechanism we've been discussing] produces a non-monotonic free energy landscape [New — the consequence we're introducing] with a local minimum at intermediate stimulus complexity [Newest — the specific feature of that landscape]."

Better (Given-New, with the ATLAS voice): "The prediction-error machinery we have been describing [Given] produces a surprising result [bridge to New]: there is a sweet spot of complexity [New] — not too simple, not too chaotic — where the brain's processing is maximally efficient [Newest — why it matters]."

**Rule of thumb**: If the grammatical subject of a sentence is something the reader has not encountered in the last two sentences, the sentence probably violates Given-New.

---

### Norm 3: The Stress Position (Williams)

**The norm**: Place the most important information at the end of a sentence — the *stress position*. Readers unconsciously treat the end of a sentence as its rhetorical climax.

**Why it matters**: English syntax creates a natural emphasis gradient: the beginning of a sentence is the topic position (what we're talking about), the middle is the supporting material, and the end is the stress position (the point). When writers bury their main claim in a subordinate clause in the middle of a sentence and then trail off with qualifications, they are fighting the language's own emphasis structure.

**Example**:

Weak stress: "Under conditions of moderate visual complexity and adequate natural lighting, participant stress levels were significantly reduced, as measured by salivary cortisol, in a large-scale field study conducted in Scandinavian offices."

Strong stress: "A large-scale field study in Scandinavian offices found that moderate visual complexity combined with adequate natural lighting significantly reduced participant stress — as confirmed by salivary cortisol measurements."

The second version puts the finding (reduced stress) and its measurement (cortisol) at the end, where the reader naturally assigns emphasis.

**Corollary**: The Given-New contract and the stress position work together. Given → New means topic → stress. If you get the topic right (sentence-initial, familiar), the stress position (sentence-final, important) follows naturally.

---

### Norm 4: Kill the Zombie Nouns (Lanham, Sword)

**The norm**: Identify nominalizations — abstract nouns derived from verbs — and restore the buried verb. "The optimization of" → "optimizing"; "an investigation of" → "investigating"; "the implementation of" → "implementing."

**Why it matters**: Nominalizations are what Sword calls "zombie nouns": they are dead verbs walking around disguised as nouns, and they bring two pathologies. First, they eliminate the agent — "the optimization of prediction error" hides *who* is optimizing. Second, they force the writer to use weak verbs ("is," "was," "involves," "performs") as syntactic scaffolding for the noun, producing sentences where nothing actually happens: "The investigation of the relationship between ceiling height and creative output was performed using a series of laboratory studies." Compare: "We investigated whether ceiling height affects creative output in a series of laboratory studies."

**Diagnostic**: Scan for these suffixes: *-tion, -ment, -ness, -ity, -ence, -ance, -ism*. Each one is a candidate for de-nominalization. Not all should be changed — some nominalizations are the standard term in a field (e.g., "optimization" in engineering, "cognition" in psychology). But if a nominalization can be restored to its verb form without awkwardness, it should be.

**The Lanham test**: Circle every preposition in a paragraph. If more than one sentence in three starts with a prepositional chain ("In the investigation of the effect of..."), the paragraph has a nominalization problem.

---

### Norm 5: The Paramedic Method — A Revision Protocol (Lanham)

**The norm**: Apply Lanham's eight-step Paramedic Method as the first pass of every revision. This is not optional; it is a diagnostic protocol that catches 80% of prose problems in a single pass.

**The eight steps**:
1. **Circle the prepositions** ("of," "in," "by," "for," "with," "on," "at," "to," "from"). Strings of three or more prepositions signal buried verbs and excessive abstraction.
2. **Circle the "is" forms** ("is," "was," "are," "were," "has been"). These are often placeholder verbs holding up a nominalization.
3. **Find the action** — what is actually happening in this sentence? Identify the real verb hiding behind the nominalizations.
4. **Put the action in a simple active verb** — rewrite so the action is expressed by the main verb, not by a noun.
5. **Put the agent in the subject** — who is doing the action? Make them the grammatical subject.
6. **Start fast** — delete all slow windups: "It is important to note that," "There is evidence to suggest that," "It can be observed that," "The fact that."
7. **Read the original aloud, then read the revision aloud.** If the revision sounds better spoken, it reads better silently.
8. **Compute the lard factor**: (original word count − revised word count) / original word count. A lard factor above 30% means the original was significantly bloated. Typical academic prose: 40-60%.

**Example**:

Original (42 words): "The investigation of the relationship between the implementation of biophilic design elements and the reduction of occupational stress in open-plan office environments was conducted through the administration of standardized psychometric instruments to a sample of 150 knowledge workers."

After Paramedic Method (22 words, lard factor 48%): "We tested whether biophilic design reduces stress in open-plan offices, using standardized psychometrics with 150 knowledge workers."

---

### Norm 6: The Curse of Knowledge — Systematic Diagnosis (Pinker)

**The norm**: After drafting, systematically identify every point where you have assumed knowledge the reader does not possess. The curse of knowledge is not a failure of empathy; it is a failure of *simulation*. You cannot accurately simulate a mind that lacks information your own mind possesses, because the information automatically activates and colors your processing.

**Why it matters**: Pinker argues that the curse of knowledge is the single greatest cause of bad writing — greater than laziness, greater than jargon, greater than time pressure. It produces prose that is correct but incomprehensible, because the writer cannot identify the inferential gaps between their knowledge and the reader's.

**Systematic diagnosis**:
1. **Technical term audit**: List every technical term used in a passage. For each, ask: "Would a smart 3rd-year undergraduate in cognitive science know this term?" If no, define it on first use.
2. **Abbreviation audit**: List every abbreviation. Would the reader remember what it stands for after 10 pages? If not, spell it out again.
3. **Implicit argument audit**: For each paragraph, ask: "What step in my reasoning did I skip because it seemed obvious to me?" That skipped step is exactly where the reader will get lost.
4. **Background knowledge audit**: For each claim, ask: "What do I know that makes this claim plausible?" If the answer involves knowledge the reader may lack, provide it.

**The naive reader test**: Read your prose as if you had never seen the material before. This is impossible to do perfectly (the curse of knowledge, again), but even a partial attempt catches the worst gaps. Better: find an actual naive reader and watch where they stumble.

---

### Norm 7: Narrative Threading — The Story Underneath the Argument (Pinker, Sacks, Gawande)

**The norm**: Every extended document tells a story, whether or not the writer intends it. The norm is to *intend it*. Identify the narrative arc — the question, the complications, the resolution — and make it visible to the reader.

**Why it matters**: Narrative structure is not decoration; it is a cognitive scaffold. Human comprehension evolved for stories, not for logical propositions. A reader who can answer the question "What is this about and where is it going?" processes each sentence faster and retains more. A reader who cannot answer that question must hold each sentence in suspension, waiting for context that may never arrive (Pinker, 2014, Chapter 6).

**Narrative structures for academic writing**:

**For empirical papers** (Gawande's arc):
1. *Setup*: Here is a phenomenon everyone thinks they understand
2. *Complication*: But here is something wrong with the standard account
3. *Crisis*: The standard tools cannot resolve this — we need something new
4. *Resolution*: Here is what we did, here is what we found
5. *Denouement*: Here is what it means, and here is what we still don't know

**For theoretical papers** (Sacks's arc):
1. *Case presentation*: Here is a concrete instance of the thing we want to explain
2. *Inadequacy of existing accounts*: Here is why current theory fails on this case
3. *New framework*: Here is a different way to think about it
4. *Demonstration*: Watch the new framework handle the case (and three more)
5. *Implications*: Here is what changes if this framework is right

**For review/perspective papers** (Yong's arc):
1. *The hook*: Here is something strange or counterintuitive
2. *The landscape*: Here is what different people have found
3. *The synthesis*: Here is the pattern that connects them
4. *The gap*: Here is what nobody has figured out yet
5. *The question*: Here is what we should be asking next

**Implementation**: Before writing, state in one sentence: "This document's story is: ____." If you cannot complete that sentence, you do not yet know what you are writing.

---

### Norm 8: Scaffolded Explanation — The Feynman Staircase (Sagan, Yong)

**The norm**: When introducing a complex concept, build toward it through a sequence of simpler concepts, each of which the reader can verify before proceeding. Never ask the reader to accept two new ideas simultaneously.

**Why it matters**: Cognitive load theory (Sweller, 2011) shows that working memory can hold 3-5 novel chunks at once. When a writer introduces a complex idea in a single sentence, the reader's working memory overflows and comprehension collapses. The solution is *scaffolded explanation*: present the components one at a time, allow the reader to integrate each before introducing the next, and periodically consolidate what has been built.

**The Feynman Staircase** (adapted from Feynman's lecture technique and Sagan's writing):
1. **Anchor**: Connect to something the reader already knows. "You know how a thermostat maintains room temperature..."
2. **One new idea**: Introduce exactly one concept. "The brain does something similar — it maintains a prediction of what should happen next."
3. **Make it concrete**: Give a specific example. "When you walk into a familiar room, your brain has already predicted the temperature, the lighting, the sounds. If something is different — say, the lights are off when they should be on — you notice immediately."
4. **Test it**: Show the reader a consequence they can verify. "This is why you startle when someone has rearranged the furniture. Your prediction was wrong, and the error signal demands attention."
5. **Build**: Use this concept as the foundation for the next. "Now, what happens when prediction errors are constant — when the environment is perpetually surprising?"

**The Sagan technique**: When the concept requires unfamiliar magnitudes (very large, very small, very old, very fast), translate to human scale. "If the age of the universe were compressed into a single year, all of recorded human history would occur in the last 14 seconds of December 31st." This is not dumbing down — it is making the unfamiliar experientially accessible.

**The Yong technique**: When the concept requires understanding a perspective radically different from the reader's (animal senses, microbial ecology, alien cognition), lead with a specific, vivid example of what the world looks like from that perspective. Only after the reader has *felt* the difference should you explain the mechanism that produces it.

---

### Norm 9: Honest Uncertainty — Calibrated Confidence (Carson, Sagan)

**The norm**: Match the strength of your language precisely to the strength of your evidence. Never hedge reflexively ("may perhaps be somewhat related to"), and never overclaim ("clearly demonstrates"). Both are failures of intellectual honesty.

**Why it matters**: Carson and Sagan both demonstrated that acknowledging what is unknown is more persuasive than pretending everything is settled. Carson's *Silent Spring* was devastating not because it claimed certainty about DDT's effects, but because it documented with precision exactly what was known, what was suspected, and what was unknown — and then asked why the unknowns had not been investigated. Sagan's "extraordinary claims require extraordinary evidence" is not skepticism; it is a calibration tool.

**The confidence spectrum** (expanded from WRITING_STYLE_GUIDE):

| Evidence Level | Language | Example |
|---|---|---|
| **Established** (meta-analysis, d > 0.5, replicated 5+) | State as fact: "X produces Y." | "Natural daylight improves alertness through circadian regulation." |
| **Strong** (3+ studies, consistent, d > 0.3) | Confident claim: "X reliably produces Y." | "Exposed wood reliably reduces physiological stress markers." |
| **Moderate** (2-3 studies, consistent direction) | Qualified claim: "Evidence indicates that X produces Y." | "Evidence indicates that translucent partitions increase cognitive load." |
| **Preliminary** (1 study, or inconsistent results) | Cautious claim: "Initial evidence suggests X." | "Initial evidence suggests that olfactory transitions mark spatial boundaries." |
| **Theoretical prediction** (no direct data, but derived from established mechanisms) | Explicit labeling: "The framework predicts X, though this has not been directly tested." | "The Goldilocks Principle predicts cross-modal compensation between visual and acoustic channels, though no published study has tested this directly." |
| **Speculation** (interesting possibility, no data or mechanism) | Clearly marked: "We speculate that X, acknowledging that this goes beyond available evidence." | "We speculate that biophilic design may interact with circadian regulation, though this remains untested." |

**The Sagan rule**: "It pays to keep an open mind, but not so open that your brains fall out." Every claim must be traceable to either evidence or a named theoretical derivation. Untethered speculation is labeled as such.

---

### Norm 10: Defamiliarization — Making the Familiar Strange (Yong, Sacks)

**The norm**: When writing about something the reader thinks they already understand, your first job is to show them that they don't. Defamiliarization is the technique of revealing the hidden complexity or strangeness in something that appears ordinary.

**Why it matters**: The greatest barrier to learning is not ignorance — it is the illusion of knowledge. When a reader sees "visual complexity affects mood," they think they understand it. They don't. They need to be shown the specific mechanisms, the surprises, the counterintuitive consequences. Defamiliarization creates the cognitive gap that motivates learning.

**Techniques**:

**The Yong technique** (reveal hidden complexity): "You think you know what a window does. It lets in light. But a window does at least five different things to your nervous system simultaneously, through five different neural pathways, and two of them are in direct conflict."

**The Sacks technique** (reveal through pathology): Show what something does by showing what happens when it fails. "You don't notice your proprioceptive sense until it's gone. The woman who lost hers couldn't stand, couldn't walk, couldn't feed herself — not because her muscles were damaged, but because she couldn't feel where her body was in space."

**The Carson technique** (reveal invisible processes): Make the reader see a process they normally cannot perceive. "In the ten minutes you have been reading this, the air-handling system in your building has delivered approximately 200 cubic feet of conditioned air to your workstation. That air has passed through filters that remove particles larger than 10 microns, but not volatile organic compounds from the carpet adhesive installed six months ago."

**When to use**: Use defamiliarization at the opening of a section or paper. Once the reader's complacency is disrupted, they are ready to learn. Do not use it mid-argument — by that point, the reader should already be engaged.

---

### Norm 11: Structure as Communication (Doumont)

**The norm**: The organization of a document conveys meaning as powerfully as its content. A well-organized document with mediocre prose communicates more effectively than a brilliantly written document with poor organization. Therefore, invest more time in structure than in word choice.

**Why it matters**: Doumont's research shows that readers extract meaning from three structural cues before they process a single sentence: (a) the title and headings tell them what the document is about; (b) the first and last sentences of sections tell them the argument; (c) the sequence of sections tells them the logical flow. If these structural elements are clear, readers can tolerate considerable imperfection in the prose. If they are unclear, no amount of beautiful writing will save the document.

**Implementation — The Doumont Test**: Read only the title, headings, first sentence of each section, and last sentence of each section. If this gives you a coherent summary of the document's argument, the structure is working. If it does not, restructure before revising prose.

**Heading hierarchy**:
- **Level 1**: The document's major claims (3-7 per document)
- **Level 2**: The supporting arguments for each claim (2-5 per Level 1)
- **Level 3**: Specific evidence or technical detail (use sparingly — deeper than Level 3 signals organizational problems)

**Sequencing principles**:
- General → specific (overview before details)
- Known → unknown (what we know before what we discovered)
- Problem → solution (the gap before the work that fills it)
- Simple → complex (the easy case before the hard case)

---

### Norm 12: Ethical Embedding — The Responsibility of the Science Writer (Carson, Gawande)

**The norm**: When scientific findings have practical consequences for human wellbeing — as all of ATLAS's findings do, given that they concern the built environments people inhabit — the writer has an obligation to make those consequences visible without editorializing.

**Why it matters**: Carson did not write "DDT is bad" — she wrote in precise detail what DDT does to specific organisms in specific environments, and let the reader draw the conclusion. Gawande does not write "checklists save lives" — he describes in clinical detail what happens when a surgical team does and does not use a checklist, and the reader sees the difference. This technique is more persuasive than advocacy because it respects the reader's intelligence: it provides evidence, not opinions, and trusts the reader to reason from evidence to conclusion.

**For ATLAS specifically**: We are writing about how built environments affect human cognition, emotion, physiology, and behavior. When the evidence says that open offices reduce face-to-face interaction by 70% (Bernstein & Turban, 2018), or that translucent partitions exhaust cognitive control faster than no partitions at all, these findings have immediate implications for the millions of people who work in these environments. The writer's job is not to campaign for design changes but to present the mechanisms, the evidence, and the consequences with enough clarity that the reader — architect, designer, facilities manager, policy maker — can act on them.

**The test**: "Could a thoughtful decision-maker base a real decision on what I have written here?" If the evidence is clear, the mechanisms are specified, the effect sizes are reported, and the limitations are acknowledged — yes. If the writing is vague, the mechanisms are hand-waved, or the limitations are hidden — no.

---

## Genre-Specific Architecture

### Research Paper (target: *Psychological Review*, *BBS*)

| Section | Pages | Purpose | Key technique |
|---|---|---|---|
| Abstract | 0.5 | The entire argument in 250 words | Stress position: end with your strongest claim |
| Introduction | 3-4 | Pose the question; show why current answers fail | Narrative threading (Gawande's arc) |
| Theoretical Framework | 4-6 | Present the new framework | Scaffolded explanation (Feynman staircase) |
| Evidence | 6-8 | Show what the framework explains | Assertion-evidence pairs (one per subsection) |
| Predictions | 2-3 | Derive novel, testable predictions | Defamiliarization (Yong technique) |
| Discussion | 3-4 | Implications, limitations, future directions | Honest uncertainty (Sagan calibration) |
| Conclusion | 0.5-1 | One paragraph returning to the opening question | Close the narrative arc |

**Critical rule**: The Introduction and Discussion should be readable by a smart non-specialist. The Evidence section can be more technical. The reader should be able to read Intro → Discussion and understand the entire argument at a high level, then go back to Evidence for detail.

### Master Document Sections

| Element | Purpose | Key technique |
|---|---|---|
| Section header | State the claim, not the topic | Informative headings (WRITING_STYLE_GUIDE §3.3) |
| Opening paragraph | Orient the reader; state the punchline | Lead with the point (§1.1), SCQA structure (§2.1) |
| Body paragraphs | One argument per paragraph, 5-8 sentences | Given-New contract, stress position |
| Evidence presentation | Data, citations, effect sizes | Honest uncertainty, effect-size translation |
| Cross-references | Link to other sections | Forward-pointing transitions (§3.2) |
| Closing paragraph | What this means for the larger system | Ethical embedding (Carson technique) |

### Perspective/Review Article

Follow Ed Yong's arc: Hook → Landscape → Synthesis → Gap → Question. The entire article should be readable in one sitting (target: 5,000-8,000 words). Every section should contain at least one concrete example — never let the reader go more than two paragraphs without encountering a specific case.

---

## The Revision Protocol

Every document of more than 1,000 words should undergo this three-pass revision:

### Pass 1: Structural Revision (Doumont)
- Apply the Doumont Test: read only headings + first/last sentences. Does the argument hold?
- Check sequencing: does each section build on the previous?
- Check narrative arc: is there a story, and does it reach a resolution?
- Estimated time: 15-20 minutes per 3,000 words

### Pass 2: Sentence-Level Revision (Lanham + Williams)
- Apply the Paramedic Method to every paragraph
- Check Given-New contract: does each sentence begin with familiar information?
- Check stress positions: does each sentence end with its most important content?
- Kill zombie nouns: scan for -tion, -ment, -ness, -ity suffixes
- Estimated time: 30-45 minutes per 3,000 words

### Pass 3: Knowledge-Curse Audit (Pinker)
- Technical term audit: is every term defined on first use?
- Implicit argument audit: are any inferential steps skipped?
- Background knowledge audit: does every claim provide sufficient context?
- Confidence calibration: does every claim use the right evidence-level language?
- Estimated time: 20-30 minutes per 3,000 words

---

## Integration with Existing ATLAS Norms

This document extends but does not replace:

| Document | Scope | This document adds |
|---|---|---|
| `WRITING_STYLE_GUIDE.md` | Sentence, paragraph, section mechanics | Theoretical grounding (Williams, Lanham, Pinker), revision protocol, article-level architecture |
| `MATH_EXPLANATION_NORMS.md` | Formula and constant presentation | (No overlap — math norms are complementary) |
| `VISUALIZATION_NORMS.md` | Figures, charts, tables | (No overlap — visualization norms are complementary) |
| `Academic Presentation Service` | Slide design and oral presentation | (No overlap — presentation norms are complementary) |
| `docs/EPISTEMIC_PRINCIPLES.md` | QA answer epistemic rigor + science-writer principles for answers | This document provides the article-level *prose architecture*; EPISTEMIC_PRINCIPLES provides the *epistemic content standards* |

### Relationship to EPISTEMIC_PRINCIPLES.md (Principles 11-17)

The `docs/EPISTEMIC_PRINCIPLES.md` contains a second expert panel (Principles 11-17) that governs how the QA system communicates. Those 7 principles — Lead with the Human (Sacks), Give Scale (Sagan), Show the Seam (Sapolsky), Earn the Complexity (Yong), Name the Gap (Gawande), Make It Falsifiable (Pinker), The Hook and the Door (Roach) — apply to QA *answer construction* specifically. They tell the system what epistemic moves to make in an answer (defeasibility caveats, scope conditions, gap disclosure).

This document (Science Communication Norms) provides the complementary *prose techniques*: how to construct sentences (Given-New, stress position), how to structure arguments (narrative threading, scaffolded explanation), how to revise (Paramedic Method), and how to architect an entire article or document. The two documents work together: EPISTEMIC_PRINCIPLES tells you *what* epistemic commitments an answer must honor; this document tells you *how* to write prose that honors them clearly and beautifully.

### The Complete ATLAS Communication Stack

Together, these six documents constitute the complete ATLAS communication standards:

1. **Science Communication Norms** (this document) — article-level prose architecture, revision methodology, named science-writer techniques
2. **Writing Style Guide** (`contracts/WRITING_STYLE_GUIDE.md`) — sentence, paragraph, and section mechanics (the quick-reference companion)
3. **Epistemic Principles** (`docs/EPISTEMIC_PRINCIPLES.md`) — 10 epistemic norms + 7 science-writer norms governing answer content
4. **Math Explanation Norms** (`contracts/MATH_EXPLANATION_NORMS.md`) — formula and constant presentation (Strogatz, Devlin, Ellenberg reference group)
5. **Visualization Norms** (`contracts/VISUALIZATION_NORMS.md`) — figures, charts, and tables (Tufte, Cleveland & McGill)
6. **Academic Presentation Service** (`services/academic_presentation_service/SKILL.md`) — slide design and oral talks (Mayer, Feynman, Rosling)

---

## References

- Carson, R. (1962). *Silent Spring*. Houghton Mifflin. (~12,000 citations)
- Doumont, J.-L. (2009). *Trees, maps, and theorems: Effective communication for rational minds*. Principiae. (~500 citations)
- Gawande, A. (2009). *The checklist manifesto: How to get things right*. Metropolitan Books. (~4,000 citations)
- Lanham, R. A. (2006). *Revising prose* (5th ed.). Longman. (~1,800 citations)
- Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Viking. (~3,200 citations)
- Sacks, O. (1985). *The man who mistook his wife for a hat and other clinical tales*. Summit Books. (~5,000+ citations)
- Sagan, C. (1980). *Cosmos*. Random House. (~3,000+ citations)
- Sword, H. (2012). *Stylish academic writing*. Harvard University Press. (~2,100 citations)
- Sweller, J. (2011). Cognitive load theory. In J. Mestre & B. Ross (Eds.), *Psychology of learning and motivation* (Vol. 55, pp. 37-76). Academic Press.
- Williams, J. M., & Bizup, J. (2016). *Style: Lessons in clarity and grace* (12th ed.). Pearson. (~6,500 citations across editions)
- Yong, E. (2022). *An immense world: How animal senses reveal the hidden realms around us*. Random House.
