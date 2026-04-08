# Luthier — Learning Notes

This document is a companion to the project spec and implementation notes. It doesn't replace them. It's about the meta-level: how to pace yourself, where things tend to go wrong, and how to keep going when the project feels abstract or stuck.

---

## The shape of this project

The dependency chain — `rosin.comp` → `rosin.sim` → `rosin.ems` → `caul` → Luthier backend → Luthier frontend — is a feature, not a constraint. Each layer has a single job, and finishing one layer gives you something concrete before the next one gets complicated.

The risk is that the early layers feel invisible. You can spend three weeks writing solid Python physics models and have nothing to show except a passing test suite. That's fine, and it's real progress, but you need to know in advance that this phase exists so it doesn't feel like you're going nowhere.

The antidote is to keep a running notebook (a Jupyter notebook or just a Python script) from day one. Every time a model produces a number, plot it. A SoC trajectory dropping from 0.8 to 0.3 over 15 minutes, even if it's just a matplotlib figure, is something real you can look at. Don't wait for a UI.

---

## Phase 0 — Before writing any code (a few days)

Do this before touching the repo. It pays off.

**Get a real frequency time series.** RTE publishes historical FCR frequency data at rte-france.com (under "Données publiées" or the eCO2mix section). Download a few days of 1-second resolution data. Keep it somewhere. You'll use it constantly to validate `rosin.ems` and to have something real to simulate against.

**Read the RTE FCR technical requirements.** The document is publicly available. It defines the droop curve, the dead band (±10 mHz around 50 Hz where no response is required), and the activation time. You don't need to read it cover to cover — focus on the droop curve and the SoC management requirements. Everything in `PFRStrategy` comes from this document.

**Skim the PyBaMM docs.** Not to learn the library in depth, but to understand what it gives you and what it expects. The equivalent circuit model (the "thevenin" model) is probably all you need. This avoids the trap of reaching for PyBaMM mid-implementation and discovering it doesn't work the way you thought.

**Sketch the `BatteryModule` dataclass on paper.** Before writing a single line. What parameters does a real battery module datasheet give you? Nominal voltage, nominal capacity, internal resistance, max charge/discharge current, cycle life, operating temperature range. Map those to SI units. This exercise will surface missing parameters before they block you in `rosin.sim`.

---

## Phase 1 — `rosin.comp` and `rosin.sim`

This is pure Python. No Docker, no database, no framework. The only goal is getting the physics right and the dataclasses stable.

**The most important decision here is where to draw the line with PyBaMM.** PyBaMM is a powerful library, but a full electrochemical model is overkill for sizing purposes. A Thevenin equivalent circuit model (OCV curve + series resistance + one RC pair) is physically reasonable and much simpler to implement. Use PyBaMM for its cell parameter sets and OCV curves, but consider implementing the equivalent circuit yourself in `rosin.comp` so you control the model. You can always swap in a more complex PyBaMM model later.

**Don't try to model everything at once.** Start with the battery. Get a charge/discharge cycle working, plot SoC over time, verify the numbers make physical sense (a 100 kWh battery discharging at 50 kW should last about 2 hours, minus losses). Then add the PCS. Then the transformer. Each addition is a new source of bugs.

**The operating point solver in `rosin.sim` is where the real work is.** Given a power setpoint and a current state (SoC, temperature), compute what actually happens: how much SoC changes, what the losses are, whether the setpoint is achievable. This function is the core of everything. Spend time getting it right. Test it against known cases: a 0 W setpoint should produce 0 SoC change, a setpoint above the rated power should be clipped, etc.

**Common mistakes here:**
- Mixing up power and energy (Watts vs Watt-hours). The time step in the simulation is where this bites you. Always track units explicitly.
- Forgetting to clip the setpoint to SoC limits. A battery at 100% SoC cannot absorb power. This is obvious but easy to miss in the simulation loop.
- Conflating the battery terminal voltage with the OCV. The terminal voltage drops under load due to internal resistance. For the operating point solver, this matters.

---

## Phase 2 — `rosin.ems` and the PFR strategy

Still pure Python. This is the first phase where you use the real frequency time series you downloaded in Phase 0.

The PFR strategy is conceptually simple: if the frequency drops below 49.99 Hz (outside the dead band), inject power proportional to the deviation, up to the rated power. If it rises above 50.01 Hz, absorb power. The droop curve is linear between the dead band and the full activation point (typically ±200 mHz from nominal).

