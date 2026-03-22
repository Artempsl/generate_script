"""
Writes a human-readable Markdown report from extracted entities.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_entities_report(entities: dict, project_dir: str) -> str:
    """
    Generate entities_report.md in the project directory.

    Args:
        entities:    Parsed entity dict (characters / animals / objects).
        project_dir: Path to the project folder.

    Returns:
        Absolute path to the written report file.
    """
    lines = ["# Entities Extraction Report\n"]

    # ── Characters ────────────────────────────────────────────────────────────
    characters = entities.get("characters", [])
    lines.append("## Characters\n")
    if characters:
        lines.append("| ID | Name | Age | Base Prompt | Actions | Emotions |")
        lines.append("|----|----|-----|-------------|---------|----------|")
        for char in characters:
            name = char.get("name", "Unknown")
            char_id = char.get("id", "—")
            for version in char.get("versions", []):
                age = version.get("age", "—")
                base_prompt = version.get("base_prompt", version.get("description", "")).replace("|", "\\|")
                ss = version.get("scene_states", {})
                if isinstance(ss, dict):
                    actions = ", ".join(ss.get("actions", [])) or "—"
                    emotions = ", ".join(ss.get("emotions", [])) or "—"
                else:
                    actions = ", ".join(ss) if ss else "—"
                    emotions = "—"
                lines.append(f"| {char_id} | {name} | {age} | {base_prompt} | {actions} | {emotions} |")
    else:
        lines.append("*No characters found.*")

    lines.append("")

    # ── Animals ───────────────────────────────────────────────────────────────
    animals = entities.get("animals", [])
    lines.append("## Animals\n")
    if animals:
        lines.append("| ID | Type | Name | Age | Base Prompt | Actions | Emotions |")
        lines.append("|----|----|------|-----|-------------|---------|----------|")
        for animal in animals:
            a_id = animal.get("id", "—")
            a_type = animal.get("type", "Unknown")
            a_name = animal.get("name", "—")
            for version in animal.get("versions", []):
                age = version.get("age", "—")
                base_prompt = version.get("base_prompt", version.get("description", "")).replace("|", "\\|")
                ss = version.get("scene_states", {})
                if isinstance(ss, dict):
                    actions = ", ".join(ss.get("actions", [])) or "—"
                    emotions = ", ".join(ss.get("emotions", [])) or "—"
                else:
                    actions = ", ".join(ss) if ss else "—"
                    emotions = "—"
                lines.append(f"| {a_id} | {a_type} | {a_name} | {age} | {base_prompt} | {actions} | {emotions} |")
    else:
        lines.append("*No animals found.*")

    lines.append("")

    # ── Objects ───────────────────────────────────────────────────────────────
    objects = entities.get("objects", [])
    lines.append("## Objects\n")
    if objects:
        lines.append("| ID | Object | Base Prompt |")
        lines.append("|----|----|-------------|")
        for obj in objects:
            obj_id = obj.get("id", "—")
            obj_name = obj.get("name", "Unknown").replace("|", "\\|")
            base_prompt = obj.get("base_prompt", obj.get("description", "")).replace("|", "\\|")
            lines.append(f"| {obj_id} | {obj_name} | {base_prompt} |")
    else:
        lines.append("*No recurring objects found.*")

    lines.append("")

    # Write file
    report_path = Path(project_dir) / "entities_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"[file_writer] Saved entities_report.md → {report_path}")

    return str(report_path)
