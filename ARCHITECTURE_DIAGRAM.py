"""
AGENT ARCHITECTURE VISUALIZATION
================================

CURRENT IMPLEMENTATION: Linear Pipeline + Validation Loop
----------------------------------------------------------

┌─────────────────────────────────────────────────────────────────┐
│                   INITIALIZATION                                │
│  Input: {genre, idea, duration, language} → State               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  1. RETRIEVE   │ ← Pinecone query (5 sources)
                    │   (Pinecone)   │   14,452 chars
                    └────────┬───────┘
                             │ always
                             ▼
                    ┌────────────────┐
                    │ 2. WEB_SEARCH  │ ← Conditional (duration >10 min)
                    │   (SerpAPI)    │   SKIPPED for horror (1 min)
                    └────────┬───────┘
                             │ always
                             ▼
                    ┌────────────────┐
                    │ 3. SYNTHESIZE  │ ← OpenAI GPT-4o-mini
                    │ (Combine ctx)  │   Pinecone + Web → Insights
                    └────────┬───────┘   4,205 chars output
                             │ always
                             ▼
                    ┌────────────────┐
                    │ 4. OUTLINE     │ ← OpenAI GPT-4o-mini
                    │ (Generate)     │   Uses synthesized context
                    └────────┬───────┘   2,270 chars output
                             │ always
                             ▼
                    ┌────────────────┐
                    │ 5. SCRIPT      │ ← OpenAI GPT-4o-mini
                    │ (Generate)     │   Uses outline
                    └────────┬───────┘   1,108 chars (iter 1)
                             │ always
                             ▼
                    ┌────────────────┐
                    │ 6. VALIDATE    │ ← Length check (90-110%)
                    │ (Check length) │   
                    └────────┬───────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        if valid (90-110%)          if invalid
        OR max_iterations=3         AND iterations < 3
              │                             │
              ▼                             ▼
    ┌─────────────────┐          ┌────────────────┐
    │    8. END       │          │ 7. REGENERATE  │ ← Adjustment instruction
    │  (Return state) │◄─────────│  (Retry script)│   "REDUCE by X chars"
    └─────────────────┘          └────────┬───────┘
                                          │ loop back
                                          └─────────► (back to VALIDATE)


DECISION POINTS:
----------------
Only ONE conditional branch: should_regenerate()

if script_length in [90%, 110%] of target:
    → END
elif iteration_count >= max_iterations (3):
    → END
else:
    → REGENERATE


HORROR SCRIPT EXECUTION TRACE:
------------------------------
Step 1: retrieve_pinecone      → 5 sources (14,452 chars, 3,613 tokens)
Step 2: web_search             → skipped (duration ≤ 10 min)
Step 3: synthesize_context     → 4,205 chars (4,799 tokens)
Step 4: generate_outline       → 2,270 chars (1,727 tokens)
Step 5: generate_script (i=1)  → 1,108 chars ✗ (110.8% - too long)
Step 6: validate               → invalid
Step 7: regenerate (i=2)       → 1,152 chars ✗ (115.2% - too long)
Step 6: validate               → invalid
Step 7: regenerate (i=3)       → 1,096 chars ✓ (109.6% - valid!)
Step 6: validate               → valid
Step 8: END                    → success


WHY NOT FULL ReAct?
-------------------

Full ReAct Agent:
  Observation → [LLM decides] → Action → Observation → ...
  ├─ Dynamic tool selection
  ├─ Reasoning traces ("I should use tool X because...")
  ├─ Flexible routing (can skip/repeat arbitrary steps)
  └─ Multi-branch decision tree

Current Implementation:
  Fixed Pipeline → [ONE condition] → Loop or End
  ├─ Predetermined sequence
  ├─ No intermediate reasoning
  ├─ Only 1 loop (regenerate)
  └─ Binary decision (valid/invalid)


ADVANTAGES OF CURRENT DESIGN:
-----------------------------
✓ Predictable execution time
✓ Fixed token budget (no runaway costs)
✓ Guaranteed termination (max 3 iterations)
✓ Easy monitoring (7 steps always in order)
✓ Production-ready (no infinite loops)
✓ n8n-compatible (fixed workflow nodes)
✓ Debugging-friendly (clear flow trace)


WHEN TO USE FULL ReAct:
-----------------------
✗ Research tasks (need to explore multiple paths)
✗ Complex problem-solving (need backtracking)
✗ Unknown workflows (agent decides steps)
✗ Long-running tasks (hours/days)

"""

print(__doc__)
