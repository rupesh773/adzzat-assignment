# Adzzat Labs Take-Home: Terminal-Bench Tasks + Task Viewer

## Project Overview
Two verifiable tasks in Harbor / Terminal-Bench format, plus a minimal FastAPI web page that lists them.

| Task | Type | What the agent must do |
|---|---|---|
| `task-1-legacy-fix` | Language-driven | Fix two bugs in a Fortran 90 payroll program (`payroll.f90`) |
| `task-2-log-summary` | Outcome-driven | Produce `/app/summary.json` (final status count per service) from a messy JSONL log, in any language |

## Folder Structure
```
tasks/
  task-1-legacy-fix/
    task.toml  instruction.md
    environment/  Dockerfile  payroll.f90  hours.txt
    solution/     solve.sh
    tests/        test.sh  test_outputs.py
  task-2-log-summary/
    task.toml  instruction.md
    environment/  Dockerfile  server_logs.jsonl
    solution/     solve.sh
    tests/        test.sh  test_outputs.py  server_logs_reference.jsonl
web/
  main.py     # FastAPI: GET /api/tasks, serves index.html
  index.html  # vanilla JS, two-column viewer
NOTES.md
```

## Setup & Run

### Verify a task with Docker
Requires Docker. Run from the repo root (PowerShell shown; use `$(pwd)` on Mac/Linux).

Task 1:
```bash
docker build -t task1 tasks/task-1-legacy-fix/environment
docker run -it --rm -v "${PWD}/tasks/task-1-legacy-fix/tests:/tests" -v "${PWD}/tasks/task-1-legacy-fix/solution:/solution" task1 bash
# inside the container:
python3 -m pytest /tests/test_outputs.py -q   # fails on the buggy code
bash /solution/solve.sh                       # applies the reference fix
python3 -m pytest /tests/test_outputs.py -q   # passes
```

Task 2:
```bash
docker build -t task2 tasks/task-2-log-summary/environment
docker run -it --rm -v "${PWD}/tasks/task-2-log-summary/tests:/tests" -v "${PWD}/tasks/task-2-log-summary/solution:/solution" task2 bash
# inside the container:
pytest /tests/test_outputs.py -q              # fails (no summary.json yet)
bash /solution/solve.sh
pytest /tests/test_outputs.py -q              # passes
```

### Run the web page
Requires Python 3.11+ (uses `tomllib`).
```bash
pip install fastapi uvicorn
uvicorn web.main:app --reload
```
Open http://127.0.0.1:8000. The API is at `/api/tasks`.

## How the Graders Prevent Shortcuts
- **Task 1:** the grader recompiles `/app/payroll.f90` from scratch and runs it against hidden inputs: fixed boundary cases (exactly 40 h, 40.25 h, 44/45 h, 0 h) plus fresh random data on every run. Results are compared with an independent `Decimal` reference. Printing the sample output or hardcoding values fails. Random cases that land exactly on half a cent are skipped so floating-point rounding cannot cause unfair failures.
- **Task 2:** the grader computes expected counts from a private pristine copy of the log with its own reference implementation, checks the exact schema (integer counts, no extra keys), checks the input log was not edited, and cross-checks totals against the number of distinct valid IDs. The log deliberately includes mixed UTC offsets, exact-timestamp ties, duplicate IDs whose service changes, and several kinds of malformed lines. Known limit: because only an output file is produced, an agent could in principle hardcode the final JSON for this one fixed log; a stronger version would regenerate a hidden log at grading time.
