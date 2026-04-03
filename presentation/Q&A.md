# Q&A Preparation Guide
**AI Storytelling Platform | April 2, 2026**

---

## Overview

This document prepares you for the 10-15 minute Q&A session following your presentation. The goal is to demonstrate deep understanding of your technical choices, business model, compliance reasoning, and honest assessment of weaknesses.

---

## Category 1: Business Model & Financial Questions

### Q: "Why do you think you can charge $29/month when Midjourney charges $10?"

**Prepared Answer:**
> "Three reasons: **(1) Differentiated value proposition** — We solve the #1 pain point (character consistency) that Midjourney publicly admits they can't fix. Users currently waste $3,000 testing multiple tools; our $29/month is 1% of their current burn rate. **(2) Target market positioning** — We're between Midjourney ($10, hobbyists) and Adobe Creative Cloud ($55, professionals). Our customers are semi-professionals (YouTubers with 50K+ subscribers, professional educators) who monetize content, not hobbyists. **(3) Unit economics validation** — At $29 ARPU with $6 LLM costs, we get 79.3% gross margin and 2.4-month CAC payback. This sustains reinvestment in R&D (character consistency improvements) that free-tier competitors can't afford."

**Supporting Data:**
- Competitor ARPU benchmarks: Midjourney $10 (hobbyists), Runway $15 (prosumers), Adobe CC $55 (professionals)
- Our $29 positioning: Mid-market prosumer tier (validates with YouTuber target: monetized channels earn $100-5,000/month, can afford $29 tool)
- Gross margin comparison: 79.3% (us) vs 60-70% (typical AI SaaS) — healthy reinvestment capacity

---

### Q: "Your Optimistic scenario assumes 4% monthly organic growth. Isn't that unrealistic for a bootstrapped startup?"

**Prepared Answer:**
> "**Absolutely correct** — it's the *most unrealistic assumption*, which is why I added **R16: Unit Economics Collapse** as the 4th critical risk. The Optimistic scenario (+67.9% ROI, Month 13 break-even) assumes **best-case on ALL metrics simultaneously**: 4% organic growth AND 4% churn AND $55 CAC. Statistically unlikely. Here's the **Realistic Scenario**:"
>
> **Optimistic (67.9% ROI):** CAC $55, Churn 4%, LTV $575, LTV/CAC 10.5x  
> **Realistic (20-30% ROI):** CAC $80, Churn 8%, LTV $319, LTV/CAC 3.99x  
> **Break-even:** Month 18-22 (vs Optimistic Month 13)
>
> "**Why Realistic is more likely:** **(1) Bootstrap SaaS see 70-80% paid acquisition Year 1, not 60% organic.** **(2) Churn 4% is best-in-class, takes 12-18 months — new products start at 8-12%.** **(3) Organic growth 4%/month needs viral loop + exceptional product — takes 6-12 months to build.** The 8-week Pilot will validate which scenario we're in."

**Supporting Data:**
- **NEW:** Realistic LTV/CAC 3.99x is marginal (>3x threshold) but acceptable — leaves no room for error
- If churn rises to 10%, LTV/CAC drops to 2.83x (<3x = unhealthy) → shutdown threshold
- Base Case (11.4% ROI) still viable if we reduce marketing spend 45% → 30% (slower growth)

---

### Q: "How realistic is the Optimistic scenario really? It sounds too good to be true."

**Prepared Answer (Honest):**
> "**It's optimistic for a reason** — achieving 67.9% ROI requires executing perfectly on every metric. Here's the honest breakdown:"
>
> | Assumption | Optimistic | Realistic | Probability |
> |------------|-----------|-----------|-------------|
> | **CAC** | $55 (60% organic) | $80 (30% organic) | **30%** — Viral loop unproven |
> | **Churn** | 4%/month | 8%/month | **20%** — Takes 12+ months to hit 4% |
> | **Organic Growth** | 4%/month | 2-3%/month | **25%** — Requires exceptional product |
> | **All 3 simultaneously** | — | — | **~2-5%** (0.3 × 0.2 × 0.25) |
>
> "**My honest expectation:** We'll land somewhere between Base Case (11.4% ROI, Month 27 break-even) and Realistic Scenario (20-30% ROI, Month 18-22 break-even). Optimistic is the *ceiling*, not the *target*. Conservative planning uses Base Case assumptions."

