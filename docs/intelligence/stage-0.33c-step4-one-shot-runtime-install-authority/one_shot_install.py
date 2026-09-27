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


AUTHORITY_ID = "7bc638e2-e1f4-4e87-a54a-4d0df031b130"
BASELINE = "ca7940b8b94237611a37189e0bed10b002167e78"
REPOSITORY = Path("/opt/aios-src")
REL_EXECUTOR = Path("docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py")
REL_POLICY = Path("docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md")
REL_R13_AUTHORITY = Path("docs/intelligence/stage-0.33c-p4s7-runtime-install-execution-authority/00_FINAL_ONE_SHOT_RUNTIME_INSTALL_AUTHORITY.md")
RUNTIME_PARENT = Path("/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c")
ACTIVATION_RECORD = RUNTIME_PARENT / "p4s7-recovery-activation.json"
TRUST_SELECTOR = RUNTIME_PARENT / "p4s7-recovery-review-merge-trust.json"
REL_R32 = Path("docs/intelligence/stage-0.33c-p4s7-r32-recovery-bindings/00_RECOVERY_EXECUTOR_PACKAGE_BINDING_AMENDMENT.md")
REL_R34 = Path("docs/intelligence/stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md")
REL_TRUST = Path("docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md")
EVIDENCE_PREFIX = "docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/records/"
R32_MERGE = "ba717f6990d775748f46d62ef03a696f1618077b"
R34_MERGE = "8e9a8023742773b055e17dba002b2ebf07528118"
TRUST_MERGE = "7f124e307d9a516b4ce278d800c92d29d476cf5e"
TRUST_SHA256 = "7b9e5ee9daf7b9ffe387b63ebff6629d97546a27eb0f5207271ac5ec1fb9f957"
SELECTOR_KEYS = frozenset({"schema_version", "evidence_commit", "evidence_path", "evidence_transport_sha256"})
EVIDENCE_KEYS = frozenset({"schema_version", "repository", "binding_id", "authority_id",
    "policy_reference", "activation_governance_reference", "approval_id", "package_payload_sha256",
    "expected_runtime_head", "executor_sha256", "policy_sha256", "reader", "r32", "r34", "supersedes"})
REVIEW_KEYS = frozenset({"pr_number", "reviewed_head_sha", "merge_sha"})
PREDECESSOR_KEYS = frozenset({"kind", "commit", "path", "transport_sha256"})
UUID_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

INPUT_SOURCE_PARENT = Path("/run/aios/stage-0.33c-p4s5-source")
APPROVAL_SOURCE_PARENT = Path("/run/aios/stage-0.33c-p4s5-recovery-source")
RECOVERY_APPROVAL_ID = "3a478d87-5c4f-4778-9f88-2228f4d7167f"
RECOVERY_APPROVED_AT = "2026-09-26T23:24:12.093093Z"
RECOVERY_NOT_AFTER = "2026-10-03T23:24:12.093093Z"
RECOVERY_PAYLOAD_SHA256 = "be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e"
RECOVERY_TF_A = "c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065"
RETAINED_DATA_ROOT = Path("/opt/aios/data/documents")
EVIDENCE_DIR = "runtime-sync-evidence"
MARKER = f"step4-install-authority-{AUTHORITY_ID}.json"
RESULT = MARKER + ".result.json"
HARNESS_SHA256 = "b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad"
MANIFEST_ID = "9801b5e4-453d-429a-b51f-e8ffaa17a2c9"
FILES = (
    ("approved-input.json", 1327, 1328, "e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d"),
    ("approved-input-approval.json", 3579, 3580, "6ea5fc118e375ac035f321110198eb43811fb5b991a095554c15d0a6cbeb16c9"),
)

INPUT_TYPES={"text","image","voice","document","pdf","doc","spreadsheet","video","audio","web_link","youtube_link","unknown"}
PIPELINE_COMPAT={"pdf":"document","doc":"document","spreadsheet":"document","web_link":"text","youtube_link":"text"}
EVENT_FAILURE_CODES={"TIMEOUT","UNAVAILABLE","REJECTED","UNKNOWN"}
EXPECTED_INTERPRETER = "/opt/aios/runtime/venv/bin/python"
EXPECTED_PYTHON_VERSION = (3, 12, 3)
ACTIVATION_SCHEMA_VERSION = "aios-stage-0.33c-p4s7-recovery-activation-v1"
ACTIVATION_KEYS = frozenset({
    "schema_version", "authority_id", "expected_runtime_head", "executor_sha256",
    "policy_reference", "approval_id", "package_payload_sha256", "activated_at_utc",
})


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
class ArtifactState:
    staged: bool = False
    preverified: bool = False
    published: bool = False
    final_verified: bool = False
    cleanup_complete: bool = False
    writable_fd_closed: bool = False
    writable_fd_absent: bool = False
    stage_device_verified: bool = False
    final_inode_verified: bool = False
    final_metadata: dict[str, int] | None = None
    semantic_prefix_hash_verified: bool = False
    transport_bytes_verified: bool = False



@dataclass
class ExecutionState:
    authority_commit: str = ""
    executor_sha: str = ""
    consumption_state: str = "UNUSED"
    current_stage: str = "PRECONDITION"
    parent_metadata: dict[str, int] | None = None
    pre_targets_absent: bool | None = None
    approval_freshness_valid: bool | None = None
    source_semantic_sha256: tuple[str, str] | None = None
    source_transport_bytes: tuple[int, int] | None = None
    input: ArtifactState = None
    approval: ArtifactState = None
    input_staged: bool = False
    input_published: bool = False
    input_final_verified: bool = False
    input_cleanup_complete: bool = False
    approval_staged: bool = False
    approval_published: bool = False
    approval_final_verified: bool = False
    approval_cleanup_complete: bool = False

    def __post_init__(self):
        if self.input is None: self.input = ArtifactState()
        if self.approval is None: self.approval = ArtifactState()

def derive_primary_classification(state: ExecutionState, failure_context: object = None) -> str:
    context = failure_context if isinstance(failure_context, dict) else {}
    if state.consumption_state == "CLAIMED":
        return "CONSUMPTION_DURABILITY_UNCERTAIN"
    if context.get("cleanup") == "postpublication":
        return APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE
    if state.input.final_verified and not state.approval.final_verified and state.consumption_state in {"DURABLY_CONSUMED", "EXECUTION_STARTED"}:
        return STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION
    if context.get("cleanup") == "prepublication":
        return "APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE"
    if context.get("stage") == "staging":
        return APPROVED_INPUT_STAGING_FAILED
    if context.get("classification"):
        return context["classification"]
    if (state.consumption_state in {"DURABLY_CONSUMED", "EXECUTION_STARTED"} and
            state.input.published and state.input.final_verified and state.input.cleanup_complete and
            state.approval.published and state.approval.final_verified and state.approval.cleanup_complete and
            context.get("pair_reverified") is True):
        return "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED"
    return PRECONDITION_FAILED

def validate_uuid4_canonical_lowercase(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", value) or str(uuid.UUID(value)) != value: raise Stop(APPROVED_BYTES_INVALID, "UUID")
    return value

def validate_sha256_lowercase(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value): raise Stop(APPROVED_BYTES_INVALID, "SHA")
    return value

def validate_utc_microsecond_z(value: object) -> dt.datetime:
    try:
        return parse_utc(value)
    except GovernedStop as exc:
        raise Stop(APPROVED_BYTES_INVALID, "TIMESTAMP") from exc

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
    if type(item_count) is not int or not 1 <= item_count <= 10: raise Stop(APPROVED_BYTES_INVALID,"PROVENANCE")
    base={"/trusted_receipt_facts/supplier_name","/trusted_receipt_facts/document_number","/trusted_receipt_facts/document_date","/trusted_receipt_facts/received_at"}
    fields=("candidate_material_description","canonical_display_name","size_description","specification","material_id","full_colly_count","qty_per_full_colly","partial_qty","total_qty","unit","line_number")
    return base | {f"/trusted_receipt_facts/items/{i}/{field}" for i in range(item_count) for field in fields}

def _read_regular_nofollow(path: Path, stage: str) -> tuple[bytes, os.stat_result]:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as exc:
        raise Stop(APPROVED_BYTES_INVALID, stage, errno_code=exc.errno) from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise Stop(APPROVED_BYTES_INVALID, stage)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks), info
    finally:
        os.close(fd)


