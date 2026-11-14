import re
import tomllib
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

BASE = Path(__file__).resolve().parent
TASKS_DIR = BASE.parent / "tasks"
app = FastAPI(title="Terminal-Bench task viewer")


def section(text: str, name: str) -> str:
    """Return the body of a '## name' section of a markdown file."""
    m = re.search(rf"^## {name}\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def load_task(folder: Path) -> dict:
    meta = tomllib.loads((folder / "task.toml").read_text(encoding="utf-8")).get("metadata", {})
    md = (folder / "instruction.md").read_text(encoding="utf-8")
    return {
        "id": folder.name,
        "title": meta.get("title", folder.name),
        "type": meta.get("task_type", "unknown"),
        "difficulty": meta.get("difficulty", ""),
        "statement": section(md, "Statement"),
        "environment": section(md, "Environment"),
        "difficulty_note": section(md, "Difficulty Note"),
        "shortcut_prevention": meta.get("shortcut_prevention", ""),
    }


@app.get("/api/tasks")
def list_tasks():
    return [load_task(p.parent) for p in sorted(TASKS_DIR.glob("*/task.toml"))]


@app.get("/")
def index():
    return FileResponse(BASE / "index.html")
