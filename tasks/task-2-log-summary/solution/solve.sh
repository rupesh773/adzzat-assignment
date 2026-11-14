#!/bin/bash
set -e
cd /app
python3 - <<'PY'
import json
from datetime import datetime
best = {}
for line in open("server_logs.jsonl", encoding="utf-8"):
    try:
        r = json.loads(line)
        if not isinstance(r, dict):
            continue
        vals = [r[k] for k in ("request_id", "service", "status", "timestamp")]
        if not all(isinstance(v, str) and v for v in vals):
            continue
        t = datetime.fromisoformat(r["timestamp"])
        if t.tzinfo is None:
            continue
    except (ValueError, KeyError):
        continue
    cur = best.get(r["request_id"])
    if cur is None or t >= cur[0]:
        best[r["request_id"]] = (t, r)
out = {}
for _, r in best.values():
    out.setdefault(r["service"], {}).setdefault(r["status"], 0)
    out[r["service"]][r["status"]] += 1
json.dump(out, open("summary.json", "w"), indent=2, sort_keys=True)
PY
