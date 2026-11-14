! payroll.f90 - weekly gross pay calculator
! Reads NAME HOURS RATE records from hours.txt and prints gross pay.
program payroll
  implicit none
  integer, parameter :: dp = kind(1.0d0)
  integer, parameter :: unit_in = 10
  real(dp), parameter :: ot_threshold = 45.0_dp

  character(len=20) :: name
  real(dp) :: hours, rate, reg_hours, ot_hours, gross, ot_factor
  integer :: ot_num, ot_den, ios
  integer(8) :: cents, total_cents

  ot_num = 3
  ot_den = 2
  ot_factor = ot_num / ot_den

  open(unit=unit_in, file='hours.txt', status='old', action='read', iostat=ios)
  if (ios /= 0) then
    write(*,'(A)') 'ERROR: cannot open hours.txt'
    stop 1
  end if

  total_cents = 0
  do
    read(unit_in, *, iostat=ios) name, hours, rate
    if (ios /= 0) exit

    if (hours > ot_threshold) then
      reg_hours = ot_threshold
      ot_hours = hours - ot_threshold
    else
      reg_hours = hours
      ot_hours = 0.0_dp
    end if

    gross = reg_hours * rate + ot_hours * rate * ot_factor
    cents = nint(gross * 100.0_dp, 8)
    total_cents = total_cents + cents
    write(*,'(A20,F12.2)') name, real(cents, dp) / 100.0_dp
  end do
  close(unit_in)

  write(*,'(A20,F12.2)') 'TOTAL', real(total_cents, dp) / 100.0_dp
end program payroll
