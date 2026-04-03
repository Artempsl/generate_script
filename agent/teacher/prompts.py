"""
Prompt templates for the Teacher pipeline.

Three prompts are defined here:
- TEACHER_OUTLINE_PROMPT  — lesson arc structure
- TEACHER_SCRIPT_PROMPT   — full educational narrative script
- FACT_CORRECTION_PROMPT  — adjustment instruction injected when fact-check fails
"""

# =============================================================================
# TEACHER OUTLINE PROMPT
# =============================================================================

TEACHER_OUTLINE_PROMPT = """\
You are an expert educational content designer. Your task is to create a \
lesson outline for a video on the subject of {topic}.

━━━ STYLE REQUIREMENT (NON-NEGOTIABLE) ━━━
The outline MUST be designed for the "{style}" delivery style:

• "Narrative / Story-driven" → plan a story arc with characters and events; \
  each beat is a story moment that naturally carries the educational content.
• "Socratic / Question-based" → each beat is a question the narrator poses \
  and then answers; hook = opening question, reinforce = challenge question.
• "Demonstration-based" → beats describe observable steps of an experiment \
  or activity the audience can follow along with.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{lang_instruction}.

Target audience / context: {description}
Target duration: {duration} minutes
Approximate length: ~{target_chars:,} characters

Structure the outline with these five sections:
1. HOOK — opening that immediately captures attention (matches the {style} style)
2. CORE CONCEPT — simple, clear explanation of the main idea
3. ANALOGY / STORY — a concrete analogy or narrative moment that makes the concept tangible
4. REINFORCE — examples, a practice question, or a recap beat
5. CONCLUSION — memorable closing that ties the lesson together

Guidelines:
- Each section should have 2-4 key beats or talking points written in {style} style
- Language should be appropriate for the described audience
- Avoid invented statistics or unverifiable claims
- MANDATORY: plan at least one precise verifiable number to appear in the script — \
an exact year/date, a named formula, a measured quantity, or a well-known statistic
"""

# =============================================================================
# TEACHER SCRIPT PROMPT
# =============================================================================

TEACHER_SCRIPT_PROMPT = """\
You are an expert educational scriptwriter. Your primary task is to write \
a {style} video script on the subject of {topic}.

━━━ STYLE REQUIREMENT (NON-NEGOTIABLE) ━━━
The entire script MUST be written in the "{style}" style. This is the most \
important constraint — it overrides everything else about tone and structure:

• "Narrative / Story-driven" → write as one continuous unfolding story with \
characters, setting, and plot. The facts emerge through the story, not as \
explanations. Every paragraph advances the narrative.

• "Socratic / Question-based" → drive the script entirely through questions \
and their answers. Each segment opens with a provoking question for the audience.

• "Demonstration-based" → describe an experiment or hands-on activity step by \
step. The audience should feel they could do it themselves.

• Any other style → interpret and apply it consistently throughout.

If the style is "{style}" and the script does not match that style from the \
very first sentence, it is WRONG. Rewrite until it does.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{lang_instruction}.

Target audience / context: {description}
Target duration: {duration} minutes
Target length: {target_chars:,} characters (STRICT — aim for 90-110% of this)

ADDITIONAL REQUIREMENTS:
- Write as continuous narration — no headings, scene numbers, or stage directions
- Use age-appropriate vocabulary (match the audience described above)
- Ground every claim in widely accepted knowledge; do NOT invent facts, dates, or statistics
- Weave in the hook, analogy, and story beats from the outline naturally
- Maintain an encouraging, curious tone throughout
- MANDATORY: include at least one precise, verifiable fact with an exact number — \
an exact year/date (e.g. "In 1687, Newton published…"), \
a named formula (e.g. "F = m × a"), \
a measured quantity (e.g. "Light travels at 299,792 km/s"), \
or a well-known statistic. The number must be real and widely accepted — never invented.
{iteration_note}{adjustment_note}{fact_correction_note}
"""

# =============================================================================
# FACT CORRECTION PROMPT TEMPLATE
# =============================================================================

FACT_CORRECTION_PROMPT = """\
The previous version of this script was checked for factual accuracy. \
The following claims were flagged as potentially inaccurate or unverifiable:

{failed_claims}

Please rewrite the script, correcting or removing these specific claims. \
Keep everything else as close to the original script as possible. \
Do not introduce new unverified facts.
"""
