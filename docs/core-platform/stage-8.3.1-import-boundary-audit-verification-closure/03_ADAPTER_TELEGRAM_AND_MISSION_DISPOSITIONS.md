# Adapter, Telegram SDK, and Mission Status Dispositions

The Adapter's internal runtime imports are limited to Universal Ingestion and
the exact Mission Status edge. It does not import Registry, Event Engine, AIOS
Core, Storage internals, Metadata, Manifest, Brain, Memory, Specialist Router,
or concrete business modules.

Telegram SDK coupling is exactly:

`EXPLICITLY DEFERRED / ACCEPTED TECHNICAL DEBT`

Its exception scope remains only Adapter, classifier, Universal Ingestion,
Asset Pipeline, and Telegram Storage. The AST guard permits no Telegram import
in Registry, Event Engine, AIOS Core, Domain Foundation, Brain, Memory, or
Specialist Router.

The exact historical disposition is:

`Adapter → core.mission.status = ACCEPTED EXISTING OUT-OF-PIPELINE BEHAVIOR FOR STAGE 8.3.1`

It is not official ingestion, a generic Mission/business exemption, new command
authority, or architecture expansion.
