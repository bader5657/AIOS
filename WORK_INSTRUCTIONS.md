# AIOS Work Instructions

## Project Status

AIOS is currently in the implementation phase.

The Blueprint is frozen.

The Roadmap is frozen.

Implementation must follow the Blueprint.

---

## Source of Truth

Priority:

1. Blueprint
2. Roadmap
3. Existing implementation

Never create a second source of truth.

---

## Engineering Principles

- Business First
- Simplicity First
- Calm Engineering
- Zero Surprise
- Freeze Policy

---

## Development Workflow

Implement one milestone at a time.

Never leave incomplete work.

Do not redesign architecture.

Do not modify frozen modules unless explicitly requested.

---

## Testing

Before every commit:

python3 -m pytest tests/unit

Requirements:

- All tests pass
- No warnings
- Repository compiles successfully

---

## Commit Policy

Use Conventional Commits.

Examples:

feat(core-platform): add event engine

fix(storage): resolve metadata issue

docs: update implementation guide

---

## AI Assistant Rules

Always:

- Read Blueprint first.
- Read Roadmap second.
- Respect frozen architecture.
- Stop after one completed milestone.
- Report progress before continuing.

Never:

- Invent roadmap items.
- Skip milestones.
- Change architecture.
