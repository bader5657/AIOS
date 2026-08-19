# Baseline and Authority Trace

The exact approval baseline is:

`cd44f4b2fd0b18cc2e716ba9619e0ac7d00dfb1e`

At approval preparation, `HEAD`, local `main`, and `origin/main` resolved to that
SHA and the main worktree was clean. The baseline contains the merged Stage 8.1.2
verification closure and therefore preserves the completed Stage 8.1.1 and 8.1.2
gates.

Controlling authority is, in descending order, the Blueprint, Frozen Roadmap,
Authority Hierarchy, Canonical Model, Layer Architecture, Core Platform Execution
Plan, accepted Stage 3 Manifest authority, accepted Stage 5 Registry authority,
accepted Stage 6 Event Engine authority, and closed Stage 8.1.1–8.1.2 evidence.

The Execution Plan row is exactly:

`8.1.3 Integrate Document Manifest → PostgreSQL Registry → Event Engine`

Stage 8.1.4 owns the later Event Engine → AIOS Core boundary.
