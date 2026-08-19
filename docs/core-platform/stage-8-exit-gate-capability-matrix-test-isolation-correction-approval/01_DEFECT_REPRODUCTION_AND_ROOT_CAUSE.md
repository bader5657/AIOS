# Defect Reproduction and Root Cause

At baseline `936cc68cb663c71a25cd6796dbfb3eb2454ef303`, the capability matrix
passes alone with `5` tests and `15` subtests. It produces `11` capability
subfailures when relevant real runtime modules are imported first and within the
full cumulative suite.

The test installs fake Telegram and Storage modules through import-time
`sys.modules` substitution. That substitution controls a fresh isolated import,
but it cannot replace references already held by cached production modules.
The resulting behavior depends on collection/import order and can reach real
Telegram context or Registry dependencies.

Classification: `TEST ISOLATION DEFECT`. It is not a runtime, Registry,
Adapter, Universal Ingestion, architecture, or Stage 8 contract defect.
