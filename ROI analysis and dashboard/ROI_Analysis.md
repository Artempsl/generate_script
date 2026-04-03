# SaaS ROI Analysis
**B2C AI Image Generation · US Market · Three-Scenario Model · 36-Month Horizon**

All figures are derived from the financial model in `SaaS_ROI_PowerBI_v3.xlsx`.

---

## Executive Summary

| Metric | Pessimistic | Base Case | Optimistic |
|---|---|---|---|
| Setup Cost | $3,000 | $2,000 | $1,000 |
| ARPU | $15/mo | $23/mo | $29/mo |
| CAC | $90 | $60 | $55 |
| Monthly Churn | 9% | 6% | 4% |
| LLM Cost/User | $8/mo | $7/mo | $6/mo |
| Contribution Margin | $7/user | $16/user | $23/user |
| Gross Margin | 46.7% | 69.6% | 79.3% |
| LTV | $78 | $267 | $575 |
| LTV/CAC | 0.9x | 4.4x | 10.5x |
| CAC Payback | 12.9 months | 3.8 months | 2.4 months |
| Break-Even Month | Not reached | Month 27 | Month 13 |
| **ROI at 12 months** | **-85.4%** | **-39.6%** | **-3.8%** |
| **ROI at 36 months** | **-73.1%** | **+11.4%** | **+67.9%** |
| Users at Month 36 | 40 | 1,160 | 53,472 |
| Revenue at Month 36 | $594/mo | $26,689/mo | $1,550,686/mo |

---

## Scenario 1 — Pessimistic

### 1. Cost Estimate — Upfront

| Item | Cost | Notes |
|---|---|---|
| Product development (MVP) | $1,500–$2,500 | Freelance dev or no-code + custom API integration |
| Domain + hosting setup | $50–$100 | Annual domain + initial cloud instance |
| AI API integration & testing | $200–$300 | Initial API credits consumed during build & QA |
| Design & brand assets | $100–$200 | Figma templates, logo, landing page |
| Legal / terms of service | $50–$150 | Template-based ToS + privacy policy |
| **Total** | **$3,000** | One-time, spent before Month 1 |

### 2. Cost Estimate — Ongoing (Monthly, at Scale)

Ongoing costs scale with the user base. The model uses stepped fixed costs and revenue-based marketing spend.

| Cost Category | Driver | Month 1 (est.) | Month 36 (est.) |
|---|---|---|---|
| Fixed: team + infra | Step-up by users | $1,000 | $1,000–$15,000 |
| Marketing spend | 25% of prior revenue | $300 (floor) | Scales with revenue |
| LLM / API fees | $8/user/month | Near $0 | Scales with users |
| Payment processing | ~2.9% of revenue | Minimal | Scales with revenue |
| **Total monthly avg** | | | **$1,615/mo avg** |

### 3. Business Value Estimate

| Value Driver | Metric | Estimate |
|---|---|---|
| Recurring subscription revenue | ARPU × paying users | $15/user/mo × growing base |
| Revenue at Month 12 | 26 users × $15 | $395/mo |
| Revenue at Month 36 | 40 users × $15 | $594/mo |
| Lifetime value per user | (ARPU − LLM) ÷ churn rate | $78 per user |
| CAC payback period | CAC ÷ contribution margin | 12.9 months |
| LTV/CAC ratio | LTV ÷ CAC | 0.9x |
| Gross margin per user | (ARPU − LLM) ÷ ARPU | 46.7% |

### 4. ROI Calculation

**Formula: ROI = (Net Benefit / Total Cost) × 100 | Net Benefit = Total Revenue − Total Cost**

| Metric | 12 Months | 36 Months |
|---|---|---|
| Total Revenue | $2,955 | $15,670 |
| Total Cost (incl. setup) | $20,176 | $58,157 |
| Net Benefit | -$17,221 | -$42,487 |
| **ROI** | **-85.4%** | **-73.1%** |

> **ROI Verdict**
> - **12-month ROI: -85.4%** — Heavy burn phase. Normal for pre-traction SaaS.
> - **36-month ROI: -73.1%** — Does not recover investment within 3 years at current parameters. The core problem is slow user growth driven by high CAC ($90) and high churn (9%), which prevents revenue from compounding.

### 5. Break-Even Point

