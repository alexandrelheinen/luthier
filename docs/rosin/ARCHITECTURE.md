# Luthier — Implementation Notes

## Stack

**Backend (`rosin`, `caul`, Luthier API):** Python 3.12+. FastAPI for the Luthier API — Python-native, generates API documentation automatically, handles async requests well, and the syntax will feel immediately familiar.

**ORM and migrations:** SQLAlchemy 2.0 (ORM style) with Alembic for schema migrations. SQLAlchemy maps naturally to Python dataclasses. Alembic handles schema changes over time without manual SQL.

**Scientific dependencies:** PyBaMM for cell-level battery models. NumPy and SciPy for numerical simulation in `rosin.sim`. No need to implement ODE solvers or electrochemical models from scratch.

**Frontend (Luthier):** React with TypeScript, built with Vite. Large ecosystem, realistic for collaboration, and TypeScript's type system will feel familiar given a C++ background.

**Infrastructure:** Docker and Docker Compose from day one. Each service (PostgreSQL, FastAPI backend, React frontend) runs in its own container. The local development environment and the production server use the same configuration.

**Database hosting:** Supabase for managed PostgreSQL. The free tier covers development and early use. Migrating to self-hosted PostgreSQL later is a one-line change in the connection string.

**Async job queue:** Celery with Redis as broker, for simulation jobs. FastAPI background tasks work for simple cases but Celery gives persistent job state, retries, and a monitoring dashboard (Flower) without much extra work.

---

## `rosin` — task list

Pure Python, no infrastructure. Start here. No new tools to learn, and it forces the parameter definitions to be nailed down before anything touches a database.

**Setup:**
- [ ] Initialize the project: `pyproject.toml`, `src/rosin/`, `tests/`
- [ ] Create the three subpackage directories: `src/rosin/comp/`, `src/rosin/sim/`, `src/rosin/ems/`
- [ ] Set up a virtual environment and verify the package installs cleanly
- [ ] Add dependencies: PyBaMM, NumPy, SciPy

**`rosin.comp` — component models:**
- [ ] `BatteryModule` dataclass: nominal capacity (Wh), nominal voltage (V), internal resistance (Ω), max C-rate charge/discharge, round-trip efficiency, operating temperature range, cycle degradation rate, weight (kg)
- [ ] Battery physical model: OCV curve vs SoC, internal resistance vs SoC and temperature — wrap PyBaMM or implement a simplified equivalent circuit model (Thevenin)
- [ ] `PCS` dataclass: rated power (W), DC voltage range (V), AC voltage (V), efficiency curve (dict of load fraction → efficiency), response time (s), max ramp rate (W/s)
- [ ] PCS model: compute output power and losses given a setpoint and current operating conditions
- [ ] `Transformer` dataclass: rated power (VA), primary/secondary voltage (V), impedance (%), no-load losses (W), load losses (W)
- [ ] Transformer model: compute losses and secondary voltage given load

**`rosin.sim` — system simulation:**
- [ ] `BESSConfig` dataclass: one `BatteryModule` + one `PCS` + one `Transformer`, plus topology parameters (number of battery strings in series/parallel)
- [ ] Operating point solver: given a `BESSConfig` and a power setpoint, compute SoC change, losses, efficiency, terminal voltage
- [ ] Time-domain simulation: given a `BESSConfig`, an initial SoC, and a power setpoint time series, integrate the operating point over the time horizon and return SoC trajectory, energy delivered, total losses, temperature profile
- [ ] Performance metrics: round-trip efficiency, available energy at current SoC, max sustainable power, ramp rate

**`rosin.ems` — EMS strategies:**
- [ ] Define the `Strategy` base class or protocol: takes grid state (frequency, voltage, time) as input, returns a power setpoint (W)
- [ ] `PFRStrategy`: implements FCR droop curve — maps frequency deviation from 50 Hz to a power setpoint proportional to rated power. Configurable dead band and droop slope. Reference: RTE FCR technical requirements.
- [ ] PFR simulation runner: takes a `BESSConfig`, a `PFRStrategy`, and a frequency time series; runs `rosin.sim` at each timestep and returns full system state history

