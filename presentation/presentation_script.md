# Presentation Script — AI Storytelling Agent
## 9 Slides | Investor + Lab Evaluator Edition
**Date:** March 22, 2026 | **Duration:** 5–7 minutes

---

## Slide 1 — Title Slide

**Bullets:**

* **Project:** AI Storytelling Script Generation Agent

* **Value Proposition:** The only end-to-end AI pipeline that generates, segments, voices, and extracts character consistency data for storytelling video — in one automated workflow


**Speaker Notes:**

Welcome. This presentation covers both the business opportunity and the technical implementation of an AI agent built for storytelling video production.

The product solves a problem that has been publicly confirmed by 50 independent market sources and acknowledged by the category leader — Midjourney — in their own words on February 18, 2026: character visual consistency across scenes is completely unsolved in the current generation of AI video tools.

We built an end-to-end pipeline that takes a raw idea and produces a segmented, voiced script with extracted character and entity data — the foundation for consistent image generation. The slides are structured in two halves: Slides 1–6 focus on market and business logic; Slides 7–9 go deep on technical implementation and evaluation methodology.

---

## Slide 2 — Product Overview

**Bullets:**

* **End-to-end pipeline:** Idea → RAG retrieval → Outline → Script → Validation → Segmentation → TTS Audio → Entity extraction
* **Problem solved:** Storytelling creators cannot complete AI-assisted projects because character appearance resets with every scene — forcing manual correction at every step
* **What the agent produces:** Validated script · Segmented scenes · MP3 audio per segment · `entities.json` with character visual base prompts · Human-readable entity report
* **Key differentiator #1 — Visual consistency system:** Automatic extraction of recurring characters, animals, and objects with base visual prompts for downstream image generation
* **Key differentiator #2 — Checkpoint pipeline:** Validate → approve → proceed at every stage; no credit burned on unreviewed output
* **Key differentiator #3 — Text preservation guarantee:** Character-level validation ensures the original script is never rewritten during segmentation (text_coverage = 1.000 in all experiments)
* **Integration:** REST API (FastAPI) — connectable to n8n, Zapier, or any no-code automation platform

**Speaker Notes:**

The product is a stateful autonomous agent orchestrated with LangGraph. It is not a chatbot — it is a deterministic pipeline with conditional logic, retry handling, and output validation at each node.

The pipeline has nine stages. You submit an idea, genre, duration, and language via a single API call. The agent retrieves storytelling best practices from Pinecone, synthesizes them, generates a structured outline, writes the script, validates it against the target length (90–110% tolerance), segments it into audio-visual moments, generates TTS audio for each segment, and then extracts all recurring entities — characters, animals, and objects — as structured visual identity data.

The entity extraction stage is specifically designed to power consistent image generation in the next phase of the product. Each entity gets a base visual prompt that can be injected into any text-to-image model to anchor visual appearance across all scenes.

The key differentiator versus all current competitors is not just what the pipeline produces — it is the architecture that prevents waste: validate before generating, not after.

---

## Slide 3 — Problem (Market Pain)

**Bullets:**

* **#1 Pain (22 / 50 sources):** Character visual consistency fails across scenes — confirmed by Midjourney in official company voice, February 18, 2026. Every tool in the market, without exception, resets character appearance between generations
* **#2 Pain (12 sources):** Credits burn on failed/unusable outputs — users pay per generation attempt, not per usable result. Documented waste: $3,000–$4,000 per user across multiple tools
* **#3 Pain (11 sources):** Billing traps destroy trust — unauthorized renewals, "unlimited" plans secretly capped, missing cancel buttons. Present in every major competitor's Trustpilot profile
* **#4 Pain (8 sources):** Irreversible work and data loss — platforms delete projects overnight on plan changes. Documented loss: 200+ hours of director work, months of illustration projects
* **#5 Pain (4+ sources):** No end-to-end pipeline — users must stitch 3+ separate tools that share no context, breaking character state at every tool boundary
* **Market sentiment:** Trustpilot scores — RunwayML 1.2/5 · Midjourney 1.5/5 · CapCut 1.2/5 · InVideo Studio 2.5/5 — across 916–941 reviews each. This is not an outlier signal
* **Buyer psychology:** "I'd switch tomorrow if any tool could give me consistent characters across 10 scenes" — r/Filmmakers, 1,300 upvotes (Source F5)

