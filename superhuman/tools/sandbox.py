from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path("./workspace").resolve()


def resolve_workspace_path(relative_path: str) -> Path:
    """Resolve a path under ./workspace and reject path traversal.

    This is the Phase 1 placeholder guard. Future filesystem tools should call
    this utility before reading or writing files.
    """

    candidate = (WORKSPACE_ROOT / relative_path).resolve()
    if candidate != WORKSPACE_ROOT and WORKSPACE_ROOT not in candidate.parents:
        raise ValueError("Path escapes the workspace root")
    return candidate
