# Exact Deferred and Historical Exceptions

`TELEGRAM SDK COUPLING = EXPLICITLY DEFERRED / ACCEPTED TECHNICAL DEBT`.

The exception is limited to the existing Telegram-facing Adapter, input
classifier, Universal Ingestion, Asset Pipeline, and Telegram Storage paths.
It does not permit Telegram SDK imports in Registry, Event Engine, AIOS Core,
Domain Foundation, Brain, Memory, or Specialist Router. Stage 8.3.1 authorizes
no ports/adapters redesign, DTO normalization layer, or SDK decoupling.

The exact edge `core.adapters.telegram.main → core.mission.status` is classified:

`ACCEPTED EXISTING OUT-OF-PIPELINE BEHAVIOR FOR STAGE 8.3.1`.

This exception applies only to the existing status-command import. It does not
make Mission Status part of official ingestion, grant semantic or business
ownership to Adapter, permit arbitrary downstream imports, authorize new
commands, or expand architecture.
