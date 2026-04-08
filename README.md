# LUTHIER

<img src="docs/images/luthier.svg" alt="LUTHIER Logo" width="120" align="left">

LUTHIER (Layered Unification of all the Hardware and Intelligence for Embedded Robotics) is a complete robotic platform that integrates three independent projects into a single, working system:

- [ARCO](https://github.com/alexandrelheinen/arco) — motion planning, spatial perception, and control algorithms (Python)
- [FRET](https://github.com/alexandrelheinen/fret) — ROS 2 robotic arm stack with simulation, IK, and trajectory execution
- [BOSSA](https://github.com/alexandrelheinen/bossa) — real-time embedded framework for hardware abstraction on ARM64

Each layer can run independently. LUTHIER is the integration layer that connects them into a full pipeline from high-level planning to physical actuation.

## Stack Overview

```
┌─────────────────────────────────────────┐
│  ARCO  │  Planning · Guidance · Mapping │  Python
├─────────────────────────────────────────┤
│  FRET  │  ROS 2 · URDF · IK · Control   │  Python / ROS 2 Jazzy
├─────────────────────────────────────────┤
│  BOSSA │  Daemon · HAL · Real-time IO   │  C++20 / ARM64
└─────────────────────────────────────────┘
        ↕ LUTHIER integration layer
```

## Documentation Index

- [Project Roadmap](docs/roadmap.md)
- [Architecture overview](docs/ARCHITECTURE.md)
- [Integration guide](docs/INTEGRATION.md)
- [ARCO submodule](https://github.com/alexandrelheinen/arco)
- [FRET submodule](https://github.com/alexandrelheinen/fret)
- [BOSSA submodule](https://github.com/alexandrelheinen/bossa)
- [Coding guidelines](docs/guidelines.md)
- [Contributing guide](CONTRIBUTING.md)

## Repository Layout

```
.
├── docs/                  ← architecture, integration, and design docs
├── config/                ← platform-level configuration files
├── scripts/               ← setup, build, and deployment utilities
├── tests/
│   ├── functional/        ← Level 1: end-to-end system tests
│   └── integration/       ← Level 2: cross-layer integration tests
├── .github/
│   └── workflows/         ← CI/CD pipelines
├── arco/                  ← git submodule
├── fret/                  ← git submodule
└── bossa/                 ← git submodule
```

## Development and Validation Levels

LUTHIER follows a four-level SDLC that mirrors the architecture:

| Level | Scope | When |
|-------|-------|------|
| Level 1 — Functional | Full system, end-to-end behavior | Release gates |
| Level 2 — Integration | Cross-layer interfaces (ARCO↔FRET, FRET↔BOSSA) | PR to main |
| Level 3 — Module / PR | Changes within a single subproject | PR to subproject |
| Level 4 — Unit / Commit | Individual functions and classes | Every commit |

Levels 3 and 4 are enforced inside each subproject's own CI. LUTHIER owns Levels 1 and 2.

## Setup

Clone with submodules:

```bash
git clone --recurse-submodules https://github.com/alexandrelheinen/luthier.git
cd luthier
```

Install all dependencies:

```bash
./scripts/setup.sh
```

This installs Python dependencies (ARCO), ROS 2 Jazzy workspace dependencies (FRET), and cross-compilation toolchain (BOSSA).

## Running the Stack

### Simulation (SITL)

Launch the full stack in simulation:

```bash
./scripts/launch_sitl.sh
```

This starts BOSSA in mock mode, FRET in Gazebo, and connects ARCO for trajectory generation.

### Hardware-in-the-Loop (HITL)

```bash
./scripts/launch_hitl.sh -t pi@raspberry.local
```

### Physical prototype

```bash
./scripts/launch_physical.sh -t pi@raspberry.local
```

## Continuous Integration

GitHub Actions runs the integration validation pipeline on pull requests and pushes to `main`.

Workflows are defined in `.github/workflows/`:

- **Integration tests** (`integration.yml`): cross-layer interface validation
- **Functional tests** (`functional.yml`): end-to-end system scenarios (simulation-only)
- **Submodule sync** (`submodule-check.yml`): verifies submodules point to passing commits

Recommended required checks before merging to `main`:

- Integration / cross-layer tests
- Functional / SITL scenarios
- Submodule sync check

## Contributing

Before contributing, read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/guidelines.md](docs/guidelines.md).

Changes to ARCO, FRET, or BOSSA go through their own repositories and SDLC. LUTHIER PRs are for integration-level work: connecting layers, platform configuration, cross-layer tests, and deployment scripts.

## License

MIT License. See [LICENSE](LICENSE).
