"""Grader for the Fortran payroll task.

Anti-shortcut design: the agent's source is recompiled from scratch and run
against hidden inputs (fixed edge cases + fresh random data every run), and
compared with an independent Decimal reference. Output of the sample file
alone is never trusted.
"""
import os
import random
import subprocess
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest

APP = Path(os.environ.get("APP_DIR", "/app"))
SRC = APP / "payroll.f90"
CENT = Decimal("0.01")


def reference(rows):
    """rows: list of (name, hours_str, rate_str) -> (lines, total) as strings."""
    out, total = [], Decimal(0)
    for name, h, r in rows:
        h, r = Decimal(h), Decimal(r)
        reg = min(h, Decimal(40))
        ot = max(h - Decimal(40), Decimal(0))
        gross = (reg * r + ot * r * Decimal("1.5")).quantize(CENT, ROUND_HALF_UP)
        total += gross
        out.append((name, gross))
    return out, total


def is_tie(h, r):
    h, r = Decimal(h), Decimal(r)
    reg = min(h, Decimal(40))
    ot = max(h - Decimal(40), Decimal(0))
    g = (reg * r + ot * r * Decimal("1.5")) * 100
    return g - g.to_integral_value(rounding="ROUND_FLOOR") == Decimal("0.5")


@pytest.fixture(scope="module")
def exe(tmp_path_factory):
    assert SRC.exists(), "/app/payroll.f90 is missing"
    d = tmp_path_factory.mktemp("build")
    binary = d / "payroll_bin"
    r = subprocess.run(["gfortran", "-o", str(binary), str(SRC)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"compile failed:\n{r.stderr}"
    return binary


def run(exe, rows):
    with tempfile.TemporaryDirectory() as wd:
        Path(wd, "hours.txt").write_text(
            "".join(f"{n} {h} {r}\n" for n, h, r in rows))
        p = subprocess.run([str(exe)], cwd=wd, capture_output=True,
                           text=True, timeout=20)
    assert p.returncode == 0, p.stderr
    return [ln.split() for ln in p.stdout.strip().splitlines()]


def check(exe, rows):
    got = run(exe, rows)
    exp, total = reference(rows)
    assert len(got) == len(exp) + 1, f"expected {len(exp)+1} lines, got {got}"
    for (gname, gval), (ename, eval_) in zip(got, exp):
        assert gname == ename
        assert Decimal(gval) == eval_, f"{ename}: got {gval}, want {eval_}"
    assert got[-1][0] == "TOTAL"
    assert Decimal(got[-1][1]) == total, f"total {got[-1][1]} != {total}"


def test_sample_file(exe):
    rows = [l.split() for l in (APP / "hours.txt").read_text().splitlines() if l.strip()]
    check(exe, [tuple(r) for r in rows])


def test_boundaries(exe):
    rows = [("A", "40.0", "17.00"), ("B", "40.25", "17.00"),
            ("C", "39.75", "17.00"), ("D", "44.0", "20.00"),
            ("E", "45.0", "20.00"), ("F", "60.0", "12.00"),
            ("G", "0.0", "25.00"), ("H", "41.0", "10.00")]
    assert not any(is_tie(h, r) for _, h, r in rows)
    check(exe, rows)


def test_no_overtime_not_inflated(exe):
    check(exe, [("Z", "40.0", "33.33"), ("Y", "12.5", "9.99")])


def test_overtime_rate_is_one_and_half(exe):
    got = run(exe, [("Q", "50.0", "10.00")])
    assert Decimal(got[0][1]) == Decimal("550.00")


def test_single_employee_and_total(exe):
    check(exe, [("Solo", "48.5", "19.75")])


@pytest.mark.parametrize("seed", [None, None, None])
def test_random_hidden_inputs(exe, seed):
    rng = random.Random(int.from_bytes(os.urandom(8), "big"))
    rows = []
    while len(rows) < 12:
        h = f"{rng.randint(0, 260) * 0.25:.2f}"
        r = f"{rng.randint(900, 6000) / 100:.2f}"
        if not is_tie(h, r):
            rows.append((f"Emp{len(rows)}", h, r))
    check(exe, rows)