def _retained_original_path(storage_path: object, retained_root: Path) -> Path:
    if not isinstance(storage_path, str) or not storage_path:
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH")
    candidate = Path(storage_path)
    if not candidate.is_absolute():
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH")
    try:
        candidate.relative_to(retained_root)
    except ValueError as exc:
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH") from exc
    if candidate == retained_root or ".." in candidate.parts:
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH")
    current = Path(candidate.anchor)
    for component in candidate.parts[1:-1]:
        current /= component
        try:
            info = os.stat(current, follow_symlinks=False)
        except OSError as exc:
            raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH", errno_code=exc.errno) from exc
        if not stat.S_ISDIR(info.st_mode):
            raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_PATH")
    return candidate


def verify_retained_manifest(manifest_reference: str, evidence: dict[str, object], *, manifest_root: Path | None = None, retained_root: Path | None = None) -> dict[str, object]:
    if not isinstance(manifest_reference, str) or not re.fullmatch(r"/opt/aios/data/documents/manifests/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json", manifest_reference):
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST")
    path = (manifest_root / Path(manifest_reference).name) if manifest_root is not None else Path(manifest_reference)
    data, _ = _read_regular_nofollow(path, "MANIFEST")
    if sha256(data) != evidence.get("manifest_sha256") or len(data) != evidence.get("manifest_size_bytes"):
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
    obj = exact_json(data)
    try:
        from core.storage.document_manifest import validate_manifest
        validate_manifest(obj)
    except Exception as exc:
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_SCHEMA") from exc
    if (obj.get("manifest_id") != evidence.get("manifest_id") or
            obj.get("represented_media_type") != evidence.get("represented_media_type") or
            obj.get("received_at") != evidence.get("manifest_received_at")):
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
    metadata = obj.get("metadata", {})
    if evidence.get("mime_type") != metadata.get("mime_type"):
        raise Stop(APPROVED_BYTES_INVALID, "MIME_BINDING")
    original_root = retained_root if retained_root is not None else RETAINED_DATA_ROOT
    original = _retained_original_path(obj.get("storage_path"), original_root)
    original_bytes, original_info = _read_regular_nofollow(original, "ORIGINAL")
    original_digest = sha256(original_bytes)
    if original_info.st_size != obj.get("file_size_bytes") or original_digest != obj.get("checksum_sha256"):
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_BINDING")
    if evidence.get("stored_original_size_bytes") is not None and evidence["stored_original_size_bytes"] != original_info.st_size:
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_BINDING")
    if evidence.get("stored_original_sha256") is not None and evidence["stored_original_sha256"] != original_digest:
        raise Stop(APPROVED_BYTES_INVALID, "ORIGINAL_BINDING")
    return obj


def validate_manifest_evidence(e: object, *, authoritative: dict[str, object] | None = None) -> None:
    if not isinstance(e,dict): raise Stop(APPROVED_BYTES_INVALID,"APPROVAL_EVIDENCE")
    ref=e.get("manifest_reference"); mid=e.get("manifest_id")
    if not isinstance(ref,str) or not re.fullmatch(r"/opt/aios/data/documents/manifests/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json",ref) or ref[-41:-5] != mid: raise Stop(APPROVED_BYTES_INVALID,"MANIFEST_BINDING")
    if authoritative:
        for key in ("manifest_sha256","manifest_size_bytes","represented_media_type","manifest_received_at","stored_original_size_bytes","stored_original_sha256","mime_type","registry_record_id"):
            if key in authoritative and e.get(key) != authoritative[key]: raise Stop(APPROVED_BYTES_INVALID,"EVIDENCE_BINDING")

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
    validate_manifest_evidence(e)
    if type(e["manifest_size_bytes"]) is not int or not 0 <= e["manifest_size_bytes"] <= 4194304:
        raise Stop(APPROVED_BYTES_INVALID, "EVIDENCE_SIZE")
    registry_id = e["registry_record_id"]
    if registry_id is not None and (type(registry_id) is not int or not 1 <= registry_id <= 9223372036854775807):
        raise Stop(APPROVED_BYTES_INVALID, "EVIDENCE_REGISTRY")
    if e["stored_original_size_bytes"] is not None and (type(e["stored_original_size_bytes"]) is not int or not 0<=e["stored_original_size_bytes"]<=9223372036854775807): raise Stop(APPROVED_BYTES_INVALID,"EVIDENCE_SIZE")
    for k in ("stored_original_sha256",):
        if e[k] is not None: validate_sha256_lowercase(e[k])
    if e["mime_type"] is not None: validate_approval_safe_string(e["mime_type"],255)
    for k in ("trusted_facts_sha256","input_semantic_sha256","input_transport_sha256"): validate_sha256_lowercase(p[k])
    if (type(p["input_semantic_bytes"]) is not int or type(p["input_transport_bytes"]) is not int or
            not 0 <= p["input_semantic_bytes"] <= 86835 or p["input_transport_bytes"] != p["input_semantic_bytes"] + 1 or
            type(p["item_count"]) is not int or not 1 <= p["item_count"] <= 10):
        raise Stop(APPROVED_BYTES_INVALID, "INPUT_BINDING")
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

def validate_registry_binding(approved_input: dict[str, object], approval: dict[str, object]) -> None:
    ingestion = approved_input["ingestion_result"]
    evidence = approval["package_payload"]["evidence"]
    succeeded = ingestion["registration_succeeded"]
    input_id = ingestion["registry_record_id"]
    approval_id = evidence["registry_record_id"]
    if type(succeeded) is not bool:
        raise Stop(APPROVED_BYTES_INVALID, "REGISTRY_BINDING")
    if succeeded:
        if type(input_id) is not int or not 1 <= input_id <= 9223372036854775807:
            raise Stop(APPROVED_BYTES_INVALID, "REGISTRY_BINDING")
    elif input_id is not None:
        raise Stop(APPROVED_BYTES_INVALID, "REGISTRY_BINDING")
    if approval_id != input_id or type(approval_id) is not type(input_id):
        raise Stop(APPROVED_BYTES_INVALID, "REGISTRY_BINDING")


def trusted_facts_dto_sha256(trusted: dict[str, object]) -> str:
    """Project validated harness facts into the authoritative TF-A DTO hash."""

    try:
        from decimal import Decimal
        from core.app.material_receipts.candidate_create_authorization import (
            trusted_facts_sha256,
        )
        from core.app.material_receipts.candidate_input import (
            TrustedReceiptFacts,
            TrustedReceiptItemFacts,
        )

        received_at = validate_utc_microsecond_z(trusted["received_at"])
        document_date = (
            dt.date.fromisoformat(trusted["document_date"])
            if trusted["document_date"] is not None
            else None
        )
        items = tuple(
            TrustedReceiptItemFacts(
                line_number=item["line_number"],
                candidate_material_description=item["candidate_material_description"],
                canonical_display_name=item["canonical_display_name"],
                size_description=item["size_description"],
                specification=item["specification"],
                material_id=(uuid.UUID(item["material_id"]) if item["material_id"] else None),
                full_colly_count=item["full_colly_count"],
                qty_per_full_colly=(Decimal(item["qty_per_full_colly"]) if item["qty_per_full_colly"] is not None else None),
                partial_qty=Decimal(item["partial_qty"]),
                total_qty=Decimal(item["total_qty"]),
                unit=item["unit"],
            )
            for item in trusted["items"]
        )
        facts = TrustedReceiptFacts(
            supplier_name=trusted["supplier_name"],
            document_number=trusted["document_number"],
            document_date=document_date,
            received_at=received_at,
            items=items,
        )
        return trusted_facts_sha256(facts)
    except GovernedStop:
        raise
    except Exception as exc:
        raise Stop(APPROVED_BYTES_INVALID, "TRUSTED_FACTS_PROJECTION") from exc