**Why This Answer Works:**
- Shows self-awareness (not blindly optimistic CEO)
- Quantifies probability (~2-5% all metrics hit)
- Sets realistic expectations (Base Case = planning baseline)

---

### Q: "What happens if the Realistic Scenario is confirmed — can you still survive?"

**Prepared Answer:**
> "**Yes, but margin for error shrinks.** Realistic Scenario (LTV/CAC 3.99x) is marginally healthy (>3x threshold). Two mitigation strategies:"
>
> **Strategy 1: Launch Premium $49/month tier (Month 6):**
> - 20 scripts/month (vs Pro 10 scripts), voiceover/music included, longer videos
> - LTV = $525 ($42 margin / 0.08 churn)
> - LTV/CAC = $525 / $80 = **6.56x** (healthy, back to strong unit economics)
> - **If 30%+ users upgrade to Premium:** Blended LTV rises to $400+, project viable
>
> **Strategy 2: Reduce marketing spend 45% → 30% (slower growth):**
> - Accept Month 22-24 break-even (vs Month 13 Optimistic)
> - LTV/CAC improves as CAC drops slightly (less aggressive paid ads)
> - Still achieve 15-25% ROI at 36 months (vs Base Case 11.4%)
>
> "**Shutdown threshold:** If Pilot Week 8 shows LTV/CAC <3x (e.g., churn 10%+, CAC $100+) → project not viable, cut losses at $1,500 total investment."

---

### Q: "When do you actually become profitable? Your numbers show -3.8% ROI at 12 months."

**Prepared Answer:**
> "Excellent question — this clarifies the difference between **break-even** (recover all invested capital) and **profitability** (monthly revenue > monthly costs). Here's the timeline for **both scenarios**:"
>
> **OPTIMISTIC (67.9% ROI):**  
> **Month 11-12:** Monthly cash-flow positive  
> **Month 13:** Break-even — All $45,889 cumulative investment recovered  
> **Month 36:** +67.9% ROI ($3.27M net profit)
>
> **REALISTIC (20-30% ROI):**  
> **Month 14-16:** Monthly cash-flow positive  
> **Month 18-22:** Break-even — Cumulative investment recovered  
> **Month 36:** +20-30% ROI (~$1M net profit, vs $3.27M Optimistic)
>
> "The -3.8% ROI at 12 months (Optimistic) is *expected for SaaS* — we're in the J-curve investment phase. **Realistic scenario adds 5-9 months to break-even** but still achieves positive ROI by Month 36. Compare to VC-backed SaaS: Dropbox took 4 years to profitability, Slack 6 years."

**Visual Aid (if allowed):**
```
SaaS J-Curve Comparison:
OPTIMISTIC:
Month 12: -$1,742 (-3.8% ROI)
Month 13: $0 (break-even)
Month 36: +$3.27M (+67.9% ROI)

REALISTIC:
Month 12: -$8,000 (-18% ROI)
Month 18: -$2,000 (-5% ROI)
Month 22: $0 (break-even)
Month 36: +$1M-1.5M (+20-30% ROI)
```

---

### Q: "How do you justify the 79.3% gross margin? That seems too high for an AI tool."

