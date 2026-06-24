# Contributing to luthier

This document is the single source of truth for how humans and AI agents contribute to this repository. Do not duplicate these rules in `AGENTS.md`, `.cursor/rules/`, or other files unless explicitly requested by a maintainer.

## Table of contents

1. [Development setup](#development-setup)
2. [Spec-driven development (SDD)](#spec-driven-development-sdd)
3. [Software development lifecycle (V-cycle)](#software-development-lifecycle-v-cycle)
4. [Combining SDD, V-cycle, and TDD](#combining-sdd-v-cycle-and-tdd)
5. [Unitary commits](#unitary-commits)
6. [Quality gates](#quality-gates)
7. [Pull request workflow](#pull-request-workflow)
8. [Code principles](#code-principles)
9. [Rules for AI agents](#rules-for-ai-agents)
10. [Reference documents](#reference-documents)
11. [Pre-merge checklist](#pre-merge-checklist)

## Development setup

Requirements: Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
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
| **pytest** | Unit tests and coverage report | `pytest --cov=luthier --cov-report=term-missing` |

All checks must pass on all supported Python versions in the CI matrix before merge.

Configuration lives in `pyproject.toml`. Do not add duplicate tool config in standalone files unless a maintainer approves an exception.

## Pull request workflow

1. Branch from `main` with a descriptive name (e.g. `feat/add-parser`, `ci/matrix-3.13`).
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
- [ ] **Unitary commits** — each commit is a single logical step.
- [ ] `black --check src tests` passes.
- [ ] `ruff check src tests` passes.
- [ ] `mypy` passes.
- [ ] `pytest` passes with coverage for touched code.
- [ ] CI is green on all matrix Python versions.
- [ ] No secrets, credentials, or generated junk committed.
- [ ] Public API changes are typed and documented if user-facing.
- [ ] PR has summary and test plan.
- [ ] No duplicate AI guideline files were added outside this document.

If any item fails, do not merge. Fix forward with new unitary commits.