**Write the strategy first, then run it against the real frequency data, then connect it to `rosin.sim`.** Don't try to do all three at once. A standalone `PFRStrategy` that takes a frequency float and returns a power setpoint float is easy to test in isolation.

**The SoC management problem will appear here.** A BESS providing PFR continuously will drift toward 0% or 100% SoC depending on whether the grid is running low or high. Real FCR systems solve this with a SoC restoration mechanism: when SoC drifts too far, the strategy adds a small correction signal. The RTE document describes the allowed approaches. This is the most interesting engineering problem in the whole PFR simulation, and it's worth getting right.

**The validation notebook matters.** After the full simulation runs, compare your results against the published IEEE paper ("Simplistic Revenue Based BESS Sizing Tool in Python", 2022). If the results are in the same ballpark for the same input parameters, your model is probably correct. If they differ by a factor of 2, something is wrong. This is the only meaningful validation you have before the platform has real users.

---

## Phase 3 — Docker and PostgreSQL (in parallel, not blocking)

This is a deliberate deviation from the strict dependency chain. **Start this before `caul` is fully designed.** The goal is to learn Docker Compose in isolation, without the pressure of having a broken database block your physics work.

**The exercise:** get a PostgreSQL 16 container running with Docker Compose, connect to it from a Python script using psycopg2, create a table, insert a row, read it back. That's it. This takes an afternoon and teaches you everything you need to know about Docker volumes, environment variables, and port mapping before the codebase gets complex.

**Common Docker mistakes:**
- Forgetting to persist the database with a volume. Without a named volume in `docker-compose.yml`, your data disappears every time the container restarts.
- Using `localhost` inside a container to connect to another container. Containers talk to each other by service name (`db`, not `localhost`). This trips up almost everyone once.
- Not setting `POSTGRES_PASSWORD` and wondering why the container won't start.

Learn to read Docker logs early: `docker compose logs db` is your first debugging tool when a container won't start.

---

## Phase 4 — `caul`

By this point you have stable dataclasses and a running PostgreSQL container. `caul` is mostly plumbing.

**SQLAlchemy 2.0 has two styles:** Core (write SQL directly) and ORM (Python classes that map to tables). Use the ORM style. It maps naturally to your `rosin.comp` dataclasses and the official docs for it are good. Read the ORM tutorial at docs.sqlalchemy.org before writing any models.

**Alembic feels like ceremony at first.** You write a Python migration file to create a table instead of just writing `CREATE TABLE`. This feels like extra work when you only have one schema version. It pays off the second time you change the schema — instead of manually editing the database, you write a migration and every environment stays in sync. Treat every schema change, even during development, as a migration.

**The CLI tool is motivating.** `caul battery list` printing a table of components in the terminal, with real (even fake) data you inserted yourself, is the first moment the project feels like software. Make sure you get here. Put a few fake battery modules in YAML files and import them. Having data in the database makes everything after this more concrete.

**Serialization is where the two worlds meet.** A `BatteryModule` dataclass becomes a SQLAlchemy ORM object to be stored, and comes back out as a dataclass when read. Write this conversion explicitly and test it: insert a dataclass, read it back, verify the two are equal. This round-trip test catches unit mismatches and field mapping errors before they propagate.

---

## Phase 5 — FastAPI

Start with the simplest possible thing: a single `GET /batteries` endpoint that reads from `caul` and returns JSON. No auth, no filtering, no async. Just a list of components.

**FastAPI's automatic docs are a genuine superpower.** Go to `http://localhost:8000/docs` the first time you run the server and you'll see an interactive API explorer built from your code. You can call your endpoints from the browser without writing any frontend. This is useful for development and keeps you in the loop on what the API actually looks like.

**Pydantic models are not the same as SQLAlchemy models, and not the same as `rosin.comp` dataclasses.** You'll have three representations of a battery module: the dataclass in `rosin`, the ORM model in `caul`, and the Pydantic schema in the FastAPI layer (what the API sends and receives). This is correct and intentional, but it takes a moment to internalize why all three exist. The short answer: the dataclass is for physics, the ORM model is for persistence, and the Pydantic model is for the HTTP contract. They're different jobs.

**Add authentication last, even within this phase.** Write all the component endpoints first, test them, then add Google OAuth. Authentication is fiddly and tends to break things in subtle ways. Having working endpoints before adding auth means you know what's supposed to work and can tell when it breaks.

---

## Phase 6 — React and TypeScript