**Prepared Answer:**
> "**UPDATE:** The 79.3% was Optimistic scenario with $6 API cost (voiceover + music mandatory for all users). **Realistic Scenario shows 87.9% margin** because music/voiceover are **optional add-ons**, not default:"
>
> **Realistic API Cost Breakdown (per user/month):**
> - 10 scripts × $0.360 images = $3.60
> - Voiceover addon (50% adoption): $0.018 × 5 scripts = $0.09
> - Music addon (50% adoption): $0.010 × 5 scripts = $0.05
> - **Total: $3.74 → conservatively $3.50/user**
>
> **Margins:**
> - **Realistic:** $29 ARPU − $3.50 API = $25.50 margin = **87.9%** (better than Optimistic!)
> - **If forced to fal.ai** (kie.ai DPA rejected): $29 − $6.42 = $22.58 margin = **77.9%** (still healthy)
>
> "**Caveat:** Kie.ai dependency is now **R16 critical risk**. If we can't sign DPA (GDPR blocker), forced migration to fal.ai ($0.039/img vs $0.020) drops margin to 77.9%. Still healthy for AI SaaS (60-70% norm), but LTV drops $319 → $275."

**Supporting Data:**
- Kie.ai company: NEXUSAI SERVICES LLC, Denver, Colorado, USA (verified)
- Privacy Policy Section 10: "Data transferred to United States" — requires GDPR DPA
- No DPA visible on website → Week 3-4 contact support@kie.ai (LAUNCH BLOCKER)
- Fallback: fal.ai has public DPA, but 95% more expensive

---

## Category 2: Technical & Product Questions

### Q: "You claim 85-90% character consistency in POC. How did you measure this?"

**Prepared Answer:**
> "Honest answer: **Informal manual testing**, not rigorous scientific measurement. Here's what we did: Generated 45 demo videos (6 scenes each), counted how many scenes showed *recognizably the same character* (same hair color, same clothing, same facial structure within tolerance). Result: 85-90% of scenes passed visual similarity test."
>
> "**Production plan:** Month 7, we'll implement **automated quality scoring** using CLIP model (OpenAI's vision-language model) to measure cosine similarity between character sheet and each scene. Target: 0.85+ similarity = 'consistent.' This gives us objective, reproducible metrics. Pilot Phase will validate if users *perceive* 85-90% as 'good enough' or if we need 95%+ before launch."

**Supporting Data:**
- Competitor baseline: ≤2 scenes (0% consistency after Scene 2) — Our 85-90% is 40-45x improvement
- Target: 95% by Month 12 (production-grade)
- Validation method: Pilot user survey "Rate character consistency 1-5" + CLIP automated scoring

---

### Q: "Why LangGraph instead of just using LangChain or custom code?"

**Prepared Answer:**
> "LangGraph solves **three problems native to our workflow**: **(1) Conditional routing** — We need to dynamically choose YouTube vs Teacher pipeline based on `use_case` field. LangGraph's `StateGraph` makes this trivial with conditional edges. **(2) Iterative loops** — Fact-checking requires regeneration if claims fail (max 2 iterations). LangGraph handles loop logic + termination conditions without messy custom code. **(3) Visual debugging** — LangGraph renders state machine diagrams, making it easy to explain workflow to non-technical stakeholders (e.g., investors, educators testing the product)."
>
> "**Alternative considered:** LangChain LCEL (LangChain Expression Language) — More flexible, but requires writing state management manually. For POC speed, LangGraph's opinionated structure saved ~20 hours development time."

**Supporting Data:**
- LangGraph state machine: 17 nodes (YouTube pipeline) vs 19 nodes (Teacher pipeline, +2 for fact-checking)
- Code comparison: ~150 lines LangGraph vs ~400 lines custom orchestration (estimated)
- Production benefit: Checkpointing (resume failed generations) built into LangGraph

---

### Q: "What happens if Pollinations.ai shuts down tomorrow?"

**Prepared Answer:**
> "**Short answer:** POC stops working, but production is unaffected because we're migrating to Stability AI in Month 3 (before Pilot launch). **Long answer:** Pollinations.ai is POC-only due to lack of GDPR Data Processing Agreement (DPA). We cannot use it in production with EU users. Migration timeline:"
>
> **Week 1-2 (Pilot prep):** Integrate Stability AI SDXL 1.0 API, test image quality  
> **Week 3:** Run A/B test: Pollinations.ai (free, POC quality) vs Stability AI ($0.04/image, higher quality)  
> **Week 4:** Flip switch to Stability AI before Pilot launch (May 1, 2026)
>
> "Cost impact: $0.023/video (POC with free Pollinations) → $0.26/video (production with Stability AI). Gross margin drops from 79.3% to ~75%, still healthy."