def validate_frozen_package(input_transport: bytes, approval_transport: bytes, *, manifest_root: Path | None = None, retained_root: Path | None = None) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    if not input_transport.endswith(b"\n") or input_transport.endswith(b"\n\n"):
        raise Stop(APPROVED_BYTES_INVALID, "INPUT_TRANSPORT")
    if not approval_transport.endswith(b"\n") or approval_transport.endswith(b"\n\n"):
        raise Stop(APPROVED_BYTES_INVALID, "APPROVAL_TRANSPORT")
    input_semantic = input_transport[:-1]
    approval_semantic = approval_transport[:-1]
    input_obj = exact_json(input_semantic)
    validate_approved_input_closed_schema(input_obj)
    if json.dumps(input_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() != input_semantic:
        raise Stop(APPROVED_BYTES_INVALID, "INPUT_CANONICAL")
    approval = exact_json(approval_semantic)
    validate_approval_closed_schema(approval)
    if json.dumps(approval, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() != approval_semantic:
        raise Stop(APPROVED_BYTES_INVALID, "APPROVAL_CANONICAL")
    payload = approval["package_payload"]
    if (payload["input_semantic_bytes"] != len(input_semantic) or
            payload["input_transport_bytes"] != len(input_transport) or
            payload["input_semantic_sha256"] != sha256(input_semantic) or
            payload["input_transport_sha256"] != sha256(input_transport)):
        raise Stop(APPROVED_BYTES_INVALID, "INPUT_HASH")
    trusted = input_obj["trusted_receipt_facts"]
    # TF-A binds semantic DTO facts. The two checks above independently bind
    # exact semantic input bytes and exact transport bytes (including the LF).
    if payload["trusted_facts_sha256"] != trusted_facts_dto_sha256(trusted):
        raise Stop(APPROVED_BYTES_INVALID, "TRUSTED_FACTS_HASH")
    if payload["item_count"] != len(trusted["items"]):
        raise Stop(APPROVED_BYTES_INVALID, "ITEM_COUNT")
    validate_registry_binding(input_obj, approval)
    evidence = payload["evidence"]
    ingestion = input_obj["ingestion_result"]
    if ingestion["manifest_path"] != evidence["manifest_reference"] or evidence["manifest_id"] != evidence["manifest_reference"][-41:-5]:
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
    manifest = verify_retained_manifest(evidence["manifest_reference"], evidence, manifest_root=manifest_root, retained_root=retained_root)
    if manifest["manifest_id"] != evidence["manifest_id"]:
        raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
    validate_recovery_binding(input_transport, approval_transport, input_obj, approval)
    return input_obj, approval, manifest


def validate_recovery_binding(input_transport: bytes, approval_transport: bytes,
                              input_obj: dict, approval: dict) -> None:
    """Bind the schema-validated package to the single reviewed recovery pair."""
    payload = approval["package_payload"]
    if payload["approval_id"] != RECOVERY_APPROVAL_ID:
        raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_APPROVAL_ID")
    if (payload["approved_at_utc"] != RECOVERY_APPROVED_AT or
            payload["not_after_utc"] != RECOVERY_NOT_AFTER):
        raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_APPROVAL_TIME")
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode()
    if not sha256(canonical) == approval["package_payload_sha256"] == RECOVERY_PAYLOAD_SHA256:
        raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_PAYLOAD_HASH")
    if not payload["trusted_facts_sha256"] == trusted_facts_dto_sha256(input_obj["trusted_receipt_facts"]) == RECOVERY_TF_A:
        raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_TRUSTED_FACTS_HASH")
    ingestion = input_obj["ingestion_result"]
    if (payload["evidence"]["registry_record_id"] is not None or
            ingestion["registry_record_id"] is not None or
            ingestion["registration_succeeded"] is not False):
        raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_MODEL_B")
    for data, (name, semantic, transport, digest) in zip((input_transport, approval_transport), FILES):
        if (len(data) != transport or semantic != transport - 1 or
                data[semantic:] != b"\n" or sha256(data[:semantic]) != digest):
            raise Stop(APPROVED_BYTES_INVALID, "RECOVERY_SOURCE_BINDING", name)


def _decimal_string(value: object, maximum: str, zero_allowed: bool = True) -> None:
    if not isinstance(value,str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{0,5}[1-9])?",value): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    from decimal import Decimal
    try: d=Decimal(value)
    except Exception: raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    if not d.is_finite() or d<0 or (not zero_allowed and d==0) or d>Decimal(maximum): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    t=d.as_tuple();
    if max(-t.exponent,0)>6 or len(t.digits)+max(t.exponent,0)>20 or (t.sign and d!=0): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")
    # Integer trailing zeros are valid; fractional trailing zeros are noncanonical.
    if "." in value and value.endswith("0"): raise Stop(APPROVED_BYTES_INVALID,"INPUT_DECIMAL")

def validate_approved_input_closed_schema(value: object) -> dict[str, object]:
    top={"schema_version","ingestion_result","trusted_receipt_facts"}
    if not isinstance(value,dict) or set(value)!=top or value["schema_version"]!="aios-stage-0.33c-one-shot-input-v1": raise Stop(APPROVED_BYTES_INVALID,"INPUT_SCHEMA")
    i=value["ingestion_result"]; ik={"input_type","recognized_input_type","stored_path","manifest_path","metadata","text","register_handoff_ready","process_handoff_ready","route_handoff_ready","respond_acknowledgement_ready","registration_succeeded","registry_record_id","event_publication_attempted","event_delivery_succeeded","event_delivery_failure_code","brain_result"}
    if not isinstance(i,dict) or set(i)!=ik: raise Stop(APPROVED_BYTES_INVALID,"INPUT_SCHEMA")
    if i["input_type"] not in INPUT_TYPES or i["recognized_input_type"] not in INPUT_TYPES or i["input_type"] != PIPELINE_COMPAT.get(i["recognized_input_type"], i["recognized_input_type"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_VALUE")
    if not isinstance(i["manifest_path"],str) or not re.fullmatch(r"/opt/aios/data/documents/manifests/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json",i["manifest_path"]): raise Stop(APPROVED_BYTES_INVALID,"INPUT_MANIFEST")
    if i["registration_succeeded"]:
        if type(i["registry_record_id"]) is not int or not 1<=i["registry_record_id"]<=9223372036854775807: raise Stop(APPROVED_BYTES_INVALID,"INPUT_REGISTRY")
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
        if type(item["line_number"]) is not int or not 1<=item["line_number"]<=500 or item["line_number"] in lines: raise Stop(APPROVED_BYTES_INVALID,"INPUT_ITEM")
        lines.append(item["line_number"])
        for k in ("candidate_material_description","canonical_display_name","size_description","specification"):
            if item[k] is not None and (not isinstance(item[k],str) or not item[k] or len(item[k])>512 or any(ord(c)<32 or ord(c)==127 or 0xd800<=ord(c)<=0xdfff for c in item[k])): raise Stop(APPROVED_BYTES_INVALID,"INPUT_TEXT")
        if item["material_id"] is not None: validate_uuid4_canonical_lowercase(item["material_id"])
        c=item["full_colly_count"]
        if type(c) is not int or not 0<=c<=1000000: raise Stop(APPROVED_BYTES_INVALID,"INPUT_QTY")
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
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z", value):
        raise Stop("invalid approval expiry")
    parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)
    return parsed


def check_no_args_root() -> None:
    if len(sys.argv) != 1:
        raise Stop("arguments are prohibited")
    if os.geteuid() != 0 or pwd.getpwuid(os.geteuid()).pw_name != "root":
        raise Stop("executor must run as root")
    os.umask(0o077)


def _git_command(*args: str) -> tuple[str, ...]:
    # Command-line disabling cannot be undone by inherited replacement settings:
    # both subprocess helpers construct a fresh PATH-only environment.
    return ("/usr/bin/git", "--no-replace-objects", "-c",
            "safe.directory=/opt/aios-src", "-C", str(REPOSITORY), *args)


def run_git(*args: str) -> str:
    try:
        completed = subprocess.run(
            _git_command(*args),
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, env={"PATH": "/usr/bin:/bin"},
        )
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise Stop(PRECONDITION_FAILED, "RUNTIME_REPOSITORY", errno_code=getattr(exc, "errno", None)) from exc
    return completed.stdout.rstrip("\n")


def _git_bytes(*args: str) -> bytes:
    try:
        return subprocess.run(
            _git_command(*args),
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"},
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Stop(PRECONDITION_FAILED, "RUNTIME_REPOSITORY", errno_code=getattr(exc, "errno", None)) from exc


def _require(condition: bool, stage: str) -> None:
    if not condition:
        raise Stop(PRECONDITION_FAILED, stage)


def _closed(value: object, keys: frozenset[str], stage: str) -> None:
    _require(type(value) is dict and set(value) == keys, stage)


def _hex(value: object, length: int) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{%d}" % length, value) is not None


def canonical_record(transport: bytes, stage: str) -> dict[str, object]:
    try:
        _require(transport.endswith(b"\n") and not transport.startswith(b"\xef\xbb\xbf"), stage)
        semantic = transport[:-1]
        value = exact_json(semantic)
        canonical = json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        _require(type(value) is dict and canonical == semantic, stage)
        return value
    except (GovernedStop, ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Stop(PRECONDITION_FAILED, stage) from exc


def _protected_record(path: Path, stage: str) -> bytes:
    """Fixed caller constants only; retain and recheck every traversal descriptor."""
    descriptors = []
    try:
        descriptors.append(os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC))
        for component in path.parent.parts[1:]:
            descriptors.append(os.open(component, os.O_RDONLY | os.O_DIRECTORY |
                                       os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=descriptors[-1]))
        parent = os.fstat(descriptors[-1])
        governed_gid = pwd.getpwnam("aiosadmin").pw_gid
        parent_signature = lambda i: (i.st_dev, i.st_ino, i.st_mode, i.st_uid,
                                      i.st_gid, i.st_mtime_ns, i.st_ctime_ns)
        _require(stat.S_ISDIR(parent.st_mode) and parent.st_uid == 0
                 and parent.st_gid == governed_gid
                 and stat.S_IMODE(parent.st_mode) == 0o750, stage)
        fd = os.open(path.name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=descriptors[-1])
        descriptors.append(fd)
        before = os.fstat(fd)
        _require(stat.S_ISREG(before.st_mode) and before.st_uid == before.st_gid == 0
                 and stat.S_IMODE(before.st_mode) == 0o400 and before.st_nlink == 1, stage)
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        signature = lambda i: (i.st_dev, i.st_ino, i.st_mode, i.st_uid, i.st_gid,
                               i.st_nlink, i.st_size, i.st_mtime_ns, i.st_ctime_ns)
        entry = os.stat(path.name, dir_fd=descriptors[-2], follow_symlinks=False)
        _require(signature(before) == signature(after) == signature(entry), stage)
        for parent_fd, child_fd, component in zip(descriptors[:-2], descriptors[1:-1], path.parent.parts[1:]):
            info = os.fstat(child_fd)
            entry = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            _require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                     and not stat.S_IMODE(info.st_mode) & 0o022
                     and stat.S_IMODE(info.st_mode) & 0o100
                     and (info.st_dev, info.st_ino) == (entry.st_dev, entry.st_ino), stage)
        final_parent = os.fstat(descriptors[-2])
        final_entry = os.stat(path.parent.name, dir_fd=descriptors[-3], follow_symlinks=False)
        _require(stat.S_ISDIR(final_parent.st_mode) and final_parent.st_uid == 0
                 and final_parent.st_gid == governed_gid
                 and stat.S_IMODE(final_parent.st_mode) == 0o750
                 and not stat.S_IMODE(final_parent.st_mode) & 0o022
                 and parent_signature(parent) == parent_signature(final_parent)
                 == parent_signature(final_entry), stage)
        return b"".join(chunks)
    except (OSError, KeyError) as exc:
        raise Stop(PRECONDITION_FAILED, stage, errno_code=getattr(exc, "errno", None)) from exc
    finally:
        close_error = None
        for fd in reversed(descriptors):
            try:
                os.close(fd)
            except OSError as exc:
                close_error = exc
        if close_error is not None:
            raise Stop(PRECONDITION_FAILED, stage, errno_code=close_error.errno) from close_error


def read_activation_record() -> dict[str, object]:
    activation = canonical_record(_protected_record(ACTIVATION_RECORD, "ACTIVATION"), "ACTIVATION_SCHEMA")
    validate_activation_schema(activation, activation.get("executor_sha256"))
    return activation


def validate_activation_schema(activation: dict[str, object], executor_sha: str) -> None:
    stage = "ACTIVATION_SCHEMA"
    _closed(activation, ACTIVATION_KEYS, stage)
    _require(all(type(v) is str for v in activation.values()) and
             activation["schema_version"] == ACTIVATION_SCHEMA_VERSION and
             activation["authority_id"] == AUTHORITY_ID and
             activation["approval_id"] == RECOVERY_APPROVAL_ID and
             activation["package_payload_sha256"] == RECOVERY_PAYLOAD_SHA256 and
             activation["policy_reference"] == str(REL_POLICY) and
             _hex(activation["expected_runtime_head"], 40) and
             _hex(activation["executor_sha256"], 64) and
             activation["executor_sha256"] == executor_sha, stage)
    try:
        parse_utc(activation["activated_at_utc"])
    except (GovernedStop, ValueError) as exc:
        raise Stop(PRECONDITION_FAILED, stage) from exc


def _evidence_path(path: object) -> bool:
    return type(path) is str and re.fullmatch(re.escape(EVIDENCE_PREFIX) + UUID_PATTERN + r"\.json", path) is not None


def validate_selector(value: dict[str, object]) -> None:
    _closed(value, SELECTOR_KEYS, "SELECTOR_SCHEMA")
    _require(value["schema_version"] == "aios-p4s7-recovery-review-merge-trust-v1" and
             _hex(value["evidence_commit"], 40) and _evidence_path(value["evidence_path"]) and
             _hex(value["evidence_transport_sha256"], 64), "SELECTOR_SCHEMA")


def validate_evidence(value: dict[str, object], path: str) -> None:
    stage = "EVIDENCE_SCHEMA"
    _closed(value, EVIDENCE_KEYS, stage)
    fixed = {"schema_version": "aios-p4s7-recovery-review-merge-evidence-v1",
             "repository": "bader5657/AIOS", "authority_id": AUTHORITY_ID,
             "policy_reference": str(REL_POLICY), "activation_governance_reference": str(REL_R34),
             "approval_id": RECOVERY_APPROVAL_ID, "package_payload_sha256": RECOVERY_PAYLOAD_SHA256}
    _require(all(type(value[k]) is str and value[k] == v for k, v in fixed.items()), stage)
    _require(type(value["binding_id"]) is str and _evidence_path(path) and
             path == EVIDENCE_PREFIX + value["binding_id"] + ".json" and
             _hex(value["expected_runtime_head"], 40) and
             _hex(value["executor_sha256"], 64) and _hex(value["policy_sha256"], 64), stage)
    for name in ("reader", "r32", "r34"):
        review = value[name]
        _closed(review, REVIEW_KEYS, stage)
        _require(type(review["pr_number"]) is int and review["pr_number"] > 0 and
                 _hex(review["reviewed_head_sha"], 40) and _hex(review["merge_sha"], 40), stage)
    _require(value["r32"]["pr_number"] == 299 and value["r32"]["merge_sha"] == R32_MERGE and
             value["r34"]["pr_number"] == 300 and value["r34"]["merge_sha"] == R34_MERGE and
             value["reader"]["pr_number"] not in (299, 300, 301), stage)
    predecessor = value["supersedes"]
    _closed(predecessor, PREDECESSOR_KEYS, stage)
    _require(all(type(v) is str for v in predecessor.values()) and
             _hex(predecessor["commit"], 40) and _hex(predecessor["transport_sha256"], 64), stage)
    if predecessor["kind"] == "r34-baseline":
        _require(predecessor["commit"] == R34_MERGE and predecessor["path"] == str(REL_R34), stage)
    else:
        _require(predecessor["kind"] == "recovery-evidence-v1" and _evidence_path(predecessor["path"]), stage)


def _commit(commit: str) -> None:
    _require(_hex(commit, 40) and run_git("cat-file", "-t", commit) == "commit", "EVIDENCE_GIT")


def _blob(commit: str, path: str | Path) -> bytes:
    _commit(commit)
    listing = _git_bytes("ls-tree", "-z", commit, "--", str(path))
    # Fixed full path, one regular file only; no symlink/gitlink or path discovery.
    prefix, sep, name = listing.partition(b"\t")
    _require(bool(sep) and name == str(path).encode() + b"\0", "EVIDENCE_GIT")
    parts = prefix.split()
    _require(len(parts) == 3 and parts[0] in (b"100644", b"100755") and parts[1] == b"blob", "EVIDENCE_GIT")
    if str(path).startswith(EVIDENCE_PREFIX):
        _require(parts[0] == b"100644", "EVIDENCE_GIT")
    return _git_bytes("cat-file", "blob", parts[2].decode("ascii"))


def _parents(commit: str) -> tuple[str, ...]:
    """Read original commit headers, never show/rev-list's grafted graph.

    Git 2.43 still honors info/grafts even with --no-replace-objects. cat-file
    returns the original bytes; deriving edges here also avoids shallow grafts.
    Missing history fails closed instead of being treated as a root.
    """
    _commit(commit)
    raw = _git_bytes("cat-file", "commit", commit)
    _require(hashlib.sha1(b"commit " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
             == commit, "EVIDENCE_GIT")
    header, sep, _ = raw.partition(b"\n\n")
    _require(bool(sep), "EVIDENCE_GIT")
    lines = header.split(b"\n")
    _require(re.fullmatch(rb"tree [0-9a-f]{40}", lines[0]) is not None, "EVIDENCE_GIT")
    parents, end_of_parents = [], False
    for line in lines[1:]:
        if line.startswith(b"parent "):
            # Git's parent block immediately follows the tree header. Never
            # reinterpret a later arbitrary header as an ancestry edge.
            _require(not end_of_parents, "EVIDENCE_GIT")
            oid = line[7:]
            _require(re.fullmatch(rb"[0-9a-f]{40}", oid) is not None, "EVIDENCE_GIT")
            parents.append(oid.decode("ascii"))
        else:
            end_of_parents = True
    _require(len(set(parents)) == len(parents), "EVIDENCE_GIT")
    return tuple(parents)


def _ancestors(commit: str) -> set[str]:
    pending, seen = [commit], set()
    while pending:
        current = pending.pop()
        if current not in seen:
            seen.add(current)
            pending.extend(_parents(current))
    return seen


def _ancestor(old: str, new: str) -> None:
    _commit(old)
    _require(old in _ancestors(new), "EVIDENCE_ANCESTRY")


def _record_changes(parent: str, commit: str) -> list[tuple[bytes, bytes]]:
    # Two explicit trees, not a Git parent walk. No rename folding or path
    # discovery: inspect only deltas in the governed evidence namespace.
    raw = _git_bytes("diff-tree", "--no-commit-id", "--no-renames", "-r",
                     "--name-status", "-z", parent, commit, "--", EVIDENCE_PREFIX)
    if not raw:
        return []
    parts = raw.split(b"\0")
    _require(parts[-1] == b"" and len(parts) % 2 == 1, "EVIDENCE_GIT")
    return list(zip(parts[:-1:2], parts[1:-1:2]))


def _evidence_history(parents: tuple[str, ...], previous: str, path: str) -> None:
    """Check both authenticated parent histories, including erased changes.

    Only drafting A/M revisions of the selected new record on the reviewed
    branch are allowed. Prior publication, other records, deletions and type
    changes cannot be hidden by a clean final first-parent tree difference.
    """
    excluded = _ancestors(previous)
    first_history = _ancestors(parents[0])
    _require(previous in first_history, "PREDECESSOR_CONFLICT")
    pending, seen = list(parents), set(excluded)
    selected = path.encode()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        edges = _parents(current)
        _require(bool(edges), "PREDECESSOR_CONFLICT")
        for index, parent in enumerate(edges):
            changes = _record_changes(parent, current)
            if current in first_history:
                _require(not changes, "PREDECESSOR_CONFLICT")
            else:
                _require(all(name == selected and status in (b"A", b"M")
                             for status, name in changes), "PREDECESSOR_CONFLICT")
                # A prior evidence publication in the reviewed ancestry is
                # not an unpublished draft revision, even at the same path.
                if len(edges) > 1 and index == 0:
                    _require((b"A", selected) not in changes, "PREDECESSOR_CONFLICT")
        pending.extend(edges)


def _review(review: dict[str, object], paths: tuple[Path, ...]) -> None:
    merge, reviewed = review["merge_sha"], review["reviewed_head_sha"]
    _commit(merge)
    _commit(reviewed)
    parents = _parents(merge)
    _require(len(parents) == 2 and parents[1] == reviewed, "REVIEW_MERGE")
    for path in paths:
        _require(_blob(reviewed, path) == _blob(merge, path), "REVIEW_BLOB")


def _verify_evidence_record(record: dict[str, object], commit: str) -> None:
    head = record["expected_runtime_head"]
    _ancestor(head, commit)
    for component, paths in (("r32", (REL_R32, REL_EXECUTOR, REL_POLICY)),
                             ("r34", (REL_R34,)), ("reader", (REL_EXECUTOR, REL_POLICY))):
        _review(record[component], paths)
        _ancestor(record[component]["merge_sha"], head)
    _ancestor(TRUST_MERGE, record["reader"]["reviewed_head_sha"])
    contract = _blob(TRUST_MERGE, REL_TRUST)
    _require(sha256(contract) == TRUST_SHA256 and _blob(head, REL_TRUST) == contract, "TRUST_CONTRACT")
    _require(_blob(head, REL_R34) == _blob(R34_MERGE, REL_R34), "HISTORICAL_GOVERNANCE")
    executor = _blob(head, REL_EXECUTOR)
    policy = _blob(head, REL_POLICY)
    merge = record["reader"]["merge_sha"]
    _require(executor == _blob(merge, REL_EXECUTOR) and sha256(executor) == record["executor_sha256"], "EXECUTOR_BINDING")
    _require(policy == _blob(merge, REL_POLICY) and sha256(policy) == record["policy_sha256"], "POLICY_BINDING")
    try:
        text = policy.decode("utf-8")
    except UnicodeError as exc:
        raise Stop(PRECONDITION_FAILED, "POLICY_BINDING") from exc
    digests = re.findall(r"\| executor SHA-256 \| `([0-9a-f]{64})` \|", text)
    _require(digests == [record["executor_sha256"]] and AUTHORITY_ID in text and
             "P4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW" in text, "POLICY_BINDING")


def read_recovery_evidence() -> dict[str, object]:
    """Local proof only. Fresh independent operator verification is EXTERNAL.

    Identical local inputs cannot reveal an unavailable revocation/successor.
    Success is necessary, never sufficient authority to activate or execute.
    No receipt, flag, online lookup or implicit freshness mechanism is used.
    """
    transport = _protected_record(TRUST_SELECTOR, "SELECTOR")
    selector = canonical_record(transport, "SELECTOR_SCHEMA")
    validate_selector(selector)
    commit, path, digest = (selector[k] for k in ("evidence_commit", "evidence_path", "evidence_transport_sha256"))
    seen_ids, seen_refs = set(), set()
    selected = None
    while True:
        _require((commit, path) not in seen_refs, "PREDECESSOR_CYCLE")
        seen_refs.add((commit, path))
        data = _blob(commit, path)
        _require(sha256(data) == digest, "EVIDENCE_HASH")
        record = canonical_record(data, "EVIDENCE_SCHEMA")
        validate_evidence(record, path)
        _require(record["binding_id"] not in seen_ids, "PREDECESSOR_CYCLE")
        seen_ids.add(record["binding_id"])
        # Evidence must be the unique addition at its actual two-parent merge.
        parents = _parents(commit)
        _require(len(parents) == 2 and _blob(parents[1], path) == data, "EVIDENCE_MERGE")
        changes = _record_changes(parents[0], commit)
        _require(changes == [(b"A", path.encode())], "EVIDENCE_CONFLICT")
        _verify_evidence_record(record, commit)
        selected = selected or record
        previous = record["supersedes"]
        _require(previous["commit"] != commit, "PREDECESSOR_CYCLE")
        _evidence_history(parents, previous["commit"], path)
        commit, path, digest = previous["commit"], previous["path"], previous["transport_sha256"]
        if previous["kind"] == "r34-baseline":
            _require(sha256(_blob(commit, path)) == digest, "PREDECESSOR_HASH")
            break
    # Recheck fixed selector bytes/custody before returning local proof.
    _require(_protected_record(TRUST_SELECTOR, "SELECTOR") == transport, "SELECTOR_CHANGED")
    return selected


def verify_actual_interpreter(executable: str = sys.executable, version_info: object = sys.version_info) -> None:
    if executable != EXPECTED_INTERPRETER:
        raise Stop(PRECONDITION_FAILED, "INTERPRETER")
    try:
        actual = Path(executable).resolve(strict=True)
        expected = Path(EXPECTED_INTERPRETER).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise Stop(PRECONDITION_FAILED, "INTERPRETER", errno_code=getattr(exc, "errno", None)) from exc
    if actual != expected or tuple(version_info[:3]) != EXPECTED_PYTHON_VERSION:
        raise Stop(PRECONDITION_FAILED, "INTERPRETER")


def verify_merged_authority(executor_sha: str, activation: dict[str, object]) -> str:
    validate_activation_schema(activation, executor_sha)
    # Local timestamp consistency is not proof of actual creation or authority.
    activated = parse_utc(activation["activated_at_utc"])
    _require(parse_utc(RECOVERY_APPROVED_AT) <= activated < parse_utc(RECOVERY_NOT_AFTER)
             and activated <= utc_now(), "ACTIVATION_TIME")
    evidence = read_recovery_evidence()
    for field in ("authority_id", "approval_id", "package_payload_sha256", "policy_reference",
                  "expected_runtime_head", "executor_sha256"):
        _require(activation[field] == evidence[field], "ACTIVATION_BINDING")
    head = run_git("rev-parse", "HEAD")
    _require(head == evidence["expected_runtime_head"], "RUNTIME_HEAD")
    _require(not run_git("status", "--porcelain=v1", "--untracked-files=all"), "RUNTIME_CLEANLINESS")
    try:
        executor_bytes = (REPOSITORY / REL_EXECUTOR).read_bytes()
        policy_bytes = (REPOSITORY / REL_POLICY).read_bytes()
    except OSError as exc:
        raise Stop(PRECONDITION_FAILED, "EXECUTOR_HEAD", errno_code=exc.errno) from exc
    _require(executor_bytes == _blob(head, REL_EXECUTOR) and sha256(executor_bytes) == executor_sha,
             "EXECUTOR_HEAD")
    _require(policy_bytes == _blob(head, REL_POLICY) and sha256(policy_bytes) == evidence["policy_sha256"],
             "POLICY_BINDING")
    return evidence["reader"]["merge_sha"]


def open_dir(path: Path, uid: int, gid: int, mode: int, *, check_components: bool = False) -> int:
    if not path.is_absolute():
        raise Stop(PRECONDITION_FAILED, "PATH_PREFLIGHT")
    opened = [os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)]
    try:
        for component in path.parts[1:]:
            parent = opened[-1]
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent)
            opened.append(child)
            if check_components:
                info = os.fstat(child)
                entry = os.stat(component, dir_fd=parent, follow_symlinks=False)
                if (not stat.S_ISDIR(info.st_mode) or not stat.S_ISDIR(entry.st_mode) or
                        (info.st_dev, info.st_ino) != (entry.st_dev, entry.st_ino) or
                        info.st_uid != 0 or stat.S_IMODE(info.st_mode) & 0o022 or
                        not stat.S_IMODE(info.st_mode) & 0o100):
                    raise Stop(PRECONDITION_FAILED, "PATH_PREFLIGHT")
        final = os.fstat(opened[-1])
        if not stat.S_ISDIR(final.st_mode) or final.st_uid != uid or final.st_gid != gid or stat.S_IMODE(final.st_mode) != mode:
            raise Stop(PRECONDITION_FAILED, "PATH_PREFLIGHT")
        if check_components:
            for parent, child, component in zip(opened, opened[1:], path.parts[1:]):
                entry = os.stat(component, dir_fd=parent, follow_symlinks=False)
                info = os.fstat(child)
                if not stat.S_ISDIR(entry.st_mode) or (entry.st_dev, entry.st_ino) != (info.st_dev, info.st_ino):
                    raise Stop(PRECONDITION_FAILED, "PATH_PREFLIGHT")
        return opened[-1]
    except OSError as exc:
        raise Stop(PRECONDITION_FAILED, "PATH_PREFLIGHT", errno_code=exc.errno) from exc
    finally:
        for fd in opened[:-1]:
            os.close(fd)
        if sys.exc_info()[0] is not None:
            os.close(opened[-1])


def absent(dir_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return True
    return False


def preflight_install_names(parent_fd: int) -> None:
    if any(not absent(parent_fd, name) for name, _, _, _ in FILES):
        raise Stop(TARGET_ALREADY_EXISTS, "TARGET_PREFLIGHT")
    prefixes = tuple(f".{name}.stage-" for name, _, _, _ in FILES)
    try:
        names = os.listdir(parent_fd)
    except OSError as exc:
        raise Stop(PRECONDITION_FAILED, "STAGING_PREFLIGHT", errno_code=exc.errno) from exc
    if any(name.startswith(prefixes) for name in names):
        raise Stop(PRECONDITION_FAILED, "STAGING_PREFLIGHT")


def read_source(source_fd: int, name: str, semantic: int, transport: int, digest: str) -> bytes:
    fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=source_fd)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or
                stat.S_IMODE(info.st_mode) != 0o400 or info.st_nlink != 1):
            raise Stop(PRECONDITION_FAILED, "SOURCE_METADATA")
        data = b""
        while len(data) <= transport:
            chunk = os.read(fd, transport + 1 - len(data))
            if not chunk:
                break
            data += chunk
    finally:
        os.close(fd)
    # Keep the cause private while exposing the single governed pre-claim
    # classification for every source-binding mismatch.
    if len(data) != transport:
        raise Stop(APPROVED_BYTES_INVALID, "SOURCE_BYTES")
    if semantic != transport - 1 or len(data[:semantic]) != semantic:
        raise Stop(APPROVED_BYTES_INVALID, "SOURCE_BYTES")
    if data[semantic:] != b"\n":
        raise Stop(APPROVED_BYTES_INVALID, "SOURCE_BYTES")
    if sha256(data[:semantic]) != digest:
        raise Stop(APPROVED_BYTES_INVALID, "SOURCE_BYTES")
    exact_json(data[:semantic])
    return data


def write_all(fd: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        count = os.write(fd, data[offset:])
        if count <= 0:
            raise Stop("short write")
        offset += count


def durable_claim(evidence_fd: int, authority_commit: str, executor_sha: str, state: ExecutionState | None = None) -> dict[str, object]:
    if state is not None: state.consumption_state = "UNUSED"
    record: dict[str, object] = {"schema_version":"aios-stage-0.33c-p4s6-consumption-v1","authority_id":AUTHORITY_ID,"authority_commit":authority_commit,"claim_timestamp_utc":utc_text(utc_now()),"executor_path":str(REL_EXECUTOR),"executor_sha256":executor_sha,"run_as":"root","state":"DURABLY_CONSUMED"}
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    try:
        fd = os.open(MARKER, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=evidence_fd)
    except FileExistsError as exc:
        raise Stop(AUTHORITY_CONSUMED, "CLAIM") from exc
    if state is not None: state.consumption_state = "CLAIMED"
    try:
        write_all(fd, encoded); os.fsync(fd)
    except (OSError, GovernedStop) as exc:
        # The created marker is never removed, even if its content is incomplete.
        try: os.close(fd)
        except OSError: pass
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=getattr(exc, "errno", getattr(exc, "errno_code", None))) from exc
    try:
        os.close(fd)
    except OSError as exc:
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=exc.errno) from exc
    try:
        os.fsync(evidence_fd)
    except OSError as exc:
        raise Stop("CONSUMPTION_DURABILITY_UNCERTAIN", "CLAIM", errno_code=exc.errno) from exc
    if state is not None: state.consumption_state = "DURABLY_CONSUMED"
    return record


