# AI Storytelling Platform - Risk Assessment Matrix

## Executive Summary

**Document Version:** 1.0  
**Assessment Date:** April 1, 2026  
**Scope:** Full Deployment Phase (Months 3-12, 2026)  
**Risk Tolerance:** Moderate (calculated risks with mitigation)  
**Compliance Status:** Pre-Launch Preparation — **GDPR Risk: LOW** | **EU AI Act: LIMITED-RISK (Article 52)**

**Regulatory Framework:**
- **GDPR** (Regulation 2016/679) — Data Protection Impact Assessment (DPIA) completed, overall risk **LOW**
- **EU AI Act** (Regulation 2024/1689) — Classified as **LIMITED-RISK** (transparency obligations only, NOT HIGH-RISK educational system)
- Compliance documentation: [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) | [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md)

This risk assessment identifies and quantifies 16 key risks across regulatory, technical, ethical, and operational categories for the AI Storytelling Platform during the critical Full Deployment phase (scaling from 50 pilot users to 1,000+ paying customers).

**High-Risk Areas (Risk Level ≥ 15):**
- **GDPR Non-Compliance** (20/25) — Legal/regulatory exposure
- **Data Breach** (20/25) — User trust and financial liability
- **Unit Economics Collapse** (20/25) — Optimistic scenario unrealistic, LTV/CAC 3.99x vs 10.5x
- **Image Generation Quality Issues** (16/25) — User satisfaction and retention
- **API Cost Overruns** (15/25) — Financial sustainability
- **Low User Retention** (15/25) — Business viability

---

## Risk Scoring Methodology

### Likelihood Scale (1-5)
| Score | Definition | Probability |
|-------|------------|-------------|
| **1** | Very Unlikely | <10% chance in next 12 months |
| **2** | Unlikely | 10-30% chance |
| **3** | Possible | 30-50% chance |
| **4** | Likely | 50-70% chance |
| **5** | Very Likely | >70% chance |

### Impact Scale (1-5)
| Score | Definition | Business Impact |
|-------|------------|-----------------|
| **1** | Negligible | Minor inconvenience, <€1K loss, <5% user impact |
| **2** | Minor | Temporary disruption, €1K-€10K loss, 5-15% user impact |
| **3** | Moderate | Significant disruption, €10K-€50K loss, 15-30% user impact |
| **4** | Major | Severe disruption, €50K-€200K loss, 30-60% user impact |
| **5** | Severe | Business-threatening, >€200K loss, >60% user impact, legal action |

### Risk Level Matrix
| Risk Level | Color Code | Action Required |
|------------|-----------|-----------------|
| **1-4** | 🟢 Low | Monitor, routine controls |
| **5-9** | 🟡 Medium-Low | Active monitoring, preventive measures |
| **10-14** | 🟠 Medium-High | Priority mitigation, quarterly review |
| **15-19** | 🔴 High | Immediate action, monthly review, executive oversight |
| **20-25** | ⛔ Critical | Emergency response plan, weekly review, board escalation |

---

## Risk Heat Map

```
IMPACT
  5 │ R5      │        │ R12    │ R1, R2 │        │
    │         │        │        │        │        │
  4 │         │        │ R3     │ R4     │        │
    │         │        │        │        │        │
  3 │         │ R9,R10,│ R6,R13,│ R8     │        │
    │         │ R11,R14│ R15    │        │        │
  2 │         │ R7     │        │        │        │
    │         │        │        │        │        │
  1 │         │        │        │        │        │
    └─────────┴────────┴────────┴────────┴────────┴──
      1        2        3        4        5      LIKELIHOOD
```

**Legend:**
- **R1:** GDPR Non-Compliance (⛔ Critical)
- **R2:** Data Breach (⛔ Critical)
- **R3:** Image Generation Quality Issues (🔴 High)
- **R4:** API Cost Overruns (🔴 High)
- **R5:** COPPA Violation (Child Safety) (🔴 High)
- **R6:** Character Consistency Failure (🟠 Medium-High)
- **R7:** LLM Text Hallucinations (🟡 Medium-Low)
- **R8:** Low User Retention (🔴 High)
- **R9:** Poor Onboarding Experience (🟡 Medium-Low)
- **R10:** Workflow Resistance (🟡 Medium-Low)
- **R11:** Platform Misuse (Deepfakes) (🟡 Medium-Low)
- **R12:** API Integration Failures (🟠 Medium-High)
- **R13:** Video Pipeline Crashes (🟠 Medium-High)
- **R14:** CAC Exceeds ROI Targets (🟡 Medium-Low)
- **R15:** Tariff Plan Misalignment (🟠 Medium-High)
- **R16:** Unit Economics Collapse — Optimistic Scenario Unrealistic (⛔ Critical)

---

## Detailed Risk Register

### REGULATORY RISKS

#### R1: GDPR Non-Compliance ⛔ CRITICAL
**Category:** Regulatory  
**Current Status:** Pre-Launch Preparation  
**Reference:** [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) — Overall GDPR Risk: **LOW**

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | DPIA completed but legal review pending, DPAs unsigned with some processors |
| **Impact** | 5 (Severe) | €20M fine (4% revenue) or €10M (whichever higher), platform shutdown, reputational damage |
| **Risk Level** | **20** | **CRITICAL** |

**Risk Description:**
Per GDPR Documentation (Section 1.2), platform has **completed Data Protection Impact Assessment (DPIA)** and **Transfer Impact Assessment (TIA)** with overall risk rated **LOW**. However, launch-blocking gaps remain:

**Completed (per compliance/gdpr_documentation.md):**
- ✅ Data Protection Impact Assessment (DPIA) — Residual risk: LOW
- ✅ Transfer Impact Assessment (TIA) for USA transfers (OpenAI, Stripe, Google Analytics)
- ✅ Standard Contractual Clauses (SCCs) with OpenAI, Stripe, Google LLC
- ✅ EU-only hosting architecture (Hetzner Germany VPS)
- ✅ Data minimization (no user IDs sent to AI services, anonymous API requests)
- ✅ Short retention (90 days content, 180 days inactivity deletion)

**Missing (Launch Blockers):**
- ❌ Privacy Policy/Terms of Service legal review (€500-€1,000)
- ❌ DPAs unsigned: Cohere Canada, SerpAPI, Facticity API
- ❌ Pollinations.ai (no DPA) — MEDIUM risk, mitigated by generic prompts (no PII)
- ❌ Cookie consent banner implementation (Cookiebot or custom)
- ❌ User consent management system (analytics/marketing opt-in)

**Potential Consequences:**
- **Immediate:** EU Supervisory Authority complaint → investigation (72-hour response required)
- **Short-term:** Forced platform suspension until DPAs signed, Privacy Policy published
- **Long-term:** €20M or 4% global annual turnover fine (Article 83), €200K+ legal/remediation costs
- **Reputational:** Loss of trust, media coverage, user exodus (50%+ churn)

**Mitigation Strategy:**

**Phase 1: Legal Documentation (Month 3 — LAUNCH BLOCKER)**
1. **Legal review (€500-€1,000):**
   - Privacy Policy (based on gdpr_documentation.md Section 2.3 data flows)
   - Terms of Service (EU AI Act Article 52 transparency disclosures)
   - Cookie Policy (ePrivacy Directive compliance)

2. **Sign remaining DPAs:**
   - Cohere Canada (SCCs, PIPEDA compliance)
   - SerpAPI USA (SCCs or alternative web search provider)
   - Facticity API (clarify location, sign DPA if non-EU)

3. **Cookie consent implementation:**
   - Pre-blocking: Google Analytics script loads ONLY after user consent
   - Consent banner: "Reject All", "Accept All", "Customize" options
   - Account settings: Toggle "Allow analytics tracking" (revoke consent anytime)

**Phase 2: Data Architecture (Already Implemented per GDPR Doc)**
1. **EU-only hosting:**
   - VPS: Hetzner Germany (Frankfurt data center)
   - Database: PostgreSQL with SSL encryption
   - Backups: Hetzner Storage Box EU

2. **Data minimization (per Section 4.5):**
   - NO user identifiers to AI services (no email, UUID, IP)
   - OpenAI "user" parameter NOT used (anonymous requests)
   - Prompts cannot be linked to individual users

3. **Data retention (per Section 3.2):**
   - Generated content: 90 days (auto-deletion)
   - Inactive accounts: 180 days no login → soft delete (30-day grace) → hard delete
   - Application logs: 7 days (sanitized, no PII)

**Phase 3: User Rights Automation (Month 4)**
1. **Self-service data export (Article 15 - Right of Access):**
   - Download all projects, scripts, execution logs as ZIP
   - Export consent history, account data as JSON

2. **Account deletion (Article 17 - Right to Erasure):**
   - User-initiated: `DELETE /user/{id}` API endpoint
   - Cascade: PostgreSQL → Stripe (cancel subscription) → Brevo (delete contact) → File system
   - Timeline: 30-day grace period, then hard delete

**Phase 4: Third-Party Risk Management (Month 5)**
1. **Pollinations.ai migration (MEDIUM risk per Section 5.4):**
   - Plan migration to Stability AI (has DPA, GDPR-compliant)
   - Target: Month 6 (Pilot Phase)
   - Interim: Continue using (mitigated by generic prompts, no PII)

2. **External DPO appointment:**
   - Service: €200/month (handles GDPR compliance oversight)
   - Role: Annual GDPR audit, regulatory monitoring, breach response

**Phase 5: Ongoing Compliance**
- **Quarterly:** Review processor DPAs, update Privacy Policy if material changes
- **Annual:** GDPR audit (€3K), re-assess TIA for USA transfers (EDPB Schrems II compliance)
- **Ad-hoc:** Monitor regulatory changes (EDPB guidance, CJEU rulings)

**Success Metrics:**
- Month 3 Week 2: Privacy Policy live, all DPAs signed (launch readiness)
- Month 4: 100% consent capture (analytics opt-in rate >30%, marketing opt-in >15%)
- Month 12: Zero GDPR complaints, <24 hours data export/deletion response time
- Ongoing: Annual GDPR audit pass (no critical findings)