**Supporting Data:**
- Stability AI DPA signed (GDPR-compliant), SLA 99.9% uptime
- Backup plan: If Stability AI fails, use Replicate.com SDXL (similar pricing, different provider)
- No single point of failure after Pilot launch

---

### Q: "How do you handle videos longer than 1 minute? Does the workflow scale?"

**Prepared Answer:**
> "Yes, workflow scales linearly. **Example:** 10-minute video = 60 scenes (vs 6 scenes for 1-minute). Process:"
>
> **Step 1:** GPT-4o-mini generates 5,800-character script (vs 962 chars for 1-min)  
> **Step 2:** Cohere segments into 60 chunks (vs 6 chunks)  
> **Step 3:** Entity extraction identifies same characters across all 60 scenes  
> **Step 4:** Generate 60 images (30 seconds parallel processing, vs 6 images in 5 seconds)  
> **Step 5:** Generate 60 audio segments (60 seconds TTS, vs 6 segments in 10 seconds)  
> **Step 6:** MoviePy assembles 10-minute MP4 (2 minutes rendering, vs 15 seconds for 1-min video)
>
> **Total time:** ~5 minutes for 10-minute video (after user approvals), ~45 seconds for 1-minute video. Cost: $0.26 × 10 = $2.60 for 10-minute video (scales linearly)."

**Supporting Data:**
- POC tested: 15-second videos (6 scenes), 30-second videos (12 scenes), 1-minute videos (24 scenes)
- Longest demo: 1.5-minute video (36 scenes, 90 seconds generation time)
- Production optimization: GPU acceleration (MoviePy) for videos >10 minutes

---

## Category 3: Compliance & Risk Questions

### Q: "Why is this LIMITED-RISK and not HIGH-RISK under EU AI Act? Educators use it for teaching."

**Prepared Answer:**
> "**Critical distinction:** The EU AI Act classifies systems as HIGH-RISK if they **make decisions ABOUT students** (enrollment, grading, evaluation). Our platform **creates content FOR teachers**, who then decide if/how to show it to students. This is identical to PowerPoint, Canva, or ChatGPT — all used in education, none HIGH-RISK."
>
> "**Legal test (Annex III, Point 3):** Does the system 'determine access to educational institutions or evaluate persons on examinations'? **Answer: NO.** Our system generates creative content that teachers review and control. Students never create accounts, never interact with the AI, and are not tracked/evaluated/profiled."
>
> "**Fact-checking rationale:** We added fact-checking as a *voluntary quality feature* (like spell-check in Word), NOT because we're a HIGH-RISK educational AI. It reduces misinformation, but doesn't change our classification."

**Supporting Data:**
- EU AI Act Article 52 (LIMITED-RISK): "Inform users they're interacting with AI" — We watermark videos
- Annex III, Point 3 (HIGH-RISK definition): "Determine access or evaluate persons" — We do neither
- Analogous tools: ChatGPT (LIMITED-RISK, widely used in education), Grammarly (LIMITED-RISK, education writing tool)

**Reference Document:** [compliance/eu_ai_act_compliance.md](../compliance/eu_ai_act_compliance.md) Section 1.3

---

### Q: "Your GDPR risk is rated 'CRITICAL' at 20/25, but you say overall risk is LOW. Which is it?"

