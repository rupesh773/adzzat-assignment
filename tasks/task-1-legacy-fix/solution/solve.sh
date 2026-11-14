#!/bin/bash
set -e
cd /app
# Bug 1: integer division 3/2 == 1, so overtime was paid at 1.0x
sed -i 's|ot_factor = ot_num / ot_den|ot_factor = real(ot_num, dp) / real(ot_den, dp)|' payroll.f90
# Bug 2: overtime threshold was 45 instead of 40
sed -i 's|ot_threshold = 45.0_dp|ot_threshold = 40.0_dp|' payroll.f90
