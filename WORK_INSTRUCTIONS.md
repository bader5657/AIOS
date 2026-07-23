# AIOS Work Instructions

## Purpose

This repository follows the AIOS Blueprint.

The Blueprint is the single source of truth.

The Roadmap defines implementation order.

Do not redesign architecture.

---

# Core Principles

- Business First
- Simplicity First
- Calm Engineering
- Zero Surprise
- Freeze Policy

---

# Architecture Rules

Never modify architecture unless explicitly requested.

Never redesign completed modules.

Never change project structure without approval.

Always preserve backward compatibility.

---

# Development Rules

Implement only one small milestone at a time.

Keep commits small.

Do not leave partially implemented features.

---

# Testing Rules

Every change must satisfy:

- All unit tests pass.
- No warnings.
- Code compiles successfully.
- Repository remains clean.

Always run:

python3 -m pytest tests/unit

before committing.

---

# Commit Rules

Commit only after:

- Tests pass
- No warnings
- git status clean

Use Conventional Commits.

Example:

feat(core-platform): add event dispatcher

---

# Documentation

Update documentation whenever architecture changes.

Never allow documentation to diverge from implementation.

---

# AI Assistant Behavior

When working on this repository:

- Read Blueprint first.
- Read Roadmap second.
- Follow implementation order.
- Never invent roadmap items.
- Never skip milestones.
- Stop after completing one milestone.
- Report progress before continuing.