**Prepared Answer:**
> "Both are true, but measuring different things:"
>
> **GDPR Compliance Risk (20/25 CRITICAL):** Likelihood of non-compliance *before launch* if we don't fix gaps = 4 (Likely) × 5 (Severe) = 20. This is **execution risk** (will we complete Privacy Policy review? Will we sign DPAs?). It's CRITICAL because inaction = €20M fine exposure."
>
> **GDPR Data Processing Risk (LOW):** After mitigation, *actual data handling risk* = LOW per DPIA. Why? **(1) Data minimization** — No user IDs sent to AI services, anonymous requests. **(2) EU-only hosting** — Hetzner Germany, no USA data transfers. **(3) Short retention** — 90 days auto-deletion. **(4) SCCs signed** — OpenAI, Stripe, Google have Standard Contractual Clauses."
>
> "**Mitigation plan:** €8K-€13K investment (Month 3-5: legal review, DPAs, security audit) reduces likelihood from 4 → 2. New risk level: 10 (Medium-High), manageable."

**Supporting Data:**
- DPIA conclusion (compliance/gdpr_documentation.md Section 4.7): "Overall Residual Risk: LOW"
- Risk Assessment Matrix: R1 GDPR (20/25) → 10/25 after mitigation
- Launch blockers: Privacy Policy legal review (€500-€1K), DPAs with Cohere/SerpAPI/Facticity (€0, standard templates)

---

### Q: "What's your biggest GDPR vulnerability right now?"

**Prepared Answer:**
> "**Pollinations.ai** — no Data Processing Agreement (DPA), unknown location, free tier with no SLA. This is a MEDIUM risk (not critical) because **(1) we send NO user identifiers** (only generic image prompts like 'astronaut on moon'), and **(2) it's POC-only, won't touch production.** But if we hypothetically launched with Pollinations.ai today, a GDPR auditor would flag it immediately."
>
> "**Mitigation:** Replace with Stability AI (has DPA, GDPR-compliant) by Week 3 of Pilot prep. Timeline is non-negotiable — we CANNOT launch Pilot without Stability AI migration complete."

**Supporting Data:**
- GDPR Documentation Section 5.4: "Pollinations.ai — MEDIUM risk, mitigated by generic prompts (no PII)"
- Timeline: Week 1-2 (integrate Stability AI), Week 3 (A/B test), Week 4 (flip switch before Pilot Day 1)

---

## Category 4: Market & Competition Questions

### Q: "What if Midjourney fixes character consistency tomorrow?"

**Prepared Answer:**
> "**Short answer:** We have 6-12 month window before Midjourney catches up, but our moat isn't just technology — it's **workflow + pricing + trust**. **Detailed response:**"
>
> **Scenario 1 (Midjourney fixes it):**
> - **Our advantage:** We've already built step-by-step approval workflow (solves TRIAD-2) and transparent billing (solves TRIAD-3). Midjourney charges per generation, no preview, credits expire. Even if they match our character consistency, they don't solve cost-per-usable crisis.
> - **Our pricing:** $29/month subscription (50 videos/day Pro tier) vs Midjourney $30/month (200 generations = ~20 usable videos after failures). Our $/usable-video ratio is 2-3x better.
>
> **Scenario 2 (Midjourney adds workflow):**
> - This requires major product redesign (6-12 months minimum for Discord bot → web dashboard migration).
> - We have first-mover advantage: 8-week Pilot validates PMF, 12-month head start on workflow optimization.
>
> **Scenario 3 (Midjourney targets our market):**
> - Midjourney's focus is high-end creative professionals ($30-60 ARPU). Our target is semi-professional creators ($15-29 ARPU). Different market segments."

**Supporting Data:**
- Midjourney's Feb 18, 2026 admission confirms they don't have solution yet (3-month lag minimum)
- Workflow redesign timeline: Discord bot → web app typically 6-12 months (industry norm)
- Our differentiation: 3 TRIADs (character consistency + workflow + billing), not just 1

---

### Q: "Why wouldn't users just use ChatGPT + Midjourney separately for free?"

