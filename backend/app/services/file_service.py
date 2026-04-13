from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
    "venv",
}

IGNORED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".dll",
    ".pyc",
}


def scan_repository_files(repo_path: str) -> list[dict]:
    root = Path(repo_path)
    results = []

    for path in root.rglob("*"):
        if path.is_dir():
            continue

        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue

        results.append({
            "path": str(path.relative_to(root)),
            "file_type": path.suffix.lower().lstrip(".") or "unknown"
        })

    return results