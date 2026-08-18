# Prohibited Scope

Stage 5.4.1 must not:

- expose or recover `manifest_id`;
- change Document Manifest or Asset Pipeline contracts/runtime;
- parse Manifest content or infer identity from its filename;
- modify `core/registry/postgres_registry.py`, Registry exports, schema, or migrations;
- create Registry Entry or canonical Registry identity;
- add delete, upsert, deduplication, retry, pooling, ORM, optimization, or indexes;
- add status vocabulary, relationship semantics, business persistence, or media behavior;
- change adapters, Blueprint, Roadmap, architecture, Stage 3, or Stage 4;
- connect to or migrate production PostgreSQL; or
- begin Stage 5.5 or later work.

Original binary remains outside PostgreSQL. No credentials or runtime data may
enter Git.