| Break-Even Type | Month | What it means |
|---|---|---|
| Monthly cash-flow positive | ~Month 33+ | Revenue first exceeds monthly operating costs |
| Cumulative break-even | Not reached | All invested capital not recovered within 36 months |
| CAC payback (per user) | 12.9 months | Revenue from one user covers the cost of acquiring them |

---

## Scenario 2 — Base Case

### 1. Cost Estimate — Upfront

| Item | Cost | Notes |
|---|---|---|
| Product development (MVP) | $1,000–$1,500 | Founder-led build with some freelance support |
| Domain + hosting setup | $50–$100 | Annual domain + initial cloud instance |
| AI API integration & testing | $200–$300 | Initial API credits consumed during build & QA |
| Design & brand assets | $100–$200 | Figma templates, logo, landing page |
| Legal / terms of service | $50–$150 | Template-based ToS + privacy policy |
| **Total** | **$2,000** | One-time, spent before Month 1 |

### 2. Cost Estimate — Ongoing (Monthly, at Scale)

| Cost Category | Driver | Month 1 (est.) | Month 36 (est.) |
|---|---|---|---|
| Fixed: team + infra | Step-up by users | $1,000 | $1,000–$11,000 |
| Marketing spend | 35% of prior revenue | $600 (floor) | Scales with revenue |
| LLM / API fees | $7/user/month | Near $0 | Scales with users |
| Payment processing | ~2.9% of revenue | Minimal | Scales with revenue |
| **Total monthly avg** | | | **$6,805/mo avg** |

### 3. Business Value Estimate

| Value Driver | Metric | Estimate |
|---|---|---|
| Recurring subscription revenue | ARPU × paying users | $23/user/mo × growing base |
| Revenue at Month 12 | 108 users × $23 | $2,475/mo |
| Revenue at Month 36 | 1,160 users × $23 | $26,689/mo |
| Lifetime value per user | (ARPU − LLM) ÷ churn rate | $267 per user |
| CAC payback period | CAC ÷ contribution margin | 3.8 months |
| LTV/CAC ratio | LTV ÷ CAC | 4.4x |
| Gross margin per user | (ARPU − LLM) ÷ ARPU | 69.6% |

### 4. ROI Calculation

**Formula: ROI = (Net Benefit / Total Cost) × 100 | Net Benefit = Total Revenue − Total Cost**

| Metric | 12 Months | 36 Months |
|---|---|---|
| Total Revenue | $16,309 | $272,984 |
| Total Cost (incl. setup) | $27,002 | $244,981 |
| Net Benefit | -$10,693 | +$28,003 |
| **ROI** | **-39.6%** | **+11.4%** |

> **ROI Verdict**
> - **12-month ROI: -39.6%** — Still in investment phase. Loss is narrowing month-on-month.
> - **36-month ROI: +11.4%** — Marginally profitable. The model works — break-even at Month 27 confirms that compounding user growth eventually outpaces costs. Optimizing LLM cost or churn would accelerate this significantly.

### 5. Break-Even Point

| Break-Even Type | Month | What it means |
|---|---|---|
| Monthly cash-flow positive | ~Month 24 | Revenue first exceeds monthly operating costs |
| Cumulative break-even | **Month 27** | All invested capital fully recovered |
| CAC payback (per user) | 3.8 months | Revenue from one user covers the cost of acquiring them |

---

## Scenario 3 — Optimistic

### 1. Cost Estimate — Upfront

| Item | Cost | Notes |
|---|---|---|
| Product development (MVP) | $500–$800 | Founder builds with existing tooling + templates |
| Domain + hosting setup | $50–$100 | Annual domain + initial cloud instance |
| AI API integration & testing | $100–$150 | Optimized build process, fewer wasted credits |
| Design & brand assets | $50–$100 | Minimal viable brand, iterate post-launch |
| Legal / terms of service | $50–$150 | Template-based ToS + privacy policy |
| **Total** | **$1,000** | One-time, spent before Month 1 |

### 2. Cost Estimate — Ongoing (Monthly, at Scale)

| Cost Category | Driver | Month 1 (est.) | Month 36 (est.) |
|---|---|---|---|
| Fixed: team + infra | Step-up by users | $1,000 | $11,000–$15,000 |
| Marketing spend | 45% of prior revenue | $800 (floor) | Scales with revenue |
| LLM / API fees | $6/user/month | Near $0 | Scales with users |
| Payment processing | ~2.9% of revenue | Minimal | Scales with revenue |
| **Total monthly avg** | | | **$133,666/mo avg** |

