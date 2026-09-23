"""R18B: real file reads and main-path stops, using only temporary fixtures."""
import importlib.util
import json
import os
import sys
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest


EXECUTOR = Path(__file__).resolve().parents[3] / (
    "docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
)
spec = importlib.util.spec_from_file_location("stage033c_r18b_executor", EXECUTOR)
executor = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = executor
spec.loader.exec_module(executor)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


@pytest.fixture
def valid():
    return {
        "schema_version": executor.ACTIVATION_SCHEMA_VERSION,
        "authority_id": executor.AUTHORITY_ID,
        "pr_number": 289,
        "reviewed_head_sha": executor.R13_REVIEWED_HEAD,
        "authority_merge_sha": "b" * 40,
        "expected_runtime_head": "c" * 40,
        "executor_sha256": "d" * 64,
        "policy_reference": str(executor.REL_POLICY),
        "activated_at_utc": "2026-09-20T00:00:00.000000Z",
    }


@pytest.fixture
def reader(tmp_path):
    path = tmp_path / "transport-fixture"
    real_read = executor.read_activation_record
    real_fstat = os.fstat

    def root_ownership(fd):
        # Only ownership is simulated on non-root CI. Actual file type, mode,
        # link count, open(O_NOFOLLOW), and file bytes remain under test.
        fields = list(real_fstat(fd))
        fields[4] = fields[5] = 0
        return os.stat_result(fields)

    with patch.object(executor.os, "fstat", side_effect=root_ownership), \
         patch.object(executor, "check_no_args_root"), \
         patch.object(executor, "read_activation_record", side_effect=lambda: real_read(path)):
        yield path, lambda: real_read(path)


def write_transport(path, data):
    path.write_bytes(data)
    path.chmod(0o400)


def assert_preclaim_stop():
    with ExitStack() as stack:
        counters = [stack.enter_context(patch.object(owner, name)) for owner, name in (
            (executor, "durable_claim"), (executor, "stage_and_publish"),
            (executor.os, "link"),
        )]
        # No later repository/runtime access is allowed to mask a reader failure.
        authority = stack.enter_context(patch.object(
            executor, "verify_merged_authority", side_effect=AssertionError("past reader")))
        with pytest.raises(executor.GovernedStop) as caught:
            executor.main()
        assert caught.value.classification == executor.PRECONDITION_FAILED
        assert caught.value.stage in ("ACTIVATION", "ACTIVATION_SCHEMA")
        for label, counter in zip(("claim", "staging", "publication"), counters):
            assert counter.call_count == 0, label
        authority.assert_not_called()


MALFORMED = {
    "reordered_keys": lambda v: json.dumps(v, separators=(",", ":")).encode() + b"\n",
    "spaces": lambda v: json.dumps(v, sort_keys=True).encode() + b"\n",
    "indentation": lambda v: json.dumps(v, sort_keys=True, indent=2).encode() + b"\n",
    "crlf": lambda v: canonical(v) + b"\r\n",
    "missing_lf": lambda v: canonical(v),
    "double_lf": lambda v: canonical(v) + b"\n\n",
    "trailing_space": lambda v: canonical(v) + b" \n",
    "bom": lambda v: b"\xef\xbb\xbf" + canonical(v) + b"\n",
    "duplicate_key": lambda v: b'{"pr_number":289,' + canonical(v)[1:] + b"\n",
    "invalid_utf8": lambda v: canonical(v).replace(b"2026", b"\xff026") + b"\n",
    "unknown_key": lambda v: canonical({**v, "unknown": 1}) + b"\n",
    "missing_key": lambda v: canonical({k: x for k, x in v.items() if k != "pr_number"}) + b"\n",
    "empty": lambda v: b"",
    "only_lf": lambda v: b"\n",
    "bytes_after_lf": lambda v: canonical(v) + b"\nx\n",
    "trailing_tab": lambda v: canonical(v) + b"\t\n",
    "escaped_ascii": lambda v: canonical(v).replace(b"authority_id", b"\\u0061uthority_id") + b"\n",
}


@pytest.mark.parametrize("case", MALFORMED)
def test_noncanonical_main_rejection(case, valid, reader):
    path, _ = reader
    write_transport(path, MALFORMED[case](valid))
    assert_preclaim_stop()


@pytest.mark.parametrize("value", ["289", 289.0, True, False, None])
def test_pr_number_exact_int_main_rejection(value, valid, reader):
    path, _ = reader
    write_transport(path, canonical({**valid, "pr_number": value}) + b"\n")
    assert_preclaim_stop()


@pytest.mark.parametrize("value", [
    "2026-09-20T00:00:00.000000+00:00",
    "2026-09-20T00:00:00Z",
    "2026-09-20T00:00:00.000Z",
    "2026-09-20T00:00:00.0000000Z",
    "2026-09-20T00:00:00.000000z",
    "2026-09-20T00:00:00.000000+07:00",
    "2026-02-30T00:00:00.000000Z",
])
def test_timestamp_main_rejection(value, valid, reader):
    path, _ = reader
    write_transport(path, canonical({**valid, "activated_at_utc": value}) + b"\n")
    assert_preclaim_stop()


def test_canonical_transport_accepted(valid, reader):
    path, read = reader
    write_transport(path, canonical(valid) + b"\n")
    result = read()
    assert result == valid
    assert len(result) == 9
    assert type(result["pr_number"]) is int
    executor.validate_activation_schema(result, valid["executor_sha256"])


@pytest.mark.parametrize("case", ["symlink", "directory", "mode", "nlink", "uid", "gid"])
def test_metadata_main_rejection(case, valid, reader):
    path, _ = reader
    write_transport(path, canonical(valid) + b"\n")
    if case == "symlink":
        target = path.with_name("symlink-target")
        path.rename(target)
        path.symlink_to(target)
    elif case == "directory":
        path.unlink()
        path.mkdir()
    elif case == "mode":
        path.chmod(0o600)
    elif case == "nlink":
        os.link(path, path.with_name("hardlink"))
    if case in ("uid", "gid"):
        current_fstat = executor.os.fstat

        def bad_owner(fd):
            fields = list(current_fstat(fd))
            fields[4 if case == "uid" else 5] = 1000
            return os.stat_result(fields)

        with patch.object(executor.os, "fstat", side_effect=bad_owner):
            assert_preclaim_stop()
    else:
        assert_preclaim_stop()
