program model
implicit none
  ! position, heading, time of day, day of study
  real :: easting, northing
  real :: direction
  real :: currenthour
  real :: deltad
  real :: deltax
  real :: deltay
  real :: swimspeed
  integer :: day
  
  ! Starting values
  easting = 559566.0
  northing = 5364248.0
  direction = 0.0
  swimspeed = 1.0 ! m/s
  currenthour = 0.0
  day = 0
  deltad = 0.0
  print *, "easting, northing, direction, time"

  do while (day < 14)
    call random_number(deltad)
    deltad = deltad - 0.5
    direction = direction + deltad * 3.141592654
    if (direction > 6.283185308) then
      direction = direction - 6.283185308
    else if (direction < 0) then
      direction = direction + 6.283185308
    end if

    deltax = cos(direction) * swimspeed
    deltay = sin(direction) * swimspeed

    easting = easting + deltax
    northing = northing + deltay

    currenthour = currenthour + 0.00277778
    if (currenthour > 24.0) then
      day = day + 1
      currenthour = 0.0
    end if

    print *, easting, ",", northing, ",", direction, ",", currenthour

  end do

end program model
