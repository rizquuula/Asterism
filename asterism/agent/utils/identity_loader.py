"""Identity loader for agent self-awareness.

Reads SOUL.md, PERSONALITY.md, and AGENT.md from the workspace root
and builds a combined identity context injected into all node prompts.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_IDENTITY_FILES = ["SOUL.md", "PERSONALITY.md", "AGENT.md"]
_cache: dict[str, str] = {}


def load_identity_context(workspace_root: str) -> str:
    """Load and combine identity files into a single context block.

    Reads SOUL.md, PERSONALITY.md, and AGENT.md from workspace_root.
    Missing files are skipped with a warning. Results are cached per
    workspace_root path so files are only read once per process.

    Args:
        workspace_root: Path to the workspace directory.

    Returns:
        Combined identity context string, or empty string if no files found.
    """
    if workspace_root in _cache:
        return _cache[workspace_root]

    root = Path(workspace_root)
    sections: list[str] = []

    for filename in _IDENTITY_FILES:
        file_path = root / filename
        if not file_path.exists():
            logger.debug(f"Identity file not found, skipping: {file_path}")
            continue
        try:
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                sections.append(content)
        except OSError as e:
            logger.warning(f"Could not read identity file {file_path}: {e}")

    if not sections:
        _cache[workspace_root] = ""
        return ""

    identity_context = "\n\n---\n\n".join(sections)
    result = f"# Your Identity and Core Behavior\n\n{identity_context}\n\n---"

    _cache[workspace_root] = result
    return result
