# Prohibited Reverse-Edge Matrix

The focused AST/static audit must prove these runtime dependency classes absent:

| Source | Prohibited targets |
|---|---|
| Storage | App, Universal Ingestion, Registry, Event Engine, AIOS Core, Brain, Specialist Router, business modules |
| Registry | Universal Ingestion, Asset Pipeline, Storage/Metadata/Manifest runtime owners, Event Engine, AIOS Core, Brain |
| Event Engine | Universal Ingestion, Registry runtime, AIOS Core, Brain, Memory, Specialist Router, business consumers |
| AIOS Core | Universal Ingestion, Registry, Event Engine runtime, Brain runtime, Memory, Specialist Router, business modules, persistence/network clients |
| Domain Foundation | Adapter, Ingestion, Pipeline, Storage, Registry, Event Engine runtime, AIOS Core runtime, infrastructure |
| Asset Pipeline | Registry, Event Engine, AIOS Core, Brain, Specialist Router, business modules |

The audit must also prove that the Stage 8 runtime has zero Brain, Memory, and
Specialist Router imports and no direct dependency on concrete business-domain
behavior. `AIOS_BRAIN_BOUNDARY` is an approved target name, not a Brain runtime
import.
