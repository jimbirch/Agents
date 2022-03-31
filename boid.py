##############################################################################
### Boid object for QGIS fish school plugin                                ###
### 2022 Jim Burchfield                                                    ###
##############################################################################
# Instantiates a boid as a simple agent-based model for a schooling fish.    #
# Boids are based on Craig Reynolds's 1986 model for simulating flocking beh-#
# aviour in birds. Three simple behaviours are essential to boid (bird-oid   #
# objects). Boids must maintain separation to avoid crowding and collisions  #
# with schoolmates, adjust their courses to align with the courses of their  #
# schoolmates, and adjust their courses to maintain school cohesion.         #
##############################################################################
# Properties of these boids:                                                 #
#   Initialization: x, y, width, height                                      #
#     x, y:                                                                  #
#       The initial position of the boid before starting the simulation.     #
#     width, height:                                                         #
#       The bounds of the study area                                         #
#                                                                            #
#   Important variables that can currently only be adjusted here:            #
#     self.aWeight, self.cWeight, self.sWeight:                              #
#       The weights associated with alignment¹, cohesion², and separation²,  #
#       respectively.                                                        #
#     self.maxSwimSpeed:                                                     #
#       How fast the boid can swim expressed in [dist units] / [time step]   #
#     self.maxDelta:                                                         #
#       How fast can the boid accelerate to achieve its behavioural goals?   #
#     self.perceptionDistance:                                               #
#       How far can the boid see to align and cohese with other boids,       #
#       expressed in [dist units].                                           #
#     self.avoidanceDistance:                                                #
#       How close can the boid be to another boid before it is concerned     #
#       about crashing (currently only used in avoidance).                   #
##############################################################################
# Important methods:                                                         #
#   __init__(self, x, y, width, height):                                     #
#     Instantiate a boid a location [x, y] in a rectangular study area bound-#
#     ed by (0 ≤ x ≤ width) and (0 ≤ y ≤ height).                            #
#   update(self):                                                            #
#     Conclude the "turn" updates the position and velocity, set the delta to#
#     the zero vector³. Polices max speed and max delta.                     #
#   behave(self, boids):                                                     #
#     Provide the boid a list of other boids to perform its behaviours with. #
#     Calls other behaviour functions and weights them appropriately.        #
##############################################################################
# Notes: ¹Alignment is calculated as the acceleration necessary to exactly   #
#         align with the target velocity in the next turn. aWeight should be #
#         between 0 and 1. Values slightly higher than 1 will overcorrect and#
#         could be interesting idk.                                          #
#        ²Cohesion and avoidance are calculated as the direction necessary to#
#         achieve the target behaviour. cWeight and dWeight should be between#
#         1 and maxDelta.                                                    #
#        ³It is possible to use other methods for initial deltas, random for-#
#         aging, etc.                                                        #
##############################################################################
# Operational notes:                                                         #
#   Every turn, the boid's position is updated, then its velocity, then its  #
#   acceleration according to the following equations:                       #
#     1. P(n+1) = P(n) + V(n)                                                #
#     2. V(n+1) = V(n) + ΔV(n)                                               #
#     3. ΔV(n+1) = ΔV(align) * W(a) + ΔV(cohese) * W(c) + ΔV(separate) * W(s)#
#   V and ΔV are constrained to physically plausible maximum V and ΔV by the #
#   following formulae:                                                      #
#     V = min(V, V * maxV / ||V||2)                                          #
#     ΔV = min(ΔV, ΔV * maxΔV / ||ΔV||2)                                     #
##############################################################################

import numpy as np