**TypeScript first.** Spend a few hours with the TypeScript Handbook (typescriptlang.org/docs/handbook) before writing any React. Focus on interfaces and type annotations. You don't need generics deeply at this point. The TypeScript investment pays off fast when the compiler catches a misspelled field name that would otherwise be a runtime bug.

**Start with the component browser.** It's read-only, no forms, no auth, just a table of data fetched from the API. This is the right scope for learning React's component model and `useEffect` for data fetching. The mental model of "fetch data on mount, display it, handle the loading state" covers 80% of what the frontend does.

**`useEffect` will confuse you.** It runs after render, not before, and its dependency array controls when it re-runs. If you find yourself in an infinite loop of fetches, the dependency array is probably wrong. Read the official React docs on `useEffect` carefully; the examples there are better than most tutorials.

**The async job flow is the hardest frontend piece.** The user submits a sizing job, and the frontend needs to poll `GET /jobs/{id}` until the status changes from `queued` to `completed`. This involves a polling interval, cleanup on unmount, and handling the transition from loading to results. Leave this for last, after everything else in the frontend works.

---

## Phase 7 — Celery and the job queue

This is the last piece and the most operationally complex. Celery adds Redis as a dependency and introduces worker processes that run separately from the web server.

**Flower is worth running from day one.** It's a web dashboard for Celery that shows running tasks, their status, and their results. Start it with `celery --app=luthier.worker flower` and keep it open in a browser tab while developing. It makes the async job flow visible.

**The job queue is where the full system finally closes.** A user submits requirements through the React form, the FastAPI backend enqueues a Celery task, the worker pulls configurations from `caul`, runs `rosin` simulations, and writes results to the database. The frontend polls for completion and displays results. The first time this works end-to-end is the clearest moment of satisfaction in the whole project.

---

## Staying motivated

A few patterns that tend to kill solo projects:

**The "I'll clean this up later" trap.** The code will never be cleaned up later. Write tests as you go, even minimal ones. A test that runs in 50ms and tells you the operating point solver is broken is worth more than clean code that silently returns wrong numbers.

**Scope creep into the "out of scope" list.** The spec says peak shaving, backup power, and arbitrage are out of scope. They're out of scope because they require the same infrastructure but different EMS strategies, and adding them before the infrastructure is solid just adds bugs. Finish PFR properly before thinking about the others.

**Getting stuck on a perfect model.** The battery model in `rosin.comp` does not need to be publication-quality. A Thevenin equivalent circuit with a good OCV curve is plenty for sizing purposes. The point is to have something that produces physically reasonable results, not to replicate PyBaMM's full DFN model. Move forward with "good enough" and revisit if the numbers are clearly wrong.

**Long stretches without a visible artifact.** Every week or two, make something you can look at: a plot, a CLI output, an API response in the browser. If you find yourself writing code for two weeks with nothing to show, stop and write the simplest possible thing that produces output.

**Not having a real use case to anchor the work.** You mentioned potential professional interest in the field. If you know of a real BESS project (even a public one, a case study, a published tender), use its parameters as your test case from the beginning. Simulating a real 1 MW / 2 MWh BESS providing FCR for the French grid gives the project weight that a synthetic `BatteryModule(capacity=100e3, voltage=400)` doesn't.

---

## Things the spec doesn't mention that will come up

**Environment variables.** From day one, put database URLs, secrets, and API keys in a `.env` file and load them with `python-dotenv`. Never hardcode them. When you add Docker Compose, the `.env` file feeds directly into the container environment. Add `.env` to `.gitignore` immediately.

**A `Makefile` or `justfile`.** As soon as you have more than two or three shell commands to remember (start the database, run migrations, run the tests, start the API), write a `Makefile`. `make test`, `make db-up`, `make migrate` saves a lot of mental overhead and makes it easier to get back into the project after a break.

**Git from day one.** Even for a solo project. Commit often with short messages. The ability to `git diff` your last working state when something breaks is worth the habit.

**The database in tests.** Integration tests for `caul` need a database. Use a separate test database (a different Docker Compose profile, or a different database name in the same container). Never run tests against the development database. This is worth setting up correctly once, early.

**PyBaMM installation.** PyBaMM has a few optional solvers (IDAKLU, CasADi) that require compiled extensions. On some systems they're fiddly to install. Pin your dependency to a specific version in `pyproject.toml` and test the install in a clean virtual environment before writing code that depends on it.