**Tests and validation:**
- [ ] Unit tests for each component model (charge/discharge cycle, efficiency at various loads)
- [ ] Unit test for the PFR strategy (frequency step input → expected power output)
- [ ] Integration test: full PFR simulation over a 15-minute frequency time series, verify SoC stays within bounds and power response matches droop curve
- [ ] Validation notebook: run a known BESS configuration against published FCR test cases and compare results

---

## `caul` — task list

Depends on `rosin.comp` dataclasses being stable. Do not start until the component dataclasses are finalized.

**Setup:**
- [ ] Initialize the project: `pyproject.toml`, `src/caul/`, `tests/`
- [ ] Add dependencies: SQLAlchemy 2.0, Alembic, psycopg2-binary, `rosin`
- [ ] Set up Docker Compose with a local PostgreSQL 16 container
- [ ] Configure Alembic: `alembic init`, point at the local database URL via environment variable

**Schema:**
- [ ] SQLAlchemy ORM model for `battery_modules` table — columns mirror `BatteryModule` dataclass fields
- [ ] SQLAlchemy ORM model for `pcs_units` table — mirrors `PCS` dataclass
- [ ] SQLAlchemy ORM model for `transformers` table — mirrors `Transformer` dataclass
- [ ] Write and run the initial Alembic migration
- [ ] Verify schema against a running PostgreSQL container

**Database access layer:**
- [ ] Session management: context manager for database sessions, connection pool configuration
- [ ] `get(id)`, `list()`, `insert(obj)`, `delete(id)` for each component type
- [ ] Range filter queries: `list_batteries(capacity_min, capacity_max, ...)`, same pattern for PCS and transformers
- [ ] Serialization: `rosin.comp` dataclass → ORM object, and the reverse

**CLI tool (`caul` command):**
- [ ] `caul battery add <file.yaml>` — insert a battery module from a YAML file
- [ ] `caul battery delete <id>`
- [ ] `caul battery list` — tabular output with key parameters
- [ ] `caul battery export <file.yaml>` — dump all battery modules to YAML
- [ ] `caul import <file.yaml>` — bulk import, any component type, from a single structured file
- [ ] Same set of subcommands for `pcs` and `transformer`

**Tests:**
- [ ] Unit tests for serialization round-trip: dataclass → ORM → dataclass
- [ ] Integration tests against a test database container: insert, query, filter, delete

---

## Luthier — task list

The backend depends on `caul` (and through it, `rosin`) being stable. The frontend can start in parallel once the API contract is defined — use mock data until the backend is ready.

**Backend (FastAPI):**
- [ ] Initialize the project: `pyproject.toml`, `src/luthier/`, `frontend/`
- [ ] Add dependencies: FastAPI, Uvicorn, `caul`, Celery, Redis, python-jose (JWT), authlib (Google OAuth)
- [ ] Extend Docker Compose to add the FastAPI service and Redis container
- [ ] Component endpoints: `GET /batteries`, `GET /batteries/{id}`, `GET /batteries?capacity_min=&capacity_max=&...` — same pattern for PCS and transformers
- [ ] Google OAuth flow: redirect, callback, JWT token generation
- [ ] Auth middleware: verify JWT on protected endpoints
- [ ] Admin role check: decorator or dependency for admin-only endpoints
- [ ] Sizing job endpoints: `POST /jobs` (submit a sizing job), `GET /jobs/{id}` (poll status and results)
- [ ] Celery worker: receives a job, iterates over candidate configurations from `caul`, runs `rosin` simulations, writes results to the simulation table
- [ ] Alembic migration for the `simulation_jobs` and `simulation_results` tables
- [ ] Admin endpoints: `POST /batteries`, `DELETE /batteries/{id}`, bulk import

