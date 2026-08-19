# Failure and Registry Exclusion

- Storage failure returns bounded non-success/readiness false and makes zero
  Metadata and Manifest calls.
- Metadata failure propagates after one Storage and one Metadata call and makes
  zero Manifest calls.
- Manifest failure propagates after one Store/Metadata/Manifest attempt and
  produces no result or readiness.
- Existing Document Manifest regressions separately prove failed writes leave
  no valid-looking completed artifact.
- All spies prove no retry or fallback.

Universal Ingestion handoff evidence supplies an explicit forbidden Registry
fake. The non-ready handoff result makes zero Registry calls. Direct Pipeline
lifecycle evidence ends at Manifest/readiness and imports or calls no Registry,
Event Engine, AIOS Core, or Brain boundary.
