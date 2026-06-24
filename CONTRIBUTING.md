# Contributing to luthier

This document is the single source of truth for how humans and AI agents contribute to this repository. Do not duplicate these rules in `AGENTS.md`, `.cursor/rules/`, or other files unless explicitly requested by a maintainer.

## Table of contents

1. [Development setup](#development-setup)
2. [Software development lifecycle (V-cycle)](#software-development-lifecycle-v-cycle)
3. [Unitary commits](#unitary-commits)
4. [Quality gates](#quality-gates)
5. [Pull request workflow](#pull-request-workflow)
6. [Code principles](#code-principles)
7. [Rules for AI agents](#rules-for-ai-agents)
8. [Pre-merge checklist](#pre-merge-checklist)

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
- Follow the V-cycle: requirement → design → implementation → tests at the matching level.

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

## Pre-merge checklist

Every contributor (human or agent) must confirm before merge:

- [ ] Requirement or issue scope is clear and addressed.
- [ ] Changes follow the V-cycle (design + matching tests).
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
