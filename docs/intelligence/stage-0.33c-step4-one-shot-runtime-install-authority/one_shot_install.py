#!/opt/aios/runtime/venv/bin/python
"""Closed, one-shot Stage 0.33C Step-4 package installer.

This file has no command-line interface.  It performs no network, database,
service, harness, candidate, or authorization operation.
"""

from __future__ import annotations

import datetime as dt
import errno
import hashlib
import json
import os
import pwd
import re
import stat
import subprocess
import sys
import uuid
from pathlib import Path


AUTHORITY_ID = "9d29c855-0f23-4539-a9b9-2e17dc89c49d"
BASELINE = "ca7940b8b94237611a37189e0bed10b002167e78"
REPOSITORY = Path("/opt/aios-src")
REL_EXECUTOR = Path("docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py")
REL_POLICY = Path("docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md")
RUNTIME_PARENT = Path("/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c")
SOURCE_PARENT = Path("/run/aios/stage-0.33c-p4s5-source")
EVIDENCE_DIR = "runtime-sync-evidence"
MARKER = f"step4-install-authority-{AUTHORITY_ID}.json"
RESULT = MARKER + ".result.json"
HARNESS_SHA256 = "b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad"
MANIFEST_ID = "9801b5e4-453d-429a-b51f-e8ffaa17a2c9"
FILES = (
    ("approved-input.json", 1327, 1328, "e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d"),
    ("approved-input-approval.json", 3549, 3550, "266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57"),
)


class Stop(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_json(data: bytes) -> object:
    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for key, value in pairs:
            if key in out:
                raise Stop("duplicate JSON member")
            out[key] = value
        return out

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicate)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Stop("invalid governed JSON") from exc


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_text(value: dt.datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_utc(value: object) -> dt.datetime:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", value):
        raise Stop("invalid approval expiry")
    parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)
    return parsed


def check_no_args_root() -> None:
    if len(sys.argv) != 1:
        raise Stop("arguments are prohibited")
    if os.geteuid() != 0 or pwd.getpwuid(os.geteuid()).pw_name != "root":
        raise Stop("executor must run as root")
    os.umask(0o077)


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ("/usr/bin/git", "-C", str(REPOSITORY), *args),
        check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, env={"PATH": "/usr/bin:/bin"},
    )
    return completed.stdout.strip()


def verify_merged_authority(executor_sha: str) -> str:
    policy = (REPOSITORY / REL_POLICY).read_text(encoding="utf-8")
    match = re.search(r"\| executor SHA-256 \| `([0-9a-f]{64})` \|", policy)
    if match is None or match.group(1) != executor_sha:
        raise Stop("executor is not hash-bound by authority policy")
    if AUTHORITY_ID not in policy or "P4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW" not in policy:
        raise Stop("authority policy identity/classification absent")
    if run_git("status", "--porcelain", "--", str(REL_EXECUTOR), str(REL_POLICY)):
        raise Stop("authority artifacts are not a clean repository revision")
    head = run_git("rev-parse", "HEAD")
    if run_git("merge-base", "--is-ancestor", BASELINE, head) != "":
        # merge-base --is-ancestor intentionally has no stdout on success.
        raise Stop("unexpected merge-base output")
    head_blob = subprocess.run(
        ("/usr/bin/git", "-C", str(REPOSITORY), "show", f"{head}:{REL_EXECUTOR}"),
        check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    ).stdout
    if head_blob != (REPOSITORY / REL_EXECUTOR).read_bytes():
        raise Stop("executor differs from checked-out authority revision")
    merges = run_git("rev-list", "--first-parent", "--merges", head).splitlines()
    for commit in merges:
        try:
            blob = subprocess.run(
                ("/usr/bin/git", "-C", str(REPOSITORY), "show", f"{commit}:{REL_EXECUTOR}"),
                check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            ).stdout
            merged_policy = subprocess.run(
                ("/usr/bin/git", "-C", str(REPOSITORY), "show", f"{commit}:{REL_POLICY}"),
                check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            ).stdout.decode("utf-8")
        except (subprocess.CalledProcessError, UnicodeError):
            continue
        if sha256(blob) == executor_sha and f"`{executor_sha}`" in merged_policy and AUTHORITY_ID in merged_policy:
            return commit
    raise Stop("no merged authority commit contains the reviewed executor and policy binding")


def open_dir(path: Path, uid: int, gid: int, mode: int) -> int:
    if not path.is_absolute():
        raise Stop("directory path must be absolute")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for component in path.parts[1:]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
    except BaseException:
        os.close(fd)
        raise
    info = os.fstat(fd)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != uid or info.st_gid != gid or stat.S_IMODE(info.st_mode) != mode:
        os.close(fd)
        raise Stop(f"unsafe directory metadata: {path}")
    return fd


def absent(dir_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return True
    return False


def read_source(source_fd: int, name: str, semantic: int, transport: int, digest: str) -> bytes:
    fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=source_fd)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o400:
            raise Stop("unsafe private source metadata")
        data = b""
        while len(data) <= transport:
            chunk = os.read(fd, transport + 1 - len(data))
            if not chunk:
                break
            data += chunk
    finally:
        os.close(fd)
    if len(data) != transport or data[semantic:] != b"\n" or sha256(data[:semantic]) != digest:
        raise Stop("private source byte contract mismatch")
    exact_json(data[:semantic])
    return data