**Speaker Notes:**

All data on this slide comes from 50 independently sourced market signals — competitor Trustpilot profiles, Reddit threads, user forums, and public developer communities. None of these numbers are modeled; they are directly extracted from documented user statements.

The most important number is 22 out of 50. Character visual consistency was the spontaneously named top blocker by nearly half of all active market sources. It was not a leading question — these users volunteered it as the single condition they would need satisfied to switch platforms immediately.

The second critical signal is the trust destruction across every competitor. When every major player in a category has a Trustpilot score below 2.5, that is not a product quality problem — it is a structural market failure. Every dissatisfied user in those review profiles is a potential first-mover acquisition for any entrant that solves the core problem and does billing correctly.

For investors: this is demand-capture, not demand-creation. The buyers exist, have already spent $3,000–4,000 trying to solve the problem, are still unsatisfied, and have explicitly named the switching condition.

---

## Slide 4 — Market Opportunity

**Bullets:**

* **TAM — Global Generative AI in Content Creation:**
  $14.8B (2024) → $80.1B (2030) · CAGR 32.5% (Grand View Research)
* **SAM — English-language AI video & creator tools (NA + UK + AU/NZ):**
  $1.61B (2024) → $6.30B (2029) · CAGR 31.4%
* **SOM — Script-first, narrative-first, storyboard-first AI tools (est. 8% of SAM):**
  $128.6M (2024) → $535.4M (2029) · CAGR 33.0%
* **SOM capture milestones:**
  1% of SOM 2026 ($227.6M) = **$2.28M ARR** — viable Seed milestone
  3% of SOM 2026 = **$6.83M ARR** — credible Series A entry
* **Demand-side scale:** 50M+ active creators (SignalFire); 3M+ monetized YouTube channels; 2M+ full-time creators; 44M+ SMBs in North America pursuing content marketing
* **Market timing:** AI video tools are in **early growth** phase — 12 identifiable competitors with published pricing, documented user bases, but zero that have solved character consistency
* **Trust vacuum = entrant advantage:** No competitor has established brand trust. The category leader (Midjourney) has a 1.5/5 Trustpilot score. An entrant that ships clean billing plus the core technical capability starts with an unoccupied trust position

**Speaker Notes:**

The TAM at $14.8B contextualizes the category — generative AI in content creation is a real, investor-tracked market growing at over 30% per year. The number that matters for this product is the SOM: the specific niche of storytelling, narrative, and script-first AI tools.

The 8% SOM ratio is our estimate — it is a logical derivation, not a published research number, and that is stated transparently. We have cross-validated it bottom-up: at a $19/month ARPU, the SAM translates to approximately 7.1M potential paying accounts in 2026. Even capturing 0.5% of that base — 35,000 users — produces $8M+ ARR.

The critical insight is the competitive timing. The market is in early growth phase, not early stage. Competitors exist, users are paying, but the core technical problem remains completely unsolved. This is the window: after market validation, before consolidation. Once a well-funded incumbent ships character consistency, the window narrows significantly.

---

## Slide 5 — Use Cases

**Bullets:**

* **Use Case 1 — Multi-scene narrative video (22 sources):** Independent filmmaker or solo creator producing character-based stories — short films, branded narratives, YouTube series. Primary pain: same character must look identical across all scenes. Value: unlocks story-based AI video production for the first time
* **Use Case 2 — Commercial / client video production (12 sources):** Freelancer or small studio producing AI-assisted deliverables for paying clients. Value: reduces total production cost per accepted deliverable; eliminates manual frame-fixing cycles that currently consume 4× the production time vs. traditional methods
* **Use Case 3 — Book, comic, and graphic novel illustration (4+ sources):** Writer or illustrator creating a consistent visual character across multiple pages or panels. Value: single reference image anchors visual identity for the full project run
* **Use Case 4 — Automated YouTube / social media content pipeline (4 sources):** Creator automating recurring channel content — requires consistent brand character or host persona across videos over time. Value: batch production flow with a stable visual identity system
* **Use Case 5 — Multilingual / dubbed video for international distribution (3 sources):** Filmmaker or distributor producing AI-voiced content in multiple languages. Value: TTS pipeline already supports Russian and English with language-specific character rates (RU: 1,450 chars/min · EN: 1,000 chars/min)
* **Target ICP:** Independent filmmaker, creative producer, or visual storyteller who has already spent $1,400–$4,000 testing multiple AI tools, has switched platforms 4+ times, and has not found a working solution
* **Switching condition:** Binary — users have explicitly stated they would move immediately upon seeing consistent characters across ≥ 10 scenes in a live demonstration