**Residual Risk After Mitigation:** Likelihood 2 (Unlikely) → Risk Level **10** (Medium-High)  
**Rationale:** DPIA rates overall risk as LOW, but execution risk remains until launch checklist completed.

---

#### R2: Data Breach (User Scripts, Personal Data) ⛔ CRITICAL
**Category:** Regulatory  
**Reference:** [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) Section 7 (Technical & Organizational Measures)

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | Production security measures designed but not fully implemented/tested |
| **Impact** | 5 (Severe) | GDPR Article 33 breach notification (72 hours), €10M fine, user trust loss |
| **Risk Level** | **20** | **CRITICAL** |

**Risk Description:**
Attacker gains unauthorized access to:
- **PostgreSQL database** (user credentials, scripts, project metadata) — Hetzner Germany VPS
- **Video files** on VPS file system (`projects/{slug}/` directories)
- **API keys** (OpenAI, Cohere, Pinecone, Facticity) in environment variables
- **Backups** on Hetzner Storage Box (daily automated backups)

**Attack Vectors:**
- **SQL injection** in FastAPI endpoints (if parameterized queries not enforced)
- **Server compromise** (outdated OS/dependencies, SSH brute force, unpatched CVEs)
- **API key exposure** (.env file committed to Git, application logs leaked with keys)
- **Backup theft** (Hetzner Storage Box credentials compromised)
- **Insider threat** (solo founder with root access, no audit trail for destructive actions)

**Potential Consequences:**
- **Legal:** GDPR Article 33 breach notification to DPA within 72 hours, fines up to €10M
- **Financial:** €50K-€200K incident response (forensics, legal, user notification)
- **Reputational:** Media coverage, user exodus (50%+ churn), competitor advantage
- **Operational:** Platform downtime 3-7 days for remediation

**Mitigation Strategy:**