def write_all(fd: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        count = os.write(fd, data[offset:])
        if count <= 0:
            raise Stop("short write")
        offset += count


def durable_claim(evidence_fd: int, authority_commit: str, executor_sha: str) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "aios-stage-0.33c-p4s6-consumption-v1",
        "authority_id": AUTHORITY_ID,
        "authority_commit": authority_commit,
        "claim_timestamp_utc": utc_text(utc_now()),
        "executor_path": str(REL_EXECUTOR),
        "executor_sha256": executor_sha,
        "run_as": "root",
        "state": "DURABLY_CONSUMED",
    }
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    try:
        fd = os.open(MARKER, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=evidence_fd)
    except FileExistsError as exc:
        raise Stop("AUTHORITY_CONSUMED") from exc
    try:
        write_all(fd, encoded)
        os.fsync(fd)
    finally:
        # A close error is a STOP and leaves durability uncertain.
        os.close(fd)
    os.fsync(evidence_fd)
    return record


def stage_and_publish(parent_fd: int, source: bytes, final: str, semantic: int, digest: str) -> None:
    stage = f".{uuid.uuid4()}"
    fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
    try:
        write_all(fd, source)
        os.fsync(fd)
        os.fchown(fd, 0, pwd.getpwnam("aiosadmin").pw_gid)
        os.fchmod(fd, 0o440)
        os.fsync(fd)
    finally:
        os.close(fd)
    verify_file(parent_fd, stage, source, semantic, digest)
    os.link(stage, final, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
    os.fsync(parent_fd)
    verify_file(parent_fd, final, source, semantic, digest)
    os.unlink(stage, dir_fd=parent_fd)
    os.fsync(parent_fd)
    verify_file(parent_fd, final, source, semantic, digest)


def verify_file(parent_fd: int, name: str, source: bytes, semantic: int, digest: str) -> None:
    fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent_fd)
    try:
        info = os.fstat(fd)
        data = b""
        while True:
            chunk = os.read(fd, 8192)
            if not chunk:
                break
            data += chunk
    finally:
        os.close(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or
            info.st_gid != pwd.getpwnam("aiosadmin").pw_gid or
            stat.S_IMODE(info.st_mode) != 0o440 or data != source or
            data[semantic:] != b"\n" or sha256(data[:semantic]) != digest):
        raise Stop("staged/final verification failed")


def write_result(evidence_fd: int, claim: dict[str, object], classification: str) -> None:
    result = dict(claim)
    result.update({"schema_version": "aios-stage-0.33c-p4s6-result-v1", "claim_outcome": "CLAIMED",
                   "durability_outcome": "FILE_FSYNC_CLOSE_PARENT_FSYNC_PASS",
                   "final_consumed_status": "DURABLY_CONSUMED", "execution_classification": classification})
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    fd = os.open(RESULT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=evidence_fd)
    try:
        write_all(fd, encoded)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(evidence_fd)


def main() -> int:
    check_no_args_root()
    executor_bytes = (REPOSITORY / REL_EXECUTOR).read_bytes()
    executor_sha = sha256(executor_bytes)
    authority_commit = verify_merged_authority(executor_sha)
    aios = pwd.getpwnam("aiosadmin")
    parent_fd = open_dir(RUNTIME_PARENT, 0, aios.pw_gid, 0o750)
    source_fd = open_dir(SOURCE_PARENT, 0, 0, 0o700)
    evidence_fd = os.open(EVIDENCE_DIR, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent_fd)
    try:
        info = os.fstat(evidence_fd)
        if info.st_uid != aios.pw_uid or info.st_gid != aios.pw_gid or stat.S_IMODE(info.st_mode) != 0o700:
            raise Stop("unsafe consumption directory")
        if not absent(evidence_fd, MARKER) or not absent(evidence_fd, RESULT):
            raise Stop("AUTHORITY_CONSUMED")
        if any(not absent(parent_fd, name) for name, _, _, _ in FILES):
            raise Stop("target already exists")
        sources = [read_source(source_fd, *spec) for spec in FILES]
        approval = exact_json(sources[1][:-1])
        if not isinstance(approval, dict) or approval.get("schema_version") != "aios-stage-0.33c-step4-approved-input-v1":
            raise Stop("approval schema mismatch")
        payload = approval.get("package_payload")
        if not isinstance(payload, dict) or payload.get("harness_sha256") != HARNESS_SHA256:
            raise Stop("approval binding mismatch")
        evidence = payload.get("evidence")
        if not isinstance(evidence, dict) or evidence.get("manifest_id") != MANIFEST_ID:
            raise Stop("manifest binding mismatch")
        if utc_now() >= parse_utc(payload.get("not_after_utc")):
            raise Stop("approval expired")
        # Both target-absence and expiry gates have passed; only now claim.
        claim = durable_claim(evidence_fd, authority_commit, executor_sha)
        for source, spec in zip(sources, FILES):
            stage_and_publish(parent_fd, source, spec[0], spec[1], spec[3])
        for source, spec in zip(sources, FILES):
            verify_file(parent_fd, spec[0], source, spec[1], spec[3])
        write_result(evidence_fd, claim, "STEP4_APPROVED_INPUT_PAIR_INSTALLED_VERIFIED")
        return 0
    finally:
        os.close(evidence_fd)
        os.close(source_fd)
        os.close(parent_fd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Stop, OSError, subprocess.CalledProcessError) as exc:
        print(f"STOP: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