**Speaker Notes:**

These five use cases are ranked by the frequency of independent market signal confirmations — they are not personas we invented. Use Case 1 alone represents 22 of 50 sources. That is not a niche — that is the market.

The ICP is unusually well-defined for a pre-launch product. We know the buyer: they are technically sophisticated, have high spending tolerance when ROI is believable, have zero platform loyalty after being burned by billing traps and data loss, and are making adoption decisions on proof, not promise.

What this means for go-to-market: the acquisition strategy is demonstration-first. Before any paid channel, ship a publicly accessible proof of concept showing consistent characters across 10+ scenes. The conversion trigger has already been named. The task is to show it, not explain it.

---

## Slide 6 — Investor Dashboard

**Bullets:**

* **Dashboard:** Power BI interactive model — `SaaS_ROI_PowerBI_v2.xlsx` · 24-month projection · 3 scenario slicer (Pessimistic / Base Case / Optimistic)
* **Pessimistic (worst case):** ARPU $15, LLM cost $18/user, CAC $120, churn 9% → Contribution margin **-$3/user** (structurally non-viable) → Cumulative PnL M24: **-$35,518** · **No break-even within 24 months** · LTV/CAC: -0.3x
* **Base Case (realistic):** ARPU $19, LLM cost $12/user, CAC $70, churn 7% → Contribution margin **$7/user** → Cumulative PnL M24: **-$28,824** · 133 users · Break-even: ~Month 36–40 · LTV/CAC: 1.4x · CAC payback: 10 months · Gross margin 37%
* **Optimistic (best case):** ARPU $29, LLM cost $6/user, CAC $35, churn 4% → Contribution margin **$23/user** → Cumulative PnL M24: **+$3,526,979** · 73,593 users · Break-even: **Month 7** · LTV/CAC: **16.4x** · CAC payback: 1.5 months · Gross margin 79%
* **Break-even accelerator (Base → 24-month):** 4 interdependent changes:
  Reduce LLM cost $12 → $7 (caching, model routing) +
  Raise ARPU $19 → $24 (annual plans, Pro tier) +
  Reduce churn 7% → 5% (onboarding + email reactivation) +
  Reduce CAC $70 → $45 (PLG loop + referral program)
* **Key investor signals to watch:** LTV/CAC target >3x; CAC payback <12 months; Gross margin >60%; Monthly churn <5%; MoM user growth >10–15%
* **Critical structural constraint:** The base case has positive unit economics ($7/user contribution margin) — the problem is growth velocity, not viability. The business can reach profitability; it requires operational optimization, not a model redesign

**Speaker Notes:**

The Power BI dashboard is a 24-month operating model with fully adjustable parameters — ARPU, LLM cost, CAC, churn rate, organic growth rate. Every input cell drives all charts dynamically. The scenario slicer filters all four visualizations simultaneously: Cumulative P&L line chart, Revenue vs. Total Cost chart, User Growth area chart, and Monthly P&L column chart.

The most important dashboard view for an investor is the Cumulative P&L chart in Base Case. The line should be consistently flattening and approaching zero — that indicates the model is working. A line declining steeply at Month 12 signals a parameter problem.

The pessimistic scenario is not an operating plan — it is a risk boundary. The critical number there is the negative contribution margin: -$3/user. That is not a scale problem; it means every new user increases losses. The fix is structural: either raise ARPU above $18 or reduce LLM cost below $15.

The base case is the realistic starting point. The unit economics are positive — $7/user contribution margin, 37% gross margin, 10-month CAC payback. The challenge is growth speed: with CAC at $70 and revenue-capped marketing spend, user growth is too slow to reach break-even within 24 months. Break-even occurs around Month 36–40 under base case assumptions.

