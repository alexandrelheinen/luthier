# Contributing to luthier

This document is the single source of truth for how humans and AI agents contribute to this repository. Do not duplicate these rules in `AGENTS.md`, `.cursor/rules/`, or other files unless explicitly requested by a maintainer.

## Table of contents

1. [Development setup](#development-setup)
2. [Spec-driven development (SDD)](#spec-driven-development-sdd)
3. [Software development lifecycle (V-cycle)](#software-development-lifecycle-v-cycle)
4. [Combining SDD, V-cycle, and TDD](#combining-sdd-v-cycle-and-tdd)
5. [Requirement traceability](#requirement-traceability)
6. [Unitary commits](#unitary-commits)
7. [Quality gates](#quality-gates)
8. [Method enforcement (CI/CD)](#method-enforcement-cicd)
9. [Definition of Ready and Definition of Done](#definition-of-ready-and-definition-of-done)
10. [Pull request workflow](#pull-request-workflow)
11. [Code principles](#code-principles)
12. [Rules for AI agents](#rules-for-ai-agents)
13. [Reference documents](#reference-documents)
14. [Pre-merge checklist](#pre-merge-checklist)

## Development setup

Requirements: Python 3.12 (see `.python-version` and `pyproject.toml`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,reconstruction]"
```

Run the same checks CI runs locally before opening or updating a pull request:

```bash
black src tests
ruff check src tests
mypy
pytest --cov=luthier --cov-report=term-missing
```

## Spec-driven development (SDD)

**Spec-driven development** treats written specifications—not code—as the primary artifact. Code, tests, and design notes are derived from and validated against those specs. In this repository, `CONTRIBUTING.md` is the project constitution; issues, PR descriptions, and acceptance criteria are the feature-level specifications.

### What a spec must contain

Before implementation starts, the spec for a change must be clear enough that an independent reviewer (human or agent) could verify completion without guessing intent:

| Element | Purpose | Where it lives |
| --- | --- | --- |
| **Intent** | Why the change exists | Issue title/body or PR summary |
| **Scope** | What is in and out of bounds | Issue or PR description |
| **Acceptance criteria** | Observable conditions of done | Issue checklist or PR test plan |
| **Constraints** | Non-negotiable rules (types, style, dependencies) | This file + `pyproject.toml` |
| **Design notes** | Interfaces, modules, edge cases (when non-trivial) | PR description or `docs/` |

Write acceptance criteria in concrete, testable language (for example EARS-style: “When …, the system shall …”). Ambiguous specs produce ambiguous code—refine the spec before coding.

### SDD workflow in this repo

1. **Specify** — Capture intent, scope, and acceptance criteria in an issue or PR description. Do not choose implementation details yet unless they are constraints.
2. **Plan** — For non-trivial work, outline modules, public API, dependencies, and test levels (unit / integration / acceptance). Planning is part of the V-cycle left side, not a substitute for it.
3. **Task** — Break the plan into unitary commits (one logical step each). Each task should trace back to at least one acceptance criterion.
4. **Implement & verify** — Execute tasks using TDD at the unit level and the V-cycle at every level. Update the spec if discovery changes scope; do not silently drift.
5. **Review** — PR review checks that code matches the spec and that tests prove the acceptance criteria.

### Rigor levels

| Level | When to use | Spec artifact |
| --- | --- | --- |
| **Spec-first** | Any merged change | Issue or PR with acceptance criteria |
| **Spec-anchored** | Features touching public API or architecture | Above + design notes and test plan |
| **Spec-as-source** | Large or AI-assisted features | Above + explicit task breakdown before coding |

Default for this project: **spec-first** minimum; **spec-anchored** when boundaries or APIs change.

### Rules

- Do not implement without a written spec (issue scope or PR description with acceptance criteria).
- When requirements change mid-task, update the spec first, then code and tests.
- Regressions: extend the spec with a failing test that encodes the bug, then fix.
- Do not add duplicate guideline files (`AGENTS.md`, `.cursor/rules/`); this document is the constitution.

Further reading on SDD methodology: [GitHub Spec Kit — Spec-Driven Development](https://github.com/github/spec-kit/blob/main/spec-driven.md), [Microsoft — Diving into Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit).

## Software development lifecycle (V-cycle)

All work follows the V-model: each downstream activity is validated against its upstream specification. No change skips a left-side phase or its matching right-side verification.

```text
Requirements ──────────────► Acceptance testing
     │                              ▲
System design ─────────────► System testing
     │                              ▲
Architecture ──────────────► Integration testing
     │                              ▲
Detailed design ───────────► Unit testing
     │                              ▲
Implementation ────────────► (executes unit tests)
```

| Phase | Left (specify / design) | Right (verify) | Artifact |
| --- | --- | --- | --- |
| 1 | Capture requirements and acceptance criteria | Acceptance tests / demo against criteria | Issue, spec, or PR description |
| 2 | System design: boundaries, interfaces, failure modes | System-level tests or integration scenarios | Design notes in PR or `docs/` |
| 3 | Architecture: modules, dependencies, public API | Integration tests across modules | Code structure, imports |
| 4 | Detailed design: functions, types, edge cases | Unit tests per module | Typed implementation |
| 5 | Implementation | Unit tests pass locally and in CI | Code + tests |

**Rules:**

- Do not implement without a clear requirement or issue scope.
- Do not merge implementation without tests that exercise the change at the appropriate level (unit minimum; integration when boundaries change).
- Regressions must add a failing test first, then the fix.
- Documentation and type annotations are part of detailed design, not optional cleanup.

## Combining SDD, V-cycle, and TDD

SDD, the V-cycle, and test-driven development (TDD) operate at different layers. Use them together in this order and with this attention:

```text
SDD (what & why)  →  V-cycle (structure each level)  →  TDD (build each unit)
     spec                 design ↔ tests                    red → green → refactor
```

### Order of work

| Step | Method | Activity | Attention |
| --- | --- | --- | --- |
| 1 | **SDD** | Write intent, scope, acceptance criteria | Completeness and testability—no coding yet |
| 2 | **V-cycle** | Map criteria to test levels (acceptance → system → integration → unit) | Every requirement has a matching verification |
| 3 | **V-cycle** | System / architecture / detailed design | Types, modules, public API—still no feature code |
| 4 | **TDD** | Implement each unit: failing test → minimal code → refactor | One behavior at a time; strict typing |
| 5 | **V-cycle** | Run tests bottom-up (unit → integration → acceptance) | Right-side verification against left-side specs |
| 6 | **SDD** | Update spec if behavior changed; PR proves all criteria | Spec and code stay aligned |

### How they reinforce each other

- **SDD → V-cycle:** Acceptance criteria from the spec become acceptance- and system-level tests. Design notes become integration and unit test boundaries.
- **V-cycle → TDD:** Detailed design defines *what* to unit-test; TDD is how you implement and verify at the lowest V level.
- **TDD → SDD:** Failing tests are executable spec fragments. If a test is hard to write, the spec or design is probably unclear—fix upstream.
- **V-cycle discipline:** Do not skip a left-side phase (e.g. implement without design) or its right-side test. Do not merge code without tests at the appropriate level.

### Test-driven development (TDD) in this repo

At the **implementation / unit testing** step of the V-cycle, use TDD:

1. **Red** — Write a small automated test for one behavior; it must fail.
2. **Green** — Write the minimum code to pass.
3. **Refactor** — Remove duplication; keep types and style clean.

Rules (from Kent Beck): do not write production code without a failing test; eliminate duplication. Apply TDD inside `src/luthier/` modules; use pytest under `tests/`. For regressions, the failing test comes first, then the fix.

TDD does not replace higher-level specs: it executes detailed design. System and acceptance tests still come from SDD acceptance criteria via the V-cycle.

### When to pause and re-spec

Stop and update the spec (step 1) when:

- Acceptance criteria are ambiguous or contradictory.
- The change needs a new runtime dependency or public API break.
- Integration tests reveal a requirement that was never specified.
- Scope grows beyond the original issue—split work or amend the spec explicitly.

## Requirement traceability

Every requirement must be **traceable in both directions**: from an acceptance
criterion down to the test that proves it, and from any test back up to the
criterion it verifies. This closes the gap the V-cycle assumes but does not by
itself guarantee — that no left-side requirement is silently dropped on the
right side.

### Acceptance-criteria identifiers

- Acceptance criteria live in [docs/specification.md §10](docs/specification.md)
  and use stable identifiers: `AC-<AREA>-<NN>` (for example `AC-CLI-02`,
  `AC-REC-01`, `AC-QG-02`).
- Identifiers are **append-only**. Never renumber or reuse a retired id; mark it
  removed in the specification change log instead.

### How to trace

| Direction | Where the link lives | Form |
| --- | --- | --- |
| Criterion → verification | Test docstring or test id, **or** the traceability table in [docs/testing.md §3](docs/testing.md) | `"""AC-CLI-02."""` in the test, or a row in the matrix |
| Verification → criterion | Same | The `AC-*` token referenced by the test or row |
| Quality-gate criteria (`AC-QG-*`) | [docs/testing.md §9 CI mapping](docs/testing.md) | A CI step is the verification, mapped in the table |

**Rule:** every `AC-*` defined in the specification must be referenced by at
least one test file or by `docs/testing.md`. A criterion with no verification is
an incomplete spec, not "future work" — either add the (possibly `xfail`) test or
remove the criterion from the spec. This is enforced automatically; see
[Method enforcement](#method-enforcement-cicd).

### No silent skips

Tests are the executable right side of the V-cycle. They must not be quietly
disabled:

- `@pytest.mark.skip` / `skipif` and `xfail` are allowed **only** with a
  `reason=` that names the blocking `AC-*` id or a tracking note (for example a
  milestone such as M1, or an environmental precondition such as missing golden
  images). Markers are validated with `--strict-markers` / `--strict-config`.
- Do not lower or remove a quality gate (coverage `fail_under`, lint rule
  selection, the supported Python version) to make a change pass. Changing a gate requires a
  matching update to [docs/decisions.md](docs/decisions.md) and a note in the PR.

## Unitary commits

**Each logical step is one commit.** A PR may contain many commits; that is expected and preferred over squashing unrelated work.

A unitary commit:

- Addresses exactly one concern (e.g. “add pytest config”, “add ruff lint rules”, “implement `hello()`”).
- Builds and passes relevant checks for that concern where applicable.
- Has a message that states *why* in one short subject line (50–72 characters), with optional body for context.

Examples of **separate** commits:

- `build: add pyproject.toml with hatchling and project metadata`
- `feat: add luthier package scaffold under src layout`
- `test: add pytest suite and configuration`
- `chore: configure Black formatter`
- `chore: configure Ruff linter`
- `chore: configure mypy strict mode`
- `ci: add GitHub Actions quality workflow`
- `docs: add CONTRIBUTING.md`

Do **not** combine unrelated changes in one commit (e.g. formatting + feature + CI in a single commit).

### Commit message convention (enforced)

Subjects follow **[Conventional Commits](https://www.conventionalcommits.org/)**
so history is machine-parseable and the unitary-commit rule is checkable:

```text
<type>(<optional scope>): <imperative summary>
```

| Rule | Value |
| --- | --- |
| Allowed `type` | `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, `style`, `revert` |
| Subject length | ≤ 72 characters; imperative mood; no trailing period |
| Body (optional) | Blank line, then *why* and context; wrap at ~72 columns |
| Breaking change | `!` after type/scope (e.g. `feat!:`) or a `BREAKING CHANGE:` body footer |

Branch names follow `<type>/<slug>` (for example `feat/add-parser`,
`ci/governance-job`). Both the subject convention and branch prefix are validated
in CI on pull requests; see [Method enforcement](#method-enforcement-cicd).

### Git safety (humans and agents)

- Never update git config in this repository.
- Never run destructive git commands (`push --force`, `reset --hard`, etc.) unless a maintainer explicitly requests it.
- Never skip hooks (`--no-verify`, `--no-gpg-sign`) unless explicitly requested.
- Never force-push to `main`.
- Avoid `git commit --amend` except when: (1) amend was explicitly requested, or (2) a commit you just created was auto-modified by a hook and has not been pushed.
- If a commit fails due to a hook, fix the issue and create a **new** commit; do not amend a failed commit.
- Never commit secrets (`.env`, credentials, keys). Warn maintainers if they ask to commit sensitive files.
- Do not push or create commits unless asked; when asked, follow the unitary-commit rule above.

## Quality gates

CI enforces the following on every push to `main` and on every pull request:

| Tool | Purpose | Command |
| --- | --- | --- |
| **Black** | PEP 8 formatting | `black --check src tests` |
| **Ruff** | Linting (style, bugs, imports) | `ruff check src tests` |
| **mypy** | Static type checking (`strict`) | `mypy` |
| **pytest** | Unit tests and coverage report (≥ 80% line coverage on `luthier`; see `fail_under` in `pyproject.toml`) | `pytest --cov=luthier --cov-report=term-missing` |

All checks must pass on Python 3.12 in CI before merge.

Configuration lives in `pyproject.toml`. Do not add duplicate tool config in standalone files unless a maintainer approves an exception.

## Method enforcement (CI/CD)

A method that is only documented is a suggestion. In this repository the method
is **mechanically enforced**: the same checks run for a human and for any AI
agent, and they cannot be skipped to land a change. CI is the gate, not a
courtesy.

### Enforcement matrix

Each methodology rule maps to an automated check and the CI job that runs it.
"No skip allowed" means the job is **required** and failing it blocks merge.

| Method rule (this document) | Automated check | CI job / step |
| --- | --- | --- |
| PEP 8 formatting | `black --check src tests` | `quality` |
| Lint, imports, bugs | `ruff check src tests` | `quality` |
| Typed detailed design | `mypy` (strict) | `quality` |
| Unit + integration tests pass | `pytest` (strict markers/config) | `quality` |
| Coverage ≥ threshold (AC-QG-02) | `pytest --cov` + `fail_under` | `quality` |
| Supported Python (AC-QG-01) | `quality` job on Python 3.12 | `quality` |
| SDD artifacts exist | presence checks for `docs/*.md`, `README.md` | `governance` |
| Single constitution (no duplicate guideline files) | guard against `AGENTS.md`, `.cursor/rules/`, `CLAUDE.md`, `.github/copilot-instructions.md` | `governance` |
| Requirement traceability (every `AC-*` verified) | `scripts/check_governance.py` | `governance` |
| Stack ↔ code consistency (`{algorithm_name}.py` matches `name` and is documented) | `scripts/check_governance.py` | `governance` |
| Conventional, unitary commits | commit-subject lint over the PR commit range | `governance` (PR only) |
| Branch naming `<type>/<slug>` | branch-name check | `governance` (PR only) |
| PR has Summary + Test plan | PR-body check | `governance` (PR only) |
| Acceptance criteria on golden data | `pytest -m acceptance` when golden images present | `acceptance` (PR and `main` push) |

The authoritative implementation is [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
and the reusable script [`scripts/check_governance.py`](scripts/check_governance.py).
Run the governance script locally before pushing:

```bash
python scripts/check_governance.py
```

### Rules

- Do **not** weaken, comment out, or `continue-on-error` a required check to make
  CI green. Fix the change, not the gate.
- Required checks must remain required. Removing a gate is itself a spec change
  (update `docs/decisions.md` and explain it in the PR).
- New layers, slots, or algorithm modules must keep the governance checks green
  (matching files, names, and documentation) — see
  [docs/architecture.md §10.3](docs/architecture.md#103-adding-a-new-algorithm).

## Definition of Ready and Definition of Done

These bound when work may **start** and when it may **merge**. They make the
SDD → V-cycle → TDD flow checkable rather than aspirational.

### Definition of Ready (before coding)

- [ ] Intent, scope, and **acceptance criteria** are written (issue or PR), each
      with an `AC-*` id where it asserts observable behavior.
- [ ] Rigor level chosen (spec-first / spec-anchored / spec-as-source) per
      [SDD rigor levels](#rigor-levels).
- [ ] Test levels identified for each criterion (unit / integration / acceptance).
- [ ] No undocumented new runtime dependency or public-API break.

### Definition of Done (before merge)

- [ ] Every touched or added `AC-*` is verified by a test or `docs/testing.md`
      mapping (traceability check passes).
- [ ] Unitary, Conventional commits; branch named `<type>/<slug>`.
- [ ] All required CI jobs green (`quality`, `governance`, and `acceptance` when
      applicable) on Python 3.12.
- [ ] Docs updated when behavior, architecture, or the algorithm stack changed
      (`specification.md`, `architecture.md`, `testing.md`, `decisions.md`,
      `algorithms.md`, `README.md` as relevant).
- [ ] No quality gate weakened to pass.

## Pull request workflow

1. Branch from `main` with a descriptive name (e.g. `feat/add-parser`, `ci/single-python`).
2. Make **unitary commits** as you work.
3. Push the branch and open a PR against `main`.
4. PR description must include:
   - **Summary** — what changed and why (1–3 bullets).
   - **Test plan** — checklist of manual or automated verification steps.
5. Ensure CI is green before requesting review.
6. Address review feedback in new unitary commits (not amended mega-commits unless maintainer requests squash).

Maintainers use `gh` for GitHub operations when automating PR creation.

## Code principles

1. **Minimize scope** — smallest correct diff. No drive-by refactors or unrelated edits.
2. **Avoid over-engineering** — no premature abstractions, wrappers, or speculative error handling.
3. **Match existing conventions** — read surrounding code; match naming, types, imports, and documentation level.
4. **Comments** — code should be self-explanatory; comment only non-obvious business logic or deep technical constraints.
5. **Useful tests only** — add tests that cover real behavior and regressions; avoid trivial assertions.
6. **Type annotations** — public API and new code must be fully typed; mypy strict must pass.
7. **Dependencies** — justify new runtime dependencies in the PR; prefer stdlib when reasonable.

## Rules for AI agents

These rules apply to Cursor agents, cloud agents, and any other automated contributors.

### Context and intent

- Infer intent from the full conversation and issue scope, not only the latest message.
- Treat mid-task messages as refinements unless the user clearly changes direction.
- Read `CONTRIBUTING.md` (this file) before making changes; it supersedes generic model habits.

### Scope and files

- Do not create `AGENTS.md`, `.cursor/rules/`, or duplicate guideline files; **this file is the only guideline document**.
- Do not edit unrelated files, non-primary git worktrees, or ignored paths unless explicitly asked.
- Do not add markdown files the user did not request (README/CONTRIBUTING updates only when part of the task).

### Execution

- Use the tools available (terminal, tests, linters); do not guess when verification is possible.
- Run quality gates locally when feasible before pushing.
- Fix linter/type errors you introduce; do not disable rules without maintainer approval.
- Follow SDD first (clear spec), then the V-cycle (design ↔ tests at each level), then TDD for unit implementation.

### Git and PRs

- **Unitary commits** — one logical step per commit; many commits per PR is correct.
- Create commits only when the user asks (or when completing an explicit “create PR” request that implies commits).
- When creating a PR: inspect `git status`, `git diff`, and branch history; write an accurate summary and test plan.
- Return the PR URL when creation succeeds.
- Never force-push `main`; never amend pushed commits unless explicitly requested.
- **PR completion gate** — work on a pull request is **not complete** until the branch is **pushed** and **every required CI job is green** on that push (`quality`, `governance`, and `acceptance` when it runs). Poll CI after each push (for example `gh pr checks <number>`); fix failures and push again until all jobs pass. Do not tell the user the PR is ready for review or merged-worthy while any job is failing or pending.

### Communication

- Be precise and concise; use code citations when referencing existing code.
- Proportional responses — simple fixes do not need long essays.
- Do not end every message with unsolicited follow-up offers.

## Reference documents

Use these resources to understand the methods, standards, and tools enforced in this repository. When an external guide conflicts with this file or `pyproject.toml`, **this repository wins**.

### Development methods

| Topic | Resource | Notes |
| --- | --- | --- |
| **Spec-driven development (SDD)** | [GitHub Spec Kit — Spec-Driven Development](https://github.com/github/spec-kit/blob/main/spec-driven.md) | Primary SDD methodology reference |
| | [Microsoft — Spec-Driven Development with Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit) | Workflow: specify → plan → tasks → implement |
| | [SpecDD framework](https://specdd.ai/) | File-based, source-adjacent specs (optional pattern) |
| **Test-driven development (TDD)** | [Kent Beck — Test-Driven Development: By Example](https://www.pearson.com/en-us/subject-catalog/p/test-driven-development-by-example/P200000003380) (book) | Canonical TDD reference |
| | [Kent Beck — Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd) | Modern summary of the TDD workflow |
| | [IBM — What is TDD?](https://www.ibm.com/think/topics/test-driven-development) | Accessible overview |
| **V-cycle / V-model** | [Teaching Agile — V-Model](https://teachingagile.com/sdlc/models/v-model) | Verification vs validation; phase correspondence |
| | [IAPM — The V-model explained](https://www.iapm.net/en/blog/v-model/) | Historical context and phase diagram |
| **SDLC** | [ISO/IEC/IEEE 12207 — Software life cycle processes](https://www.iso.org/standard/90219.html) | International SDLC process framework |
| | [ISO/IEC/IEEE 15289 — Life-cycle information items](https://www.iso.org/standard/74909.html) | Documentation content for SDLC phases |

### Python language and style

| Topic | Resource | Notes |
| --- | --- | --- |
| **PEP 8** | [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) | Formatting and naming; enforced via Black + Ruff |
| **PEP 257** | [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) | Docstrings for public API |
| **PEP 484** | [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) | Typing model; enforced via mypy strict |
| **PEP 561** | [PEP 561 — Distributing type information](https://peps.python.org/pep-0561/) | Typed package metadata (`Typing :: Typed`) |

### Packaging and project layout

| Topic | Resource | Notes |
| --- | --- | --- |
| **Project metadata** | [PEP 621 — pyproject.toml metadata](https://peps.python.org/pep-0621/) | `[project]` table in `pyproject.toml` |
| **Build interface** | [PEP 517 — Build backend interface](https://peps.python.org/pep-0517/) | `hatchling` as build backend |
| **Src layout** | [PyPA — src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | This repo uses `src/luthier/` |
| | [pyOpenSci — Python package structure](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html) | Practical layout guide |
| **Hatchling** | [Hatchling documentation](https://hatch.pypa.io/latest/config/build/) | Build backend configured in `pyproject.toml` |

### Quality tools (repo configuration)

| Tool | Resource | Command in this repo |
| --- | --- | --- |
| **Black** | [Black documentation](https://black.readthedocs.io/en/stable/) | `black src tests` |
| **Ruff** | [Ruff documentation](https://docs.astral.sh/ruff/) | `ruff check src tests` |
| **mypy** | [mypy documentation](https://mypy.readthedocs.io/en/stable/) | `mypy` (strict mode) |
| **pytest** | [pytest documentation](https://docs.pytest.org/en/stable/) | `pytest --cov=luthier --cov-report=term-missing` |

Configuration for all tools lives in `pyproject.toml`. Do not duplicate settings in standalone config files without maintainer approval.

## Pre-merge checklist

Every contributor (human or agent) must confirm before merge:

- [ ] Spec is clear: intent, scope, and acceptance criteria are written and addressed.
- [ ] Changes follow SDD → V-cycle → TDD (spec, design/tests at each level, TDD for units).
- [ ] Every touched `AC-*` is traceable to a test or `docs/testing.md` mapping.
- [ ] **Unitary, Conventional commits** — each commit is a single logical step; branch is `<type>/<slug>`.
- [ ] `black --check src tests` passes.
- [ ] `ruff check src tests` passes.
- [ ] `mypy` passes.
- [ ] `pytest` passes with coverage for touched code.
- [ ] `python scripts/check_governance.py` passes.
- [ ] CI is green on Python 3.12 (`quality`, `governance`, and `acceptance` when applicable).
- [ ] No quality gate was weakened to pass.
- [ ] No secrets, credentials, or generated junk committed.
- [ ] Public API changes are typed and documented if user-facing.
- [ ] PR has summary and test plan.
- [ ] No duplicate AI guideline files were added outside this document.

If any item fails, do not merge. Fix forward with new unitary commits.
