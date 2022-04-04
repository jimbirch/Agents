import numpy as np

class Boid():
  def __init__(self, x, y, width, height):
    self.position = np.array([x,y])
    self.velocity = np.array((np.random.rand(2) - 0.5)*10)
    self.acceleration = np.array((np.random.rand(2) - 0.5)/2)

    self.width = width
    self.height = height

    self.boidID = np.random.random()

    self.speed_limit = 10
    self.max_delta = 0.2
    self.sight_distance = 100
    self.aweight = 0.5
    self.cweight = 0.5
    self.sweight = 0.5

  def update(self):
    self.position += self.velocity
    self.velocity += self.acceleration
    if np.linalg.norm(self.velocity) > self.speed_limit:
      self.velocity = self.velocity / np.linalg.norm(self.velocity) * self.speed_limit
    self.acceleration = np.zeros(2)

  def edges(self):
    # Resolves out of bounds by moving animals from one edge to the opposite
    # TODO replace with a real method.
    if self.position[0] > self.width:
      self.position[0] = 0
    elif self.position[0] < 0:
      self.position[0] = self.width

    if self.position[1] > self.height:
      self.position[1] = 0
    elif self.position[1] < 0:
      self.position[1] = self.height

  def align(self, boids):
    # Allows the boid to realign with nearby boids.
    # 1. Detect all boids within the sight distance
    # 2. Average the velocity of all detected boids
    # 3. Find the direction of the average velocity
    # 4. Multiply the average velocity by a set speed
    # 5. Calculate the acceleration necessary to match
    adjust_delta = np.array(np.zeros(2))
    total = 0
    avg_velocity = np.array(np.zeros(2))
    for boid in boids:
      if np.linalg.norm(boid.position - self.position) < self.sight_distance:
        avg_velocity += boid.velocity
        total += 1
    if total > 0:
      avg_velocity /= total
      mag_velocity = np.linalg.norm(avg_velocity)
      if mag_velocity > 0:
        avg_velocity = (avg_velocity / mag_velocity) * self.speed_limit
      adjust_delta = avg_velocity - self.velocity
      if np.linalg.norm(adjust_delta) > self.max_delta:
        adjust_delta = adjust_delta * self.max_delta / np.linalg.norm(adjust_delta)

    return adjust_delta

  def cohesion(self, boids):
    # Steers the boid toward the middle of any nearby group, allows school 
    # cohesion.
    # 1. Detect all boids within the sight distance.
    # 2. Average the position of all boids within sight distance
    # 3. Determine the direction to the middle of the group.
    # 4. Determine the acceleration necessary to reach the middle of the group.
    adjust_delta = np.array(np.zeros(2))
    total = 0
    center_of_mass = np.array(np.zeros(2))
    for boid in boids:
      if np.linalg.norm(boid.position - self.position) < self.sight_distance:
        center_of_mass += boid.position
        total += 1
    if total > 0:
      center_of_mass /= total
      vec_to_com = center_of_mass - self.position
      if np.linalg.norm(vec_to_com) > 0:
        vec_to_com = (vec_to_com / np.linalg.norm(vec_to_com)) * self.speed_limit
      adjust_delta = vec_to_com - self.velocity
      if np.linalg.norm(adjust_delta) > self.max_delta:
        adjust_delta = (adjust_delta / np.linalg.norm(adjust_delta)) * self.max_delta

      return adjust_delta

  def separation(self, boids):
    # Steers the boid away from nearby boids, allows boids to avoid collisions.
    # 1. Detect all boids within the sight distance.
    # 2. Determine the distance to each boid with sight distance
    # 3. Weight the impact of each nearby boid by the inverse of its distance.
    # 4. Determine the acceleration necessary to avoid colliding with others.
    adjust_delta = np.array(np.zeros(2))
    total = 0
    avg_vector = np.array(np.zeros(2))
    for boid in boids:
      dist_xy = self.position - boid.position
      distance = np.linalg.norm(dist_xy)
      # distance += 0.001 # Prevent divide-by-zero
      if distance > 0 and distance < self.sight_distance: # As written there is
                                                          # no mechanism to re-
                                                          # solve collisions at
                                                          # exactly the same
                                                          # location.
        dist_xy /= distance
        avg_vector += dist_xy
        total += 1
    if total > 0:
      avg_vector /= total
      adjust_delta = avg_vector - self.velocity
      if np.linalg.norm(adjust_delta) > self.max_delta:
        adjust_delta = (adjust_delta / np.linalg.norm(adjust_delta)) * self.max_delta

    return adjust_delta

  def apply_behaviour(self, boids):
    alignment = self.align(boids)
    cohesion = self.cohesion(boids)
    separation = self.separation(boids)

    self.acceleration = self.acceleration + alignment * self.aweight
    self.acceleration = self.acceleration + cohesion * self.cweight
    self.acceleration = self.acceleration + separation * self.sweight

