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
from dataclasses import dataclass
from contextlib import ExitStack
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

INPUT_TYPES={"text","image","voice","document","pdf","doc","spreadsheet","video","audio","web_link","youtube_link","unknown"}
PIPELINE_COMPAT={"pdf":"document","doc":"document","spreadsheet":"document","web_link":"text","youtube_link":"text"}
EVENT_FAILURE_CODES={"TIMEOUT","UNAVAILABLE","REJECTED","UNKNOWN"}


class GovernedStop(RuntimeError):
    def __init__(self, classification: str, stage: str, artifact: str | None = None, errno_code: int | None = None):
        super().__init__(classification); self.classification=classification; self.stage=stage; self.artifact=artifact; self.errno_code=errno_code

class Stop(GovernedStop):
    def __init__(self, message: str, stage: str = "UNKNOWN", artifact: str | None = None, errno_code: int | None = None):
        super().__init__(message, stage, artifact, errno_code)

PRECONDITION_FAILED="PRECONDITION_FAILED"
APPROVAL_EXPIRED="APPROVAL_EXPIRED"
TARGET_ALREADY_EXISTS="TARGET_ALREADY_EXISTS"
APPROVED_BYTES_INVALID="APPROVED_BYTES_INVALID"
AUTHORITY_CONSUMED="AUTHORITY_CONSUMED"
APPROVED_INPUT_STAGING_FAILED="APPROVED_INPUT_STAGING_FAILED"
STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION="STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION"
APPROVED_INPUT_FINAL_VERIFICATION_FAILED="APPROVED_INPUT_FINAL_VERIFICATION_FAILED"
APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE="APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE"
RESULT_EVIDENCE_WRITE_FAILED="RESULT_EVIDENCE_WRITE_FAILED"
_WRITABLE_FDS: dict[int, tuple[str, int, int]] = {}
TERMINAL_CLASSIFICATIONS = frozenset({PRECONDITION_FAILED, APPROVAL_EXPIRED, TARGET_ALREADY_EXISTS, APPROVED_BYTES_INVALID, AUTHORITY_CONSUMED, "CONSUMPTION_DURABILITY_UNCERTAIN", "CONSUMPTION_DURABILITY_FAILED", APPROVED_INPUT_STAGING_FAILED, STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION, APPROVED_INPUT_FINAL_VERIFICATION_FAILED, APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE, RESULT_EVIDENCE_WRITE_FAILED, "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED"})

@dataclass
class ExecutionState:
    authority_commit: str = ""
    executor_sha: str = ""
    consumption_state: str = "NOT_CONSUMED"
    current_stage: str = "PRECONDITION"
    input_staged: bool = False
    input_published: bool = False
    input_final_verified: bool = False
    input_cleanup_complete: bool = False
    approval_staged: bool = False
    approval_published: bool = False
    approval_final_verified: bool = False
    approval_cleanup_complete: bool = False