class Boid():
  def __init__(self, x, y, width, height):
    # Setup boids using constructor variables. Tell boids where to form, what 
    # their initial velocity is, and what their initial acceleration is.
    self.position = np.array([x, y])
    self.velocity = (np.random.rand(2) - 0.5) * 10
    self.delta = (np.random.rand(2) - 0.5) * 10

    # Initialize the bounds of our study area
    self.rangeX = width
    self.rangeY = height

    # Give each boid a unique ID for mapping reasons
    self.boidID = np.random.random()

    # Boid properties: define the maximum speed that a boid can swim, the
    # distance the boid can see, the too-close distance to other boids, the
    # maximum acceleration (delta), and the weight of the three behaviours
    self.maxSwimSpeed = 10
    self.perceptionDistance = 50
    self.avoidanceDistance = 10
    self.maxDelta = 1
    self.aWeight = 0.5 # Alignment weight
    self.cWeight = 0.5 # Cohesion weight
    self.sWeight = 20 # Separation (avoidance) weight

  def highwayPatrol(self):
    # Oh no it's the cops!
    # Reduce velocity to maxSwimSpeed
    currentSpeed = np.linalg.norm(self.velocity)
    if currentSpeed > self.maxSwimSpeed:
      self.velocity = self.velocity * self.maxSwimSpeed / currentSpeed

  def constrainDelta(self):
    # Limits the delta (accleration) in any turn to maxDelta
    currentDelta = np.linalg.norm(self.delta)
    if currentDelta > self.maxDelta:
      self.delta = self.delta * self.maxDelta / currentDelta

  def update(self):
    # What do we do each time the boid updates? At minimum we need to update
    # position, velocity, and delta (acceleration).
    # Position[n+1] = Position[n] + Velocity[n]
    # Velocity[n+1] = Velocity[n] + Delta[n]
    # Delta[n] = [0, 0] OR a random vector
    # Also use this method to police the speed and acceleration limits

    # Update the boid's position
    self.highwayPatrol()
    self.position += self.velocity

    # Update the boid's velocity
    self.constrainDelta()
    self.velocity += self.delta

    # Provide a new initial acceleration
    # TODO: a user controllable random fluctuation
    self.delta = np.zeros(2)

  def outOfBounds(self):
    # How do we handle animals leaving the study area?
    # Currently moves them to the opposite edge
    # TODO: replace with something better
    if self.position[0] > self.rangeX:
      self.position[0] = 0
    elif self.position[0] < 0:
      self.position[0] = self.rangeX
    if self.position[1] > self.rangeY:
      self.position[1] = 0
    elif self.position[1] < 0:
      self.position[1] = self.rangeY

  def align(self, boids):
    # Attempts to align the boid's direction to the average direction of the
    # other boids that are visible to it.
    # 1. Generate a target velocity based on the average velocity of visible
    #    boids (boids within the perception distance:
    #    V(target) = Σ(0→ N)V(n)/N
    # 2. Determine the acceleration necessary to meet the target velocity:
    #    ΔV(target) = V(target) - V(self)
    dDelta = np.zeros(2)
    totalNearby = 0

    # Average the velocity of all boids within perceptionDistance
    for boid in boids:
      difference = boid.position - self.position
      distance = np.linalg.norm(difference)
      if distance > 0 and distance < self.perceptionDistance:
        dDelta += boid.velocity
        totalNearby += 1
    if totalNearby > 0:
      dDelta /= totalNearby
      # Find the change in velocity necessary to match the average velocity of
      # the group.
      dDelta -= self.velocity

    return dDelta

  def cohese(self, boids):
    # Attempts to steer the boid toward the middle of any visible group of
    # boids, maintains school cohesion.
    # 1. Generate a target position (the center of the group):
    #    P(target) = Σ(0→ N)P(n)/N
    # 2. Find the direction to the target position:
    #    D(target) = P(target) - P(self)
    # 3. Normalize the vector to the target:
    #    ΔV = D(target) / ||D(target)||2
    dDelta = np.zeros(2)
    totalNearby = 0

    # Average the position of all boids within perceptionDistance
    for boid in boids:
      difference = boid.position - self.position
      distance = np.linalg.norm(difference)
      if distance > 0 and distance < self.perceptionDistance:
        dDelta += boid.position
        totalNearby += 1
    if totalNearby > 0:
      dDelta /= totalNearby

      # Find the direction to the average position of the group
      dDelta -= self.position

      # Normalize the direction
      magDelta = np.linalg.norm(dDelta)
      if magDelta > 0:
        dDelta /= magDelta

    return dDelta

  def separate(self, boids):
    # Attempts to steer the boid away from any boid within its collision
    # avoidance radius.
    # 1. Determine the distance to the too-close boid
    #    D = ||P(target) - P(self)||2
    # 2. Determine the direction to the too-close boid
    #    d = (P(target) - P(self)) / D
    # 3. Weight by distance
    #    d = d / D
    # 3. Determine acceleration to avoid collision
    #    ΔV = Σ(0→ N)d(n) / N
    dDelta = np.zeros(2)
    totalNearby = 0
    # Average direction away from too-close boids (within avoidanceDistance)
    for boid in boids:
      difference = self.position - boid.position
      distance = np.linalg.norm(difference)
      if distance > 0 and distance < self.avoidanceDistance: # The only boid at
        direction = difference / distance                    # position 0 is us
        direction /= distance                                # (hopefully) no
        dDelta += direction                                  # divide-by-zero 
        totalNearby += 1                                     # is needed. 
    if totalNearby > 0:
      dDelta /= totalNearby

    return dDelta

  def behave(self, boids):
    # Master behaviour method, applies behaviours and weights to the primary
    # boid behaviours. If you want to add additional behaviours (foraging,
    # predation avoidance, phototaxis, unaliving, etc.), put them here.
    #
    # A note on weights as the apply to boid behaviours: 
    # 1. Alignment provides the exact acceleration necessary to match align-
    #    ment, use a weight of between 0 and 1 to adjust toward others each 
    #    turn, slightly higher than 1 should overcorrect and might be inter-
    #    esting. Don't exceed these bounds.
    # 2. Cohesion and separation provide normalized vectors (directions only).
    #    These can be freely adjusted to any acceleration, but should probably
    #    be in the interval: (1 ≤ C ≤ maxDelta). Does the animal care more
    #    about eating than schooling? Set cWeight near 1. Will bumping into a
    #    nearby boid start an aggressive fight? Set sWeight near maxDelta.
    # 3. It is okay for the resulting acceleration in this method to exceed
    #    maxDelta (you can even set weights ≥ maxDelta if you want). Speed and
    #    acceleration limits are enforced in the update method.
    alignment = self.align(boids) * self.aWeight
    cohesion = self.cohese(boids) * self.cWeight
    separation = self.separate(boids) * self.sWeight

    self.delta = self.delta + alignment + cohesion + separation;