### 3. Business Value Estimate

| Value Driver | Metric | Estimate |
|---|---|---|
| Recurring subscription revenue | ARPU × paying users | $29/user/mo × growing base |
| Revenue at Month 12 | 323 users × $29 | $9,362/mo |
| Revenue at Month 36 | 53,472 users × $29 | $1,550,686/mo |
| Lifetime value per user | (ARPU − LLM) ÷ churn rate | $575 per user |
| CAC payback period | CAC ÷ contribution margin | 2.4 months |
| LTV/CAC ratio | LTV ÷ CAC | 10.5x |
| Gross margin per user | (ARPU − LLM) ÷ ARPU | 79.3% |

### 4. ROI Calculation

**Formula: ROI = (Net Benefit / Total Cost) × 100 | Net Benefit = Total Revenue − Total Cost**

| Metric | 12 Months | 36 Months |
|---|---|---|
| Total Revenue | $44,146 | $8,081,475 |
| Total Cost (incl. setup) | $45,889 | $4,811,986 |
| Net Benefit | -$1,742 | +$3,269,489 |
| **ROI** | **-3.8%** | **+67.9%** |

> **ROI Verdict**
> - **12-month ROI: -3.8%** — Essentially at break-even after 12 months. Exceptional for a SaaS at this stage.
> - **36-month ROI: +67.9%** — Strong return driven by compounding user growth. 53,000+ users at Month 36 generate $1.5M/mo in revenue. This scenario requires simultaneously achieving low CAC ($55), low churn (4%), and strong organic growth (4%/mo) — individually realistic, but challenging in combination at pre-PMF stage.

### 5. Break-Even Point

| Break-Even Type | Month | What it means |
|---|---|---|
| Monthly cash-flow positive | ~Month 10 | Revenue first exceeds monthly operating costs |
| Cumulative break-even | **Month 13** | All invested capital fully recovered |
| CAC payback (per user) | 2.4 months | Revenue from one user covers the cost of acquiring them |

---

## Assumptions Table

All assumptions apply across scenarios unless noted. Scenario-specific values shown where they differ.

| Assumption | Pessimistic | Base Case | Optimistic | Justification |
|---|---|---|---|---|
| ARPU ($/user/mo) | $15 | $23 | $29 | Market range: Midjourney $10 → Adobe CC $55. Base reflects mid-market B2C prosumer. |
| CAC ($) | $90 | $60 | $55 | Paid social B2C avg $40–$120. Lower in Optimistic assumes PLG referral loop active. |
| Monthly churn | 9% | 6% | 4% | B2C AI tools industry norm: 5–10%/mo. Lower churn requires strong onboarding + habit loop. |
| LLM API cost/user/mo | $8 | $7 | $6 | Image gen via FAL/Replicate. Optimistic reflects prompt caching + model routing savings. |
| Organic growth rate | 1%/mo | 3%/mo | 4%/mo | % of existing base acquired via word-of-mouth. Requires shareable output or referral program. |
| Marketing spend | 25% of revenue | 35% of revenue | 45% of revenue | Revenue-based model keeps marketing sustainable. Floor prevents stall at zero revenue. |
| Marketing floor | $300/mo | $600/mo | $800/mo | Minimum spend to guarantee new user acquisition before significant revenue exists. |
| Setup cost | $3,000 | $2,000 | $1,000 | Lower in Optimistic assumes founder-led build with existing tooling/templates. |
| Fixed cost tiers | $1K–$15K | $1K–$11K | $1K–$11K | Step-up based on user count. Reflects real hiring + infra scaling milestones. |
| Initial users | 0 | 0 | 0 | Pre-launch model. No existing audience assumed. |
| Projection horizon | 36 months | 36 months | 36 months | Standard seed-stage investor model window. |
| Revenue model | Subscription only | Subscription only | Subscription only | No one-time purchases, API upsells, or enterprise tiers modeled. |
| Freemium conversion | Not modeled | Not modeled | Not modeled | Model assumes direct paid acquisition. Freemium conversion would improve effective CAC. |

---

*End of document*