The optimistic scenario — break-even Month 7, $3.5M by Month 24, LTV/CAC 16.4x — requires all levers simultaneously: PLG-driven CAC of $35, LLM cost optimization to $6/user, churn below 4%, and organic growth above 6%/month. Each lever is achievable individually. Achieving all four simultaneously at pre-PMF stage is aggressive — this is the target state, not the launch assumption.

The founder's North Star from the model is the contribution margin. Everything — pricing, infrastructure, product — should be evaluated by whether it moves that number toward $12–15, which is the threshold at which the base case reaches break-even within 24 months.

---

## Slide 7 — Agent Architecture (Technical)

**Bullets:**

* **Agent type:** ReAct-style stateful agent — LangGraph StateGraph with deterministic conditional routing
* **9-node pipeline:**
  `retrieve` → `synthesize` → `generate_outline` → `generate_script` → `validate` → `segment_script` → `generate_audio` → `extract_entities` → `save_execution_report`
* **Conditional logic:** `validate` node routes to `regenerate` if script is outside 90–110% length tolerance (max 3 iterations); routes to `segment_script` on pass
* **Tools and services used:**
  OpenAI GPT-4o-mini — script generation, outline, synthesis, entity extraction
  Cohere command-r-08-2024 — script segmentation (temp=0.0)
  Pinecone serverless — RAG retrieval for storytelling best practices (6 embeddings, 1024-dim)
  OpenAI TTS-1 — MP3 generation per segment
  SerpAPI — optional web search for scripts >10 minutes
* **Entity extraction module (`agent/entity/`):** Separate sub-pipeline analyzing the final script; extracts characters, animals, and objects with base visual prompts and per-scene states (actions, emotions) — designed for consumption by text-to-image generation systems
* **Production-grade features:** Idempotency via SQLite `request_id` deduplication · Tenant retry logic (exponential backoff 2–10s, 3 attempts per tool) · 300s request timeout · LRU-cached LLM clients · Structured JSON logging
* **API:** FastAPI on port 8001 — `POST /generate-script`, `GET /health`, `GET /test` — integrates directly with n8n or any REST-capable automation

**Speaker Notes:**

The agent architecture is a LangGraph StateGraph — not a sequential script, but a state machine with typed state transitions and conditional edges. This design was chosen specifically because the generation workflow requires a retry loop: if the generated script fails the length validation check, the graph routes back to `generate_script` with feedback, up to three attempts.

The state carries all data through the pipeline: retrieved context, outline, script, segments, audio paths, and entity data. SQLite records every execution keyed by `request_id` — this implements idempotency, which is critical when the API is called from n8n workflows that retry on failure. A second identical request returns the cached result without re-running the pipeline.

The entity extraction module is a new stage added after audio generation. It runs a separate GPT-4o-mini call with a specialized prompt designed around visual identity consistency principles: strict separation of base visual identity (constant across all scenes) from scene states (dynamic per scene). The output is `entities.json` and `entities_report.md` in the project directory — ready for use as input to image generation prompts.

The RAG component deserves mention: each script generation call is enriched by retrieving the top-k most relevant storytelling best practices from Pinecone before outline generation. This acts as a quality anchor — the agent does not generate from zero context but from documented narrative guidance. The knowledge base contains 6 high-quality chunks extracted from domain-specific best practices material.

---

## Slide 8 — Evaluation (LangSmith)

**Bullets:**

* **Evaluation task:** Script segmentation quality — does the model correctly identify and group narrative visual moments from a pre-written script?
* **Dataset:** `storytelling_segmentation_eval_v1` · 10 examples · LangSmith EU endpoint (eu.api.smith.langchain.com) · Reference: 10-segment ground truth (character-based fantasy story)
* **Experiment design:** 3 models × 10 examples = **30 target calls** · 4 evaluators × 30 = **120 evaluator calls** · Temperature: 0.0 (deterministic) for all experiments
* **Evaluator categories:**
  *Structure:* `structure_valid`, `valid_segment_ratio`, `length_score` — validates output format
  *Reference similarity:* `boundary_similarity`, `segment_count_match`, `exact_text_match`, `text_coverage` — compares to human-annotated ground truth
  *LLM-as-judge (GPT-4o-mini):* `judge_relevance`, `judge_coherence`, `judge_visualizability`, `judge_completeness`, `judge_overall` — holistic quality
