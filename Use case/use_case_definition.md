# Use Case Definition: AI Storytelling Platform
**Version:** 2.0 (Optimistic ROI Scenario + Step-by-Step Approval)  
**Date:** April 1, 2026  
**Status:** Pre-Launch MVP (POC Complete)  
**Document Purpose:** Academic/Business Submission — Structured AI Solution Definition

---

## Table of Contents

1. [Business Problem Statement](#1-business-problem-statement)
2. [Company Profile](#2-company-profile)
3. [Proposed AI Solution](#3-proposed-ai-solution)
4. [Key Stakeholders](#4-key-stakeholders)
5. [Success Criteria](#5-success-criteria)
6. [Out-of-Scope Boundaries](#6-out-of-scope-boundaries)

---

## 1. Business Problem Statement

### 1.1 The Character Consistency Crisis (TRIAD-1 — Dominant Market Signal)

Content creators attempting multi-scene storytelling with AI tools face a **catastrophic consistency failure**: the same character appears with a completely different face in every scene, rendering story-based video content unusable.

**Market Evidence (22 Independent Sources):**
- **User Quote (1.3K upvotes):** *"I'd switch tomorrow if any tool could give me consistent characters"*
- **Competitor Admission:** Midjourney (category leader) publicly stated: *"We understand how frustrating it can be when you're aiming for character consistency"* (February 18, 2026)
- **Current Market Benchmark:** ≤2 scenes before character appearance completely changes
- **Real User Complaint:** *"The characters get replaced by completely new faces throughout the scenes. It's completely UNUSABLE for any story-based content."* (InVideo Studio user, Trustpilot)

**Quantified Pain:**
- **$3,000** average spend testing tools before finding solution (1.6K upvotes)
- **$1,400** spent on single tool (Arcads) with zero usable output
- **4x more manual fix time** than traditional production (970 upvotes)

### 1.2 The Cost-Per-Usable Crisis (TRIAD-2 — 12 Sources)

Users pay for **every failed generation attempt**, not just successful videos. Existing AI tools charge per generation regardless of output quality, leading to catastrophic ROI failures.

**Burn Rate Examples:**
- $3,000+ total testing spend across multiple tools
- $1,400 on Arcads alone (zero usable videos delivered)
- $4,000 on fixing outputs (still requiring manual production)

**Market Demand:** *"Pay only for usable output, not cost-per-generation"* (12 sources cite this as primary value metric)

**Why Existing Solutions Fail:**
Users cannot preview or approve intermediate steps. They pay upfront for full generation, discover failures only at the end, and cannot iterate without burning more credits.

### 1.3 The Billing Trust Crisis (TRIAD-3 — 11 Sources)

**Systematic billing hostility across competitors:**
- Unauthorized charges ($129–588 documented cases)
- Credits expire without warning ($175 lost, InVideo user)
- Non-functional "Cancel" buttons (Leonardo AI, CapCut)
- "Unlimited" plans secretly capped (bait-and-switch)

**User Quote:** *"$40 worth of credits just vanished. No warning, no email, no refund."* (C19)

### 1.4 Educational Sector Pain

Teachers spend **3-5 hours per 5-minute educational video** and risk spreading misinformation without fact-checking, yet lack technical skills for traditional video editing.

### 1.5 Target Users (Re-Prioritized by Market Signals)

**1. Content Creators (PRIMARY — Addresses TRIAD-1)**
- YouTubers creating story-driven shorts (5-10 videos/week)
- TikTokers needing character-consistent series
- Social media managers producing branded content
- **Pain:** $3K testing spend, 4x manual fixing, character drift

**2. Educators (SECONDARY — Fact-Checking Differentiator)**
- K-12 teachers creating lesson videos (2-5 videos/week)
- University professors for online courses
- Online course creators (Udemy, Coursera)
- **Pain:** 3-5 hours/video, factual accuracy risk, skills gap

**3. Marketing Teams (TERTIARY)**
- SME/startup marketing leads (2-5 explainer videos/month)
- Agencies producing client content
- **Pain:** $200/video freelance costs, slow turnaround

### 1.6 Current Alternatives & Why They Fail

| Alternative | Time | Cost | Character Consistency | Why It Fails |
|------------|------|------|-----------------------|--------------|
| **AI tools** (Runway, Midjourney, InVideo) | 30-60s/video | $5-20/attempt | ❌ **≤2 scenes** | *"Same character looks different every scene"* — 22 sources |
| **Manual production** | 3-5 hours | $50-200/video | ✅ Perfect | Too slow, requires editing skills |
| **Fragmented workflow** (ChatGPT + Midjourney + manual) | 2-3 hours | $10-50/video | ❌ Character drift | No integration, manual stitching, pay for each failed attempt |
| **Templates** (Canva, Renderforest) | 30 min | $15-30/video | ⚠️ Limited | Not AI-powered, no personalization |

---

## 2. Company Profile

### 2.1 Company Overview

**Name:** AI Storytelling Platform

**Industry:** AI-Powered Content Creation SaaS (EdTech + Creator Economy)

**Company Size:** Startup (Pre-Seed Stage)
- **Founding Team:** 1-2 developers (founder-led build)
- **Stage:** Proof of Concept Complete (April 1, 2026)
- **Legal Entity:** [To be specified — recommend Delaware C-Corp for US investment or German GmbH for EU focus]
- **Funding Status:** Self-funded POC ($1,000 setup cost), preparing for pre-seed raise

### 2.2 Development Status

**POC Completion:**
- ✅ Dual-pipeline AI system (YouTube + Teacher) operational
- ✅ GDPR documentation complete (120+ pages, pre-launch compliant)
- ✅ Demo validated (Apollo 11 educational video, full fact-checking trace)
- ✅ Entity extraction for character consistency (85-90% across 6 scenes)

**Technology Stack:**
- **Backend:** Python FastAPI, LangGraph orchestration
- **AI Services:** OpenAI GPT-4o-mini, Facticity API, Stability AI, Pinecone, Cohere
- **Infrastructure:** Hetzner Germany (EU GDPR-compliant hosting)
- **Compliance:** EU AI Act LIMITED-RISK classification

**Timeline to Production:** 6-8 weeks (user accounts, authentication, rate limiting, monitoring)

### 2.3 Market Positioning

**Unique Value Propositions:**

1. **TRIAD-1 Solution:** Entity extraction technology maintains character consistency across 6+ scenes (vs competitor benchmark ≤2 scenes)
2. **TRIAD-2 Solution:** **Step-by-step approval workflow** — users control and approve every micro-stage before paying
3. **TRIAD-3 Solution:** Transparent subscription pricing (no credits, no expiry, no billing traps)
4. **Educational Differentiator:** Automatic fact-checking via Facticity API (Teacher pipeline)

**Competitive Moat (Validated by Midjourney Admission):**

Midjourney's public statement (Feb 18, 2026) confirms character consistency is an **unsolved category-wide problem**. Our entity extraction pipeline solves this validated white space.

### 2.4 Business Model & Financial Projections (Optimistic Scenario)

**Pricing Tiers:**

| Tier | Price | Daily Limit | Monthly Videos | Target Users |
|------|-------|-------------|----------------|--------------|
| **Free** | $0/month | 3 videos/day | ~90 videos | Hobbyists, students testing platform |
| **Starter** | $15/month | 10 videos/day | ~300 videos | Individual creators, teachers |
| **Pro** | $29/month | 50 videos/day | ~1,500 videos | Power users, agencies, course creators |

**Revenue Model:** Subscription-only (no one-time purchases, no credits, no expiry)

**Key Financial Metrics (Optimistic Scenario — 36 Months):**

| Metric | Value | Industry Context |
|--------|-------|------------------|
| **ARPU** | $29/month | Mid-market prosumer (Midjourney $10 → Adobe CC $55) |
| **CAC** | $55 | Low due to PLG referral loop + organic growth |
| **Monthly Churn** | 4% | Best-in-class for B2C AI SaaS (industry norm 5-10%) |
| **LLM Cost/User** | $6/month | Optimized via prompt caching + model routing |
| **Gross Margin** | 79.3% | Exceptionally healthy for AI SaaS |
| **LTV** | $575 | Strong retention + low churn |
| **LTV/CAC Ratio** | 10.5x | Excellent (>3x considered healthy) |
| **CAC Payback** | 2.4 months | Fast capital recovery |
| **Break-Even** | Month 13 | All invested capital recovered |
| **ROI at 12 months** | -3.8% | Near break-even (exceptional for SaaS) |
| **ROI at 36 months** | +67.9% | Strong return on invested capital |

**Growth Trajectory (Optimistic):**

| Milestone | Users | Monthly Revenue | Cumulative Investment |
|-----------|-------|-----------------|----------------------|
| **Month 1** | 10 paying | $290 | $1,000 (setup) + $1,000 (ops) |
| **Month 12** | 323 paying | $9,362/month | $45,889 total cost |
| **Month 36** | 53,472 paying | $1,550,686/month | $4,811,986 total cost |

**Assumptions Behind Optimistic Scenario:**
- **4% monthly organic growth** (requires shareable output + referral program)
- **45% of revenue → marketing spend** (aggressive growth investment)
- **Low CAC ($55)** assumes product-led growth (PLG) with viral loop
- **Low churn (4%)** requires strong onboarding + habit formation

**Reality Check:** Achieving all simultaneously (low CAC + low churn + 4% organic growth) is challenging pre-PMF but individually realistic. Conservative planning should use Base Case (11.4% ROI at 36 months, break-even Month 27).

### 2.5 Geographic Focus

- **Primary Market:** EU (GDPR-compliant hosting, transparent billing addresses TRIAD-3)
- **Expansion:** Global English-speaking (USA, UK, Canada, Australia)
- **Compliance:** EU AI Act LIMITED-RISK, GDPR pre-launch ready

---

## 3. Proposed AI Solution

### 3.1 Solution Overview

**AI Storytelling Platform** transforms text prompts into complete multi-scene videos with **guaranteed character consistency** in 30-45 seconds. Unlike competitors where characters change faces after ≤2 scenes, our platform maintains exact same character appearance for 6+ scenes using **entity extraction technology**.

### 3.2 Core Innovation #1: Entity Extraction (Solves TRIAD-1)

**The Character Consistency Problem:**
- User prompt: "Apollo 11 moon landing"
- Competitor output: Neil Armstrong looks completely different in scenes 1, 3, 5, 6 (unusable for storytelling)
- Market benchmark: ≤2 scenes before catastrophic failure

**Our Solution (Entity Extraction Pipeline):**

```
Step 1: Script Generation
GPT-4o-mini generates 962-character script with 6 narrative segments

Step 2: Entity Extraction (THE INNOVATION)
GPT-4o-mini identifies recurring characters/objects:
  - Character: "Neil Armstrong — Male astronaut, late 30s, 1960s NASA white 
    spacesuit with American flag patch, short brown hair, determined facial 
    expression, calm demeanor"
  - Object: "Saturn V Rocket — Massive white rocket, multi-stage, 363 feet tall, 
    NASA logo on side, launchpad visible"

Step 3: Visual Consistency Enforcement
Same entity description injected into ALL image generation prompts:
  - Segment 1 prompt: "Saturn V Rocket — Massive white rocket... launching"
  - Segment 3 prompt: "Neil Armstrong — Male astronaut... standing on moon"
  - Segment 5 prompt: "Neil Armstrong — Male astronaut... planting flag"
  - Segment 6 prompt: "Neil Armstrong — Male astronaut... inside capsule"

Step 4: Result
Armstrong appears identical across segments 1, 3, 5, 6 (POC: 85-90% consistency)
vs. Competitor: Each scene shows different person (0% consistency after scene 2)
```

**Market Validation:**
- Solves #1 pain (22 sources): *"I'd switch tomorrow if consistent characters"*
- Competitor gap confirmed: Midjourney admits frustration (Feb 18, 2026)
- Our answer: 6+ scenes with 85-90% visual consistency (POC validated)

### 3.3 Core Innovation #2: Step-by-Step Approval Workflow (Solves TRIAD-2 & TRIAD-3)

**The Pay-for-Failures Problem:**
- Existing tools: User pays upfront → full generation runs → discovers failures at end → burns credits on garbage
- User complaint: *"$1,400 spent on Arcads, ZERO usable videos"*

**Our Solution (Micro-Stage Approval):**

```
Production SaaS Architecture (Live in Month 2):

┌─────────────────────────────────────────────────────────────────────┐
│ USER DASHBOARD — Step-by-Step Approval Workflow                    │
└─────────────────────────────────────────────────────────────────────┘

[STAGE 1: TOPIC INPUT]
User enters: "Apollo 11 moon landing" + selects "Teacher" pipeline
▼ FREE (no charge)

[STAGE 2: SCRIPT PREVIEW] ← **USER APPROVAL CHECKPOINT #1**
System shows:
  - Generated script (962 characters, 6 segments)
  - Estimated cost: $0.023
  - Character entities identified: Neil Armstrong, Saturn V Rocket
▼ 
User reviews → clicks "Approve Script" or "Regenerate" (uses 1 quota in Year 1)
▼ NO FINAL CHARGE YET (but regeneration counts toward daily limit)

[STAGE 3: FACT-CHECK REVIEW] (Teacher pipeline only) ← **CHECKPOINT #2**
System shows:
  - 4 claims verified (3 TRUE, 1 FALSE + correction provided)
  - Citations: NASA.gov, History.com
▼
User reviews → clicks "Accept Corrections" or "Skip Fact-Check"
▼ NO CHARGE YET

[STAGE 4: IMAGE PREVIEW] ← **USER APPROVAL CHECKPOINT #3**
System generates 6 images (with entity consistency) and displays grid:
  [Img 1] [Img 2] [Img 3]
  [Img 4] [Img 5] [Img 6]
▼
User reviews → clicks "Approve Images" or "Regenerate Failed Ones"
  - Selective regeneration: Only regenerate image #3 if character looks wrong (uses quota in Year 1)
  - User sees EXACTLY what will be in final video before finalizing
▼ NO FINAL CHARGE YET (but regenerations count toward daily limit in Year 1)

[STAGE 5: AUDIO PREVIEW] ← **USER APPROVAL CHECKPOINT #4**
System generates TTS audio (OpenAI TTS-1, 24kHz MP3)
▼
User plays audio → clicks "Approve Voice" or "Change Voice/Speed"
▼ NO CHARGE YET

[STAGE 6: FINAL VIDEO GENERATION] ← **PAYMENT TRIGGER**
User clicks "Generate Final Video" (only after approving all stages)
▼ 
**CHARGE APPLIED: $0.023** (or deduct 1 from daily quota)
▼
System assembles MP4 (MoviePy, H.264 encoding, 30 seconds processing)
▼
User downloads final_video.mp4 (guaranteed usable because all stages pre-approved)
```

**Why This Solves TRIAD-2 (Cost-Per-Usable Crisis):**
1. **No blind payments:** User sees EXACTLY what they're paying for before charge
2. **Free iterations:** Regenerate script/images until satisfied (no credit burn)
3. **Selective fixes:** Only regenerate specific failed images (not entire project)
4. **Guaranteed usability:** Payment triggers ONLY when user confirms "this is good"

**Why This Solves TRIAD-3 (Billing Trust Crisis):**
1. **Transparent pricing:** User sees exact cost ($0.023) before final approval
2. **No surprise charges:** Payment happens at explicit user action ("Generate Final Video")
3. **No credit expiry:** Subscription = daily quota (50 videos/day Pro tier), not credits
4. **Functional cancel:** Standard Stripe cancellation (no dark patterns)

**Competitive Advantage:**

| Feature | Competitors | AI Storytelling Platform |
|---------|-------------|--------------------------|
| **Payment Model** | ❌ Pay upfront per attempt (failures burn credits) | ✅ Preview all stages before finalizing (transparent workflow) |
| **Preview Before Pay** | ❌ No preview (blind generation) | ✅ Preview script, images, audio at each checkpoint |
| **Iteration Cost (Year 1)** | ❌ Each regeneration = new charge | ⚠️ Regenerations use daily quota (transparent limit) |
| **Iteration Cost (Year 2+)** | ❌ Each regeneration = new charge | ✅ Free regenerations within approval stages (no quota penalty) |
| **Selective Fixes** | ❌ Regenerate entire project | ✅ Regenerate only failed images (granular control) |
| **Transparency** | ❌ Hidden costs, credit expiry, surprise charges | ✅ Exact cost shown upfront, no expiry, subscription quota |

### 3.4 Dual-Pipeline Architecture

Unlike single-purpose tools, our system routes requests to specialized workflows:

| Feature | YouTube Pipeline | Teacher Pipeline |
|---------|------------------|------------------|
| **Use Case** | `use_case: "youtube"` | `use_case: "teacher"` |
| **Target** | Entertainment, social media | Education, fact-verified content |
| **Character Consistency** | ✅ Entity extraction (TRIAD-1 solution) | ✅ Entity extraction (TRIAD-1 solution) |
| **Fact-Checking** | ❌ NO (creative freedom) | ✅ YES (Facticity API, cites sources) |
| **Step-by-Step Approval** | ✅ Script → Images → Audio → Video | ✅ Script → Fact-Check → Images → Audio → Video |
| **Speed** | ~30 seconds (after approvals) | ~45 seconds (+15s fact-check, after approvals) |
| **Quality Focus** | Engagement, creativity | Factual accuracy, pedagogy |

### 3.5 Technical Architecture

**AI Services Stack:**

1. **Script Generation:** OpenAI GPT-4o-mini ($0.15/$0.60 per 1M tokens)
2. **Entity Extraction:** GPT-4o-mini identifies characters/objects → visual base descriptions
3. **Fact-Checking:** Facticity API (Teacher pipeline) — verifies claims, provides citations
4. **RAG Retrieval:** Pinecone vector DB + Cohere embeddings (storytelling best practices)
5. **Image Generation:** Pollinations.ai (POC) → Stability AI (production, Month 3)
6. **Text-to-Speech:** OpenAI TTS-1 (alloy voice, 24kHz MP3)
7. **Video Assembly:** MoviePy (Python library, H.264 MP4 encoding)
8. **Orchestration:** LangGraph StateGraph (conditional routing, iterative refinement)

**Infrastructure:**
- **Backend:** FastAPI (async Python web framework)
- **Database:** SQLite (POC) → PostgreSQL (production, Month 2)
- **Hosting:** Hetzner Germany (EU GDPR-compliant, €40/month VPS)
- **Monitoring:** (Production Month 4: Sentry error tracking, Grafana metrics)

### 3.6 End-to-End Workflow (User Perspective — Production SaaS)

```
User Experience (Pro Tier, Morning Routine):

8:00 AM — User logs in to dashboard
  - Sees quota: "47/50 videos remaining today"
  
8:02 AM — Creates Project #1: "Ancient Rome gladiator training"
  - Selects YouTube pipeline (entertainment)
  - System generates script in 5 seconds
  - User reviews script, clicks "Approve" (no charge)
  
8:03 AM — Reviews 6 generated images (entity extraction: same gladiator across all scenes)
  - Image #4 looks off (gladiator helmet wrong angle)
  - Clicks "Regenerate Image #4" only (uses 1 quota in Year 1, 8 seconds)
  - New image #4 looks good → "Approve Images"
  - Note: In Year 2+, regenerations within approval stage won't count toward quota
  
8:05 AM — Reviews audio preview
  - Voice sounds good → "Approve Audio" (no charge yet)
  
8:06 AM — Clicks "Generate Final Video"
  - System charges: $0.023 or uses 1/50 daily quota
  - 30 seconds later: final_video.mp4 ready
  - User downloads, posts to YouTube Shorts
  
8:07 AM — Creates Project #2: "Photosynthesis lesson" (Teacher pipeline)
  - [Same approval workflow as above, +15s for fact-checking stage]
  
Total time: Creates 2 usable videos in 10 minutes (used 4 of 50 daily quota: 2 final videos + 2 regenerations)
vs competitors: 2 hours + $10+ burned on failures with zero preview capability

Note: For long-form content (30+ min videos), workflow is identical but generation takes proportionally longer (e.g., 60-scene video = ~5 minutes generation time after all approvals). Step-by-step approval ensures user validates every stage regardless of video length (30 seconds or 2 hours).
```

### 3.7 EU AI Act Compliance

**Risk Classification:** LIMITED-RISK (transparency obligations only)

**Obligations Met:**
- ✅ Disclose AI-generated content (watermark on videos: "Generated by AI")
- ✅ Provide human contact (support email: support@example.com)
- ✅ Allow opt-out (users can cancel subscription anytime via dashboard)

**Not High-Risk:** No employment decisions, no credit scoring, no law enforcement, no critical infrastructure

### 3.8 Market Positioning Statement

> *"The first AI video platform that solves character consistency — the #1 market blocker cited by 22 independent sources and publicly admitted by Midjourney. While competitors charge $5-20 per blind attempt (failures burn credits), we let users preview and approve every stage before paying $0.02 per guaranteed-usable video. For educators, add automatic fact-checking. For all users, add transparent billing (no credit expiry, no surprise charges, no dark patterns)."*

---

## 4. Key Stakeholders

### 4.1 End Users (Who Uses the System)

| Segment | Role | Use Case | Frequency | Pain Solved |
|---------|------|----------|-----------|-------------|
| **Content Creators** (PRIMARY) | YouTubers, TikTokers, social media managers | Story-driven shorts with recurring characters | 10-20 videos/week | Character consistency (TRIAD-1), $3K testing waste eliminated |
| **Educators** (SECONDARY) | Teachers, professors, course creators | Educational videos for lessons (History, Science, etc.) | 5-10 videos/week | Saves 3-5 hours/video, automatic fact-checking, no editing skills needed |
| **Marketing Teams** (TERTIARY) | SME/startup marketing leads | Explainer videos, product demos | 2-5 videos/month | Reduces cost from $200/video (freelancer) to $0.60/video (20 videos @ $0.03 each) |

**Market-Validated User Quotes:**

**Content Creators:**
- *"I'd switch tomorrow if any tool could give me consistent characters"* (1.3K upvotes) — TRIAD-1
- *"The quality is now sometimes good enough. The reliability, never."* (970 upvotes) — Consistency gap
- *"Show me one tool that maintains a character across a 10-scene sequence and we'll talk"* (727 upvotes) — Adoption trigger

**Educators:**
- 3-5 hours per video (manual production) → 10 minutes (our platform)
- Fact-checking eliminates misinformation risk for classroom use

**Marketing Teams:**
- $200/video freelance cost → $0.60/month (20 videos Pro tier)
- Faster iteration cycles (10 mins vs 2 weeks agency turnaround)

### 4.2 Decision Makers (Who Decides to Adopt)

| Stakeholder | Authority | Concerns | Success Criteria |
|-------------|-----------|----------|------------------|
| **Individual Creators** (B2C) | Personal budget decision | Cost (<$30/month), ease of use, output quality | Creates >10 usable videos/week |
| **Individual Educators** (B2C) | Personal/school budget | GDPR compliance, factual accuracy, ease of use | Saves >2 hours/video, zero misinformation |
| **School Administrators** (B2B, future) | Budget approval for staff licenses | Student data safety, educational value, ROI | Improves lesson quality, teacher efficiency |
| **Marketing Directors** (B2B, future) | Approve SaaS tools for team | ROI (cost vs freelancer), brand safety, quality | Reduces video cost by >80% |

### 4.3 Affected Parties (Who Is Impacted)

| Party | Impact | Concerns | Mitigation |
|-------|--------|----------|------------|
| **Students / Learners** | Consume AI-generated educational videos | Factual accuracy, misinformation risk | Fact-checking API (Teacher pipeline), human review recommended |
| **Video Editors / Freelancers** | Potential job displacement | Livelihood threat | Position as "tool for non-editors" (like Canva vs designers), not pro replacement |
| **AI Service Providers** | Data processing (OpenAI, Cohere, Facticity, Stability AI) | GDPR compliance, liability | SCCs, DPAs, data minimization (no PII sent to AI APIs) |
| **Platform Moderators** | YouTube, TikTok content policies | AI-generated spam, policy violations | Watermark AI content, rate limiting (3 videos/day Free, 50/day Pro) |

### 4.4 Regulatory Stakeholders

| Authority | Jurisdiction | Requirements | Compliance Status |
|-----------|--------------|--------------|-------------------|
| **Data Protection Authorities (DPAs)** | EU GDPR | User consent, data subject rights, breach reporting | ✅ GDPR documentation complete, pre-launch compliant |
| **EU AI Act Authorities** | EU AI Act (Regulation 2024/1689) | Transparency obligations (LIMITED-RISK) | ✅ AI content watermarked, human contact available, opt-out enabled |
| **Consumer Protection Agencies** | National laws (Germany, France, etc.) | Terms of Service, refund policies, cancellation rights | ⚠️ Legal review needed (production Week 5) |
| **Stripe / Payment Processors** | PCI-DSS compliance | Secure payment handling | ✅ Stripe handles all payment data (PCI compliant) |

---

## 5. Success Criteria

### 5.1 Success Criterion #1: Character Consistency Rate (Solves TRIAD-1)

**Metric:** % of multi-scene videos where same character maintains visual consistency across ALL scenes (human evaluation + automated similarity scoring)

**Targets (Optimistic Growth Scenario):**

| Milestone | Target | Measurement Method |
|-----------|--------|-------------------|
| **POC Baseline (April 2026)** | 85-90% consistency across 6 scenes | Moon demo: Armstrong identical in 4/6 scenes showing him |
| **Month 1 (Launch)** | >90% consistency | Entity extraction prompt refinement, 100 test videos |
| **Month 6** | >93% consistency | User feedback loop, automated cosine similarity >0.88 |
| **Month 12** | >95% consistency | Production-grade, industry-leading (target for funding pitch) |
| **Month 36** | >97% consistency | Category-defining performance (vs competitors ≤2 scenes) |

**Market Context:**
- **Competitor Benchmark:** ≤2 scenes before catastrophic failure (22 sources)
- **Adoption Trigger:** *"I'd switch tomorrow if consistent characters"* (1.3K upvotes)
- **Category Leader Admission:** Midjourney admits character consistency frustration (Feb 18, 2026)

**Measurement Method:**
1. **Automated:** Compare entity visual base descriptions vs generated image embeddings (CLIP cosine similarity >0.85 = pass)
2. **Manual QA:** 100 random videos/week, human evaluators rate character consistency (Pass/Fail binary)
3. **User Feedback:** NPS question "Character looked consistent across scenes?" (Yes/No)

**Why This Metric Matters:**
- Directly solves dominant market signal (TRIAD-1, 22 sources)
- Unique competitive moat (competitors benchmark ≤2 scenes = catastrophic)
- Measurable proof-of-capability for investor pitch
- User switching trigger: *"Show me one tool that maintains a character across 10 scenes"* (727 upvotes)

### 5.2 Success Criterion #2: Cost Per Usable Output (Solves TRIAD-2)

**Metric:** Average cost to generate ONE usable, deliverable video that user actually publishes/uses (not cost per failed attempt)

**Targets (Optimistic Scenario — Driven by Step-by-Step Approval):**

| Milestone | Target Cost/Video | Usability Rate | Why Achievable |
|-----------|-------------------|----------------|----------------|
| **POC Baseline** | $0.023/video | 100% usable (user approves all stages) | Step-by-step approval eliminates failures |
| **Month 1** | $0.020/video | 100% usable | Prompt optimization, reduce tokens by 20% |
| **Month 6** | $0.015/video | 100% usable | Redis caching 40% hit rate, batch API calls |
| **Month 12** | $0.012/video | 100% usable | Bulk pricing with OpenAI/Stability AI |
| **Month 36** | <$0.010/video | 100% usable | Scale efficiencies, model improvements |

**Note:** "100% usable" means finalized videos meet user approval (not abandoned/refunded). However, reaching approval may require regenerations:
- **Year 1:** Each regeneration (script/images/audio) consumes daily quota (e.g., 2 script iterations + 1 image fix = uses 3 of 50 daily quota)
- **Year 2+:** Free regenerations within approval stages (iterate without quota penalty once positive cash flow achieved)

**Market Context:**
- **Competitor Benchmark:** $3-5 per **attempt** (most attempts fail, users pay for garbage)
- **User Pain:** $1,400 spent on Arcads with zero usable videos (C26)
- **Market Demand:** "Pay only for usable output, not cost-per-generation" (12 sources, TRIAD-2)

**Why Step-by-Step Approval Achieves High Usability:**
1. User previews script → approves or regenerates (consumes quota/credit)
2. User previews images → approves or regenerates specific failed ones (consumes quota/credit)
3. User previews audio → approves or adjusts (consumes quota/credit)
4. Payment triggers when user confirms "Generate Final Video"
5. **Result:** User sees EXACTLY what they're paying for before finalizing (transparency, not free iterations)

**Note on Regenerations (Year 1 vs Year 2+):**
- **Year 1 (Launch - Month 12):** Each regeneration consumes daily quota (e.g., regenerate script = uses 1 of 50 daily videos). This ensures cost control during early growth phase when API costs must stay within margins.
- **Year 2+ (Month 13+):** Free regenerations within approval stages (iterate script/images without quota penalty) — enabled after achieving positive cash flow ($15K+ MRR) and economies of scale. Requires optimized caching, bulk API pricing with OpenAI/Stability AI, and 40%+ cache hit rates.

**Why This Phased Approach:**
- **Year 1 priority:** Prove product-market fit, achieve break-even (Month 13), avoid subsidizing unlimited regenerations pre-revenue
- **Year 2 priority:** Maximize user satisfaction with free iterations, reduce friction for power users (enabled by scale efficiencies)

**Measurement Method:**
- Track all AI API costs per video (OpenAI, Cohere, Facticity, Stability AI)
- Define "usable": User clicks "Download" AND does not request refund within 24h
- Calculate: `Total AI costs / Count of downloaded videos`

**Business Viability (Break-Even Analysis):**
- Pro user ($29/month) generates avg 500 videos/month (16/day)
- Cost: 500 videos × $0.012 = $6/month AI costs
- Revenue: $29/month
- Margin: $29 - $6 = **$23/user/month** (79% margin)
- Aligns with Optimistic ROI scenario (79.3% gross margin)

### 5.3 Success Criterion #3: Revenue / MRR (Business Viability)

**Metric:** Monthly Recurring Revenue from paid subscriptions (Starter $15 + Pro $29 tiers)

**Targets (Optimistic Scenario — 36 Months):**

| Milestone | Target MRR | Paying Users | ARPU | Cumulative Revenue |
|-----------|------------|--------------|------|-------------------|
| **Month 1 (Launch)** | $290 | 10 users | $29 avg | $290 |
| **Month 6** | $2,900 | 100 users | $29 avg | ~$10,000 |
| **Month 12** | $9,362 | 323 users | $29 avg | $44,146 |
| **Month 24** | $159,000 | 5,483 users | $29 avg | $1.4M |
| **Month 36** | **$1,550,686** | **53,472 users** | **$29 avg** | **$8,081,475** |

**Secondary Revenue Metrics:**

| Metric | Target (Month 12) | Target (Month 36) | Industry Benchmark |
|--------|-------------------|-------------------|-------------------|
| **Conversion Rate (Free → Paid)** | 8% | 10% | SaaS freemium: 5-10% |
| **Monthly Churn** | 5% | 4% | B2C AI SaaS: 5-10% (our target: best-in-class) |
| **CAC** | $55 | $55 | B2C paid social: $40-120 (our PLG model) |
| **LTV** | $450 | $575 | (ARPU - Costs) / Churn = ($29-$6)/4% = $575 |
| **LTV/CAC** | 8.2x | 10.5x | Healthy >3x, excellent >5x (we're exceptional) |

**Measurement Method:**
- Stripe revenue reporting (MRR, active subscribers, churn cohorts)
- Cohort analysis: Track Month 1 signups → Month 6 retention rate
- NPS survey: "Would you recommend?" (target >40 for product-market fit)

**Break-Even Analysis (Optimistic Scenario):**

| Metric | Value | Notes |
|--------|-------|-------|
| **Break-Even Month** | Month 13 | Cumulative revenue = cumulative costs ($45,889) |
| **Monthly cash-flow positive** | Month 10 | Revenue exceeds monthly operating costs |
| **ROI at 12 months** | -3.8% | Near break-even (exceptional for early SaaS) |
| **ROI at 36 months** | +67.9% | Strong return ($3.27M profit on $4.81M invested) |
| **Users at 36 months** | 53,472 | Requires 4%/mo organic growth (challenging but achievable with PLG) |

**Validation Triggers for Seed Funding:**
- **Month 6:** $2,900 MRR (100 paying users) = early traction signal
- **Month 12:** $9,362 MRR (323 paying users) = product-market fit evidence
- **Target for Seed Raise:** $15K-20K MRR (~500-700 paying users) validates business model

### 5.4 Success Criterion #4: Step-by-Step Approval Adoption (TRIAD-2/3 Validation)

**Metric:** % of users who utilize step-by-step approval checkpoints vs skipping directly to final generation

**Targets:**

| Milestone | Target Adoption Rate | What This Proves |
|-----------|---------------------|------------------|
| **Month 1** | >60% of users review at least 1 checkpoint | Feature discovery working |
| **Month 6** | >80% review script + images before final | Users value preview-before-pay |
| **Month 12** | >90% use at least 2 approval steps | Core workflow habit formed |

**Measurement Method:**
- Track user actions: `script_approved`, `images_regenerated`, `audio_previewed`
- Calculate: `Users with ≥1 approval action / Total users generating videos`

**Why This Validates TRIAD-2/3 Solution:**
- High adoption of approval checkpoints proves users value transparency
- Regeneration frequency indicates users catch failures BEFORE paying
- Proves step-by-step workflow solves "pay for failures" pain point

### 5.5 Success Criterion #5: Educational Fact-Check Accuracy (Teacher Pipeline)

**Metric:** % of educational videos with zero factual errors after Facticity API verification

**Targets:**

| Milestone | Target Accuracy | Measurement |
|-----------|----------------|-------------|
| **POC Baseline** | 75% (3/4 claims TRUE on first pass) | Moon demo validation |
| **Month 6** | >85% | Facticity confidence threshold tuning |
| **Month 12** | >90% | Human review queue for low-confidence claims |
| **Month 36** | >95% | AI + human hybrid verification system |

**Measurement Method:**
- Facticity API verdicts: `TRUE claims / Total claims verified`
- Manual spot-check: Educators review 50 random Teacher videos/month
- User reports: Track "Report Factual Error" button clicks (target <1% of videos)

**Why This Differentiates Teacher Pipeline:**
- No competitor offers automatic fact-checking
- Builds trust with educators (accuracy non-negotiable for classroom)
- Validates Facticity API integration quality

---

## 6. Out-of-Scope Boundaries

### 6.1 Real-Time Streaming / Live Generation ❌

**Why Out-of-Scope:**
- POC workflow takes 30-45s (LLM → RAG → image → TTS → assembly), incompatible with real-time
- Market demand: Near-zero signal for "live AI video generation" (0 sources in market analysis)
- Technical complexity: Would require complete architecture redesign (pre-rendered templates vs on-demand)
- Our focus: Asynchronous batch generation for YouTube Shorts/TikTok (99% of target use cases)

**Not in our JTBD:** Users want *pre-produced* short-form content they can schedule/edit, not live streams.

### 6.2 Post-Generation Video Editing (Trimming, Transitions, Audio Mixing) ❌

**Why Out-of-Scope:**
- Market alternative: CapCut, Premiere Rush, DaVinci Resolve (purpose-built, mature tools)
- Our value: *Generation* (AI creates video from text), not *editing* (user modifies existing)
- Technical rationale: MoviePy is assembly tool (concat clips), not full video editor
- Feature creep risk: Trying to compete with Adobe = unfocused product

**Strategic Decision:** Partner with editing tools (export-to-CapCut button) vs build inferior version.

### 6.3 3D Animation / CGI Rendering ❌

**Why Out-of-Scope:**
- POC uses 2D image generation (Stability AI), not 3D models
- Market demand: 3D storytelling is niche (Blender, Cinema 4D users), not our target (content creators)
- Cost prohibitive: 3D rendering requires GPU clusters ($5-10/video vs our $0.02)
- Quality gap: Open-source 3D models can't match Pixar-level expectations, risky brand perception

**Not in our JTBD:** TRIAD-1 users want *consistent 2D characters* (Midjourney style), not 3D animation.

### 6.4 Human Actor Footage / Real-World Video ❌

**Why Out-of-Scope:**
- POC is AI-generated imagery only (Stability AI → cartoons/illustrations)
- Market alternative: Stock footage (Pexels, Shutterstock), user-recorded phone videos
- Legal complexity: Using AI to generate "deepfake-style" human faces = regulatory nightmare (EU AI Act high-risk)
- Our moat: Character consistency in *illustrated/cartoon* domain (lower regulatory risk)

**Strategic Decision:** Stay in "AI-generated art" category, avoid human likeness controversy.

### 6.5 Credits-Based / Pay-Per-Generation Pricing ❌ (STRATEGIC — Solves TRIAD-3)

**Why Out-of-Scope:**
- **Market pain (TRIAD-3, 11 sources):** *"$40 worth of credits just vanished"* (C19, expired without warning)
- **Trust crisis:** Users hate credits that expire, burn on failed attempts, or disappear mysteriously
- **VM-1 demand:** "Pay for usable output, not cost-per-generation" (12 sources)
- **Our model:** Freemium subscription (3 videos/day Free, 50/day Pro $29/month) — predictable, transparent

**Competitive Advantage:** Midjourney charges $10/month for 200 *attempts* (85% fail), we charge $29 for 1,500 *usable* videos. Our step-by-step approval ensures users see exact output before finalizing (Year 1: regenerations use quota; Year 2+: free iterations within approval stages).

**Explicitly Excluded:**
- No "buy 100 credits for $20" bundles
- No "1 credit = 1 generation (whether usable or not)" system
- No expiring credits ("use within 30 days or lose them")

### 6.6 Enterprise Collaboration Tools (Multi-User Workspaces) ❌

**Why Out-of-Scope (Year 1):**
- **POC optimized for:** Individual creators (B2C), not team workflows (B2B)
- **Technical complexity:** Team workspaces require permissions, version control, commenting, approval workflows
- **Strategic focus:** Validate product-market fit with individual users FIRST (B2C), then add B2B features (Month 12+)
- **Market priority:** TRIAD-1 users are individual creators/educators, not enterprises

**Future Consideration:** Add team workspaces in Month 12-24 after PMF validation (admin dashboards, user roles, shared asset libraries).

### 6.7 Professional Filmmaking (Feature Films, Commercials with Legal Liability) ❌

**Why Out-of-Scope:**
- **Quality bar:** Hollywood-level expectations vs POC = illustrative/cartoon style (good for YouTube, insufficient for cinema)
- **Legal liability:** Professional use requires indemnification, IP guarantees, insurance (startup risk too high)
- **Fact-check limitations:** Teacher pipeline catches basic errors, but NOT legal/medical claims requiring expert review
- **Our positioning:** "AI storytelling for creators/educators" (individual use), NOT "enterprise production tool"

**Explicitly Excluded Use Cases:**
- TV commercials (legal approval process incompatible with AI unpredictability)
- Medical training videos (fact-check API not FDA-compliant)
- Legal/financial advice content (regulatory compliance nightmare)

**Strategic Boundary:** If user-generated content causes harm, Section 230 protections apply (platform, not publisher). If we position as "professional tool," we become liable.

---

## Summary Table: In-Scope vs Out-of-Scope

| Capability | Status | Rationale |
|---|---|---|
| **Short-to-Long-Form Video (30s - 2 hours)** | ✅ **IN-SCOPE** | Step-by-step approval works for any length (user controls each stage) |
| **Character Consistency (6+ scenes)** | ✅ **IN-SCOPE** | Core value prop, answers TRIAD-1 (22 sources), entity extraction |
| **Step-by-Step Approval Workflow** | ✅ **IN-SCOPE** | Solves TRIAD-2 (transparency), TRIAD-3 (billing trust), production architecture |
| **Fact-Checking (Educational)** | ✅ **IN-SCOPE** | Differentiator for Teacher pipeline, Facticity API integrated |
| **Dual Pipelines (YouTube/Teacher)** | ✅ **IN-SCOPE** | Serve creators + educators without feature bloat |
| **Freemium Subscription Pricing** | ✅ **IN-SCOPE** | Answers TRIAD-3, transparent alternative to credits |
| **Free Regenerations (Year 2+)** | ⚠️ **ROADMAP** | Year 1: Regenerations use quota; Year 2+: Free iterations within approval stages |
| Real-Time Streaming | ❌ Out-of-Scope | Zero market demand, incompatible with async generation |
| Video Editing (Post-Gen) | ❌ Out-of-Scope | CapCut/Premiere exist, we focus on *generation* |
| 3D Animation / CGI | ❌ Out-of-Scope | Niche market, 10x cost, quality gap vs expectations |
| Human Actor Footage | ❌ Out-of-Scope | Legal/regulatory risk (EU AI Act), our moat = illustrated style |
| **Credits-Based Pricing** | ❌ **OUT-OF-SCOPE** | Addresses TRIAD-3 (trust crisis), strategic differentiation |
| Enterprise Collaboration (Year 1) | ❌ Out-of-Scope | B2C first, B2B features Month 12+ after PMF |
| Professional Filmmaking | ❌ Out-of-Scope | Legal liability, quality bar, positioning = creators not enterprise |

---

## Appendix: Key Market Intelligence References

**TRIAD-1 (Character Consistency Crisis) — 22 Sources:**
- *"I'd switch tomorrow if any tool could give me consistent characters"* (1.3K upvotes)
- *"Continuity errors costing studios millions — most legitimate AI problem"* (318 upvotes)
- Midjourney admission: *"We understand how frustrating it can be when you're aiming for character consistency"* (Feb 18, 2026)

**TRIAD-2 (Cost-Per-Usable Crisis) — 12 Sources:**
- $3,000+ average testing spend (F3, 1.6K upvotes)
- $1,400 on Arcads with zero usable output (C26)
- 4x more manual fix time than traditional production (F6, 970 upvotes)

**TRIAD-3 (Billing Trust Crisis) — 11 Sources:**
- $175 in credits expired without warning (C19, InVideo)
- Unauthorized charges $129-588 (documented cases)
- Non-functional "Cancel" buttons (Leonardo AI, CapCut)

**Financial Model Source:**
- ROI Analysis document: `ROI analysis and dashboard/ROI_Analysis.md`
- Optimistic scenario: 67.9% ROI at 36 months, 53,472 paying users, $1.55M MRR

---

**Document Version:** 2.0  
**Last Updated:** April 1, 2026  
**Next Review:** Post-MVP Launch (Month 2)
