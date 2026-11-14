# Fix the Fortran Payroll Calculator

## Statement

`/app/payroll.f90` is a small Fortran 90 program that reads `hours.txt` from the
current directory and prints each employee's gross weekly pay. Its output is
currently wrong for employees who work overtime.

Fix the program so it follows these rules:

- Each line of `hours.txt` is `NAME HOURS RATE` (whitespace separated). `NAME` has
  no spaces and is at most 20 characters, `HOURS` is a decimal number of hours
  worked, and `RATE` is the hourly rate in dollars.
- Hours up to and including 40 are paid at the normal rate. Hours beyond 40 are
  paid at one and a half times the normal rate.
- Each employee's gross pay is rounded to the nearest cent.
- Output is one line per employee, in input order: the name followed by the gross
  pay with two decimals. The last line is `TOTAL` followed by the sum of the
  per-employee (already rounded) amounts, with two decimals.

Keep the existing output layout and keep the program reading `hours.txt` from its
working directory. Edit `/app/payroll.f90` in place.

## Environment

- Ubuntu 22.04 container, working directory `/app`.
- `/app/payroll.f90` (the buggy source) and a sample `/app/hours.txt`.
- `gfortran` is installed. Compile with e.g. `gfortran -o payroll payroll.f90`
  and run it from the directory that holds `hours.txt`.

## Difficulty Note

There is more than one defect, and they interact: fixing only one still leaves
wrong numbers, and the sample file alone does not exercise every case. Check
boundary values (exactly 40 hours, just over 40, large hours) and arithmetic
behaviour in Fortran, not only the sample output. The fix is small, but finding
it requires reasoning about the program rather than pattern-matching.
