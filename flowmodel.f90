program model
implicit none
  ! position, heading, time of day, day of study
  real :: easting, northing
  real :: direction
  real :: currenthour
  real :: deltad
  real :: deltax, deltay
  real :: flowx, flowy
  real :: swimspeed
  real :: flowdirection, flowspeed
  integer :: day
  
  ! Starting values
  ! UTM Coordinates (Zone is unimportant, but south will alter the way direction works)
  easting = 559566.0
  northing = 5364248.0

  ! Initial direction. Change to whatever you want, probably unimportant really.
  direction = 0.0

  ! The fish's swim speed. Constant in this version.
  swimspeed = 1.0 ! m/s

  ! Initialize the beginning of the model
  currenthour = 0.0
  day = 0
  deltad = 0

  ! Flow direction and speed.
  flowdirection = 1.0472 ! Radians counter clockwise from east. (I know right?)
  flowspeed = 1.0 ! m/s

  ! Put out a CSV header.
  print *, "easting, northing, direction, time"

  do while (day < 14) ! Change to whatever day you want to stop.
    call random_number(deltad)
    deltad = deltad - 0.5
    direction = direction + deltad * 3.141592654
    if (direction > 6.283185308) then
      direction = direction - 6.283185308
    else if (direction < 0) then
      direction = direction + 6.283185308
    end if

    ! Calculate the distance the fish would move without a current.
    deltax = cos(direction) * swimspeed
    deltay = sin(direction) * swimspeed

    ! Calculate how much the fish would drift if it didn't move.
    flowx = cos(flowdirection) * flowspeed
    flowy = sin(flowdirection) * flowspeed

    ! Add the movement and the drift together.
    deltax = deltax + flowx
    deltay = deltay + flowy

    ! Update the fish's geographical coordinates.
    easting = easting + deltax
    northing = northing + deltay

    currenthour = currenthour + 0.00277778
    if (currenthour > 24.0) then
      day = day + 1
      currenthour = 0.0
    end if

    ! Dump everything to stdout. Sophistacted eh?
    print *, easting, ",", northing, ",", direction, ",", currenthour

  end do

end program model
