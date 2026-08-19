# Authority, Baseline, Layer Map, and Import Graph

The Blueprint, Active Layer Architecture, Stage 3.1.4 scoped extension, Core
Platform Execution Plan, Stage 3–8 authorities, and Stage 8.3.1 approval PR #70
control this closure. At verification baseline
`6dab3f786d61006ae1f7899336bca21fa7630a5e`, `HEAD`, local `main`, and
`origin/main` resolved identically and the worktree was clean.

The accepted graph is Adapter→Universal Ingestion; Ingestion→Input Classifier,
RequestContext, Asset Pipeline, Registry, DomainEvent/EventEnvelope, Event
Engine, and AIOS Core; Asset Pipeline→Telegram Storage, Metadata, and Manifest;
Telegram Storage→File Storage; and Event Engine/AIOS Core→Domain Foundation
EventEnvelope contracts. Adapter→Mission Status is the separately classified
exact historical exception.

The active layer map remains Adapter, Ingestion, App, Storage, Core, Domain
Foundation contract, and the bounded Brain target. No Brain, Memory, Specialist,
or business runtime is added. Orchestration does not transfer semantic ownership.