def validate_uuid4_canonical_lowercase(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", value) or str(uuid.UUID(value)) != value: raise Stop(APPROVED_BYTES_INVALID, "UUID")
    return value

def validate_sha256_lowercase(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value): raise Stop(APPROVED_BYTES_INVALID, "SHA")
    return value

def validate_utc_microsecond_z(value: object) -> dt.datetime:
    return parse_utc(value)

def validate_approval_safe_string(value: object, max_len: int = 256) -> str:
    if not isinstance(value, str) or len(value) > max_len or any(ord(c) < 0x20 or ord(c) == 0x7f or 0xd800 <= ord(c) <= 0xdfff for c in value): raise Stop(APPROVED_BYTES_INVALID, "SAFE_STRING")
    return value


@dataclass(frozen=True)
class VerifiedFile:
    st_dev: int
    st_ino: int
    st_uid: int
    st_gid: int
    mode: int
    size: int

def make_stage_name(final_basename: str) -> str:
    if final_basename not in {x[0] for x in FILES} or "/" in final_basename or "\\" in final_basename:
        raise Stop(PRECONDITION_FAILED, "STAGING_BASENAME")
    return f".{final_basename}.stage-{uuid.uuid4()}"

def staging_name(final: str) -> str:
    if final not in {x[0] for x in FILES} or "/" in final or "\\" in final:
        raise Stop(PRECONDITION_FAILED, "STAGING_BASENAME")
    return make_stage_name(final)

def expected_provenance_pointers(item_count: int) -> set[str]:
    if not isinstance(item_count,int) or not 1 <= item_count <= 10: raise Stop(APPROVED_BYTES_INVALID,"PROVENANCE")
    base={"/trusted_receipt_facts/supplier_name","/trusted_receipt_facts/document_number","/trusted_receipt_facts/document_date","/trusted_receipt_facts/received_at"}
    fields=("candidate_material_description","canonical_display_name","size_description","specification","material_id","full_colly_count","qty_per_full_colly","partial_qty","total_qty","unit","line_number")
    return base | {f"/trusted_receipt_facts/items/{i}/{field}" for i in range(item_count) for field in fields}

def validate_approval_closed_schema(value: object) -> dict[str, object]:
    top={"schema_version","package_payload","package_payload_sha256"}
    if not isinstance(value,dict) or set(value)!=top: raise Stop(APPROVED_BYTES_INVALID,"APPROVAL_SCHEMA")
    if value["schema_version"]!="aios-stage-0.33c-step4-approved-input-v1": raise Stop(APPROVED_BYTES_INVALID,"APPROVAL_SCHEMA")
    p=value["package_payload"]
    keys={"approval_id","approved_at_utc","not_after_utc","project_owner_approval_reference","repository_commit","harness_sha256","python_path","python_version","controlled_callable","evidence","trusted_facts_sha256","input_semantic_sha256","input_transport_sha256","input_semantic_bytes","input_transport_bytes","item_count","trusted_fact_provenance","more_than_three_items_justification"}
    if not isinstance(p,dict) or set(p)!=keys: raise Stop(APPROVED_BYTES_INVALID,"APPROVAL_PAYLOAD")
    validate_uuid4_canonical_lowercase(p["approval_id"]); approved=validate_utc_microsecond_z(p["approved_at_utc"]); expiry=validate_utc_microsecond_z(p["not_after_utc"])
    if approved>expiry or expiry<=utc_now(): raise Stop(APPROVAL_EXPIRED,"APPROVAL_TIME")
    validate_approval_safe_string(p["project_owner_approval_reference"],128)
    if not isinstance(p["repository_commit"],str) or not re.fullmatch(r"[0-9a-f]{40}",p["repository_commit"]): raise Stop(APPROVED_BYTES_INVALID,"COMMIT")
    if p["harness_sha256"]!=HARNESS_SHA256: raise Stop(APPROVED_BYTES_INVALID,"HARNESS")
    if p["python_path"]!="/opt/aios/runtime/venv/bin/python" or p["python_version"]!="3.12.3" or p["controlled_callable"]!="core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate": raise Stop(APPROVED_BYTES_INVALID,"RUNTIME")
    e=p["evidence"]; ek={"manifest_reference","manifest_id","manifest_sha256","manifest_size_bytes","represented_media_type","manifest_received_at","stored_original_size_bytes","stored_original_sha256","mime_type","registry_record_id"}
    if not isinstance(e,dict) or set(e)!=ek: raise Stop(APPROVED_BYTES_INVALID,"APPROVAL_EVIDENCE")
    validate_uuid4_canonical_lowercase(e["manifest_id"]); validate_sha256_lowercase(e["manifest_sha256"]); validate_utc_microsecond_z(e["manifest_received_at"])
    if not isinstance(e["manifest_reference"],str) or not re.fullmatch(r"/opt/aios/data/documents/manifests/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json",e["manifest_reference"]): raise Stop(APPROVED_BYTES_INVALID,"MANIFEST")
    for k,lo,hi in (("manifest_size_bytes",0,4194304),("registry_record_id",0,9223372036854775807)):
        if not isinstance(e[k],int) or not lo<=e[k]<=hi: raise Stop(APPROVED_BYTES_INVALID,"EVIDENCE_SIZE")
    if e["stored_original_size_bytes"] is not None and (not isinstance(e["stored_original_size_bytes"],int) or not 0<=e["stored_original_size_bytes"]<=9223372036854775807): raise Stop(APPROVED_BYTES_INVALID,"EVIDENCE_SIZE")
    for k in ("stored_original_sha256",):
        if e[k] is not None: validate_sha256_lowercase(e[k])
    if e["mime_type"] is not None: validate_approval_safe_string(e["mime_type"],255)
    for k in ("trusted_facts_sha256","input_semantic_sha256","input_transport_sha256"): validate_sha256_lowercase(p[k])
    if p["input_semantic_bytes"]!=1327 or p["input_transport_bytes"]!=1328 or p["item_count"]<1 or p["item_count"]>10: raise Stop(APPROVED_BYTES_INVALID,"INPUT_BINDING")
    if not isinstance(p["trusted_fact_provenance"],dict) or set(p["trusted_fact_provenance"]) != expected_provenance_pointers(p["item_count"]): raise Stop(APPROVED_BYTES_INVALID,"PROVENANCE")
    for k,v in p["trusted_fact_provenance"].items():
        if v not in {"EVIDENCE_DERIVED","PROJECT_OWNER_APPROVED"}: raise Stop(APPROVED_BYTES_INVALID,"PROVENANCE")
    if p["more_than_three_items_justification"] is not None: validate_approval_safe_string(p["more_than_three_items_justification"],512)
    validate_sha256_lowercase(value["package_payload_sha256"])
    canonical = json.dumps(p, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if sha256(canonical) != value["package_payload_sha256"]: raise Stop(APPROVED_BYTES_INVALID, "PAYLOAD_HASH")
    if p["item_count"] > 3 and (not isinstance(p["more_than_three_items_justification"], str) or not p["more_than_three_items_justification"]): raise Stop(APPROVED_BYTES_INVALID, "JUSTIFICATION")
    if p["item_count"] <= 3 and p["more_than_three_items_justification"] is not None: raise Stop(APPROVED_BYTES_INVALID, "JUSTIFICATION")
    return value

def _decimal_string(value: object, maximum: str, zero_allowed: bool = True) -> None:
    if not isinstance(value,str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{0,5}[1-9])?",value): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    from decimal import Decimal
    try: d=Decimal(value)
    except Exception: raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    if not d.is_finite() or d<0 or (not zero_allowed and d==0) or d>Decimal(maximum): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    t=d.as_tuple();
    if max(-t.exponent,0)>6 or len(t.digits)+max(t.exponent,0)>20 or (t.sign and d!=0): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    rendered=format(d,"f").rstrip("0").rstrip(".") or "0"
    if rendered!=value: raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")

def validate_approved_input_closed_schema(value: object) -> dict[str, object]:
    top={"schema_version","ingestion_result","trusted_receipt_facts"}
    if not isinstance(value,dict) or set(value)!=top or value["schema_version"]!="aios-stage-0.33c-one-shot-input-v1": raise Stop(APPROVED_BYTES_INVALID,"INPUT_SCHEMA")
    i=value["ingestion_result"]; ik={"input_type","recognized_input_type","stored_path","manifest_path","metadata","text","register_handoff_ready","process_handoff_ready","route_handoff_ready","respond_acknowledgement_ready","registration_succeeded","registry_record_id","event_publication_attempted","event_delivery_succeeded","event_delivery_failure_code","brain_result"}
    if not isinstance(i,dict) or set(i)!=ik: raise Stop(APPROVED_BYTES_INVALID,"INPUT_SCHEMA")
    if i["input_type"] not in INPUT_TYPES or i["recognized_input_type"] not in INPUT_TYPES or i["input_type"] != PIPELINE_COMPAT.get(i["recognized_input_type"], i["recognized_input_type"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_VALUE")
    if not isinstance(i["manifest_path"],str) or not re.fullmatch(r"/opt/aios/data/documents/manifests/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json",i["manifest_path"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_MANIFEST")
    if i["registration_succeeded"]:
        if not isinstance(i["registry_record_id"],int) or not 1<=i["registry_record_id"]<=9223372036854775807: raise Stop(APPROVED_BYTES_INVALID,"INPUT_REGISTRY")
    elif i["registry_record_id"] is not None: raise Stop(APPROVED_BYTES_INVALID,"INPUT_REGISTRY")
    if i["event_delivery_succeeded"] and not i["event_publication_attempted"]: raise Stop(APPROVED_BYTES_INVALID,"INPUT_EVENT")
    if i["route_handoff_ready"] and not i["event_delivery_succeeded"]: raise Stop(APPROVED_BYTES_INVALID,"INPUT_EVENT")
    if i["event_publication_attempted"] and not i["registration_succeeded"]: raise Stop(APPROVED_BYTES_INVALID,"INPUT_EVENT")
    if i["event_publication_attempted"] and not i["event_delivery_succeeded"] and (not isinstance(i["event_delivery_failure_code"],str) or not i["event_delivery_failure_code"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_EVENT")
    if (not i["event_publication_attempted"] or i["event_delivery_succeeded"]) and i["event_delivery_failure_code"] is not None: raise Stop(APPROVED_BYTES_INVALID,"INPUT_EVENT")
    if not isinstance(i["input_type"],str) or not isinstance(i["recognized_input_type"],str) or i["stored_path"] is not None or i["metadata"]!={} or i["text"]!="" or i["brain_result"] is not None: raise Stop(APPROVED_BYTES_INVALID,"INPUT_VALUE")
    if i["process_handoff_ready"] is not False or i["register_handoff_ready"] is not True or i["respond_acknowledgement_ready"] is not True: raise Stop(APPROVED_BYTES_INVALID,"INPUT_VALUE")
    if not all(type(i[k]) is bool for k in ("route_handoff_ready","registration_succeeded","event_publication_attempted","event_delivery_succeeded")): raise Stop(APPROVED_BYTES_INVALID,"INPUT_VALUE")
    f=value["trusted_receipt_facts"]; fk={"supplier_name","document_number","document_date","received_at","items"}
    if not isinstance(f,dict) or set(f)!=fk: raise Stop(APPROVED_BYTES_INVALID,"INPUT_SCHEMA")
    if not isinstance(f["supplier_name"],str) or not 1<=len(f["supplier_name"])<=128 or any(ord(c)<32 or ord(c)==127 or 0xd800<=ord(c)<=0xdfff for c in f["supplier_name"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_TEXT")
    if f["document_number"] is not None and not isinstance(f["document_number"],str): raise Stop(APPROVED_BYTES_INVALID,"INPUT_TEXT")
    if f["document_date"] is not None and (not isinstance(f["document_date"],str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",f["document_date"])): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DATE")
    validate_utc_microsecond_z(f["received_at"])
    if not isinstance(f["items"],list) or not 1<=len(f["items"] )<=10: raise Stop(APPROVED_BYTES_INVALID,"INPUT_ITEMS")
    lines=[]
    for item in f["items"]:
        keys={"line_number","candidate_material_description","canonical_display_name","size_description","specification","material_id","full_colly_count","qty_per_full_colly","partial_qty","total_qty","unit"}
        if not isinstance(item,dict) or set(item)!=keys: raise Stop(APPROVED_BYTES_INVALID,"INPUT_ITEM")
        if not isinstance(item["line_number"],int) or not 1<=item["line_number"]<=500 or item["line_number"] in lines: raise Stop(APPROVED_BYTES_INVALID,"INPUT_ITEM")
        lines.append(item["line_number"])
        for k in ("candidate_material_description","canonical_display_name","size_description","specification"):
            if item[k] is not None and (not isinstance(item[k],str) or not item[k] or len(item[k])>512 or any(ord(c)<32 or ord(c)==127 or 0xd800<=ord(c)<=0xdfff for c in item[k])): raise Stop(APPROVED_BYTES_INVALID,"INPUT_TEXT")
        if item["material_id"] is not None: validate_uuid4_canonical_lowercase(item["material_id"])
        c=item["full_colly_count"]
        if not isinstance(c,int) or not 0<=c<=1000000: raise Stop(APPROVED_BYTES_INVALID,"INPUT_QTY")
        if c==0 and item["qty_per_full_colly"] is not None: raise Stop(APPROVED_BYTES_INVALID,"INPUT_QTY")
        if c>0: _decimal_string(item["qty_per_full_colly"],"1000000",False)
        _decimal_string(item["partial_qty"],"100000000",True); _decimal_string(item["total_qty"],"100000000",False)
        if item["unit"] not in {"sheet","pcs","kg","roll","pack"}: raise Stop(APPROVED_BYTES_INVALID,"INPUT_UNIT")
        from decimal import Decimal
        q = Decimal(item["qty_per_full_colly"]) if item["qty_per_full_colly"] is not None else Decimal(0)
        partial = Decimal(item["partial_qty"]); total = Decimal(item["total_qty"])
        if total != Decimal(c)*q + partial: raise Stop(APPROVED_BYTES_INVALID,"INPUT_EQUATION")
        if item["unit"] == "sheet" and any(x != x.to_integral_value() for x in (partial,total,q)): raise Stop(APPROVED_BYTES_INVALID,"INPUT_UNIT")
    return value

def validate_approved_input(value: object) -> dict[str, object]: return validate_approved_input_closed_schema(value)


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
    except OSError as exc:
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=exc.errno) from exc
    try:
        os.close(fd)
    except OSError as exc:
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=exc.errno) from exc
    try:
        os.fsync(evidence_fd)
    except OSError as exc:
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=exc.errno) from exc
    return record


def stage_and_publish(parent_fd: int, source: bytes, final: str, semantic: int, digest: str) -> None:
    stage = make_stage_name(final)
    fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd); _WRITABLE_FDS[fd] = (final, 0, 0)
    try:
        write_all(fd, source)
        os.fsync(fd)
        os.fchown(fd, 0, pwd.getpwnam("aiosadmin").pw_gid)
        os.fchmod(fd, 0o440)
        os.fsync(fd)
    finally:
        os.close(fd); _WRITABLE_FDS.pop(fd, None)
    stage_meta = verify_file(parent_fd, stage, source, semantic, digest)
    parent_meta = os.fstat(parent_fd)
    if stage_meta.st_dev != parent_meta.st_dev: raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "DEVICE", final)
    if any(dev == stage_meta.st_dev and ino == stage_meta.st_ino for _, dev, ino in _WRITABLE_FDS.values()): raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "WRITABLE_FD", final)
    os.link(stage, final, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
    os.fsync(parent_fd)
    final_meta = verify_file(parent_fd, final, source, semantic, digest)
    if final_meta.st_dev != parent_meta.st_dev or final_meta.st_dev != stage_meta.st_dev or final_meta.st_ino != stage_meta.st_ino:
        raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "INODE", final)
    os.unlink(stage, dir_fd=parent_fd)
    os.fsync(parent_fd)
    verify_file(parent_fd, final, source, semantic, digest)


def verify_file(parent_fd: int, name: str, source: bytes, semantic: int, digest: str) -> VerifiedFile:
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
    return VerifiedFile(info.st_dev, info.st_ino, info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode), len(data))


def write_failure_result(evidence_fd: int, state: ExecutionState, failure: GovernedStop) -> None:
    record = {"schema_version":"aios-stage-0.33c-p4s6-result-v1", "authority_id":AUTHORITY_ID, "executor_sha256":state.executor_sha, "authority_commit":state.authority_commit, "timestamp_utc":utc_text(utc_now()), "stage":failure.stage, "classification":failure.classification, "consumption_state":state.consumption_state, "artifact_role":failure.artifact or "NONE", "input_published":state.input_published, "input_verified":state.input_final_verified, "approval_published":state.approval_published, "approval_verified":state.approval_final_verified, "errno_code":failure.errno_code}
    fd = os.open(RESULT, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC, 0o600, dir_fd=evidence_fd)
    try:
        write_all(fd, json.dumps(record, sort_keys=True, separators=(",", ":")).encode()+b"\n"); os.fsync(fd); os.close(fd)
    except OSError as exc:
        try: os.close(fd)
        except OSError: pass
        raise Stop(RESULT_EVIDENCE_WRITE_FAILED, "RESULT", errno_code=exc.errno) from exc
    os.fsync(evidence_fd)

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
        input_obj = exact_json(sources[0][:-1])
        validate_approved_input_closed_schema(input_obj)
        if json.dumps(input_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() != sources[0][:-1]: raise Stop(APPROVED_BYTES_INVALID, "INPUT_CANONICAL")
        approval_bytes = sources[1][:-1]
        approval = exact_json(approval_bytes)
        validate_approval_closed_schema(approval)
        if sha256(sources[0][:-1]) != approval["package_payload"]["input_semantic_sha256"] or sha256(sources[0]) != approval["package_payload"]["input_transport_sha256"]: raise Stop(APPROVED_BYTES_INVALID, "INPUT_HASH")
        payload = approval["package_payload"]
        trusted = input_obj["trusted_receipt_facts"]
        if sha256(json.dumps(trusted, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()) != payload["trusted_facts_sha256"]: raise Stop(APPROVED_BYTES_INVALID, "TRUSTED_FACTS_HASH")
        ev = payload["evidence"]
        if input_obj["ingestion_result"]["manifest_path"] != ev["manifest_reference"] or ev["manifest_id"] != ev["manifest_reference"][-41:-5]: raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
        if json.dumps(approval, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() != approval_bytes:
            raise Stop(APPROVED_BYTES_INVALID, "APPROVAL_CANONICAL")
        payload = approval.get("package_payload")
        if not isinstance(payload, dict) or payload.get("harness_sha256") != HARNESS_SHA256:
            raise Stop("approval binding mismatch")
        evidence = payload.get("evidence")
        if not isinstance(evidence, dict) or evidence.get("manifest_id") != MANIFEST_ID:
            raise Stop("manifest binding mismatch")
        if utc_now() >= parse_utc(evidence.get("not_after_utc")):
            raise Stop(APPROVAL_EXPIRED, "APPROVAL_EXPIRY")
        # Both target-absence and expiry gates have passed; only now claim.
        claim = durable_claim(evidence_fd, authority_commit, executor_sha)
        state = ExecutionState(authority_commit=authority_commit, executor_sha=executor_sha, consumption_state="DURABLY_CONSUMED")
        for index, (source, spec) in enumerate(zip(sources, FILES)):
            state.current_stage = "INPUT" if index == 0 else "APPROVAL"
            try:
                stage_and_publish(parent_fd, source, spec[0], spec[1], spec[3])
            except GovernedStop as failure:
                if index == 1 and state.input_final_verified: failure = GovernedStop(STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION, failure.stage, spec[0], failure.errno_code)
                try: write_failure_result(evidence_fd, state, failure)
                except GovernedStop: pass
                raise failure
            if index == 0: state.input_published = state.input_final_verified = state.input_cleanup_complete = True
            else: state.approval_published = state.approval_final_verified = state.approval_cleanup_complete = True
        write_result(evidence_fd, claim, "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED")
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