def stage_and_publish(parent_fd: int, source: bytes, final: str, semantic: int, digest: str, artifact: ArtifactState | None = None) -> None:
    artifact = artifact if artifact is not None else ArtifactState()
    stage = make_stage_name(final)
    stage_identity = None
    closed = False
    try:
        fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
        artifact.staged = True
        _WRITABLE_FDS[fd] = (final, 0, 0)
        try:
            info = os.fstat(fd)
            stage_identity = (info.st_dev, info.st_ino)
            _WRITABLE_FDS[fd] = (final, *stage_identity)
            write_all(fd, source)
            os.fsync(fd)
            os.fchown(fd, 0, pwd.getpwnam("aiosadmin").pw_gid)
            os.fchmod(fd, 0o440)
            os.fsync(fd)
        finally:
            os.close(fd)
            closed = True
            _WRITABLE_FDS.pop(fd, None)
        artifact.writable_fd_closed = True
        stage_meta = verify_file(parent_fd, stage, source, semantic, digest)
        parent_meta = os.fstat(parent_fd)
        if stage_meta.st_dev != parent_meta.st_dev: raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "DEVICE", final)
        artifact.stage_device_verified = True
        if any(dev == stage_meta.st_dev and ino == stage_meta.st_ino for _, dev, ino in _WRITABLE_FDS.values()): raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "WRITABLE_FD", final)
        artifact.writable_fd_absent = True
        artifact.preverified = True
        os.link(stage, final, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
        artifact.published = True
        os.fsync(parent_fd)
        final_meta = verify_file(parent_fd, final, source, semantic, digest)
        if final_meta.st_dev != parent_meta.st_dev or final_meta.st_dev != stage_meta.st_dev or final_meta.st_ino != stage_meta.st_ino:
            raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "INODE", final)
        artifact.final_inode_verified = True
        artifact.final_metadata = {"device": final_meta.st_dev, "inode": final_meta.st_ino, "uid": final_meta.st_uid, "gid": final_meta.st_gid, "mode": final_meta.mode, "size": final_meta.size}
        artifact.semantic_prefix_hash_verified = True
        artifact.transport_bytes_verified = True
        artifact.final_verified = True
        os.unlink(stage, dir_fd=parent_fd)
        os.fsync(parent_fd)
        if not absent(parent_fd, stage): raise Stop(APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE, "CLEANUP", final)
        artifact.cleanup_complete = True
        verify_file(parent_fd, final, source, semantic, digest)
    except (OSError, GovernedStop) as exc:
        code = getattr(exc, "errno", getattr(exc, "errno_code", None))
        if artifact.final_verified and not artifact.cleanup_complete:
            classification = APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE
        elif artifact.published:
            artifact.final_verified = False
            classification = APPROVED_INPUT_FINAL_VERIFICATION_FAILED
        else:
            classification = APPROVED_INPUT_STAGING_FAILED
            if artifact.staged:
                try:
                    # Clean only our exact, still-identical unpublished staging inode.
                    info = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
                    if not closed or stage_identity != (info.st_dev, info.st_ino):
                        raise Stop("unsafe staging cleanup", "CLEANUP", final)
                    os.unlink(stage, dir_fd=parent_fd)
                    os.fsync(parent_fd)
                    if not absent(parent_fd, stage): raise Stop("staging remains", "CLEANUP", final)
                    artifact.cleanup_complete = True
                except (OSError, GovernedStop):
                    classification = "APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE"
        raise Stop(classification, "CLEANUP" if "CLEANUP" in classification else "STAGING", final, code) from exc


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


