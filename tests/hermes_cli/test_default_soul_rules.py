"""The shipped SOUL.md carries the Ask Dealer working rules and only routes to skills that ship."""

import os
import re
from pathlib import Path
from unittest.mock import patch

from hermes_cli.config import ensure_hermes_home
from hermes_cli.default_soul import DEFAULT_SOUL_MD

REPO_ROOT = Path(__file__).resolve().parents[2]

# The one-paragraph default this fork seeded before the working rules were added, hardcoded (not read
# from the module) so the fixture keeps describing that older text if the module changes again.
_PERSONA_ONLY_SOUL = (
    "You are Gideon, Acme Corp's private AI assistant. Never refer to yourself as Hermes or Hermes Agent. "
    "Be direct: match the length of your reply to the weight of "
    "the ask — a one-line question gets a one-line answer, and finished work gets a short report of what "
    "changed, what's verified, and what's left, never a replay of the process. No filler (\"Great question,\" "
    "\"I'd be happy to\"), no restating the request back, no re-summarizing what you already said, no narrating "
    "tool calls the user can see. Plain claims over adjectives; when unsure, say so plainly. Agree because it's "
    "right, not because the user said it. Depth is earned — give it when the user asks for detail, teaches, or "
    "the stakes demand it, not by default."
)


def test_untouched_persona_only_default_is_upgraded_to_the_rules(tmp_path):
    # An install seeded before the rules existed holds text nobody wrote, so it must pick the rules up.
    assert _PERSONA_ONLY_SOUL != DEFAULT_SOUL_MD

    with patch.dict(os.environ, {"HERMES_HOME": str(tmp_path)}):
        soul_path = tmp_path / "SOUL.md"
        soul_path.write_text(_PERSONA_ONLY_SOUL, encoding="utf-8")
        ensure_hermes_home()
        assert soul_path.read_text(encoding="utf-8") == DEFAULT_SOUL_MD


def test_edited_persona_only_default_is_left_alone(tmp_path):
    edited = _PERSONA_ONLY_SOUL + " Always reply in French."

    with patch.dict(os.environ, {"HERMES_HOME": str(tmp_path)}):
        soul_path = tmp_path / "SOUL.md"
        soul_path.write_text(edited, encoding="utf-8")
        ensure_hermes_home()
        assert soul_path.read_text(encoding="utf-8") == edited


def test_every_skill_the_rules_load_ships_in_the_repo():
    # A rule that names a skill the app does not ship sends the agent to "skill not found".
    named = set(re.findall(r"load the `([a-z0-9-]+)` skill", DEFAULT_SOUL_MD))
    assert named, "the default SOUL.md should route to at least one skill"

    shipped = {path.parent.name for path in (REPO_ROOT / "skills").rglob("SKILL.md")}
    assert named <= shipped, f"SOUL.md loads skills that are not in skills/: {sorted(named - shipped)}"
