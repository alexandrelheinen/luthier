# Contributing to luthier

This document holds luthier's own project context: requirement traceability,
the CI-enforced governance mechanism, and the quality gates specific to this
repository. Generic engineering method (spec-driven development, the V-cycle,
TDD, git safety, code principles, naming, Python style) lives in the shared
[.guidelines/](.guidelines/) submodule; `AGENTS.md` and `CLAUDE.md` are thin
bridge files pointing there and to this document. Do not add `.cursor/rules/`,
`GEMINI.md`, `.windsurfrules`, `.github/copilot-instructions.md`, or any other
rule-dump file — those remain the sanctioned exception's only two siblings.

## Table of contents

1. [Development setup](#development-setup)
2. [Spec-driven development, the V-cycle, and TDD](#spec-driven-development-the-v-cycle-and-tdd)
3. [Requirement traceability](#requirement-traceability)
4. [Unitary commits](#unitary-commits)
5. [Quality gates](#quality-gates)
6. [Method enforcement (CI/CD)](#method-enforcement-cicd)
7. [Definition of Ready and Definition of Done](#definition-of-ready-and-definition-of-done)
8. [Pull request workflow](#pull-request-workflow)
9. [Code principles](#code-principles)
10. [Rules for AI agents](#rules-for-ai-agents)
11. [Pre-merge checklist](#pre-merge-checklist)

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

## Spec-driven development, the V-cycle, and TDD

luthier follows the shared spec-driven development, V-cycle, and TDD method
described in [.guidelines/workflow/sdd.md](.guidelines/workflow/sdd.md),
[.guidelines/workflow/integration.md](.guidelines/workflow/integration.md),
and [.guidelines/workflow/tdd.md](.guidelines/workflow/tdd.md). Nothing about
that method is luthier-specific; the sections below cover only what is.

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

Git safety rules (no config changes, no destructive commands, no skipped
hooks, no force-push to `main`, no committed secrets) are generic and live in
[.guidelines/agents/claude.md](.guidelines/agents/claude.md).

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
| Single constitution (only the sanctioned `AGENTS.md`/`CLAUDE.md` bridge files, no other rule-dump file) | guard against `.cursor/rules/`, `GEMINI.md`, `.windsurfrules`, `.github/copilot-instructions.md` | `governance` |
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
      [.guidelines/workflow/sdd.md](.guidelines/workflow/sdd.md).
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

Scope discipline, avoiding over-engineering, matching conventions, and when
to comment are generic engineering principles; see
[.guidelines/style/comments.md](.guidelines/style/comments.md) and
[.guidelines/agents/claude.md](.guidelines/agents/claude.md). This repo adds
on top of those: public API and new code must be fully typed (mypy strict
must pass), and new runtime dependencies must be justified in the PR
(prefer stdlib when reasonable).

## Rules for AI agents

These rules apply to Cursor agents, cloud agents, and any other automated
contributors. General agent conduct (inferring intent, verifying with real
tools instead of guessing, communication style) lives in
[.guidelines/agents/claude.md](.guidelines/agents/claude.md); the rules below
are the ones specific to this repository's enforcement.

### Scope and files

- Do not create `.cursor/rules/`, `GEMINI.md`, `.windsurfrules`,
  `.github/copilot-instructions.md`, or any other duplicate guideline file.
  `AGENTS.md` and `CLAUDE.md` are the only sanctioned bridge files, and they
  must stay thin pointers to `.guidelines/` and this document.
- Do not edit unrelated files, non-primary git worktrees, or ignored paths unless explicitly asked.
- Do not add markdown files the user did not request (README/CONTRIBUTING updates only when part of the task).

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
- [ ] No rule-dump file was added beyond the sanctioned `AGENTS.md`/`CLAUDE.md`
      bridge files pointing to `.guidelines/` and this document.

If any item fails, do not merge. Fix forward with new unitary commits.
