"""
Entity extractor: orchestrates LLM call, JSON persistence, and report generation.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_entities(script: str, project_dir: str) -> dict:
    """
    Extract entities from a script and persist results to the project directory.

    Args:
        script:      Full script text.
        project_dir: Path to the project folder (e.g. projects/my-project/).

    Returns:
        dict with keys:
            entities       – raw parsed dict (characters / animals / objects)
            entities_file  – absolute path to entities.json
            entities_report – absolute path to entities_report.md
            status         – "completed" or "failed"
            error          – error message (only present on failure)
    """
    try:
        from agent.entity.llm_client import call_entity_extraction_llm
        from agent.entity.file_writer import write_entities_report
    except ModuleNotFoundError:
        import sys
        from pathlib import Path as _Path
        sys.path.insert(0, str(_Path(__file__).parent.parent.parent))
        from agent.entity.llm_client import call_entity_extraction_llm
        from agent.entity.file_writer import write_entities_report

    project_path = Path(project_dir)
    project_path.mkdir(parents=True, exist_ok=True)

    # --- LLM call ---
    try:
        entities = call_entity_extraction_llm(script)
    except RuntimeError as e:
        logger.error(f"[entity_extractor] LLM call failed: {e}")
        return {
            "entities": {},
            "entities_file": "",
            "entities_report": "",
            "status": "failed",
            "error": str(e)
        }

    # --- Save entities.json ---
    entities_json_path = project_path / "entities.json"
    try:
        entities_json_path.write_text(
            json.dumps(entities, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"[entity_extractor] Saved entities.json → {entities_json_path}")
    except OSError as e:
        logger.error(f"[entity_extractor] Failed to write entities.json: {e}")
        return {
            "entities": entities,
            "entities_file": "",
            "entities_report": "",
            "status": "failed",
            "error": f"Failed to write entities.json: {e}"
        }

    # --- Generate Markdown report ---
    try:
        report_path = write_entities_report(entities, project_dir)
    except Exception as e:
        logger.error(f"[entity_extractor] Failed to write entities_report.md: {e}")
        return {
            "entities": entities,
            "entities_file": str(entities_json_path),
            "entities_report": "",
            "status": "failed",
            "error": f"Failed to write entities_report.md: {e}"
        }

    n_chars = len(entities.get("characters", []))
    n_animals = len(entities.get("animals", []))
    n_objects = len(entities.get("objects", []))
    logger.info(
        f"[entity_extractor] Done — characters: {n_chars}, animals: {n_animals}, objects: {n_objects}"
    )
    print(
        f"  [entity_extractor] Extracted entities — "
        f"characters: {n_chars}, animals: {n_animals}, objects: {n_objects}"
    )

    return {
        "entities": entities,
        "entities_file": str(entities_json_path),
        "entities_report": report_path,
        "status": "completed"
    }
