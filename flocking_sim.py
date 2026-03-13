import math
import random

import pygame

WIDTH, HEIGHT = 800, 600
NUM_BOIDS = 40
FPS = 60

NEIGHBOR_RADIUS = 60
SEPARATION_RADIUS = 22

SEPARATION_WEIGHT = 1.6
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0

BACKGROUND_COLOR = (20, 20, 30)
BOID_COLOR = (235, 235, 245)


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def sub(self, other):
        self.x -= other.x
        self.y -= other.y

    def mult(self, scalar):
        self.x *= scalar
        self.y *= scalar

    def div(self, scalar):
        if scalar != 0:
            self.x /= scalar
            self.y /= scalar

    def mag(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        magnitude = self.mag()
        if magnitude > 0:
            self.div(magnitude)

    def limit(self, max_val):
        if self.mag() > max_val:
            self.normalize()
            self.mult(max_val)

    def copy(self):
        return Vector2(self.x, self.y)



def distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


class Boid:
    def __init__(self):
        self.position = Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        if self.velocity.mag() == 0:
            self.velocity = Vector2(1, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = 4.0
        self.max_force = 0.10

    def apply_force(self, force):
        self.acceleration.add(force)

    def flock(self, boids):
        separation_force = self.separation(boids)
        alignment_force = self.alignment(boids)
        cohesion_force = self.cohesion(boids)

        separation_force.mult(SEPARATION_WEIGHT)
        alignment_force.mult(ALIGNMENT_WEIGHT)
        cohesion_force.mult(COHESION_WEIGHT)

        self.apply_force(separation_force)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

    def separation(self, boids):
        steer = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            d = distance(self.position, other.position)
            if 0 < d < SEPARATION_RADIUS:
                diff = self.position.copy()
                diff.sub(other.position)
                diff.normalize()
                diff.div(d)
                steer.add(diff)
                count += 1

        if count > 0:
            steer.div(count)

        if steer.mag() > 0:
            steer.normalize()
            steer.mult(self.max_speed)
            steer.sub(self.velocity)
            steer.limit(self.max_force)

        return steer

    def alignment(self, boids):
        average_velocity = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            if distance(self.position, other.position) < NEIGHBOR_RADIUS:
                average_velocity.add(other.velocity)
                count += 1

        if count > 0:
            average_velocity.div(count)
            average_velocity.normalize()
            average_velocity.mult(self.max_speed)

            steer = average_velocity.copy()
            steer.sub(self.velocity)
            steer.limit(self.max_force)
            return steer

        return Vector2(0, 0)

    def cohesion(self, boids):
        center_of_mass = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            if distance(self.position, other.position) < NEIGHBOR_RADIUS:
                center_of_mass.add(other.position)
                count += 1

        if count > 0:
            center_of_mass.div(count)
            return self.seek(center_of_mass)

        return Vector2(0, 0)

    def seek(self, target):
        desired = target.copy()
        desired.sub(self.position)
        desired.normalize()
        desired.mult(self.max_speed)

        steer = desired.copy()
        steer.sub(self.velocity)
        steer.limit(self.max_force)
        return steer

    def update(self):
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.max_speed)

        self.position.add(self.velocity)
        self.acceleration = Vector2(0, 0)

        # screen wrapping
        if self.position.x < 0:
            self.position.x = WIDTH
        elif self.position.x > WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = HEIGHT
        elif self.position.y > HEIGHT:
            self.position.y = 0

    def draw(self, screen):
        angle = math.atan2(self.velocity.y, self.velocity.x)
        heading = Vector2(math.cos(angle), math.sin(angle))
        side = Vector2(-heading.y, heading.x)

        length = 11
        half_width = 4

        tip = Vector2(self.position.x + heading.x * length, self.position.y + heading.y * length)
        left = Vector2(
            self.position.x - heading.x * length * 0.5 + side.x * half_width,
            self.position.y - heading.y * length * 0.5 + side.y * half_width,
        )
        right = Vector2(
            self.position.x - heading.x * length * 0.5 - side.x * half_width,
            self.position.y - heading.y * length * 0.5 - side.y * half_width,
        )

        pygame.draw.polygon(
            screen,
            BOID_COLOR,
            [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))],
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Flocking Simulation")
    clock = pygame.time.Clock()

    boids = [Boid() for _ in range(NUM_BOIDS)]

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        for boid in boids:
            boid.flock(boids)
            boid.update()
            boid.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