**Phase 1: Encryption & Access Control (Month 3 — per GDPR Doc Section 7.1)**
1. **Data encryption (already designed per compliance docs):**
   - **At rest:** PostgreSQL SSL mode (TLS encryption for database files)
   - **In transit:** HTTPS/TLS 1.3 for all connections (Let's Encrypt certificates)
   - **Passwords:** bcrypt hashing (cost factor 12, salted per-user)
   - **Backups:** AES-256 encrypted backups on Hetzner Storage Box
   - **API keys:** Environment variables with 600 file permissions (read-only for app user)

2. **Parameterized queries (Section 7.2):**
   - Audit all FastAPI routes using SQLAlchemy ORM (prevents SQL injection)
   - Code review: No string concatenation in SQL queries
   - Static analysis: Use Bandit to detect SQL injection vulnerabilities

3. **Secrets management:**
   - Current: .env file with 600 permissions (root-only access)
   - Month 4: Migrate to HashiCorp Vault or AWS Secrets Manager (€0.40/secret/month)
   - API key rotation policy: 90-day rotation for OpenAI, Cohere, Pinecone

**Phase 2: Network Security (Month 3)**
1. **Server firewall (UFW on Hetzner):**
   - Allow: Ports 80 (HTTP redirect), 443 (HTTPS), 22 (SSH with key-only auth)
   - Deny: All other inbound traffic
   - SSH hardening: Disable password auth, require Ed25519 keys only

2. **Rate limiting (FastAPI Limiter):**
   - Global: 100 requests/minute per IP
   - Authentication endpoints: 5 login attempts/5 minutes per IP
   - Video generation: 10 concurrent jobs per user (prevent resource exhaustion)

3. **Intrusion detection:**
   - Fail2Ban: Ban IP after 5 failed SSH attempts (24-hour ban)
   - Log monitoring: Alert on suspicious patterns (mass login failures, sudo commands)

**Phase 3: Authentication & Authorization (Month 4 — per Section 3.1)**
1. **JWT authentication (already implemented):**
   - Access tokens: 15-minute expiry (short-lived to limit exposure)
   - Refresh tokens: 7-day expiry (stored in httpOnly cookies)
   - Token revocation: Blacklist on logout, password change, account deletion

2. **Role-based access control (RBAC):**
   - Roles: `user` (default), `admin` (solo founder only)
   - Permissions: Users can only access own projects, admins can view all (audit purposes)
   - Enforcement: FastAPI dependencies check user UUID matches resource owner

3. **Audit logging (Section 7.4):**
   - Track: All DB writes (project creation, deletion), API key usage, admin actions
   - Retention: 90 days (matches content retention policy)
   - Sanitization: No user input in logs (prevent log injection)

**Phase 4: Monitoring & Incident Response (Month 5)**
1. **Error tracking (Sentry €26/month):**
   - Alert on: Unhandled exceptions, API errors >5% rate, database connection failures
   - Data scrubbing: Remove PII from error traces (email → `user@*****.com`)

2. **Uptime monitoring (UptimeRobot €7/month):**
   - Check: Every 5 minutes (HTTP 200 on /health endpoint)
   - Alert: Email + SMS if down >2 minutes
   - SLA target: 99.5% uptime (43 hours downtime/year allowance)

3. **Incident response plan (GDPR Article 33 compliance):**
   - **Detection (<1 hour):** Sentry alerts, log monitoring, user reports
   - **Containment (<2 hours):** Isolate server, revoke API keys, enable maintenance mode
   - **Investigation (<24 hours):** Review logs, identify breach scope (how many users affected)
   - **Notification (<72 hours):** 
     - Email ALL users if personal data compromised
     - Notify German Supervisory Authority (BfDI) within 72 hours (GDPR requirement)
   - **Remediation (<7 days):** Patch vulnerabilities, force password resets, restore from clean backup

4. **Penetration testing:**
   - **Pre-launch:** €3K-€5K external pentest (OWASP Top 10 coverage)
   - **Annual:** €3K pentest (after major feature releases)
   - **Scope:** Web app, API, server infrastructure, backup security

**Phase 5: Ongoing Security (Month 6+)**
1. **Dependency updates:**
   - Automated: Dependabot weekly scans (GitHub security alerts)
   - Manual: Monthly review of critical CVEs, apply patches within 48 hours

2. **Backup testing:**
   - Monthly: Restore PostgreSQL from backup, verify data integrity
   - Disaster recovery drill: Simulate server failure, restore from backup in <4 hours

3. **Security reviews:**
   - Quarterly: Code review for new features (security-focused)
   - Annual: Full security audit (€5K-€8K, GDPR compliance check)

**Success Metrics:**
- Month 3 Week 2: TLS 1.3 enabled, bcrypt passwords, firewall active, rate limiting deployed
- Month 5: Zero critical/high vulnerabilities in penetration test
- Month 6: <1 hour MTTD (Mean Time to Detect) for security incidents
- Ongoing: 100% of users notified within 72 hours if breach occurs (GDPR Article 33)
- Annual: Pass GDPR security audit (no critical findings)

**Cost Impact:**
- Secrets manager: €50/month (AWS Secrets Manager for 10 secrets)
- Monitoring: €33/month (Sentry €26 + UptimeRobot €7)
- Penetration test: €3K-€5K one-time (pre-launch), €3K annual
- Security audit: €5K-€8K annual
- **Total Year 1:** €10K-€15K (setup) + €1K/month (ongoing)

**Residual Risk After Mitigation:** Likelihood 2 (Unlikely) → Risk Level **10** (Medium-High)  
**Rationale:** Strong technical measures per GDPR Documentation, but solo founder architecture limits separation of duties.

---

#### R5: COPPA Violation (Child Safety for K-12 Content) 🔴 HIGH
**Category:** Regulatory / Educational Use Classification  
**Reference:** [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md) Section 1.3 (Why Teacher Pipeline NOT HIGH-RISK)

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 1 (Very Unlikely) | Platform is B2C tool for educators; students are NOT platform users |
| **Impact** | 5 (Severe) | $46,000 per violation (FTC), platform ban in US K-12 schools |
| **Risk Level** | **5** | **LOW** (but catastrophic if triggered) |

**Risk Description:**
If platform collects personal information from children under 13 (in US) without verifiable parental consent, violates Children's Online Privacy Protection Act (COPPA).

**EU AI Act Classification Context (per compliance/eu_ai_act_compliance.md):**
- **System Type:** Creative content generation tool (LIMITED-RISK, Article 52)
- **NOT HIGH-RISK Educational AI System:** Platform does NOT "determine access to educational institutions" or "evaluate students" (Annex III, Point 3)
- **Critical Legal Distinction:** Teachers create content FOR students (viewing only), students do NOT create accounts or interact with platform
- **Analogous Systems:** PowerPoint, Canva, ChatGPT for education use (all LIMITED-RISK, not HIGH-RISK)

**COPPA Trigger Scenarios:**
- **Direct child registration:** Child (age <13) creates account independently (not through educator)
- **Platform collects child data:** "Teacher pipeline" logs student names, emails, or identifiable information
- **Third-party AI processing:** OpenAI/Cohere process child-generated prompts without COPPA compliance
- **Student accounts feature:** Future feature allowing students to create videos (would require parental consent)

**Potential Consequences:**
- **Legal:** $46,000 per child violation (FTC penalties under 15 U.S.C. § 6502)
- **Market Access:** Banned from US K-12 schools (30% of Teacher pipeline TAM)
- **Reputational:** Media scrutiny, parent advocacy groups (Common Sense Media complaints)
- **EU AI Act:** Potential reclassification to HIGH-RISK if platform directly interacts with students

**Mitigation Strategy:**

**Phase 1: Platform Design (Already Implemented per EU AI Act Doc)**
1. **B2C architecture (per Section 2.1):**
   - **Target users:** Individual educators and adult content creators (18+)
   - **Students are NOT users:** Teachers download videos, show to students offline
   - **No student accounts:** Platform does not collect student names, emails, or data
   - **Teacher retains control:** Educator reviews all content before classroom use (EU AI Act Section 1.3)

2. **Data minimization (per GDPR Doc Section 4.5):**
   - **No user IDs to AI services:** OpenAI, Cohere receive only content prompts (no child data even if teacher includes in prompt)
   - **Anonymous API requests:** AI providers cannot identify individual users or students

**Phase 2: Age Verification & Terms (Month 3)**
1. **Age gate on signup:**
   - Self-reported age: "I confirm I am 18 years or older"
   - Date of birth validation (reject if <18 years old)
   - IP-based location check (COPPA applies to US-based children only)

2. **Terms of Service (legal review €500):**
   - **Usage restriction:** "Platform is for educators and adult creators only. Children under 13 may NOT create accounts."
   - **Classroom use clause:** "Educators may show AI-generated videos to students, but students must NOT access the platform directly."
   - **COPPA compliance statement:** "We do not knowingly collect personal information from children under 13. If you believe a child has created an account, contact privacy@yourdomain.com."

3. **Teacher pipeline access control:**
   - Optional: Require school email domain verification (@school.edu, @k12.state.us)
   - Manual review: Educator provides school name, role (teacher/administrator)
   - Approval: 24-hour manual verification before Teacher pipeline access granted

**Phase 3: Educator Verification (Month 4 — If Targeting Schools)**
1. **School email verification:**
   - Database: Verify email domain against US K-12 school database (NCES, GreatSchools)
   - International: Accept @.edu.uk, @.edu.au, etc. (country-specific education domains)
   - Fallback: Manual verification (educator uploads school ID, teaching certificate)

2. **Class Code system (future feature):**
   - Teacher generates class code (e.g., MATH101-2026)
   - Students use code to access shared videos (view-only, no account required)
   - No student data collected (anonymous viewing, no tracking)

3. **FERPA compliance (US schools):**
   - Data Processing Addendum (DPA) with schools (classify platform as "School Official" under 20 U.S.C. § 1232g)
   - **Rationale:** Platform processes student data on behalf of school (but currently NO student data collected)
   - Template: Use Student Data Privacy Consortium (SDPC) DPA template

**Phase 4: Third-Party AI Compliance (Month 5)**
1. **OpenAI COPPA compliance:**
   - OpenAI policy: API data NOT used for training (no child data retention beyond 30 days)
   - OpenAI does NOT target children (B2B API service, not consumer product)
   - **Limitation:** OpenAI NOT COPPA-certified (no "Safe Harbor" status)

2. **Cohere COPPA compliance:**
   - Review Cohere Privacy Policy for child data handling
   - Confirm 30-day retention policy applies to API data

3. **Alternative (if COPPA certification required):**
   - Consider COPPA-certified AI providers (e.g., AWS Bedrock with COPPA commitments)
   - Cost: Typically 20-50% higher than standard APIs

**Phase 5: Future Student Accounts Feature (NOT in POC/Pilot)**
1. **Parental consent workflow (if implemented):**
   - Email verification: Parent receives email, clicks consent link
   - Age verification: Parent uploads ID or uses age verification service (Yoti, Jumio)
   - Consent scope: Specify data collection (name, email, usage logs), retention (180 days), sharing (with teacher only)

2. **COPPA-compliant data minimization:**
   - Collect ONLY: Student first name (no last name), age, class code
   - Do NOT collect: Email, address, phone, photos, geolocation
   - Retention: Delete student data 30 days after class ends

**Phase 6: Monitoring & Incident Response (Ongoing)**
1. **Age verification spot checks:**
   - Monthly: Review 10% of new accounts (flag suspicious young-sounding names, .edu emails from students)
   - If child detected: Immediate account suspension, email parent/guardian, delete all data within 24 hours

2. **Incident response (COPPA violation detected):**
   - Containment: Delete child account within 24 hours
   - Notification: Email parent/guardian (if contact info available), notify FTC if >10 violations
   - Remediation: Update age verification process, add stricter checks

**Success Metrics:**
- Month 3: Age gate deployed, Terms of Service updated (COPPA compliance clause)
- Month 4: 100% of Teacher pipeline users verified as educators (school email or manual review)
- Month 12: Zero direct child accounts (<13 years) created
- Ongoing: Zero COPPA complaints to FTC
- Future: DPA signed with all school/district customers (if B2B pivot)

**Cost Impact:**
- Email domain verification: €0 (open-source school domain database)
- Manual educator review: 10 hours/month × €20/hour = €200/month (if 100+ educator signups)
- Parental consent service (if student accounts): €500-€2,000/month (Yoti, Jumio pricing)

**Residual Risk After Mitigation:** Likelihood 1 (Very Unlikely) → Risk Level **5** (Low)  
**Rationale:** EU AI Act classification confirms platform is NOT educational decision-making system; students are passive viewers, not platform users.

---

### TECHNICAL RISKS

#### R3: Image Generation Quality Issues (Hallucinations, Wrong Proportions) 🔴 HIGH
**Category:** Technical

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | Pollinations.ai Flux-dev in POC has quality inconsistencies, Stability AI migration pending |
| **Impact** | 4 (Major) | User dissatisfaction, 30-40% of videos rejected, high support burden, churn |
| **Risk Level** | **16** | **HIGH** |

**Risk Description:**
AI-generated images suffer from:
- **Anatomical errors:** Wrong number of fingers, distorted faces, impossible body proportions
- **Scene composition issues:** Objects in wrong positions, floating elements, scale mismatches
- **Style inconsistencies:** Mix of art styles in single video (photorealistic + cartoon)
- **Prompt misinterpretation:** LLM generates image prompts that don't match script intent

**User Impact Examples:**
- **Science video:** Diagram of human heart with 5 chambers instead of 4
- **History video:** Medieval knight with modern rifle
- **Math lesson:** Geometric shapes with incorrect angles

**Current Quality Metrics (POC):**
- **Acceptable quality:** 60-70% of images usable without regeneration
- **Minor issues:** 20-30% need 1-2 regenerations
- **Major failures:** 10% require manual prompt editing or scene skip

**Potential Consequences:**
- **User friction:** 40% of users abandon workflow after 3+ failed image generations
- **Support costs:** 2 hours/week manual image review (€20/hour × 100 users = €2K/month)
- **Reputation:** Negative reviews ("AI generates weird-looking characters")
- **Revenue:** 25% churn due to quality issues → €15K MRR loss by Month 12

**Mitigation Strategy:**

**Phase 1: Immediate Quality Gates (Month 3)**
1. **Image validation pipeline:**
   - Add NSFW filter (Stability AI API moderation endpoint, $0.003/image)
   - Implement aspect ratio checks (reject images not 16:9 or 1:1)
   - Add resolution validation (minimum 1024×576 for video frames)

2. **User feedback loop:**
   - Add "Regenerate with changes" button (suggest prompt improvements)
   - Implement 5-star quality rating (track which prompts fail)
   - A/B test prompt templates (identify high-success patterns)

**Phase 2: Prompt Engineering (Month 4)**
1. **Enhanced prompt templates:**
   - Add negative prompts: "deformed, mutated, disfigured, wrong anatomy, extra limbs"
   - Include style anchors: "photorealistic, 8k, professional photography" for consistency
   - Use entity descriptions: "5-year-old girl with brown curly hair, consistent appearance"

2. **LLM prompt refinement:**
   - Fine-tune GPT-4o-mini on 100 high-quality script → image prompt pairs
   - Add prompt validation step (check for anatomical keywords, style conflicts)
   - Implement "prompt review" stage (user approves prompts before generation)

**Phase 3: Model Migration (Month 5-6)**
1. **Stability AI SDXL 1.0 integration:**
   - Migrate from Pollinations.ai (free) → Stability AI ($0.004/image)
   - Enable ControlNet (preserve character pose/composition across scenes)
   - Use Stable Diffusion Inpainting (fix anatomical errors in post-processing)

2. **Multi-model strategy:**
   - Primary: Stability AI SDXL (quality)
   - Fallback: Pollinations.ai Flux (speed/cost)
   - User choice: "Quality mode" vs "Fast mode"

**Phase 4: Advanced QA (Month 7+)**
1. **Automated quality scoring:**
   - Train image quality classifier (acceptable/regenerate/reject)
   - Auto-regenerate images scoring <70% quality
   - Flag anatomical errors with CLIP model (detect "extra fingers", "wrong proportions")

2. **Human-in-the-loop:**
   - Hire part-time QA reviewer (€500/month, 10 hours/week)
   - Review flagged images (30% of total)
   - Build golden dataset (500 high-quality examples)

**Success Metrics:**
- **Month 3:** 75% images usable without regeneration (up from 60-70%)
- **Month 6:** 85% images acceptable quality (post Stability AI migration)
- **Month 9:** 90% user satisfaction with image quality (survey rating >4/5)
- **Month 12:** <5% support tickets related to image quality

**Cost Impact:**
- Stability AI migration: +$0.004/image × 10 images/video = +$0.04/video
- QA reviewer: €500/month
- **Total:** €500/month + $0.04/video (~€600/month at 1,000 videos/month)

**Residual Risk After Mitigation:** Likelihood 3 → Risk Level 12 (Medium-High)

---

#### R4: API Cost Overruns (Exceeding ROI Budget) 🔴 HIGH
**Category:** Technical/Financial

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | User behavior unpredictable, no cost caps, regeneration loops |
| **Impact** | 4 (Major) | ROI model assumes $0.023-0.027/video, 50% overrun = break-even delayed 6 months |
| **Risk Level** | **16** | **HIGH** |

**Risk Description:**
AI API costs exceed ROI budget due to:
- **Regeneration loops:** Users regenerate images 5-10x to get desired quality
- **Long scripts:** Users create 20-minute videos (100+ images) vs. expected 5-minute average
- **Fact-checking overuse:** Teacher pipeline checks 50 claims/video vs. expected 20
- **TTS usage:** Users regenerate audio multiple times for pronunciation/pacing

**Current Cost Model (ROI Analysis):**
| **Component** | **Expected Cost/Video** | **Risk Scenario Cost** |
|---------------|-------------------------|------------------------|
| Script (GPT-4o-mini) | $0.001 | $0.003 (3x longer scripts) |
| Images (10 @ $0.004) | $0.040 | $0.120 (3x regenerations) |
| Fact-check (20 claims) | $0.100 | $0.250 (50 claims) |
| TTS (500 words) | $0.008 | $0.024 (3x regenerations) |
| **TOTAL** | **$0.149** | **$0.397** (+167%) |

**Impact on ROI:**
- **Break-even:** Month 13 → Month 19 (+6 months delay)
- **Profit margin:** 67.9% → 45% by Month 36
- **Cash flow crisis:** Month 6-12 burn rate doubles (€8K → €16K/month)

**Potential Consequences:**
- **Financial:** Run out of runway before profitability, need emergency fundraising
- **Product:** Forced to reduce free tier, increase prices (user backlash)
- **Competitive:** Can't compete with funded competitors (Synthesia, Pictory)

**Mitigation Strategy:**

**Phase 1: Cost Monitoring & Alerts (Month 3)**
1. **Real-time cost tracking:**
   - Add `cost_breakdown` field to database (track per-video costs)
   - Implement cost dashboard (Grafana + Prometheus, €0 self-hosted)
   - Set alerts: Email if daily costs >€200 (€6K/month threshold)

2. **User cost limits:**
   - Free tier: Max 3 videos/month, 5-minute limit, max 2 regenerations per image
   - Paid tier: Fair use policy (50 videos/month, email warning at 40)
   - Enterprise: Custom limits negotiated

**Phase 2: Cost Optimization (Month 4)**
1. **Prompt caching (OpenAI):**
   - Cache system prompts (entity extraction templates, script structure)
   - Save ~50% on repeated prompts (OpenAI prompt caching $0.075 vs $0.150/1M tokens)

2. **Image generation optimization:**
   - Batch image generation requests (3-5 images per API call, reduce overhead)
   - Cache common backgrounds (classroom, space, forest → reuse across videos)
   - Implement "low-cost mode" (512×512 images, upscale with MoviePy)

3. **Fact-checking optimization:**
   - Pre-filter claims (skip obvious facts: "The sky is blue", "1+1=2")
   - Batch claims (check 5 claims per API call vs. 1 at a time)
   - Cache fact-check results (30-day TTL for common claims)

**Phase 3: Tariff Plan Alignment (Month 5)**
1. **Usage-based pricing:**
   - **Current:** €15/month unlimited → **New:** €15/month for 20 videos + €1/additional video
   - **Reasoning:** Align revenue with costs (20 videos × €0.15 cost = €3 → €15 revenue covers costs + margin)

2. **Credits system:**
   - User buys credits (100 credits = €10, never expire per business model)
   - Video costs credits: 5-min video = 10 credits, 10-min = 20 credits, 20-min = 40 credits
   - Regenerations cost extra: +2 credits per image regeneration

3. **Upsell premium features:**
   - "Quality mode" (Stability AI SDXL): +5 credits/video (+€0.50)
   - "Fast fact-check" (parallel processing): +10 credits/video

**Phase 4: Technical Optimization (Month 6+)**
1. **Model selection:**
   - Replace GPT-4o-mini → GPT-3.5-turbo for simple tasks (2x cheaper)
   - Test open-source models (Llama 3.1 self-hosted for entity extraction, €40/month VPS)

2. **Response caching:**
   - Cache LLM responses (same script → same output, 24-hour TTL)
   - Deduplicate API calls (if user regenerates video with no changes, return cached result)

**Success Metrics:**
- **Month 3:** Real-time cost dashboard deployed, <5% costs exceed budget
- **Month 6:** Average cost/video ≤ €0.18 (20% buffer vs. €0.15 target)
- **Month 9:** 90% of users stay within fair use limits (no manual intervention)
- **Month 12:** CAC payback period ≤ 4 months (per ROI model)

**Residual Risk After Mitigation:** Likelihood 2 → Risk Level 8 (Medium-Low)

---

#### R6: Character Consistency Failure (<95% Target) 🟠 MEDIUM-HIGH
**Category:** Technical

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | POC achieves 85-90%, Stability AI migration may improve, but 95% is ambitious |
| **Impact** | 3 (Moderate) | Core value proposition, but users tolerate 90% consistency (20% churn risk) |
| **Risk Level** | **9** | **MEDIUM-LOW** |

**Risk Description:**
Platform's #1 selling point is "95% character consistency" (vs. industry 85-90%). If this fails:
- **Marketing:** Can't differentiate from competitors (Synthesia, Pictory, Runway)
- **User trust:** "They overpromised, underdelivered"
- **Revenue:** 20% of users churn due to inconsistent characters

**Current Status (POC):**
- **Achievement:** 85-90% consistency (informal testing on 45 demo videos)
- **Method:** GPT-4o-mini extracts entities → detailed visual prompts → Pollinations.ai Flux-dev
- **Failures:** Character hair color changes, age varies, clothing inconsistent

**Root Causes:**
1. **Prompt drift:** Successive images interpret "5-year-old girl" differently
2. **Model limitations:** Flux-dev doesn't support seed locking or LoRA fine-tuning
3. **Ambiguous descriptions:** "Brown hair" → light brown vs. dark brown vs. auburn

**Mitigation Strategy:**

**Phase 1: Prompt Refinement (Month 3)**
1. **Entity cards with reference images:**
   - Generate 1 "character sheet" at video start (3 angles: front, side, profile)
   - Include in all subsequent prompts: "Match appearance from reference image [URL]"
   - Store entity embeddings (CLIP vectors for visual similarity checks)

2. **Detailed visual tags:**
   - Expand entity descriptions: "Caucasian, 5-year-old girl, shoulder-length wavy brown hair (hex #8B4513), blue eyes, freckles, wearing red t-shirt and jeans"
   - Add negative prompts: "different hair color, different age, different clothing"

**Phase 2: Model Upgrade (Month 5)**
1. **Stability AI SDXL with ControlNet:**
   - Use reference images to guide generation (preserve pose, composition)
   - Enable seed locking (same seed = consistent character features)
   - Test Stable Diffusion LoRA fine-tuning (train on character sheet → 99% consistency)

2. **Fallback strategy:**
   - If consistency <90% on character sheet generation, allow user to upload reference photo
   - Use img2img mode (transform user photo → cartoon/3D style while preserving features)

**Phase 3: Automated QA (Month 7)**
1. **Consistency scoring:**
   - Compare each image to character sheet using CLIP similarity (cosine distance)
   - Threshold: >0.85 similarity = consistent, <0.85 = regenerate
   - Auto-flag videos with <90% consistency for manual review

2. **User feedback:**
   - "Character inconsistency detected" warning after video generation
   - Option to regenerate flagged scenes
   - Track user-reported consistency issues

**Success Metrics:**
- **Month 3:** 90% consistency (up from 85-90%)
- **Month 6:** 93% consistency (Stability AI + ControlNet)
- **Month 9:** 95% consistency target achieved
- <10% user complaints about character consistency

**Residual Risk After Mitigation:** Likelihood 2 → Risk Level 6 (Medium-Low)

---

#### R7: LLM Text Hallucinations (Factual Errors in Scripts) 🟡 MEDIUM-LOW
**Category:** Technical/Ethical

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 2 (Unlikely) | GPT-4o-mini has low hallucination rate, Teacher pipeline has fact-checking |
| **Impact** | 2 (Minor) | Caught by Facticity API, user reviews script before approval |
| **Risk Level** | **4** | **LOW** |

**Risk Description:**
GPT-4o-mini generates scripts with factual errors:
- **Science:** "Water boils at 90°C" (incorrect, should be 100°C at sea level)
- **History:** "Napoleon won the Battle of Waterloo" (he lost)
- **Math:** Incorrect formulas or calculation steps

**Current Mitigation (POC):**
- **Teacher pipeline:** Facticity API checks all claims (catches 90% of errors)
- **User review:** Step-by-step approval workflow (user reads script before generating images)
- **RAG system:** Pinecone retrieves best practices from knowledge base

**Potential Consequences:**
- **YouTube pipeline:** Misinformation spreads (low stakes, entertainment content)
- **Teacher pipeline:** Students learn incorrect facts → teacher complaints, school bans
- **Legal:** Liability if educational content causes harm (unlikely but possible)

**Mitigation Strategy:**
1. **Month 3:** Add disclaimer in Teacher videos: "Fact-checked by AI, but please verify critical information"
2. **Month 4:** Implement confidence scores (Facticity API returns 0-100% confidence, flag <70% claims)
3. **Month 5:** Add "Report error" button in videos (user feedback loop)
4. **Month 6:** Monthly audit of top 10 most-generated topics (manual fact-check by subject expert)

**Success Metrics:**
- <1% of Teacher videos contain factual errors (post fact-checking)
- Zero complaints from schools about misinformation
- 95% of claims rated "high confidence" (>80%) by Facticity API

**Residual Risk After Mitigation:** Likelihood 1 → Risk Level 2 (Low)

---

#### R12: API Integration Failures (OpenAI, Cohere, Facticity, Stability AI) 🟠 MEDIUM-HIGH
**Category:** Technical/Operational

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | 4 external APIs, each with 99.9% uptime = 99.6% combined uptime (35 hours downtime/year) |
| **Impact** | 4 (Major) | Video generation fails, user frustration, support burden |
| **Risk Level** | **12** | **MEDIUM-HIGH** |

**Risk Description:**
Third-party API outages or errors block video generation:
- **OpenAI downtime:** No script generation, no TTS (2-3 incidents/year, 1-4 hours each)
- **Cohere downtime:** No embeddings, no segmentation (rare, <1 incident/year)
- **Facticity API downtime:** Teacher pipeline blocked (unknown SLA, startup API)
- **Stability AI rate limits:** Image generation throttled (429 errors if exceed 100 images/minute)
- **Network issues:** Hetzner VPS loses connectivity (1-2 incidents/year, <1 hour)

**Potential Consequences:**
- **User experience:** "Video generation failed, try again later" (50% abandon workflow)
- **Support:** 10-20 tickets/day during outages (€200-€400 support costs)
- **Revenue:** 5% churn if outages >4 hours/month
- **Automation:** LangGraph workflow stuck in retry loop (database bloat, memory leaks)

**Mitigation Strategy:**

**Phase 1: Resilience (Month 3)**
1. **Retry logic with exponential backoff:**
   - Already implemented with `tenacity` library (2-10s delays, 3 attempts)
   - Add circuit breaker (after 5 consecutive failures, stop retrying for 5 minutes)
   - Implement request timeout (30s max per API call, prevent hanging)

2. **Graceful degradation:**
   - If OpenAI TTS fails → use open-source TTS (Coqui TTS self-hosted, lower quality)
   - If Facticity API fails → skip fact-checking, add disclaimer ("Not fact-checked")
   - If Stability AI fails → fallback to Pollinations.ai (free tier)

3. **User notifications:**
   - Real-time status updates: "OpenAI is slow, your video may take 5 extra minutes"
   - Email when video ready (async completion, don't block user)

**Phase 2: Monitoring (Month 4)**
1. **API health dashboard:**
   - Track API latency, error rates, uptime (Grafana dashboard)
   - Alert if error rate >5% or latency >3 seconds
   - Public status page (users can check if platform is down)

2. **Automated incident response:**
   - If API error rate >10% for 5 minutes → enable fallback mode
   - If multiple APIs failing → pause new video generations (prevent wasted credits)
   - Email admin on critical failures

**Phase 3: Multi-Provider Strategy (Month 6+)**
1. **LLM redundancy:**
   - Primary: OpenAI GPT-4o-mini → Fallback: Anthropic Claude 3 Haiku (similar cost)
   - Test weekly failover (ensure compatibility)

2. **Image generation redundancy:**
   - Primary: Stability AI → Fallback 1: Pollinations.ai → Fallback 2: Replicate.com SDXL

3. **TTS redundancy:**
   - Primary: OpenAI TTS-1 → Fallback: ElevenLabs (higher quality but 3x cost)

**Success Metrics:**
- **Month 3:** 99.5% video generation success rate (failed attempts <0.5%)
- **Month 6:** <5 minutes average downtime per API failure (fast failover)
- **Month 9:** 99.9% platform uptime (excluding scheduled maintenance)
- <2% support tickets related to "generation failed" errors

**Cost Impact:**
- Monitoring tools: €50/month (Sentry + Grafana Cloud)
- Multi-provider testing: €100/month (test fallback APIs)

**Residual Risk After Mitigation:** Likelihood 2 → Risk Level 8 (Medium-Low)

---

#### R13: Video Pipeline Crashes (MoviePy, FFmpeg Errors) 🟠 MEDIUM-HIGH
**Category:** Technical

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | MoviePy 1.0.3 has memory leaks with long videos, FFmpeg encoding errors |
| **Impact** | 3 (Moderate) | Video generation fails at final step (user loses 5-10 minutes, frustration) |
| **Risk Level** | **9** | **MEDIUM-LOW** |

**Risk Description:**
Video assembly fails after images and audio are generated:
- **Memory errors:** MoviePy crashes on 20-minute videos (>1GB RAM usage)
- **Codec issues:** FFmpeg encoding errors (unsupported audio format, framerate mismatch)
- **File corruption:** Mutagen fails to extract audio metadata → silent video
- **Disk space:** Hetzner VPS runs out of storage (100+ videos × 50MB = 5GB)

**Impact:**
- User loses 5-10 minutes waiting for generation → high frustration
- Support ticket: "My video didn't generate, but I was charged"
- Need to refund credits or regenerate (€0.15 cost + €5 support time)

**Mitigation Strategy:**

**Phase 1: Error Handling (Month 3)**
1. **Pre-flight checks:**
   - Validate image files exist, correct resolution (1024×576)
   - Validate audio file format (MP3, AAC), duration matches script
   - Check available disk space (5GB minimum free)

2. **Graceful failure:**
   - If MoviePy crashes → save partial video (images without audio)
   - Email user: "Video generation failed, we're investigating" + 100% credit refund
   - Log full error trace (Sentry for debugging)

3. **Resource limits:**
   - Kill video generation jobs after 10 minutes (prevent runaway processes)
   - Limit concurrent video generations to 3 (prevent memory exhaustion)

**Phase 2: Optimization (Month 4)**
1. **Memory management:**
   - Use MoviePy `write_videofile()` with `threads=2` (reduce memory usage)
   - Clear image cache after each scene (prevent memory leaks)
   - Compress images before assembly (reduce RAM footprint)

2. **Disk cleanup:**
   - Auto-delete temporary files after video generation (images, audio)
   - Implement 30-day retention policy (delete old videos, free space)
   - Set up disk usage alerts (email at 80% full)

**Phase 3: Infrastructure Upgrade (Month 6)**
1. **VPS scaling:**
   - Upgrade Hetzner VPS: €40/month (4GB RAM) → €80/month (8GB RAM)
   - Add external storage (Hetzner Storage Box, 1TB for €3.81/month)

2. **Alternative video encoder:**
   - Test FFmpeg-python (lower-level API, more control)
   - Consider cloud video processing (AWS MediaConvert, pay-per-use)

**Success Metrics:**
- <1% video generation failures due to pipeline crashes
- Average video generation time: 3-5 minutes (regardless of length)
- Zero disk space incidents

**Cost Impact:**
- VPS upgrade: +€40/month (Month 6+)
- External storage: +€3.81/month

**Residual Risk After Mitigation:** Likelihood 2 → Risk Level 6 (Medium-Low)

---

### ETHICAL RISKS

#### R11: Platform Misuse (Deepfakes, Misinformation Campaigns) 🟡 MEDIUM-LOW
**Category:** Ethical/Reputational

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 2 (Unlikely) | Platform generates cartoon/3D characters (not photorealistic humans), limited reach |
| **Impact** | 3 (Moderate) | Media backlash, regulatory scrutiny, pressure to shut down |
| **Risk Level** | **6** | **MEDIUM-LOW** |

**Risk Description:**
Bad actors use platform to create:
- **Political deepfakes:** Fake videos of public figures (low risk with cartoon style, but possible)
- **Misinformation campaigns:** COVID-19 conspiracy theories, election fraud claims
- **Hate speech:** Racist, sexist, or violent content
- **Impersonation:** Fake educational videos claiming to be from legitimate institutions

**Current Safeguards (POC):**
- OpenAI content policy enforcement (rejects violent/sexual prompts)
- Manual review for Teacher pipeline (educators verified)
- YouTube pipeline publicly accessible (no platform moderation)

**Potential Consequences:**
- **Regulatory:** EU AI Act "high-risk AI system" classification → compliance burden
- **Reputational:** Media article: "AI video tool used to spread misinformation"
- **Legal:** Lawsuits from individuals depicted in fake videos
- **Platform bans:** Apple/Google remove app, payment processors block account

**Mitigation Strategy:**

**Phase 1: Content Moderation (Month 3)**
1. **Automated filters:**
   - OpenAI Moderation API on all script inputs (reject hate speech, violence, sexual content)
   - Keyword blacklist (political figures, conspiracy theories, slurs)
   - NSFW image filter on generated content

2. **Terms of Service:**
   - Prohibited uses: deepfakes, impersonation, misinformation, hate speech
   - Right to terminate accounts without refund
   - DMCA takedown process for copyright violations

**Phase 2: Human Review (Month 5)**
1. **Flagged content review:**
   - Users can report videos (abuse button)
   - Manual review within 24 hours (part-time moderator, €500/month)
   - Strike system: 1st offense = warning, 2nd = suspension, 3rd = ban

2. **Proactive monitoring:**
   - Review 10% of public YouTube videos (random sampling)
   - Flag high-risk topics (politics, health, religion)

**Phase 3: Technical Controls (Month 7+)**
1. **Watermarking:**
   - Add invisible watermark to all videos (C2PA standard, provenance metadata)
   - Disclose AI-generated content (YouTube description: "Created with AI")

2. **Rate limiting:**
   - Suspicious accounts (new, high volume) → manual review before publishing
   - Limit video distribution (max 100 views/day for new accounts)

**Success Metrics:**
- <1% of content flagged for moderation
- Zero incidents of platform used in major misinformation campaigns
- 100% of flagged content reviewed within 24 hours

**Cost Impact:**
- Moderator: €500/month
- Moderation API: $0.0002/video (negligible)

**Residual Risk After Mitigation:** Likelihood 1 → Risk Level 3 (Low)

---

### OPERATIONAL RISKS

#### R8: Low User Retention (High Churn After Free Trial) 🔴 HIGH
**Category:** Operational/Product-Market Fit

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | B2C SaaS average churn 5-7%/month, AI tools have novelty factor wear-off |
| **Impact** | 3 (Moderate) | ROI assumes 5% churn, 10% churn → break-even delayed 12 months |
| **Risk Level** | **12** | **MEDIUM-HIGH** |

**Risk Description:**
Users sign up, create 1-2 videos, then never return:
- **Novelty wear-off:** "Cool tool, but I don't need it regularly"
- **Quality issues:** "Images look weird, character inconsistency frustrating"
- **Workflow friction:** "6-step approval process takes too long"
- **Value mismatch:** "Not worth €15/month for 3 videos"

**Current Assumptions (ROI Model):**
- **Target churn:** 5%/month (industry standard)
- **Cohort retention:** 60% retained after 12 months
- **Break-even:** Month 13

**Risk Scenario (10% Churn):**
- **Month 12 users:** 1,000 → 500 (vs. 600 at 5% churn)
- **MRR:** €7,500 → €6,000 (20% revenue loss)
- **Break-even:** Month 13 → Month 25

**Root Causes:**
1. **Low engagement:** Users don't have weekly video needs
2. **Poor onboarding:** Users don't understand workflow, give up
3. **Quality dissatisfaction:** 30% of users unhappy with image quality
4. **Price sensitivity:** €15/month perceived as expensive for casual use

**Mitigation Strategy:**

**Phase 1: Engagement & Activation (Month 3)**
1. **Onboarding optimization:**
   - Interactive tutorial (guided first video creation, 3 minutes)
   - Video templates (pre-made scripts: "Solar System", "Photosynthesis", "American Revolution")
   - Quick wins (1-minute demo video → email within 5 minutes)

2. **Weekly engagement triggers:**
   - Email: "Your students asked 5 questions this week → create explainer video"
   - Content calendar (suggest topics: "Monday = Science, Wednesday = History")
   - Gamification (badges: "Created 10 videos", "100 student views")

**Phase 2: Value Optimization (Month 4)**
1. **Usage analytics:**
   - Track which users created 0 videos (re-engage with email: "Need help?")
   - Identify power users (>10 videos/month → upsell to annual plan)
   - A/B test pricing: €15/month vs. €12/month vs. credits model

2. **Exit surveys:**
   - Ask churned users: "Why did you cancel?" (quality, price, lack of use, workflow)
   - Offer discounts (50% off for 3 months if reactivating)

**Phase 3: Retention Campaigns (Month 5+)**
1. **Win-back campaigns:**
   - Email churned users: "We fixed image quality, come back!"
   - Offer 1 free video (re-engagement incentive)

2. **Community building:**
   - Private Discord/Slack for educators (share tips, best practices)
   - Monthly showcase ("Video of the Month", €50 prize)

3. **Annual plans:**
   - Offer €150/year (save €30, 17% discount) → improves retention
   - Prepaid credits (€100 for 120 credits, 20% bonus)

**Success Metrics:**
- **Month 3:** 70% of new users create ≥1 video within 7 days (activation)
- **Month 6:** 5% monthly churn (meet ROI target)
- **Month 9:** 40% of users on annual plans (lower churn)
- **Month 12:** Net Revenue Retention (NRR) 95% (churn offset by upsells)

**Cost Impact:**
- Email automation: €50/month (Mailchimp)
- Discounts/promotions: €500/month (10% of MRR)

**Residual Risk After Mitigation:** Likelihood 3 → Risk Level 9 (Medium-Low)

---

#### R9: Poor Onboarding Experience (Users Abandon Before First Video) 🟡 MEDIUM-LOW
**Category:** Operational/UX

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | 6-step approval workflow complex, no hand-holding in POC |
| **Impact** | 2 (Minor) | 30% of signups never create video, but salvageable with email campaigns |
| **Risk Level** | **6** | **MEDIUM-LOW** |

**Risk Description:**
Users sign up, see complex workflow (6 approval steps), and abandon:
- **Cognitive overload:** "Too many decisions, I just want a video"
- **Unclear value:** "What am I approving? Why does this matter?"
- **Technical barriers:** "What's a 'pipeline'? YouTube vs. Teacher confusing"

**Current Onboarding (POC):**
- Landing page → Sign up → Dashboard → "Create Project" → Manual workflow

**Mitigation Strategy:**
1. **Month 3:**
   - Add interactive tutorial (overlay tooltips, 3-minute guided tour)
   - Pre-fill example (astronaut story pre-loaded, user clicks "Generate")
   - Progress bar (show "Step 2 of 6" to reduce anxiety)

2. **Month 4:**
   - Video walkthrough (2-minute explainer on homepage)
   - Live chat support (Intercom, €74/month, answer questions in real-time)

3. **Month 5:**
   - A/B test "Express mode" (skip approvals, generate video in 1 click)
   - Track completion rate (% who complete first video)

**Success Metrics:**
- 70% of signups create ≥1 video within 7 days
- <10% abandon during workflow (dropout rate)

**Residual Risk:** Likelihood 2 → Risk Level 4 (Low)

---

#### R10: Resistance to Step-by-Step Approval Workflow 🟡 MEDIUM-LOW
**Category:** Operational/Product

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | Power users want speed, 6 approval steps = friction |
| **Impact** | 2 (Minor) | Mitigated by "Express mode" option, doesn't block core value |
| **Risk Level** | **6** | **MEDIUM-LOW** |

**Risk Description:**
Users complain: "Why do I have to approve every step? Competitors let me generate in 1 click."

**Mitigation:**
1. **Month 4:** Add "Express mode" toggle (skip approvals, auto-generate)
2. **Month 5:** Remember user preference (if they always click "Approve", default to Express)
3. Track adoption: If <20% use step-by-step, consider removing

**Success Metrics:**
- 50% of users use Express mode
- <5% churn due to workflow complaints

**Residual Risk:** Likelihood 2 → Risk Level 4 (Low)

---

#### R14: Customer Acquisition Cost (CAC) Exceeds ROI Targets 🟡 MEDIUM-LOW
**Category:** Operational/Marketing

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | Organic growth slow, may need paid ads (€50 CAC vs. €30 target) |
| **Impact** | 2 (Minor) | Payback period extends from 2 months to 3-4 months (still viable) |
| **Risk Level** | **6** | **MEDIUM-LOW** |

**Risk Description:**
ROI model assumes €30 CAC (organic referrals, SEO). If need paid ads:
- **Google Ads:** €2-€5 CPC × 10 clicks/conversion = €20-€50 CAC
- **Facebook Ads:** €30-€100 CAC (education niche competitive)
- **Influencer marketing:** €500/post ÷ 10 conversions = €50 CAC

**Mitigation:**
1. **Month 3:** Focus on organic channels:
   - Reddit (r/Teachers), LinkedIn (educator groups)
   - SEO (blog posts: "How to create educational videos with AI")
   - Referral program (give 1 month free for each referral)

2. **Month 6:** Test paid channels (small budget):
   - €500/month Google Ads budget
   - Track CAC, pause if >€50

3. **Month 9:** Product-led growth:
   - Free tier with watermark (viral distribution)
   - Public video gallery (SEO + social proof)

**Success Metrics:**
- CAC ≤ €30 for 60% of users
- Payback period ≤ 4 months

**Residual Risk:** Likelihood 2 → Risk Level 4 (Low)

---

#### R15: Tariff Plan Misalignment (User Value vs. ROI Metrics) 🟠 MEDIUM-HIGH
**Category:** Operational/Product

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 3 (Possible) | Balancing user expectations (unlimited videos) vs. cost control (API usage) |
| **Impact** | 3 (Moderate) | Under-pricing → losses, over-pricing → churn |
| **Risk Level** | **9** | **MEDIUM-LOW** |

**Risk Description:**
Current tariff plan from user feedback:
- **User expectation:** €15/month → 20-30 videos
- **Your concern:** Need to cap usage to prevent API cost overruns
- **ROI model:** Assumes €0.15 cost/video → €15 price supports 100 videos/month (but unsustainable for power users)

**Potential Issues:**
1. **User complaints:** "I hit my limit after 10 videos, this is a ripoff"
2. **Power users abuse:** 1 user generates 200 videos/month → €30 cost, €15 revenue (net loss)
3. **Competitor comparison:** Synthesia charges €30/month for 10 videos (€3/video), we charge €15/month for 20 videos (€0.75/video) → we're underpriced

**Mitigation Strategy:**

**Phase 1: Pricing Research (Month 3)**
1. **Competitor analysis:**
   - Synthesia: €30/month (10 videos) = €3/video
   - Pictory: €23/month (30 videos) = €0.77/video
   - Runway: €12/month (125 credits, ~15 videos) = €0.80/video
   - **Target:** €15/month for 20 videos = €0.75/video (competitive)

2. **User surveys:**
   - Ask pilot users: "How many videos do you create per month?" (avg 5-10)
   - "What's fair pricing?" (most say €10-€20/month for 10-20 videos)

**Phase 2: Tiered Pricing (Month 4)**
1. **Free tier:**
   - 3 videos/month
   - 5-minute max, watermark, YouTube pipeline only
   - **Goal:** Viral distribution, upsell to paid

2. **Starter tier (€15/month):**
   - 20 videos/month (aligns with user feedback)
   - 10-minute max, no watermark, both pipelines
   - **Cost:** 20 × €0.15 = €3 → €12 margin (80% gross margin)

3. **Pro tier (€49/month):**
   - 100 videos/month
   - 20-minute max, priority support
   - **Cost:** 100 × €0.20 = €20 → €29 margin (59% gross margin)

4. **Enterprise tier (€299/month):**
   - Unlimited videos, white-label, API access
   - **Reasoning:** 5-10 enterprise customers = €1,500-€3,000 MRR (covers 30% of costs)

**Phase 3: Usage Monitoring (Month 5)**
1. **Fair use policy:**
   - Starter: "Up to 20 videos/month, soft limit (no hard cap but email warning at 18)"
   - Pro: "Up to 100 videos/month, overage charged at €0.50/video"

2. **Credits system (alternative):**
   - Buy credits: 100 credits = €10 (never expire)
   - Video costs credits: 5-min = 10 credits, 10-min = 20 credits
   - **Advantage:** User controls spending, we avoid losses

**Phase 4: Dynamic Pricing (Month 9+)**
1. **Test annual plans:**
   - €150/year (save €30, 17% discount)
   - Prepaid credits: €100 for 120 credits (20% bonus)

2. **A/B test pricing:**
   - Group A: €15/month for 20 videos
   - Group B: €12/month for 15 videos
   - Measure: LTV, churn, satisfaction

**Success Metrics:**
- **Month 3:** Pricing validated with 50 pilot users (<10% complaints)
- **Month 6:** 80%+ users stay within tier limits
- **Month 9:** Gross margin ≥70% (target from ROI model)
- **Month 12:** <5% of users hit overage charges

**Cost Impact:**
- Minimal (pricing research €0, A/B testing built into MVP)

**Residual Risk After Mitigation:** Likelihood 2 → Risk Level 6 (Medium-Low)

---

#### R16: Unit Economics Collapse — Optimistic Scenario Unrealistic ⛔ CRITICAL
**Category:** Operational/Financial  
**Current Status:** Under Validation (Pilot Phase Will Test Assumptions)

| **Metric** | **Score** | **Rationale** |
|------------|-----------|---------------|
| **Likelihood** | 4 (Likely) | Optimistic scenario assumes best-case on ALL metrics simultaneously (CAC, churn, organic growth, pricing) |
| **Impact** | 5 (Severe) | If assumptions fail, break-even delays from Month 13 → Month 18-24, ROI drops from +67.9% → +15-25%, potential shutdown |
| **Risk Level** | **20** | **CRITICAL** |

**Risk Description:**

The **Optimistic Scenario** (+67.9% ROI at 36 months, Month 13 break-even) presented in ROI_Analysis.md depends on achieving **exceptional unit economics** across all metrics simultaneously:

| Metric | Optimistic Assumption | Realistic Estimate | Variance | Impact on LTV/ROI |
|--------|----------------------|-------------------|----------|------------------|
| **ARPU** | $29/month | $29/month | ✅ Same | Market-tested vs Katalist $19 |
| **CAC** | $55 | **$80** | +45% | Organic growth harder than assumed |
| **Churn** | 4%/month | **8%/month** | 2x higher | Industry norm for new SaaS |
| **API Cost** | $6/user | **$3.50/user** | ✅ Better | Music/voiceover optional, not default |
| **Organic Growth** | 4%/month | 2-3%/month | -25 to -50% | Viral loop unproven |

**Recalculated Unit Economics (Realistic Scenario):**

```
OPTIMISTIC (Current Assumptions):
- ARPU: $29
- API Cost: $6/user (includes voiceover + music mandatory)
- Contribution Margin: $23 ($29 - $6)
- Churn: 4%/month
- LTV: $23 / 0.04 = $575
- CAC: $55
- LTV/CAC: 10.5x (exceptional)
- CAC Payback: 2.4 months
- Break-Even: Month 13

REALISTIC (Validated Assumptions):
- ARPU: $29 (same)
- API Cost: $3.50/user (voiceover/music optional, 50% adoption)
  - Base cost: 10 scripts/month × $0.360 images = $3.60
  - Voiceover addon: $0.018 × 5 scripts = $0.09
  - Music addon: $0.010 × 5 scripts = $0.05
  - Total: $3.74 → conservatively $3.50
- Contribution Margin: $25.50 ($29 - $3.50)
- Churn: 8%/month (2x higher, SaaS industry norm for Year 1)
- LTV: $25.50 / 0.08 = $319 (vs $575 Optimistic, -44%)
- CAC: $80 (vs $55 Optimistic, +45%)
- LTV/CAC: 3.99x (vs 10.5x, -62% decline)
- CAC Payback: 3.1 months (vs 2.4, +29% slower)
- Break-Even: Month 18-22 (vs Month 13, +38-69% delay)
```

**Why Optimistic Assumptions Are Unlikely:**

**1. CAC $55 Requires Perfect Product-Led Growth:**
- **Assumption:** 60% of signups from organic (Product Hunt viral, referrals, SEO)
- **Reality Check:** Bootstrapped SaaS typically 70-80% paid acquisition in Year 1
- **Market data:** Similar B2C tools (Jasper, Copy.ai) report CAC $80-120 first year
- **Mitigation cost:** If organic growth <2%/month, need $600+/month paid ads → CAC rises to $80-100

**2. Churn 4% Is Best-In-Class, Takes 12-18 Months:**
- **Assumption:** Exceptional onboarding + habit formation from Day 1
- **Reality Check:** New SaaS products see 8-12% churn first 6 months, stabilizing to 5-7% by Month 12
- **Pilot validation needed:** Only 8-week pilot (50 users) won't prove long-term retention
- **Competitors:** Midjourney (~6% churn), Synthesia (~7%), Runway (~8%) — all mature products

**3. 4% Organic Growth Requires Viral Loop + Exceptional Product:**
- **Assumption:** Monthly viral coefficient ~1.15 (each user brings 0.15 new users/month)
- **Reality Check:** Viral loops take 6-12 months to optimize (referral programs, product improvements)
- **Without viral success:** Growth drops to 2-3%/month → Base Case scenario (11.4% ROI at 36 months)

**4. Kie.ai Dependency — GDPR Compliance Blocker:**

**CRITICAL FINDING (verified April 2, 2026):**
- **Kie.ai company:** NEXUSAI SERVICES LLC, Denver, Colorado, USA
- **Privacy Policy Section 10:** "Your information may be transferred to and stored in the **United States**"
- **GDPR Issue:** No Data Processing Agreement (DPA) mentioned, no Standard Contractual Clauses (SCCs)
- **Governing Law:** State of Colorado (not EU jurisdiction)

**Why This Breaks Production:**
- GDPR Article 28 **requires DPA** for any processor handling EU personal data
- Post-Schrems II (2020), USA transfers need SCCs + Transfer Impact Assessment (TIA)
- **Without DPA:** Cannot use kie.ai with EU users in production → legal exposure €20M fine
- **Kie.ai upside:** Email-only collection, GDPR rights mentioned (Section 7), deletion supported
- **Kie.ai downside:** Consent-based transfers insufficient, no DPA template visible

**Migration Risk:**
- If forced to switch from kie.ai Nano Banana ($0.020/img) to fal.ai ($0.039/img):
  - API cost doubles: $3.50 → $6.42/user
  - Margin drops: 87.9% → 77.9%
  - LTV drops: $319 → $275
  - LTV/CAC drops: 3.99x → 3.44x (marginal, <3x = unhealthy)

**Potential Consequences:**

**Scenario 1: CAC $80 + Churn 8% + No Kie.ai DPA (Full Realistic):**
- API cost rises to $6.42 (fal.ai migration)
- LTV = ($29 - $6.42) / 0.08 = $282
- LTV/CAC = $282 / $80 = **3.53x** (marginal)
- Break-even: **Month 20-24** (vs Month 13 Optimistic)
- ROI at 36 months: **+20-30%** (vs +67.9% Optimistic)

**Scenario 2: If Churn Rises to 10% (High User Abandonment):**
- LTV = $22.58 / 0.10 = $226
- LTV/CAC = $226 / $80 = **2.83x** (<3x threshold, unhealthy)
- **Pivot decision required:** Month 12 shutdown unless pricing increase to $39-49

**Scenario 3: If ARPU Must Drop to $23 (Competitive Pressure):**
- Contribution margin = $23 - $6.42 = $16.58
- LTV = $16.58 / 0.08 = $207
- LTV/CAC = $207 / $80 = **2.59x** (below healthy threshold)
- **Business not viable** at $23 ARPU with realistic CAC/churn

**Mitigation Strategy:**

**Phase 1: Pilot Validation (Weeks 1-8, May-June 2026) — TEST ALL ASSUMPTIONS**

**Critical Metrics to Validate:**
1. **Activation Rate (Target: 80%+):**
   - % of 50 pilot users who generate ≥1 video within 7 days
   - **If <60%:** Onboarding broken, churn will be >10%

2. **Weekly Retention (Target: 60%+):**
   - % of week-1 active users still active week-2, week-3, week-4
   - **If <40%:** Habit formation failing, churn 10%+ confirmed

3. **Average Usage (Target: 5-10 scripts/month):**
   - Actual user behavior: light (2-3 scripts) vs heavy (15+ scripts)
   - **If 30% heavy users:** API cost blows budget → need strict caps

4. **Pricing Sensitivity (Target: <10% complaints about $29 price):**
   - User survey: "Is $29/month fair for 10 scripts?"
   - **If >20% say "too expensive":** ARPU drops to $23-25

5. **CAC Reality Check (Target: Organic signups >40%):**
   - Track: How did pilot users hear about platform? (Reddit, Product Hunt, referral)
   - **If <20% organic:** Paid acquisition mandatory → CAC $80+ confirmed

**Phase 2: Kie.ai GDPR Resolution (Week 3-4, Before Pilot Launch) — LAUNCH BLOCKER**

**Option A: Sign DPA with Kie.ai (Preferred, $0 cost):**
1. Email support@kie.ai with DPA template from gdpr_documentation.md Appendix C
2. Request: GDPR Article 28 Data Processing Agreement + Standard Contractual Clauses
3. **If approved:** Zero cost, continue with $0.020/img pricing
4. **If rejected:** Fallback to Option B

**Option B: Migrate to fal.ai Nano Banana ($0.039/img, +95% cost):**
1. fal.ai has public DPA: https://fal.ai/legal/dpa
2. API migration: 2-3 days (similar API, endpoint swap)
3. **Cost impact:** $3.50 → $6.42 API cost/user, margin 87.9% → 77.9%
4. **ROI impact:** Break-even Month 18-22 (vs Month 13), still viable

**Option C: Build In-House Image API (Last Resort, €5K-€8K):**
1. Deploy Stability AI SDXL on Hetzner GPU VPS (€200/month)
2. Self-hosted API: ~$0.015/img (cheaper than kie.ai)
3. **Tradeoff:** 40 hours dev time + GPU management overhead

**Decision Tree:**
```
START: Contact kie.ai for DPA (Week 3)
  │
  ├─► DPA SIGNED → Keep $0.020/img → LTV $319, LTV/CAC 3.99x
  │
  ├─► DPA REJECTED → Migrate to fal.ai → LTV $275, LTV/CAC 3.44x
  │
  └─► IF both fail → Build in-house (Month 6+) → LTV $330, but €5K upfront

LAUNCH BLOCKER: Cannot proceed to Pilot without DPA resolution.
```

**Phase 3: Pricing Adjustment (Month 6, Post-Pilot) — IF LTV/CAC <4x**

**Conservative Pricing Tiers (If Realistic Scenario Confirmed):**
1. **Starter $15/month:**
   - 5 scripts/month (~90 images)
   - API cost: $1.75 → margin $13.25 (88.3%)
   - LTV = $13.25 / 0.08 = $166
   - LTV/CAC = $166 / $80 = 2.08x ❌ (too low, loss-leader tier)

2. **Pro $29/month (current proposal):**
   - 10 scripts/month (~180 images)
   - API cost: $3.50 → margin $25.50 (87.9%)
   - LTV = $25.50 / 0.08 = $319
   - LTV/CAC = $319 / $80 = 3.99x ✅ (marginal but acceptable)

3. **Premium $49/month (new tier if margin pressure):**
   - 20 scripts/month (~360 images), voiceover/music included
   - API cost: $7.00 → margin $42 (85.7%)
   - LTV = $42 / 0.08 = $525
   - LTV/CAC = $525 / $80 = 6.56x ✅ (healthy)

**Strategy:** If Pilot shows 30%+ users willing to pay $49 for premium features (voiceover, music, longer videos), shift to 3-tier model.

**Phase 4: Go/No-Go Decision Criteria (Week 8 Pilot Review)**

**PROCEED to Full Deployment IF:**
- ✅ NPS >40 (product-market fit signal)
- ✅ Weekly Retention >60% (habit formation validated)
- ✅ Activation >80% (onboarding works)
- ✅ LTV/CAC >3.5x (unit economics sustainable)
- ✅ Kie.ai DPA signed OR fal.ai migration complete

**PIVOT to Base Case (Conservative) IF:**
- ⚠️ Retention 40-60% → Churn 8-10% → Extend Pilot to Month 12
- ⚠️ LTV/CAC 3.0-3.5x → Reduce marketing spend 45% → 30%, slower growth

**SHUTDOWN IF:**
- ❌ NPS <20 (no product-market fit)
- ❌ Retention <40% (churn >10%)
- ❌ LTV/CAC <3x (unprofitable even with optimization)
- ❌ Kie.ai DPA rejected AND fal.ai too expensive ($0.039/img makes LTV/CAC 2.8x)

**Success Metrics:**
- **Week 8:** Pilot validates LTV ≥$300, CAC ≤$80, churn ≤8%
- **Month 12:** Actual break-even tracking toward Month 18-22 (not Month 13, adjusted expectation)
- **Month 24:** ROI >20% (vs 67.9% Optimistic, but still positive)
- **Month 36:** ROI 20-30% (Realistic Scenario) vs Base Case 11.4%

**Cost Impact:**
- **Pilot extension (if needed):** $500/month × 4 months = $2,000
- **DPA legal review:** €500 (if kie.ai requires custom terms)
- **Fal.ai migration:** $0 dev cost (API swap), +$2.92/user ongoing
- **In-house option:** €5K-€8K setup + €200/month GPU VPS

**Residual Risk After Mitigation:**
- **IF Pilot validates Realistic Scenario:** Likelihood 3 → Risk Level 15 (High, but manageable)
- **IF forced to fal.ai:** Likelihood 4 → Risk Level 20 (Critical, need Premium $49 tier)
- **Best Case (kie.ai DPA signed):** Likelihood 2 → Risk Level 10 (Medium-High, monitoring)

**Cross-Risk Dependencies:**
- **R1 (GDPR):** Kie.ai DPA blocker affects both compliance AND unit economics
- **R4 (API Cost Overruns):** If users generate 15 scripts/month (not 10), API cost → $5.25 → LTV drops to $260
- **R8 (Low Retention):** If churn 10%, LTV drops to $255 → shutdown threshold

---

## Risk Mitigation Roadmap

### Month 3 (Immediate Priorities - Critical Risks)
| **Risk** | **Action** | **Owner** | **Budget** |
|----------|-----------|-----------|------------|
| **R1: GDPR** | Hire compliance consultant, draft Privacy Policy | Solo Founder | €8K-€13K |
| **R2: Data Breach** | Enable database encryption, implement parameterized queries | Solo Founder | €0 |
| **R3: Image Quality** | Add image validation pipeline, user feedback loop | Solo Founder | €0 |
| **R4: API Costs** | Real-time cost tracking dashboard, user limits | Solo Founder | €0 |
| **R8: Low Retention** | Optimize onboarding (tutorial, templates) | Solo Founder | €50 |
| **R16: Unit Economics** | Contact kie.ai for DPA (GDPR blocker), prepare Pilot metrics tracking | Solo Founder | €0 |

**Total Month 3 Budget:** €8,050-€13,050

---

### Month 4 (Stabilization - Medium-High Risks)
| **Risk** | **Action** | **Owner** | **Budget** |
|----------|-----------|-----------|------------|
| **R1: GDPR** | Complete DPIA, document data flows, data retention policy | Solo Founder + Consultant | €2K |
| **R2: Data Breach** | Add API authentication, RBAC, audit logging | Solo Founder | €0 |
| **R3: Image Quality** | Enhanced prompt templates, LLM fine-tuning | Solo Founder | €200 |
| **R4: API Costs** | Prompt caching, image optimization, batch requests | Solo Founder | €0 |
| **R12: API Failures** | API health dashboard, automated incident response | Solo Founder | €50 |
| **R15: Tariff Plan** | Tiered pricing launch, usage monitoring | Solo Founder | €0 |
| **R16: Unit Economics** | Kie.ai DPA resolution OR fal.ai migration ($0.039/img fallback) | Solo Founder | €500 (if DPA legal review needed) |

**Total Month 4 Budget:** €2,750 (€2,250 + €500 contingency)

---

### Month 5 (Scaling - Long-Term Risks)
| **Risk** | **Action** | **Owner** | **Budget** |
|----------|-----------|-----------|------------|
| **R1: GDPR** | Appoint DPO, security audit | Solo Founder + External DPO | €5.2K + €200/month |
| **R2: Data Breach** | Deploy Sentry, penetration test | Solo Founder | €3K-€5K |
| **R3: Image Quality** | Stability AI SDXL migration, ControlNet | Solo Founder | +€0.04/video |
| **R4: API Costs** | Tariff plan alignment (usage-based pricing) | Solo Founder | €0 |
| **R5: COPPA** | Educator verification, Class Code system | Solo Founder | €0 |
| **R8: Low Retention** | Retention campaigns, community building | Solo Founder | €550/month |
| **R16: Unit Economics** | Pilot Go/No-Go decision (Week 8), validate Realistic Scenario metrics | Solo Founder | €2K (if Pilot extension needed) |

**Total Month 5 Budget:** €10,200-€12,200 + €750/month ongoing (€200 DPO + €550 retention)

---

### Month 6-12 (Optimization & Monitoring)
- **R3 (Image Quality):** Automated QA, hire part-time reviewer (€500/month)
- **R6 (Character Consistency):** SDXL LoRA fine-tuning, 95% target
- **R12 (API Failures):** Multi-provider strategy, test failovers
- **R13 (Video Pipeline):** VPS upgrade (€80/month), external storage (€3.81/month)
- **R11 (Misuse):** Human review for flagged content (€500/month)
- **R15 (Tariff Plan):** A/B test pricing, track LTV
- **R16 (Unit Economics):** Launch Premium $49 tier if LTV/CAC <4x, track break-even Month 18-22 (vs Optimistic Month 13)

**Total Month 6-12 Ongoing:** €1,500-€2,000/month

---

## Risk Monitoring & Review Process

### Weekly Reviews
- **Metrics Dashboard:**
  - API cost per video (target ≤€0.18)
  - Video generation success rate (target ≥99.5%)
  - User churn rate (target ≤5%/month)
  - GDPR compliance checklist progress

### Monthly Reviews
- **High-Risk Items (R1, R2, R3, R4, R8):**
  - Review mitigation progress
  - Update risk scores (likelihood, impact)
  - Execute contingency plans if needed

### Quarterly Reviews
- **Full Risk Register Update:**
  - Re-assess all 15 risks
  - Add new risks (market changes, competitor actions)
  - Archive resolved risks
  - Present to advisors/investors

---

## Summary: Top 5 Risks Requiring Immediate Action

| **Rank** | **Risk** | **Risk Level** | **Month 3 Action** | **Budget** |
|----------|----------|----------------|---------------------|------------|
| **1** | GDPR Non-Compliance | ⛔ 20 | Hire compliance consultant, draft Privacy Policy | €8K-€13K |
| **2** | Data Breach | ⛔ 20 | Enable encryption, parameterized queries, firewall | €0 |
| **3** | Image Quality Issues | 🔴 16 | Image validation, user feedback, prompt templates | €0 |
| **4** | API Cost Overruns | 🔴 16 | Cost tracking dashboard, user limits, alerts | €0 |
| **5** | Low User Retention | 🔴 12 | Onboarding optimization, engagement triggers | €50 |

**Total Immediate Investment:** €8,050-€13,050

---

## Appendix: Risk Scoring Formulas

### Risk Level Calculation
```
Risk Level = Likelihood × Impact
```

### Risk Categories
- **Critical (20-25):** Immediate action, daily monitoring
- **High (15-19):** Weekly review, executive escalation
- **Medium-High (10-14):** Monthly review, active mitigation
- **Medium-Low (5-9):** Quarterly review, preventive measures
- **Low (1-4):** Annual review, routine controls

### Residual Risk
```
Residual Risk = (Post-Mitigation Likelihood) × Impact
```

Example: R1 GDPR Non-Compliance
- **Inherent Risk:** 4 (Likely) × 5 (Severe) = 20 (Critical)
- **Residual Risk:** 2 (Unlikely) × 5 (Severe) = 10 (Medium-High)
- **Mitigation Effectiveness:** 50% reduction in likelihood

---

**Document Owner:** Solo Founder  
**Next Review Date:** May 1, 2026 (after Month 3 mitigation actions)  
**Distribution:** Internal use, share with advisors/investors upon request
