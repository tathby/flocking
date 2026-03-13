import argparse
import math
import random

WIDTH, HEIGHT = 800, 600
FPS = 60

BACKGROUND_COLOR = (20, 20, 30)
BOID_COLOR = (235, 235, 245)
PANEL_COLOR = (35, 35, 50)
TEXT_COLOR = (230, 230, 235)
SLIDER_BG = (70, 70, 90)
SLIDER_FILL = (120, 180, 255)


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


class Boid:
    def __init__(self, world_width, world_height, max_speed, max_force):
        self.world_width = world_width
        self.world_height = world_height
        self.position = Vector2(random.uniform(0, world_width), random.uniform(0, world_height))
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        if self.velocity.mag() == 0:
            self.velocity = Vector2(1, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = max_speed
        self.max_force = max_force

    def apply_force(self, force):
        self.acceleration.add(force)

    def flock(self, boids, neighbor_radius, separation_radius, separation_weight, alignment_weight, cohesion_weight):
        separation_force = self.separation(boids, separation_radius)
        alignment_force = self.alignment(boids, neighbor_radius)
        cohesion_force = self.cohesion(boids, neighbor_radius)

        separation_force.mult(separation_weight)
        alignment_force.mult(alignment_weight)
        cohesion_force.mult(cohesion_weight)

        self.apply_force(separation_force)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

    def separation(self, boids, separation_radius):
        steer = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            d = distance(self.position, other.position)
            if 0 < d < separation_radius:
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

    def alignment(self, boids, neighbor_radius):
        average_velocity = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            if distance(self.position, other.position) < neighbor_radius:
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

    def cohesion(self, boids, neighbor_radius):
        center_of_mass = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue

            if distance(self.position, other.position) < neighbor_radius:
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

    def flee(self, target):
        desired = self.position.copy()
        desired.sub(target)
        if desired.mag() == 0:
            return Vector2(0, 0)

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

        if self.position.x < 0:
            self.position.x = self.world_width
        elif self.position.x > self.world_width:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = self.world_height
        elif self.position.y > self.world_height:
            self.position.y = 0

    def draw(self, screen, pygame_module):
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

        pygame_module.draw.polygon(
            screen,
            BOID_COLOR,
            [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))],
        )


class Slider:
    def __init__(self, pygame_module, label, min_value, max_value, value, x, y, width, integer=False):
        self.pygame = pygame_module
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min(value, max_value), min_value)
        self.integer = integer
        self.track_rect = pygame_module.Rect(x, y + 20, width, 8)
        self.knob_radius = 8
        self.dragging = False

    def _value_to_x(self):
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return self.track_rect.left + ratio * self.track_rect.width

    def _set_from_x(self, x_pos):
        clamped = max(self.track_rect.left, min(x_pos, self.track_rect.right))
        ratio = (clamped - self.track_rect.left) / self.track_rect.width
        value = self.min_value + ratio * (self.max_value - self.min_value)
        if self.integer:
            value = round(value)
        self.value = value

    def handle_event(self, event):
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_x = self._value_to_x()
            knob_y = self.track_rect.centery
            distance_to_knob = math.sqrt((event.pos[0] - knob_x) ** 2 + (event.pos[1] - knob_y) ** 2)
            if self.track_rect.collidepoint(event.pos) or distance_to_knob <= self.knob_radius + 2:
                self.dragging = True
                self._set_from_x(event.pos[0])
                return True

        if event.type == self.pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        if event.type == self.pygame.MOUSEMOTION and self.dragging:
            self._set_from_x(event.pos[0])
            return True

        return False

    def draw(self, screen, font):
        pygame = self.pygame
        label_value = int(self.value) if self.integer else round(self.value, 2)
        text_surface = font.render(f"{self.label}: {label_value}", True, TEXT_COLOR)
        screen.blit(text_surface, (self.track_rect.left, self.track_rect.top - 18))

        pygame.draw.rect(screen, SLIDER_BG, self.track_rect, border_radius=4)

        fill_rect = self.track_rect.copy()
        fill_rect.width = max(1, int(self._value_to_x() - self.track_rect.left))
        pygame.draw.rect(screen, SLIDER_FILL, fill_rect, border_radius=4)

        pygame.draw.circle(
            screen,
            (240, 245, 255),
            (int(self._value_to_x()), self.track_rect.centery),
            self.knob_radius,
        )


def distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


def parse_args():
    parser = argparse.ArgumentParser(description="2D boids flocking simulation")
    parser.add_argument("--num-boids", type=int, default=40, help="number of boids")
    parser.add_argument("--neighbor-radius", type=float, default=60.0, help="radius for alignment/cohesion")
    parser.add_argument("--separation-radius", type=float, default=22.0, help="radius for separation")
    parser.add_argument("--separation-weight", type=float, default=1.6, help="separation force weight")
    parser.add_argument("--alignment-weight", type=float, default=1.0, help="alignment force weight")
    parser.add_argument("--cohesion-weight", type=float, default=1.0, help="cohesion force weight")
    parser.add_argument("--max-speed", type=float, default=4.0, help="maximum boid speed")
    parser.add_argument("--max-force", type=float, default=0.10, help="maximum steering force")
    parser.add_argument("--mouse-force", type=float, default=1.5, help="multiplier for mouse seek/flee steering")
    return parser.parse_args()


def sync_boid_count(boids, target_count, max_speed, max_force):
    while len(boids) < target_count:
        boids.append(Boid(WIDTH, HEIGHT, max_speed, max_force))
    while len(boids) > target_count:
        boids.pop()


def main():
    args = parse_args()

    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Flocking Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 16)

    boids = [Boid(WIDTH, HEIGHT, args.max_speed, args.max_force) for _ in range(args.num_boids)]

    sliders = [
        Slider(pygame, "Boids", 10, 200, args.num_boids, 20, 20, 220, integer=True),
        Slider(pygame, "Neighbor Radius", 20, 180, args.neighbor_radius, 20, 70, 220),
        Slider(pygame, "Boid Speed", 1.0, 8.0, args.max_speed, 20, 120, 220),
    ]

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for slider in sliders:
                slider.handle_event(event)

        args.num_boids = int(sliders[0].value)
        args.neighbor_radius = sliders[1].value
        args.max_speed = sliders[2].value

        sync_boid_count(boids, args.num_boids, args.max_speed, args.max_force)

        for boid in boids:
            boid.max_speed = args.max_speed

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse = Vector2(mouse_x, mouse_y)
        left_pressed, _, right_pressed = pygame.mouse.get_pressed(3)

        screen.fill(BACKGROUND_COLOR)

        for boid in boids:
            boid.flock(
                boids,
                args.neighbor_radius,
                args.separation_radius,
                args.separation_weight,
                args.alignment_weight,
                args.cohesion_weight,
            )

            if left_pressed:
                seek_force = boid.seek(mouse)
                seek_force.mult(args.mouse_force)
                boid.apply_force(seek_force)

            if right_pressed:
                flee_force = boid.flee(mouse)
                flee_force.mult(args.mouse_force)
                boid.apply_force(flee_force)

            boid.update()
            boid.draw(screen, pygame)

        panel_rect = pygame.Rect(10, 10, 260, 165)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=8)
        pygame.draw.rect(screen, (90, 100, 125), panel_rect, width=1, border_radius=8)

        for slider in sliders:
            slider.draw(screen, font)

        hint_text = font.render("LMB: seek  RMB: flee", True, TEXT_COLOR)
        screen.blit(hint_text, (20, 150))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
