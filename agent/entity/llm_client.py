"""
LLM client for entity extraction.

Calls OpenAI GPT-4o-mini with the entity extraction prompt and returns
parsed JSON. Retries up to TOOL_MAX_RETRIES times on failure.
"""

import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

ENTITY_EXTRACTION_PROMPT = """You are an expert in narrative analysis, character design, and AI image generation systems.

Your task is to analyze a storytelling script and extract structured visual entities for consistent image generation.

--------------------------------
CORE OBJECTIVE
--------------------------------

Transform the script into a reusable visual system that ensures:

- consistent character identity across scenes
- reusable visual prompts
- compatibility with text-to-image models

--------------------------------
CRITICAL PRINCIPLES
--------------------------------

1. STRICT SEPARATION:

You MUST separate:

- BASE VISUAL IDENTITY (constant, reusable)
- SCENE STATES (dynamic, contextual)

DO NOT mix them under any circumstances.

2. VISUAL PRECISION OVER EMOTION:

Descriptions must prioritize:
- physical structure
- visible traits

NOT vague emotional descriptions.

--------------------------------
ENTITY TYPES
--------------------------------

Extract:

1. Characters (humans)
2. Animals
3. Objects (ONLY standalone, recurring, visually independent items)

--------------------------------
GLOBAL IDENTIFICATION RULE
--------------------------------

Each entity MUST have a unique stable ID:

- Characters: "char_1", "char_2", ...
- Animals: "animal_1", ...
- Objects: "obj_1", ...

IDs must remain consistent within the output.

--------------------------------
CHARACTER EXTRACTION RULES
--------------------------------

For EACH character:

1. Identify and group all mentions of the same entity

2. Assign:
- id
- name (create if missing)

3. Detect:
- different ages
- major physical variations

--------------------------------
CHARACTER STRUCTURE
--------------------------------

Each character must include:

A. BASE VISUAL PROMPT (MANDATORY)

This is the MOST IMPORTANT component.

Requirements:

- purely visual (NO actions)
- consistent across scenes
- highly specific
- written as a ready-to-use text-to-image prompt

MUST include:

- approximate age
- gender
- facial structure (jawline, cheekbones, eyes shape)
- eyes (color, intensity)
- hair (color, style)
- body type
- skin tone / ethnicity (if inferable)
- distinctive features
- stable clothing style with EXACT COLORS (NOT scene-specific). If the character wears any garment or costume, the color of that garment MUST be stated explicitly (e.g. "dark navy flight suit", "white lab coat", "red jacket"). Color of clothing is MANDATORY if clothing is present.

STYLE:

- cinematic
- highly detailed
- realistic
- 4k
- consistent lighting-neutral description

FORBIDDEN:

- actions
- emotions like "scared", "determined"
- environment references

--------------------------------
B. SCENE STATES
--------------------------------

Separate dynamic properties into:

{
  "scene_states": {
    "actions": [],
    "emotions": []
  }
}

Rules:

- actions = physical actions (running, hiding, fighting)
- emotions = emotional states (fear, anger)

--------------------------------
C. MULTI-VERSION HANDLING
--------------------------------

If a character appears at different ages:

- keep ONE character ID
- create multiple versions:

"versions": [
  {
    "age": "...",
    "base_prompt": "...",
    "scene_states": {...}
  }
]

--------------------------------
ANIMAL RULES
--------------------------------

Same structure as characters:

- id
- type
- optional name
- versions
- base_prompt (static)
- scene_states

Animal base_prompt MUST include the animal's body color and any distinctive markings (e.g. "black and white border collie", "tawny orange Bengal tiger with dark stripes"). Color is MANDATORY.

--------------------------------
OBJECT RULES (IMPORTANT)
--------------------------------

Extract ONLY objects that are:

- physically independent (exist on their own, not part of a body)
- recurring across multiple scenes or mentioned more than once

DO NOT extract:

- objects mentioned only once
- clothing items worn by characters (vests, jackets, pants, shoes — these belong in character base_prompt)
- body-related elements
- abstract concepts
- background scenery

Each object must include:

- id
- name
- base_prompt

--------------------------------
OBJECT BASE PROMPT RULES
--------------------------------

Must describe:

- size (approximate dimensions or scale relative to a known reference, e.g. "palm-sized", "roughly 30 cm tall", "the size of a briefcase")
- shape
- material
- color
- design
- condition

Size is MANDATORY for every object.

Example:

"palm-sized matte black semi-automatic pistol, compact rectangular frame, metallic texture, minimal scratches, modern design, highly detailed, cinematic lighting"

--------------------------------
STRICT EXCLUSIONS
--------------------------------

DO NOT include:

- vague adjectives ("cool", "dramatic")
- actions in base prompts
- emotional states in base prompts
- environment descriptions

--------------------------------
OUTPUT FORMAT (STRICT JSON)
--------------------------------

{
  "characters": [
    {
      "id": "char_1",
      "name": "...",
      "versions": [
        {
          "age": "...",
          "base_prompt": "...",
          "scene_states": {
            "actions": [],
            "emotions": []
          }
        }
      ]
    }
  ],
  "animals": [
    {
      "id": "animal_1",
      "type": "...",
      "name": "...",
      "versions": [
        {
          "age": "...",
          "base_prompt": "...",
          "scene_states": {
            "actions": [],
            "emotions": []
          }
        }
      ]
    }
  ],
  "objects": [
    {
      "id": "obj_1",
      "name": "...",
      "base_prompt": "..."
    }
  ]
}

--------------------------------
QUALITY VALIDATION (MANDATORY)
--------------------------------

Before returning output, verify:

1. Base prompts contain ONLY static visual info
2. No actions inside base prompts
3. No emotions inside base prompts
4. Entities are properly grouped
5. No duplication
6. JSON is valid

--------------------------------
OUTPUT
--------------------------------

Return ONLY JSON.
No explanations."""


def call_entity_extraction_llm(script: str) -> dict:
    """
    Call OpenAI GPT-4o-mini to extract entities from a script.

    Args:
        script: Full script text to analyze.

    Returns:
        Parsed dict with keys: characters, animals, objects.

    Raises:
        RuntimeError: If all retries are exhausted without success.
    """
    try:
        from agent.config import OPENAI_MODEL, TOOL_MAX_RETRIES
    except ModuleNotFoundError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from agent.config import OPENAI_MODEL, TOOL_MAX_RETRIES

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)

    last_error = None
    for attempt in range(TOOL_MAX_RETRIES + 1):
        try:
            logger.info(f"[entity/llm_client] Calling OpenAI for entity extraction (attempt {attempt + 1})")
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ENTITY_EXTRACTION_PROMPT},
                    {"role": "user", "content": f"SCRIPT:\n{script}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            entities = json.loads(content)

            # Ensure all required keys exist
            entities.setdefault("characters", [])
            entities.setdefault("animals", [])
            entities.setdefault("objects", [])

            logger.info(
                f"[entity/llm_client] Extracted: {len(entities['characters'])} characters, "
                f"{len(entities['animals'])} animals, {len(entities['objects'])} objects"
            )
            return entities

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            last_error = e
            logger.warning(f"[entity/llm_client] Attempt {attempt + 1} failed: {e}")
        except Exception as e:
            last_error = e
            logger.warning(f"[entity/llm_client] Attempt {attempt + 1} unexpected error: {e}")

    raise RuntimeError(f"Entity extraction LLM call failed after {TOOL_MAX_RETRIES + 1} attempts: {last_error}")