* **Results — primary metric `boundary_similarity`:**

  | Rank | Model | boundary_similarity | segment_count_match | judge_overall |
  |:---:|---|:---:|:---:|:---:|
  | **1** | **gpt-5.4** | **0.989** | **0.909** | **0.995** |
  | 2 | gpt-4o | 0.665 | 0.385 | 0.880 |
  | 3 | gpt-4o-mini | 0.665 | 0.385 | 0.870 |

* **Key finding:** gpt-4o and gpt-4o-mini produce 26 segments for a 10-segment reference story — they split at every sentence boundary. gpt-5.4 produces 11 segments: within 1 segment of ground truth
* **What universal scores tell us:** All models: text_coverage = 1.000 and structure_valid = 1.000 — the prompt architecture for format compliance and text preservation is solid regardless of model
* **Bias acknowledgment:** Judge model is gpt-4o-mini (self-similarity bias possible for gpt-4o-mini evals); single judge (no ensemble); reference anchoring effect; scores not calibrated against human raters
* **Production decision:** Use gpt-5.4 for segmentation. +49% relative improvement on boundary_similarity vs. alternatives

**Speaker Notes:**

The evaluation pipeline was built on LangSmith using the EU API endpoint. The core question we set out to answer was: which model correctly understands what a "visual moment" is in a storytelling script, and can group sentences into coherent scene units rather than treating every sentence as its own scene?

The answer is definitive. gpt-4o and gpt-4o-mini both produce 26 segments for a 10-segment reference. That is 2.6× over-segmentation. They are technically following the prompt — every segment is the right length, every segment is visualizable — but they apply the "split when action begins" rule at the micro level (every sentence contains an action), not the scene level. The result: fragmented, unusable segmentation for any downstream image generation pipeline. judge_completeness scores 0.600 for both models — the LLM judge detects that single-sentence segments feel semantically incomplete as narrative units.

gpt-5.4 produces 11 segments vs. 10 reference. One segment off from human ground truth. boundary_similarity of 0.989 means virtually every reference boundary is reproduced. judge_overall of 0.995 — near perfect holistic quality.

The text_coverage of 1.000 across all models is important: it means our text preservation architecture is working. No model rewrote or paraphrased the original script. The segmentation task is purely split-point selection, not text generation — and that is exactly what we enforced through prompt design.

On bias: we are transparent that this evaluation has known limitations. The judge model is gpt-4o-mini, which may favor its own segmentation style. The dataset is 10 identical examples of the same story, measuring consistency rather than generalization. Human annotation baselines have not yet been collected. These are documented limitations and planned improvements, not hidden problems.

---

## Slide 9 — Learnings and Challenges

**Bullets:**

* **Challenge 1 — LLM text rewriting during segmentation**
  *Problem:* Cohere command-r-08-2024 rewrote script text instead of splitting it verbatim — breaking the fundamental requirement of character-level text preservation
  *Solution:* Set temperature = 0.0 (deterministic) + explicit character-by-character copy instructions in system prompt + post-segmentation validation (character count diff >15% triggers auto-retry via `@retry` decorator)
  *Lesson:* LLM behavioral constraints require both prompt engineering AND programmatic validation — prompt alone is insufficient

* **Challenge 2 — Over-segmentation is a model-level failure, not a prompt failure**
  *Problem:* gpt-4o and gpt-4o-mini reliably produce 2.6× too many segments despite clearly worded segmentation rules. Prompt iteration did not fix it
  *Solution:* Systematic evaluation via LangSmith identified gpt-5.4 as the correct model — boundary_similarity improved +49%
  *Lesson:* Model selection is a measurable engineering decision. LangSmith evaluation framework made this decision data-driven rather than intuition-driven

* **Challenge 3 — API compatibility across model generations**
  *Problem:* gpt-5.x models do not accept the `max_tokens` parameter — returns a hard error. This is not documented prominently
  *Solution:* Added `_max_tokens_param()` helper that dispatches to `max_completion_tokens` for gpt-5.x / o1 / o3 / o4 model families and `max_tokens` for older models
  *Lesson:* When integrating multiple model generations, write compatibility shims rather than assuming API uniformity

