# 2D Flocking Simulation (Boids)

A Python + `pygame` simulation that demonstrates emergent flocking behavior from three simple local rules:

- **Separation** (avoid crowding)
- **Alignment** (match neighbor heading)
- **Cohesion** (move toward neighbors)

## Run

1. Install dependency:

```bash
pip install pygame
```

2. Start the simulation:

```bash
python flocking_sim.py
```

## Real-time on-screen controls

A control panel in the top-left can be adjusted while the simulation runs:

- **Boids**: change number of agents in real time
- **Neighbor Radius**: adjust local interaction radius in real time
- **Boid Speed**: adjust max boid velocity in real time

Drag slider knobs with the mouse to update values immediately.

## Mouse interaction

- Hold **left mouse button**: boids **seek** the mouse.
- Hold **right mouse button**: boids **flee** the mouse.

## Optional CLI defaults

You can still provide startup defaults via CLI (then fine-tune with sliders):

- `--num-boids` (default: `40`)
- `--neighbor-radius` (default: `60`)
- `--separation-radius` (default: `22`)
- `--separation-weight` (default: `1.6`)
- `--alignment-weight` (default: `1.0`)
- `--cohesion-weight` (default: `1.0`)
- `--max-speed` (default: `4.0`)
- `--max-force` (default: `0.10`)
- `--mouse-force` (default: `1.5`)

## Notes

- Boids are rendered as triangles to show heading direction.
- Boids use screen wrapping at edges.
- Neighbor detection checks all boid pairs each frame (`O(n^2)`).
  For large swarms, a spatial grid/quadtree is recommended.