**Prepared Answer:**
> "They already do — and it fails. Here's why:"
>
> **Fragmented workflow pain:**
> - **Step 1:** ChatGPT writes script (5 min)
> - **Step 2:** Manually segment into scenes (10 min)
> - **Step 3:** Copy scene descriptions to Midjourney (15 min, 6 separate prompts)
> - **Step 4:** Character drifts after 2 scenes → regenerate with adjusted prompts (30 min trial-and-error)
> - **Step 5:** Download images individually (5 min)
> - **Step 6:** Generate TTS in ElevenLabs (10 min)
> - **Step 7:** Manual video editing in CapCut (30 min)
> - **Total:** 105 minutes, requires 4 tools, $10 monthly cost across subscriptions
>
> **Our value prop:** Same output in 5 minutes (after approvals), one tool, $29/month. **ROI:** Save 100 minutes per video × 20 videos/month = 2,000 minutes (33 hours) saved. User values their time at $20/hour → $660/month time savings for $29/month subscription = 22x ROI on time."

**Supporting Data:**
- User quote (Reddit r/ChatGPT): *"I spend 2 hours stitching ChatGPT + Midjourney + CapCut — works but exhausting"*
- Our workflow automation: 105 min → 5 min (21x faster)
- Competitive moat: Integration (no manual copy-paste) + Entity extraction (automatic character consistency)

---

## Category 5: Weakness & Failure Mode Questions

### Q: "What are the main weaknesses of this project?"

**Prepared Answer (Honest):**
> "Three major weaknesses I'm actively monitoring:"
>
> **1. Single point of failure (solo founder):**
> - **Problem:** If I get sick or burn out, project stops. No co-founder, no team.
> - **Mitigation:** 8-week Pilot intentionally scoped to validate if project warrants hiring (use pilot revenue to fund first contractor).
> - **Decision point:** If Pilot NPS <40, I shut down project (cut losses at $1,500 total investment). If NPS >40, reinvest pilot revenue into part-time developer ($2K/month contractor).
>
> **2. Image quality unpredictability:**
> - **Problem:** POC shows 60-70% images usable without regeneration, but 10% are unusable garbage (wrong anatomy, floating objects). If this persists in production, user frustration kills retention.
> - **Mitigation:** Month 3-6 migration to Stability AI SDXL 1.0 (higher quality than Pollinations.ai). Month 7 automated QA (CLIP model detects anatomical errors). Target: 90% usable images by Month 9.
> - **Failure mode:** If we can't hit 85% usable by Month 9, extend Pilot to Month 12 for additional quality iteration.
>
> **3. Bootstrapped growth ceiling:**
> - **Problem:** Optimistic scenario assumes 4% monthly organic growth, but bootstrapped marketing budget ($600/month) may not achieve this. If growth <2%/month, we hit Base Case (11.4% ROI at 36 months) instead of Optimistic (67.9% ROI).
> - **Mitigation:** If Month 6 growth <2%/month, evaluate seed fundraising ($50K-$100K to boost marketing spend). Alternative: Extend timeline to Month 48 (4 years) to reach same user count, accept lower ROI.
> - **Decision point:** Month 12 — if not on track for break-even Month 13, either raise capital or shut down project."

**Why This Answer Works:**
- Shows self-awareness (not blindly optimistic)
- Each weakness has **quantified decision criteria** (NPS 40, 85% usable images, 2% growth)
- Demonstrates pivot/shutdown discipline (not sunk-cost fallacy)

---

### Q: "If you could only fix ONE of the three TRIADs, which would it be and why?"

**Prepared Answer:**
> "**TRIAD-1 (Character Consistency)** — because it's the **only unsolved problem competitors publicly admit**. Midjourney's Feb 18, 2026 statement validates this is a category-wide gap, not just user frustration. If we solve only character consistency, we can still charge $29/month (users pay premium for unique capability). If we solve only TRIAD-2 (workflow) or TRIAD-3 (billing), we're competing on UX polish against funded competitors who can copy workflow in 6-12 months."
>
> "**Market validation:** 22 independent sources cite character consistency as #1 pain (vs 12 sources for cost-per-usable, 11 for billing). User quote: *'I'd switch tomorrow if consistent characters'* — this is unmet demand, not feature request."

---

## Category 6: Numbers Mastery

### Q: "Walk me through your LTV calculation."