* **Challenge 4 — Silent evaluation breaks from hand-edited JSON**
  *Problem:* Manually editing `evaluation_results.json` to remove a placeholder entry left a trailing comma, causing `json.loads()` to fail silently. The experiment skip logic stopped loading existing results, causing all 3 experiments to re-run unnecessarily
  *Solution:* Sanitized the JSON; added explicit error logging on parse failure
  *Lesson:* Pipeline files that are both machine-written and human-edited are fragile. Validate JSON on load with clear error messages rather than silent fallbacks

* **Challenge 5 — LangSmith geographic endpoint routing**
  *Problem:* LangSmith account was registered on the EU instance; calls to the US endpoint (`api.smith.langchain.com`) returned 403 Forbidden with no explanatory message
  *Solution:* Identified EU endpoint (`eu.api.smith.langchain.com`) and configured `LANGCHAIN_ENDPOINT` accordingly
  *Lesson:* Third-party evaluation infrastructure has region-specific routing that must be explicitly configured. Default documentation often assumes US endpoint

* **What would be improved next time:**
  — Start with model evaluation before building the production pipeline: running LangSmith experiments earlier would have avoided shipping with a suboptimal segmentation model
  — Add human annotation baselines to the evaluation dataset from the start: LLM-as-judge scores are meaningful but cannot replace human ground truth
  — Apply JSON schema validation at all pipeline stages to eliminate silent parse failures
  — Expand the evaluation dataset to include multiple stories, different lengths, and Russian-language examples before finalizing model selection

**Speaker Notes:**

Slide 9 is the most honest slide in the presentation, and intentionally so. The five challenges we describe are real bugs and design mistakes encountered during development — not theoretical risks. Each one has a documented root cause, a specific fix, and a clear lesson.

Challenge 1 and Challenge 2 together tell a coherent story about AI system quality assurance. You cannot rely on a large language model to behave correctly because you told it to. You need measurement. The segmentation problem — over-splitting by gpt-4o-mini and gpt-4o — was not obvious from single test runs. It became unambiguous only after systematic evaluation across 30 target calls with structured metrics. That is what LangSmith gave us: a repeatable experimental framework that turned a subjective quality impression into a numerical result.

Challenge 3 is a practical lesson in ML infrastructure maintenance. Model generations do not maintain API compatibility. The `max_tokens` vs `max_completion_tokens` split is documented but easy to miss when you are iterating quickly. The fix is simple, but the lesson is important: version-aware shims are necessary when your pipeline spans multiple model generations.

Challenges 4 and 5 are both "silent failure" issues — the worst category of bug, because the pipeline appears to run successfully while producing incorrect results. Challenge 4 (trailing JSON comma) showed that hand-edited data files are a reliability risk. Challenge 5 (EU API routing) showed that third-party service configuration has hidden assumptions that need to be explicitly verified.

The honest summary: the development process was iterative, the evaluation framework made model selection a data-driven decision, and each bug produced a specific improvement to the engineering discipline of the system. These are the kinds of lessons that make the next version of this product more reliable.

---

*End of Presentation Script*

---

## Quick Reference — Key Numbers

| Category | Number | Source |
|---|---|---|
| SOM 2024 | $128.6M | sector_research.md |
| SOM 2029 | $535.4M (33% CAGR) | sector_research.md |
| 1% SOM 2026 capture | $2.28M ARR | sector_research.md |
| Character consistency problem frequency | 22 / 50 sources | opportunities_and_risks.md |
| Documented user testing waste | $3,000–$4,000/user | use_cases_and_market_strategy_analysis.md |
| Base Case contribution margin | $7/user/month | PowerBI_Dashboard_Documentation.docx |
| Optimistic break-even | Month 7 | PowerBI_Dashboard_Documentation.docx |
| Optimistic M24 cumulative PnL | +$3,526,979 | PowerBI_Dashboard_Documentation.docx |
| Optimistic LTV/CAC | 16.4x | PowerBI_Dashboard_Documentation.docx |
| gpt-5.4 boundary_similarity | 0.989 | evaluation_report.md |
| gpt-4o/mini boundary_similarity | 0.665 | evaluation_report.md |
| Total evaluation calls | 30 target + 120 evaluator = 150 | evaluation_report.md |
| Pipeline nodes | 9 (retrieve → report) | README.md |
