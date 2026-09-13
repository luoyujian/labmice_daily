from pathlib import Path


def resolve_spa_file(frontend_dist: str, requested_path: str):
    """Return an existing regular file only when it is inside the frontend build."""
    try:
        root = Path(frontend_dist).resolve()
        candidate = (root / requested_path).resolve()
        candidate.relative_to(root)
    except (OSError, ValueError):
        return None
    return candidate if candidate.is_file() else None