**Frontend (React + TypeScript):**
- [ ] Bootstrap with Vite: `npm create vite@latest frontend -- --template react-ts`
- [ ] Choose a component library — Mantine is well documented and covers tables, forms, and charts without fighting Tailwind
- [ ] Google login page and OAuth redirect handling
- [ ] Component browser: paginated table with filter controls for numeric parameters
- [ ] Component detail page: all parameters, image if available
- [ ] Sizing workbench: form to define grid parameters, application (PFR for now), performance requirements, budget
- [ ] Job status page: polling loop, progress indicator, results when complete
- [ ] Results display: candidate configurations ranked by a chosen metric (efficiency, cost, cycle life), charts for SoC trajectory and power response
- [ ] Admin panel: forms to add/delete components, bulk import via file upload

**Infrastructure:**
- [ ] Single `docker-compose.yml` at the repo root that starts PostgreSQL, Redis, FastAPI backend, and React frontend (via a Node dev server in development, Nginx in production)
- [ ] Environment variable management: `.env` file for local dev, documented list of required variables (database URL, Redis URL, Google OAuth client ID/secret, JWT secret)
- [ ] Supabase project setup: create the project, run migrations against it, point the production connection string there

---

## Order and dependencies

The hard dependency chain is: `rosin.comp` → `rosin.sim` → `rosin.ems` → `caul` → Luthier backend → Luthier frontend. Nothing in the chain is useful without what comes before it.

A practical order:

1. `rosin.comp` and `rosin.sim`. Pure Python, no infrastructure, no new frameworks. The only goal here is getting the physics right and the dataclasses stable. This phase also validates that the parameter set is complete — if a model needs a parameter that the dataclass does not have, better to find out now.

2. `rosin.ems` with the PFR strategy. Still pure Python. Requires finding a real FCR frequency time series to test against (RTE publishes historical data).

3. Docker and local PostgreSQL. Learn Docker Compose in isolation before the codebase gets complex. A container running PostgreSQL, accessible from a Python script, is a good self-contained exercise.

4. `caul`. Learn SQLAlchemy and Alembic here. The CLI tool gives something concrete to test without needing a web server.

5. FastAPI, starting with the read-only component endpoints and no authentication. The goal is to learn the framework with minimal scope — a few GET endpoints that return data from `caul`.

6. Google OAuth and JWT. Add authentication once the basic API works. Authentication touches both frontend and backend and is easier to add than to retrofit into a broken flow.

7. React and TypeScript. The component browser is the right starting point — read-only, no auth, no forms. Focus on learning React's component model and state management before adding complexity.

8. Celery and the simulation job queue. The most complex piece. Leave it for when the rest of the stack is solid and working end-to-end.

---

## Things to learn, in order

**Docker and Docker Compose.** The official "Getting Started" tutorial covers the basics. Focus on `docker-compose.yml` syntax, environment variables, and volume mounts for the database.

**SQLAlchemy 2.0.** Read the ORM tutorial in the official docs (not the Core tutorial — the ORM style maps naturally to Python dataclasses). Then read the Alembic "Getting Started" guide.

**FastAPI.** The official tutorial at fastapi.tiangolo.com is well written and covers 80% of what is needed. Work through it sequentially — it builds on itself.

**TypeScript.** A few hours with the TypeScript Handbook (typescriptlang.org/docs/handbook) before touching React. Focus on interfaces, type annotations, and generics. The rest comes with practice.

**React.** Start with the official docs at react.dev. Learn `useState` and `useEffect` before anything else. Avoid tutorials that use class components — they are outdated.

**Celery.** The official "First Steps with Celery" guide is enough to get started. Read it after FastAPI is working.

---

## Reference material for the domain

- RTE FCR technical requirements (available on rte-france.com) — defines the droop curve, dead band, and response time requirements for the PFR strategy
- PyBaMM documentation (pybamm.readthedocs.io) — for the battery cell models in `rosin.comp`
- "Simplistic Revenue Based BESS Sizing Tool in Python" (IEEE, 2022) — a published implementation of a PFR sizing model, useful as a reference for `rosin.ems.PFRStrategy`
