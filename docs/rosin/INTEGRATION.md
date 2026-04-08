# Luthier — Project Specification

## What this is

A software platform for sizing and optimizing Battery Energy Storage Systems (BESS) for specific grid applications. Given a set of requirements — grid parameters, target application, budget constraints — the platform helps an engineer select and configure the right combination of components (battery pack, PCS, transformer) and evaluates the resulting system's performance.

The first supported application is Primary Frequency Response (PFR): a grid service where a BESS injects or absorbs power within seconds to compensate frequency deviations from the nominal 50 Hz. This is one of the most demanding BESS applications in terms of response time and cycling, and has well-defined technical requirements published by grid operators (e.g. RTE in France, under the FCR framework).

The platform is designed to generalize to other applications (peak shaving, backup power, energy arbitrage) as the models mature.

---

## Projects

### `rosin` — Physical Models

The core scientific library. Contains the mathematical models for each component type and for the system as a whole. Has no database dependency and can be used standalone — a simulation script, an optimization tool, or a research notebook can import it without pulling in any persistence infrastructure.

Internally organized in three submodules:

**`rosin.comp`** — Component models. Dataclasses and physical models for each hardware element:

- Battery pack: electrochemical model (open-circuit voltage, internal resistance, capacity, efficiency, thermal behavior, degradation per cycle). Builds on PyBaMM for cell-level physics where appropriate.
- PCS (Power Conversion System): bidirectional inverter model — efficiency curve as a function of load, AC/DC voltage ranges, response time, harmonic distortion.
- Transformer: turns ratio, impedance, losses.

All parameters expressed in SI units.

**`rosin.sim`** — System simulation. Composes component models into a full BESS and simulates its operation over a time horizon:

- Operating point calculation for a given configuration and power setpoint
- Time-domain simulation: SoC trajectory, power output, losses, temperature
- Performance metrics: round-trip efficiency, available energy, ramp rate

**`rosin.ems`** — EMS strategies. Each strategy encodes the control logic for one application:

- `PFRStrategy`: responds to grid frequency deviations according to FCR droop curves. Takes a frequency time series as input, outputs a power setpoint sequence.
- Future strategies: `PeakShavingStrategy`, `BackupStrategy`, `ArbitrageStrategy`, etc.

The EMS submodule is what makes `rosin` application-aware. A simulation in `rosin.sim` runs against a strategy from `rosin.ems`, which defines the charge/discharge schedule.

---

### `caul` — Component Database

The persistence layer. Manages a catalog of real-world components available on the market: battery modules, PCS units, transformers.

**Contents:**

- PostgreSQL schema for each component category.
- CRUD operations for each type.
- Serialization: database records are deserialized into `rosin.comp` dataclasses, so the rest of the system always works with typed, validated objects.
- Import/export utilities for bulk-populating the database from structured files (JSON or YAML).
- A CLI tool for database administration: add, delete, list, import, export.

`caul` depends on `rosin`. It contains no physics.

---

### Luthier — Web Application

The user-facing interface. Runs in a browser, no local installation required.

**Three areas:**

**Component browser.** Browse, search, and filter the component catalog. Filter by numeric parameters (e.g. battery capacity between 100 and 500 kWh, PCS power above 1 MW). Accessible to authenticated users via Google OAuth.

**Sizing workbench.** The user defines a project: grid parameters (nominal voltage, frequency, grid code), target application (PFR, peak shaving...), performance requirements, and budget. The system searches the component catalog and runs simulations to evaluate candidate configurations. Simulation jobs run asynchronously on the server — the user can close the browser and return later to see results. Each job stores its status (queued, running, completed, failed) and full results in a dedicated database table.

**Admin panel.** Restricted to administrator accounts. Add, edit, or delete components from the catalog. Import component data from files. Mirrors the `caul` CLI in a web UI.

---

## How the three projects fit together

```
rosin/
  comp/    component models, no dependencies
  sim/     system simulation, depends on rosin.comp
  ems/     control strategies, depends on rosin.sim
    |
caul/      database layer, depends on rosin
    |
Luthier/   web app, calls caul and rosin through the backend API
```

The server running Luthier imports both `rosin` and `caul`. The browser never calls them directly — it communicates with the backend via HTTP, and the backend handles all computation and database access.

When a user submits a sizing job, the backend enqueues it, runs the `rosin` simulation asynchronously (iterating over candidate configurations from `caul`), and writes results to the simulation database. The user polls for status and retrieves results through the same API.

---

## Databases

**Component catalog (PostgreSQL).** One table per component category: `battery_modules`, `pcs_units`, `transformers`. Fixed schema per category: integer primary key, manufacturer, model name, all technical parameters as `REAL` columns in SI units, plus optional `image_url` and `notes` fields. Hosted on Supabase or equivalent managed PostgreSQL service.

**Simulation database.** Stores sizing jobs and results. Schema to be defined, but at minimum: job status, timestamps, input parameters (grid specs, application requirements, budget), and output data (candidate configurations, performance metrics, cost estimates).

---

## Related open-source projects

**PyBaMM** (Python Battery Mathematical Modelling) — cell-level electrochemical models. `rosin.comp` will use it as a dependency for battery physics rather than reimplementing from scratch.

**PyPSA** (Python for Power System Analysis) — grid-scale power system optimization. Too broad for our use case but a useful architectural reference.

**Microgrid Planner** (INFORMS) — the closest architectural analog: Python computation layer, SQL database, REST API, web frontend, Docker deployment, user authentication. Confirms our stack choices.

---

## Design decisions

**PostgreSQL from day one.** The deployment target is a multi-user web server. Starting with PostgreSQL avoids a migration later and costs nothing in local development.

**Fixed schema per component category.** Parameters are fixed and queries need to filter by numeric value. Fixed typed columns allow proper indexing and straightforward range queries.

**`rosin` has no database dependency.** Any tool that needs the physics — a standalone sizing script, a flight dynamics simulator, an optimization loop — can import `rosin` without pulling in database infrastructure.

**`rosin.ems` as a separate submodule.** EMS strategies are application-specific and will grow over time. Separating them from `rosin.sim` keeps the simulator generic and makes it easy to add new applications without touching the core physics.

**Async simulation jobs.** Sizing involves iterating over many candidate configurations, each requiring a full time-domain simulation. Running this synchronously in a web request would be impractical. An async job queue with persistent state decouples the computation from the HTTP connection.

**PyBaMM as a dependency for cell models.** Battery electrochemistry is well-studied and well-implemented in PyBaMM. Using it as a foundation avoids reinventing models that already exist and are validated.

---

## Out of scope for now

- Applications beyond PFR (peak shaving, backup, arbitrage)
- Grid code compliance checking (the platform assumes the user knows the applicable standard)
- Multi-site or networked BESS configurations
- Real-time monitoring or control (the platform is for sizing and design, not operation)
- The simulation job queue implementation details
- Luthier UI design
- Populating the component catalog with initial data