**Prepared Answer:**
> "LTV = (ARPU − Variable Cost) ÷ Churn Rate. For Optimistic scenario:"
>
> **ARPU:** $29/month  
> **Variable Cost:** $6/month (LLM + API fees per user)  
> **Contribution Margin:** $29 − $6 = $23/month  
> **Churn Rate:** 4%/month  
> **LTV:** $23 ÷ 0.04 = **$575**
>
> "This means the average user generates $575 profit over their lifetime. With CAC of $55, we get 10.5x LTV/CAC ratio (excellent — >3x is healthy). CAC payback = $55 ÷ $23/month = 2.4 months (fast capital recovery)."

**Why This Matters:**
- Proves you understand unit economics cold (not just reading slides)
- 10.5x LTV/CAC justifies aggressive growth investment (45% revenue → marketing)

---

### Q: "Why do you assume 45% marketing spend? That's very high."

**Prepared Answer:**
> "Industry benchmarks for bootstrapped SaaS: 25-35% marketing spend during growth phase. We're at 45% (Optimistic scenario) because **(1) we're bootstrapped** (no VC funding for paid acquisition), so we reinvest revenue aggressively to achieve 4% organic growth. **(2) Short CAC payback (2.4 months)** means every dollar spent on ads returns $10.50 in LTV — this justifies higher spend. **(3) Year 1 land-grab** — we have 6-12 month window before competitors copy character consistency, so we need to acquire users fast."
>
> "**Conservative check:** Base Case uses 35% marketing spend (more sustainable), still achieves 11.4% ROI at 36 months. Optimistic 45% is aggressive but defensible."

---

## Final Preparation Checklist

Before Q&A:

- [ ] **Know your numbers cold** — Don't read from slides
  - LTV: $575
  - CAC: $55
  - LTV/CAC: 10.5x
  - CAC Payback: 2.4 months
  - Break-even: Month 13
  - ROI at 36 months: 67.9% (Optimistic) or 11.4% (Base Case)

- [ ] **Know your classification reasoning** — Don't just say "it's limited risk"
  - EU AI Act Article 52 (transparency obligations)
  - NOT Annex III, Point 3 (doesn't determine access or evaluate students)
  - Teachers create content FOR students, students don't interact with AI
  - Analogous: PowerPoint, Canva, ChatGPT (all LIMITED-RISK)

- [ ] **Know your top 3 risks** — Likelihood, Impact, Mitigation
  - R1: GDPR (20/25) → Legal review €1K, DPAs signed, reduces to 10/25
  - R2: Data Breach (20/25) → PostgreSQL SSL, TLS 1.3, penetration test, reduces to 10/25
  - R3: Image Quality (16/25) → Stability AI migration, CLIP QA, reduces to 12/25

- [ ] **Prepare honest weakness answer** — "What are the main weaknesses?"
  - Solo founder risk (no team)
  - Image quality unpredictability (60-70% usable, need 90%+)
  - Bootstrapped growth ceiling (4% organic may not materialize)

- [ ] **Have pivot/shutdown criteria ready** — "What would make you stop?"
  - Pilot NPS <20 → Shut down (cut losses at $1,500)
  - Image quality <85% by Month 9 → Extend Pilot, re-evaluate
  - Growth <2%/month by Month 12 → Raise capital or shut down

---

## Mock Q&A Exercise (Practice Alone)

**Set timer for 2 minutes per question. Answer out loud without looking at notes.**

1. "Why is this LIMITED-RISK, not HIGH-RISK?"
2. "Walk me through your LTV calculation."
3. "What's your biggest GDPR vulnerability?"
4. "What if Midjourney fixes character consistency tomorrow?"
5. "What are the main weaknesses of this project?"

**Self-assessment criteria:**
- Did I answer in <2 minutes? (Concise = confidence)
- Did I cite specific numbers? (LTV $575, CAC $55, not "around $50")
- Did I acknowledge uncertainty honestly? ("Optimistic scenario assumes 4% growth, but Base Case shows 11.4% ROI if we miss")

---

**End of Q&A Preparation Guide**
