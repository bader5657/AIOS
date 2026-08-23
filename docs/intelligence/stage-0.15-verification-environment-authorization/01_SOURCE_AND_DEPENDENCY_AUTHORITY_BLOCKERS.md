# Source and Dependency Authority Blockers

## Exact source identity

Git cannot resolve requested SHA
`21aeed1ad0f87a3a28835a9aaf4b67a0f8cab44f` to an object. Git history, PR #163,
and the accepted reconciliation record identify the implementation commit as
`21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f`.

An authorization whose mandatory pre-test identity gate names a nonexistent
object cannot activate. The source SHA must first be corrected explicitly; no
history rewrite is needed or authorized.

## Test dependency authority

The repository `requirements.txt` pins runtime dependencies but does not list
`pytest`. No `pyproject.toml`, test requirements file, lock file, or other
separate current test-dependency manifest was found. Existing repository
governance also records that pytest is not pinned and no separate test
dependency manifest exists.

Therefore the instruction to install only repository-approved dependencies
does not presently authorize acquiring pytest. The exact missing authority is:

1. explicit approval of the corrected source SHA
   `21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f`; and
2. a bounded test-tooling acquisition authority defining the approved pytest
   version/source and any required test-only dependency set without changing
   production dependency authority.

No package-index access, package installation, provider SDK acquisition, live
network integration, or production mutation occurred.
