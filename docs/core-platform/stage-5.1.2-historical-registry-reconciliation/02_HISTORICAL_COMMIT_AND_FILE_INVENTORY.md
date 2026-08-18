# Historical Commit and File Inventory

## Exact Object

| Field | Value |
|---|---|
| Commit | `d58c1c341e6a27dd40de63baf004505fcc3094e2` |
| Subject | `feat(core-platform): add registry foundation` |
| Historical branch evidence | `origin/sprint-18-conversation-engine` |
| Current-main ancestry | not an ancestor; files absent from current `main` |

## Complete Component Inventory

| Historical path | Proven content |
|---|---|
| `core/registry/__init__.py` | Empty package marker |
| `core/registry/models.py` | Four-field slotted `RegistryRecord` dataclass |
| `core/registry/registry.py` | `Registry.save()` returning its input unchanged |
| `tests/unit/registry/__init__.py` | Empty test-package marker |
| `tests/unit/registry/test_registry.py` | One equality test for pass-through behavior |

The record fields were exactly `id`, `media_type`, `storage_path`, and
`manifest_path`. The test used example values `DOC-001`, `image`,
`/tmp/image.jpg`, and `/tmp/image.json`. Examples and names are historical
facts, not approved values, fields, paths, or formats.

No file is copied, restored, cherry-picked, or made current by this inventory.