def _metadata(info: os.stat_result) -> dict[str, int]:
    return {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
            "gid": info.st_gid, "mode": stat.S_IMODE(info.st_mode)}


def result_record(state: ExecutionState, failure: GovernedStop) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "aios-stage-0.33c-p4s6-result-v1",
        "authority_id": AUTHORITY_ID,
        "authority_commit": state.authority_commit,
        "executor_path": str(REL_EXECUTOR),
        "executor_sha256": state.executor_sha,
        "run_as": "root",
        "timestamp_utc": utc_text(utc_now()),
        "stage": failure.stage,
        "classification": failure.classification,
        "consumption_state": state.consumption_state,
        "claim_exclusive": state.consumption_state != "UNUSED",
        "durability_barrier_complete": state.consumption_state in {"DURABLY_CONSUMED", "EXECUTION_STARTED"},
        "parent_metadata": state.parent_metadata,
        "pre_targets_absent": state.pre_targets_absent,
        "approval_freshness_valid": state.approval_freshness_valid,
        "input_semantic_sha256": state.source_semantic_sha256[0] if state.source_semantic_sha256 else None,
        "approval_semantic_sha256": state.source_semantic_sha256[1] if state.source_semantic_sha256 else None,
        "input_transport_bytes": state.source_transport_bytes[0] if state.source_transport_bytes else None,
        "approval_transport_bytes": state.source_transport_bytes[1] if state.source_transport_bytes else None,
        "pair_reverified": state.input.final_verified and state.approval.final_verified and
                           state.input.cleanup_complete and state.approval.cleanup_complete and
                           failure.classification == "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED",
        "artifact_role": failure.artifact or "NONE",
        "errno_code": failure.errno_code,
    }
    for role in ("input", "approval"):
        artifact = getattr(state, role)
        record.update({
            f"{role}_staging_verified": artifact.preverified,
            f"{role}_writable_fd_closed": artifact.writable_fd_closed,
            f"{role}_writable_fd_absent": artifact.writable_fd_absent,
            f"{role}_stage_device_verified": artifact.stage_device_verified,
            f"{role}_published": artifact.published,
            f"{role}_verified": artifact.final_verified,
            f"{role}_final_inode_verified": artifact.final_inode_verified,
            f"{role}_final_metadata": artifact.final_metadata,
            f"{role}_semantic_prefix_hash_verified": artifact.semantic_prefix_hash_verified,
            f"{role}_transport_bytes_verified": artifact.transport_bytes_verified,
            f"{role}_cleanup_complete": artifact.cleanup_complete,
        })
    if set(record) != RESULT_KEYS:
        raise Stop(RESULT_EVIDENCE_WRITE_FAILED, "RESULT_SCHEMA")
    return record


