"""Grader for the log-summary task (outcome-driven).

Expected values come from an independent reference implementation run on a
private pristine copy of the log, so the agent cannot influence them.
"""
import json
import os
from datetime import datetime
from pathlib import Path

import pytest

APP = Path(os.environ.get("APP_DIR", "/app"))
REF = Path(__file__).parent / "server_logs_reference.jsonl"
FIELDS = ("request_id", "service", "status", "timestamp")


def parse(path):
    """Return {request_id: (instant, record)} for the winning record of each id."""
    best = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if not isinstance(r, dict) or any(
                not isinstance(r.get(k), str) or not r.get(k) for k in FIELDS):
            continue
        try:
            t = datetime.fromisoformat(r["timestamp"])
        except ValueError:
            continue
        if t.tzinfo is None:
            continue
        if r["request_id"] not in best or t >= best[r["request_id"]][0]:
            best[r["request_id"]] = (t, r)
    return best


def expected():
    out = {}
    for _, r in parse(REF).values():
        d = out.setdefault(r["service"], {})
        d[r["status"]] = d.get(r["status"], 0) + 1
    return out


@pytest.fixture(scope="module")
def summary():
    p = APP / "summary.json"
    assert p.exists(), "/app/summary.json not found"
    return json.loads(p.read_text())


def test_input_not_modified():
    assert (APP / "server_logs.jsonl").read_bytes() == REF.read_bytes()


def test_schema(summary):
    assert isinstance(summary, dict) and summary
    for svc, d in summary.items():
        assert isinstance(svc, str) and isinstance(d, dict) and d
        for st, n in d.items():
            assert isinstance(st, str)
            assert type(n) is int and n > 0, f"{svc}/{st} count must be a positive int"


def test_exact_counts(summary):
    assert summary == expected()


def test_total_equals_distinct_valid_ids(summary):
    total = sum(n for d in summary.values() for n in d.values())
    assert total == len(parse(REF))


def test_tie_goes_to_later_line():
    tie_lines = [json.loads(l) for l in REF.read_text().splitlines() if '"req-tie"' in l]
    assert len(tie_lines) == 2 and tie_lines[0]["status"] != tie_lines[1]["status"]
    last = tie_lines[-1]
    won = parse(REF)["req-tie"][1]
    assert (won["service"], won["status"]) == (last["service"], last["status"])


def test_no_malformed_ids_leaked():
    # malformed fixtures must not contribute: req-900..904 are all invalid
    ids = set(parse(REF))
    assert not ({"req-900", "req-901", "req-902", "req-903", "req-904"} & ids)
