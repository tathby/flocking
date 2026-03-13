# 2D Flocking Simulation (Boids)

A Python + `pygame` simulation that demonstrates emergent flocking behavior from three simple local rules:

- **Separation** (avoid crowding)
- **Alignment** (match neighbor heading)
- **Cohesion** (move toward neighbors)

## Learning concepts covered

- Agent representation with **position**, **velocity**, and **acceleration**
- Time-based movement updates
- Local neighbor detection by radius
- Emergent behavior from simple rules
- Parameter tuning (weights/radii, max speed/force)
- Efficiency reflection (`O(n^2)` neighbor checks)

## Run

1. Install dependency:

```bash
pip install pygame
```

2. Start the simulation:

```bash
python flocking_sim.py
```

## Default parameters

- Boids: `40`
- Neighborhood radius: `60`
- Separation radius: `22`
- Max speed: `4.0`
- Max steering force: `0.10`
- Rule weights:
  - Separation: `1.6`
  - Alignment: `1.0`
  - Cohesion: `1.0`

## Notes on behavior

- Boids are rendered as **triangles** to show heading direction.
- Boids use **screen wrapping** at edges.
- Neighbor detection currently checks all pairs of boids each frame (`O(n^2)`).
  For larger swarms, a spatial grid or quadtree can improve performance.