RESULT_KEYS = frozenset({
    "schema_version", "authority_id", "authority_commit", "executor_path", "executor_sha256",
    "run_as", "timestamp_utc", "stage", "classification", "consumption_state",
    "claim_exclusive", "durability_barrier_complete", "parent_metadata", "pre_targets_absent",
    "approval_freshness_valid", "input_semantic_sha256", "approval_semantic_sha256",
    "input_transport_bytes", "approval_transport_bytes", "pair_reverified", "artifact_role", "errno_code",
    *(f"{role}_{field}" for role in ("input", "approval") for field in (
        "staging_verified", "writable_fd_closed", "writable_fd_absent", "stage_device_verified",
        "published", "verified", "final_inode_verified", "final_metadata",
        "semantic_prefix_hash_verified", "transport_bytes_verified", "cleanup_complete")),
})


def write_failure_result(evidence_fd: int, state: ExecutionState, failure: GovernedStop) -> None:
    record = result_record(state, failure)
    fd = os.open(RESULT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=evidence_fd)
    try:
        try:
            write_all(fd, json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(evidence_fd)
    except (OSError, GovernedStop) as exc:
        raise Stop(RESULT_EVIDENCE_WRITE_FAILED, "RESULT", errno_code=getattr(exc, "errno", getattr(exc, "errno_code", None))) from exc


def write_result_with_secondary(evidence_fd: int, state: ExecutionState, primary: str, *, success: bool = False, failure: GovernedStop | None = None) -> tuple[str, str | None]:
    failure = GovernedStop(primary, "COMPLETE" if success else state.current_stage, failure.artifact if failure else None, failure.errno_code if failure else None)
    try:
        write_failure_result(evidence_fd, state, failure)
    except (GovernedStop, OSError):
        print(RESULT_EVIDENCE_WRITE_FAILED, file=sys.stderr)
        return primary, RESULT_EVIDENCE_WRITE_FAILED
    return primary, None

def sync_artifact_evidence(state: ExecutionState) -> None:
    for role in ("input", "approval"):
        artifact = getattr(state, role)
        for field in ("staged", "published", "final_verified", "cleanup_complete"):
            setattr(state, f"{role}_{field}", getattr(artifact, field))


def main() -> int:
    check_no_args_root()
    activation = read_activation_record()
    try:
        executor_bytes = (REPOSITORY / REL_EXECUTOR).read_bytes()
    except OSError as exc:
        raise Stop(PRECONDITION_FAILED, "EXECUTOR", errno_code=exc.errno) from exc
    executor_sha = sha256(executor_bytes)
    authority_commit = verify_merged_authority(executor_sha, activation)
    verify_actual_interpreter()
    aios = pwd.getpwnam("aiosadmin")
    parent_fd = open_dir(RUNTIME_PARENT, 0, aios.pw_gid, 0o750, check_components=True)
    source_fds = []
    evidence_fd = None
    try:
        # Validate both independent private parents before reading either file.
        for source_parent in (INPUT_SOURCE_PARENT, APPROVAL_SOURCE_PARENT):
            source_fds.append(open_dir(source_parent, 0, 0, 0o700))
        # Link-count and source metadata checks precede every package/target gate.
        sources = [read_source(fd, *spec) for fd, spec in zip(source_fds, FILES)]
        evidence_fd = os.open(EVIDENCE_DIR, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent_fd)
        info = os.fstat(evidence_fd)
        if info.st_uid != aios.pw_uid or info.st_gid != aios.pw_gid or stat.S_IMODE(info.st_mode) != 0o700:
            raise Stop("unsafe consumption directory")
        if not absent(evidence_fd, MARKER) or not absent(evidence_fd, RESULT):
            raise Stop("AUTHORITY_CONSUMED")
        preflight_install_names(parent_fd)
        input_obj, approval, manifest = validate_frozen_package(sources[0], sources[1])
        evidence = approval["package_payload"]["evidence"]
        if evidence["manifest_id"] != MANIFEST_ID:
            raise Stop(APPROVED_BYTES_INVALID, "MANIFEST_BINDING")
        # Both target-absence and expiry gates have passed; claim starts UNUSED -> CLAIMED -> DURABLY_CONSUMED.
        if parse_utc(approval["package_payload"]["not_after_utc"]) <= utc_now():
            raise Stop(APPROVAL_EXPIRED, "APPROVAL_TIME")
        state = ExecutionState(authority_commit=authority_commit, executor_sha=executor_sha)
        state.parent_metadata = _metadata(os.fstat(parent_fd))
        state.pre_targets_absent = True
        state.approval_freshness_valid = True
        state.source_semantic_sha256 = tuple(sha256(data[:-1]) for data in sources)
        state.source_transport_bytes = tuple(len(data) for data in sources)
        try:
            durable_claim(evidence_fd, authority_commit, executor_sha, state)
            for index, (source, spec) in enumerate(zip(sources, FILES)):
                state.current_stage = "INPUT" if index == 0 else "APPROVAL"
                state.consumption_state = "EXECUTION_STARTED"
                artifact = state.input if index == 0 else state.approval
                stage_and_publish(parent_fd, source, spec[0], spec[1], spec[3], artifact)
            state.current_stage = "PAIR_REVERIFY"
            for index, (source, spec) in enumerate(zip(sources, FILES)):
                try:
                    verify_file(parent_fd, spec[0], source, spec[1], spec[3])
                except (GovernedStop, OSError) as exc:
                    (state.input if index == 0 else state.approval).final_verified = False
                    raise Stop(APPROVED_INPUT_FINAL_VERIFICATION_FAILED, "PAIR_REVERIFY", spec[0], getattr(exc, "errno", None)) from exc
            primary = derive_primary_classification(state, {"pair_reverified": True})
        except (GovernedStop, OSError) as failure:
            classification = getattr(failure, "classification", APPROVED_INPUT_STAGING_FAILED)
            context = {"classification": classification}
            if classification == "APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE": context["cleanup"] = "prepublication"
            if classification == APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE: context["cleanup"] = "postpublication"
            primary = derive_primary_classification(state, context)
            sync_artifact_evidence(state)
            governed = GovernedStop(primary, state.current_stage, getattr(failure, "artifact", None), getattr(failure, "errno", getattr(failure, "errno_code", None)))
            write_result_with_secondary(evidence_fd, state, primary, failure=governed)
            raise governed from failure
        sync_artifact_evidence(state)
        _, secondary = write_result_with_secondary(evidence_fd, state, primary, success=primary == "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED")
        return 0 if primary == "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED" and secondary is None else 1
    finally:
        if evidence_fd is not None:
            os.close(evidence_fd)
        for source_fd in source_fds:
            os.close(source_fd)
        os.close(parent_fd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Stop, OSError, subprocess.CalledProcessError) as exc:
        print(f"STOP: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
