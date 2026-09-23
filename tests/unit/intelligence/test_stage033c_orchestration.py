import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
EXECUTOR_PATH = ROOT / "docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
spec = importlib.util.spec_from_file_location("stage033c_orchestration_executor", EXECUTOR_PATH)
executor = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = executor
spec.loader.exec_module(executor)

class PackageBindingReconciliationTests(unittest.TestCase):
    INPUT = ("approved-input.json", 1327, 1328, "e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d")
    APPROVAL = ("approved-input-approval.json", 3579, 3580, "2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26")
    OLD_APPROVAL = ("approved-input-approval.json", 3549, 3550, "266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57")
    APPROVAL_TRANSPORT_SHA256 = "1d24f693154e0e8c2ac4504b9e81086662670c870e785c4f0d4d79c3ded16ac8"

    def test_regenerated_approval_binding_is_executable(self):
        self.assertEqual(executor.FILES, (self.INPUT, self.APPROVAL))
        self.assertEqual(executor.FILES[1][1:3], (3579, 3580))
        self.assertEqual(executor.FILES[1][3], self.APPROVAL[3])

    def test_old_unavailable_approval_binding_is_rejected(self):
        self.assertNotIn(self.OLD_APPROVAL, executor.FILES)
        self.assertNotEqual(executor.FILES[1][1], 3549)
        self.assertNotEqual(executor.FILES[1][2], 3550)
        self.assertNotEqual(executor.FILES[1][3], self.OLD_APPROVAL[3])

    def test_transport_digest_is_not_a_new_executable_constant(self):
        source = EXECUTOR_PATH.read_text(encoding="utf-8")
        self.assertNotIn(self.APPROVAL_TRANSPORT_SHA256, source)

class DurabilityClassificationResultTests(unittest.TestCase):
    def state(self, **kwargs): return executor.ExecutionState(**kwargs)
    def test_state_starts_unused(self): self.assertEqual(self.state().consumption_state, "UNUSED")
    def test_claimed_is_uncertain(self): self.assertEqual(executor.derive_primary_classification(self.state(consumption_state="CLAIMED"), {}), "CONSUMPTION_DURABILITY_UNCERTAIN")
    def test_preclaim_classifications(self):
        for c in (executor.PRECONDITION_FAILED, executor.APPROVAL_EXPIRED, executor.TARGET_ALREADY_EXISTS, executor.APPROVED_BYTES_INVALID):
            with self.subTest(c=c): self.assertEqual(executor.derive_primary_classification(self.state(), {"classification": c}), c)
    def test_postdurable_staging_failure(self): self.assertEqual(executor.derive_primary_classification(self.state(consumption_state="DURABLY_CONSUMED"), {"stage":"staging"}), executor.APPROVED_INPUT_STAGING_FAILED)
    def test_prepublication_cleanup_precedence(self): self.assertEqual(executor.derive_primary_classification(self.state(consumption_state="DURABLY_CONSUMED"), {"cleanup":"prepublication"}), "APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE")
    def test_partial_precedence(self):
        s=self.state(consumption_state="DURABLY_CONSUMED"); s.input.final_verified=True
        for c in ({"stage":"staging"},{"classification":executor.TARGET_ALREADY_EXISTS},{"classification":executor.APPROVED_INPUT_FINAL_VERIFICATION_FAILED}): self.assertEqual(executor.derive_primary_classification(s,c),executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
    def test_cleanup_and_success_gate(self):
        s=self.state(consumption_state="DURABLY_CONSUMED"); self.assertEqual(executor.derive_primary_classification(s,{"cleanup":"postpublication"}),executor.APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE); s.input.published=s.input.final_verified=s.input.cleanup_complete=True; s.approval.published=s.approval.final_verified=s.approval.cleanup_complete=True; self.assertNotEqual(executor.derive_primary_classification(s,{}),"STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED"); self.assertEqual(executor.derive_primary_classification(s,{"pair_reverified":True}),"STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED")
    def test_durability_failures_no_staging_or_reset(self):
        for mode in ("write","fsync","parent"):
            with tempfile.TemporaryDirectory() as d:
                fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); s=self.state(); old=executor.MARKER; executor.MARKER="marker.json"
                try:
                    ctx=patch.object(executor,"write_all",side_effect=OSError(5,"x")) if mode=="write" else patch.object(executor.os,"fsync",side_effect=([None,OSError(5,"x")] if mode=="parent" else OSError(5,"x")))
                    with ctx,patch.object(executor,"stage_and_publish") as stage,self.assertRaises(executor.GovernedStop) as e: executor.durable_claim(fd,"a"*40,"b"*64,s)
                    self.assertEqual(e.exception.classification,"CONSUMPTION_DURABILITY_UNCERTAIN"); self.assertEqual(s.consumption_state,"CLAIMED"); stage.assert_not_called(); self.assertTrue(Path(d,"marker.json").exists())
                finally: executor.MARKER=old; os.close(fd)
    def test_existing_marker_authority_consumed(self):
        with tempfile.TemporaryDirectory() as d:
            fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); old=executor.MARKER; executor.MARKER="marker.json"
            try: Path(d,"marker.json").write_bytes(b"old"); self.assertRaises(executor.GovernedStop,executor.durable_claim,fd,"a"*40,"b"*64,self.state())
            finally: executor.MARKER=old; os.close(fd)
    def test_result_exact_schema_minimized_and_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); old=executor.RESULT; executor.RESULT="result.json"; s=self.state(authority_commit="a"*40,executor_sha="b"*64,consumption_state="DURABLY_CONSUMED")
            try:
                executor.write_failure_result(fd,s,executor.GovernedStop(executor.APPROVED_BYTES_INVALID,"X")); obj=json.loads(Path(d,"result.json").read_text()); self.assertEqual(set(obj),executor.RESULT_KEYS); self.assertNotIn("supplier",json.dumps(obj)); self.assertRaises(FileExistsError,executor.write_failure_result,fd,s,executor.GovernedStop(executor.APPROVED_BYTES_INVALID,"X"))
            finally: executor.RESULT=old; os.close(fd)
    def test_success_result_schema(self):
        with tempfile.TemporaryDirectory() as d:
            fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); old=executor.RESULT; executor.RESULT="result.json"
            try: s=self.state(authority_commit="a"*40,executor_sha="b"*64,consumption_state="EXECUTION_STARTED"); s.input.published=s.input.final_verified=s.input.cleanup_complete=True; s.approval.published=s.approval.final_verified=s.approval.cleanup_complete=True; executor.write_result_with_secondary(fd,s,"STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED",success=True); self.assertEqual(set(json.loads(Path(d,"result.json").read_text())),executor.RESULT_KEYS)
            finally: executor.RESULT=old; os.close(fd)
    def test_secondary_preserves_partial_primary(self):
        with tempfile.TemporaryDirectory() as d:
            fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY); s=self.state(consumption_state="DURABLY_CONSUMED")
            try:
                with patch.object(executor,"write_failure_result",side_effect=executor.GovernedStop(executor.RESULT_EVIDENCE_WRITE_FAILED,"RESULT")): p,q=executor.write_result_with_secondary(fd,s,executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
                self.assertEqual((p,q),(executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION,executor.RESULT_EVIDENCE_WRITE_FAILED))
            finally: os.close(fd)



# B2 closure matrix. Recovery tests above remain intact.
import contextlib
import errno
import io
import stat
from types import SimpleNamespace

UNCERTAIN = "CONSUMPTION_DURABILITY_UNCERTAIN"
SUCCESS = "STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED"
PRE_CLEANUP = "APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE"
KEYS = executor.RESULT_KEYS

class TempCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.fd)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in (("MARKER", "claim.json"), ("RESULT", "result.json")):
            self.stack.enter_context(patch.object(executor, name, value))
        self.state = executor.ExecutionState(authority_commit="a" * 40, executor_sha="b" * 64)

    def assert_nonretryable(self):
        self.assertTrue((self.root / executor.MARKER).exists())
        before = (self.root / executor.MARKER).read_bytes()
        with self.assertRaises(executor.GovernedStop) as caught:
            executor.durable_claim(self.fd, "a" * 40, "b" * 64, executor.ExecutionState())
        self.assertEqual(caught.exception.classification, executor.AUTHORITY_CONSUMED)
        self.assertEqual((self.root / executor.MARKER).read_bytes(), before)

    @contextlib.contextmanager
    def fault(self, mode):
        real_open, real_close, real_fsync = os.open, os.close, os.fsync
        opened = []
        def opening(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        def closing(fd):
            real_close(fd)
            if mode == "close" and fd in opened:
                raise OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")
        def syncing(fd):
            if (mode == "file" and fd != self.fd) or (mode == "parent" and fd == self.fd):
                raise OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")
            return real_fsync(fd)
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(executor.os, "open", side_effect=opening))
            stack.enter_context(patch.object(executor.os, "close", side_effect=closing))
            stack.enter_context(patch.object(executor.os, "fsync", side_effect=syncing))
            if mode == "write":
                stack.enter_context(patch.object(executor, "write_all", side_effect=OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")))
            try:
                yield opened
            finally:
                for fd in opened:
                    try: real_close(fd)
                    except OSError: pass

class SyntheticRun(TempCase):
    """Real temporary hard-links and bytes; only trust/ownership prerequisites stubbed.

    Schema/manifest validation is exercised by the unchanged full-chain suite.
    Every main() path is redirected before calling it; no production paths open.
    """
    def setUp(self):
        super().setUp()
        self.parent = self.root / "parent"
        self.source = self.root / "source"
        self.parent.mkdir(); self.source.mkdir()
        (self.parent / executor.EVIDENCE_DIR).mkdir(mode=0o700)
        self.evidence = self.parent / executor.EVIDENCE_DIR
        # Claim and result fault helpers use this exact evidence directory FD.
        os.close(self.fd)
        self.fd = os.open(self.evidence, os.O_RDONLY | os.O_DIRECTORY)
        self.payloads = (b'{"synthetic":"input"}\n', b'{"synthetic":"approval"}\n')
        self.specs = tuple((name, len(data)-1, len(data), executor.sha256(data[:-1]))
                           for name, data in zip(("approved-input.json", "approved-input-approval.json"), self.payloads))
        for spec, data in zip(self.specs, self.payloads):
            (self.source / spec[0]).write_bytes(data)
            (self.source / spec[0]).chmod(0o400)
        (self.root / "fixture-executor.py").write_bytes(b"synthetic executor bytes")
        real_fstat = os.fstat
        def ownership_only(fd):
            value = real_fstat(fd)
            if stat.S_ISREG(value.st_mode):
                values = list(value); values[4] = 0; values[5] = 0 if stat.S_IMODE(value.st_mode) == 0o400 else value.st_gid
                return os.stat_result(values)
            return value
        def open_fixture(path, *_, **__):
            self.assertIn(path, (self.parent, self.source))
            return os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        for name, value in (("REPOSITORY", self.root), ("REL_EXECUTOR", Path("fixture-executor.py")),
                            ("RUNTIME_PARENT", self.parent), ("SOURCE_PARENT", self.source), ("FILES", self.specs)):
            self.stack.enter_context(patch.object(executor, name, value))
        self.stack.enter_context(patch.object(executor, "check_no_args_root"))
        self.stack.enter_context(patch.object(executor, "read_activation_record", return_value={}))
        self.stack.enter_context(patch.object(executor, "verify_merged_authority", return_value="a"*40))
        self.stack.enter_context(patch.object(executor, "verify_actual_interpreter"))
        self.stack.enter_context(patch.object(executor, "open_dir", side_effect=open_fixture))
        self.stack.enter_context(patch.object(executor.pwd, "getpwnam", return_value=SimpleNamespace(pw_uid=os.geteuid(), pw_gid=os.getegid())))
        self.stack.enter_context(patch.object(executor.os, "fstat", side_effect=ownership_only))
        self.stack.enter_context(patch.object(executor.os, "fchown"))
        self.stack.enter_context(patch.object(executor, "validate_frozen_package", return_value=({}, {"package_payload":{"evidence":{"manifest_id":executor.MANIFEST_ID},"not_after_utc":"2099-01-01T00:00:00.000000Z"}}, {})))
        self.states = []
        real_state = executor.ExecutionState
        def capture_state(*args, **kwargs):
            state = real_state(*args, **kwargs); self.states.append(state); return state
        self.stack.enter_context(patch.object(executor, "ExecutionState", side_effect=capture_state))

    def assert_retry_blocked(self):
        marker = self.evidence / executor.MARKER
        self.assertTrue(marker.exists())
        before = marker.read_bytes()
        with patch.object(executor, "stage_and_publish") as stage:
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification, executor.AUTHORITY_CONSUMED)
        stage.assert_not_called()
        self.assertEqual(marker.read_bytes(), before)

class PreclaimMatrix(SyntheticRun):
    def test_staging_debris_stops_before_claim_and_publication(self):
        for final in ("approved-input.json", "approved-input-approval.json"):
            for suffix in ("123e4567-e89b-42d3-a456-426614174000", "partial"):
                with self.subTest(final=final, suffix=suffix):
                    debris = self.parent / f".{final}.stage-{suffix}"
                    debris.write_bytes(b"preserve")
                    with patch.object(executor, "durable_claim") as claim, patch.object(executor, "stage_and_publish") as stage:
                        with self.assertRaises(executor.GovernedStop) as caught: executor.main()
                    self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
                    claim.assert_not_called(); stage.assert_not_called()
                    self.assertFalse((self.evidence / executor.MARKER).exists())
                    self.assertEqual(debris.read_bytes(), b"preserve")
                    self.assertEqual(list(self.parent.glob('.approved-input*.stage-*')), [debris])
                    debris.unlink()

    def test_path_failure_stops_before_claim_and_staging(self):
        with patch.object(executor, "open_dir", side_effect=executor.Stop(executor.PRECONDITION_FAILED, "PATH_PREFLIGHT")), patch.object(executor, "durable_claim") as claim, patch.object(executor, "stage_and_publish") as stage:
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
        claim.assert_not_called(); stage.assert_not_called()
        self.assertFalse((self.evidence / executor.MARKER).exists())
        self.assertFalse(list(self.parent.glob('*.stage-*')))

    def assert_real_source_rejected_before_claim_staging_publication(self):
        with patch.object(executor, "durable_claim") as claim, patch.object(executor, "stage_and_publish") as stage, patch.object(executor.os, "link") as publish, self.assertRaises(executor.GovernedStop) as caught:
            executor.main()
        self.assertEqual(caught.exception.classification, executor.APPROVED_BYTES_INVALID)
        self.assertNotEqual(caught.exception.classification, "private source byte contract mismatch")
        self.assertNotEqual(caught.exception.classification, "UNKNOWN")
        self.assertNotEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
        self.assertEqual(claim.call_count, 0)
        self.assertEqual(stage.call_count, 0)
        self.assertEqual(publish.call_count, 0)
        self.assertFalse((self.evidence / executor.MARKER).exists())

    def bind_current_approval_contract(self, data):
        approval = PackageBindingReconciliationTests.APPROVAL
        self.specs = (self.specs[0], approval)
        self.stack.enter_context(patch.object(executor, "FILES", self.specs))
        path = self.source / approval[0]
        path.chmod(0o600)
        path.write_bytes(data)
        path.chmod(0o400)

    def test_old_semantic_byte_count_rejected_by_real_source_path(self):
        data = b"x" * 3549 + b"\n"
        self.assertEqual(len(data[:-1]), 3549)
        self.bind_current_approval_contract(data)
        self.assert_real_source_rejected_before_claim_staging_publication()

    def test_old_transport_byte_count_rejected_by_real_source_path(self):
        data = b"y" * 3549 + b"\n"
        self.assertEqual(len(data), 3550)
        self.bind_current_approval_contract(data)
        self.assert_real_source_rejected_before_claim_staging_publication()

    def test_current_approval_binding_accepted_by_real_source_path(self):
        prefix, suffix = b'{"padding":"', b'"}'
        semantic = prefix + b"n" * (3579 - len(prefix) - len(suffix)) + suffix
        data = semantic + b"\n"
        self.assertEqual((len(semantic), len(data)), (3579, 3580))
        self.bind_current_approval_contract(data)
        expected = PackageBindingReconciliationTests.APPROVAL[3]
        real_sha256 = executor.sha256
        def governed_digest(value):
            if value == semantic:
                return expected
            return real_sha256(value)
        source_fd = os.open(self.source, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, source_fd)
        with patch.object(executor, "sha256", side_effect=governed_digest):
            accepted = executor.read_source(source_fd, *executor.FILES[1])
        self.assertEqual(accepted, data)
        self.assertEqual(governed_digest(semantic), expected)
        self.assertEqual(len(real_sha256(data)), 64)

    def test_old_semantic_sha_rejected_by_real_source_path(self):
        semantic = b"z" * 3579
        self.bind_current_approval_contract(semantic + b"\n")
        real_sha256 = executor.sha256
        old_digest = PackageBindingReconciliationTests.OLD_APPROVAL[3]
        def semantic_digest(data):
            if data == semantic:
                return old_digest
            return real_sha256(data)
        with patch.object(executor, "sha256", side_effect=semantic_digest):
            self.assert_real_source_rejected_before_claim_staging_publication()

class DurabilityMatrix(SyntheticRun):
    def failed_claim(self, mode):
        # Match the actual evidence FD opened by main, not the fixture's separate FD.
        real_fsync = os.fsync
        real_close = os.close
        marker_fds = []
        real_open = os.open
        def opening(path, *args, **kwargs):
            fd = real_open(path, *args, **kwargs)
            if path == executor.MARKER: marker_fds.append(fd)
            return fd
        def syncing(fd):
            is_marker = fd in marker_fds
            if (mode == "file" and is_marker) or (mode == "parent" and not is_marker):
                raise OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")
            real_fsync(fd)
        def closing(fd):
            real_close(fd)
            if mode == "close" and fd in marker_fds: raise OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(executor.os, "open", side_effect=opening))
            stack.enter_context(patch.object(executor.os, "fsync", side_effect=syncing))
            stack.enter_context(patch.object(executor.os, "close", side_effect=closing))
            if mode == "write": stack.enter_context(patch.object(executor, "write_all", side_effect=OSError(errno.EIO, "PRIVATE_EXCEPTION_DETAIL")))
            stage = stack.enter_context(patch.object(executor, "stage_and_publish"))
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        for fd in marker_fds:
            try: real_close(fd)
            except OSError: pass
        self.assertEqual(caught.exception.classification, UNCERTAIN)
        self.assertEqual(self.states[0].consumption_state, "CLAIMED")
        return stage

    def test_01_existing_marker(self):
        (self.evidence / executor.MARKER).write_bytes(b"consumed")
        self.assert_retry_blocked()
    def test_02_marker_write(self): self.failed_claim("write")
    def test_03_marker_fsync(self): self.failed_claim("file")
    def test_04_marker_close(self): self.failed_claim("close")
    def test_05_parent_fsync(self): self.failed_claim("parent")
    def test_06_no_stage_after_write(self): self.failed_claim("write").assert_not_called()
    def test_07_no_stage_after_fsync(self): self.failed_claim("file").assert_not_called()
    def test_08_no_stage_after_close(self): self.failed_claim("close").assert_not_called()
    def test_09_no_stage_after_parent(self): self.failed_claim("parent").assert_not_called()
    def test_10_uncertain_marker_preserved_retry_prohibited(self):
        self.failed_claim("write")
        self.assert_retry_blocked()
    def test_11_postdurable_failure_retry_prohibited(self):
        with patch.object(executor, "stage_and_publish", side_effect=executor.GovernedStop(executor.APPROVED_INPUT_STAGING_FAILED, "STAGING")):
            with self.assertRaises(executor.GovernedStop): executor.main()
        self.assertEqual(self.states[0].consumption_state, "EXECUTION_STARTED")
        self.assert_retry_blocked()
    def test_12_not_started_before_staging(self):
        real_claim = executor.durable_claim
        def claim(*args):
            value = real_claim(*args)
            self.assertEqual(args[-1].consumption_state, "DURABLY_CONSUMED")
            return value
        with patch.object(executor, "durable_claim", side_effect=claim): self.assertEqual(executor.main(), 0)
    def test_13_started_at_staging(self):
        real_stage = executor.stage_and_publish
        def stage(*args, **kwargs):
            self.assertEqual(self.states[0].consumption_state, "EXECUTION_STARTED")
            self.assertEqual(json.loads((self.evidence / executor.MARKER).read_bytes())["state"], "DURABLY_CONSUMED")
            return real_stage(*args, **kwargs)
        with patch.object(executor, "stage_and_publish", side_effect=stage): self.assertEqual(executor.main(), 0)

class ClassificationMatrix(unittest.TestCase):
    def setUp(self): self.state = executor.ExecutionState()
    def expect(self, expected, context=None):
        self.assertEqual(executor.derive_primary_classification(self.state, context), expected)
    def complete(self):
        self.state.consumption_state = "EXECUTION_STARTED"
        for item in (self.state.input, self.state.approval):
            item.published = item.final_verified = item.cleanup_complete = True
    def partial(self, context):
        self.state.consumption_state = "EXECUTION_STARTED"
        self.state.input.published = self.state.input.final_verified = True
        self.expect(executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION, context)
    def test_01_precondition(self): self.expect(executor.PRECONDITION_FAILED, {"classification":executor.PRECONDITION_FAILED})
    def test_02_expired(self): self.expect(executor.APPROVAL_EXPIRED, {"classification":executor.APPROVAL_EXPIRED})
    def test_03_target_exists(self): self.expect(executor.TARGET_ALREADY_EXISTS, {"classification":executor.TARGET_ALREADY_EXISTS})
    def test_04_bytes_invalid(self): self.expect(executor.APPROVED_BYTES_INVALID, {"classification":executor.APPROVED_BYTES_INVALID})
    def test_05_consumed(self): self.expect(executor.AUTHORITY_CONSUMED, {"classification":executor.AUTHORITY_CONSUMED})
    def test_06_staging(self):
        self.state.consumption_state = "DURABLY_CONSUMED"
        self.expect(executor.APPROVED_INPUT_STAGING_FAILED, {"stage":"staging"})
    def test_07_precleanup(self): self.expect(PRE_CLEANUP, {"stage":"staging", "cleanup":"prepublication"})
    def test_08_partial_staging(self): self.partial({"stage":"staging"})
    def test_09_partial_eexist(self): self.partial({"classification":executor.TARGET_ALREADY_EXISTS})
    def test_10_partial_verify(self): self.partial({"classification":executor.APPROVED_INPUT_FINAL_VERIFICATION_FAILED})
    def test_11_cleanup(self):
        self.complete(); self.expect(executor.APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE, {"cleanup":"postpublication"})
    def test_12_input_cleanup_blocks_success(self):
        self.complete(); self.state.input.cleanup_complete = False
        self.assertNotEqual(executor.derive_primary_classification(self.state, {"pair_reverified":True}), SUCCESS)
    def test_13_approval_cleanup_blocks_success(self):
        self.complete(); self.state.approval.cleanup_complete = False
        self.assertNotEqual(executor.derive_primary_classification(self.state, {"pair_reverified":True}), SUCCESS)
    def test_14_pair_reverification_required(self):
        self.complete(); self.assertNotEqual(executor.derive_primary_classification(self.state), SUCCESS)
        self.expect(SUCCESS, {"pair_reverified":True})

class ResultEvidenceMatrix(TempCase):
    def write(self, success=False):
        if success:
            executor.write_result_with_secondary(self.fd, self.state, SUCCESS, success=True)
        else:
            executor.write_failure_result(self.fd, self.state, executor.GovernedStop(executor.APPROVED_BYTES_INVALID,"VALIDATE","input",errno.EIO))
        return (self.root / executor.RESULT).read_text()
    def test_policy_exact_keys(self):
        policy = (EXECUTOR_PATH.parent / "00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md").read_text()
        block = policy.split("The result object has this exact closed top-level key set (one key per line):", 1)[1].split("```text\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(set(block.splitlines()), KEYS)
    def test_01_exact_keys(self): self.assertEqual(set(json.loads(self.write())), KEYS)
    def test_02_no_extra_keys_success(self): self.assertEqual(set(json.loads(self.write(True))), KEYS)
    def test_03_failure_minimized(self):
        obj = json.loads(self.write()); self.assertEqual(obj["artifact_role"],"input"); self.assertEqual(obj["errno_code"],errno.EIO)
    def test_04_success_minimized(self):
        obj = json.loads(self.write(True)); self.assertEqual(obj["classification"],SUCCESS); self.assertIsNone(obj["errno_code"])
    def test_05_no_raw_input(self):
        self.state.raw_input = '{"RAW_INPUT_SECRET":123}'
        self.assertNotIn("RAW_INPUT_SECRET",self.write())
    def test_06_no_raw_approval(self):
        self.state.raw_approval = '{"RAW_APPROVAL_SECRET":456}'
        self.assertNotIn("RAW_APPROVAL_SECRET",self.write())
    def test_07_no_business_facts(self):
        self.state.supplier_name = "PRIVATE_SUPPLIER"
        text = self.write()
        for value in ("PRIVATE_SUPPLIER","supplier","quantities","document_number","items","credentials"): self.assertNotIn(value,text)
    def test_08_no_traceback(self): self.assertNotIn("Traceback",self.write())
    def test_09_no_exception_repr(self): self.assertNotIn("GovernedStop(",self.write())
    def test_10_exclusive_nofollow_flags_and_mode(self):
        with patch.object(executor.os,"open",wraps=os.open) as opening: self.write()
        call = opening.call_args
        for flag in (os.O_WRONLY,os.O_CREAT,os.O_EXCL,os.O_NOFOLLOW,os.O_CLOEXEC): self.assertTrue(call.args[1] & flag)
        self.assertEqual(stat.S_IMODE((self.root/executor.RESULT).stat().st_mode),0o600)
    def test_11_existing_result_preserved(self):
        before = self.write()
        with self.assertRaises((executor.GovernedStop,FileExistsError)): self.write()
        self.assertEqual((self.root/executor.RESULT).read_text(),before)
    def result_fault(self, mode, primary=UNCERTAIN):
        self.state.consumption_state = "CLAIMED"
        with self.fault(mode), contextlib.redirect_stderr(io.StringIO()) as stderr:
            outcome = executor.write_result_with_secondary(self.fd,self.state,primary)
        self.assertEqual(outcome,(primary,executor.RESULT_EVIDENCE_WRITE_FAILED))
        self.assertEqual(stderr.getvalue(),executor.RESULT_EVIDENCE_WRITE_FAILED+"\n")
    def test_12_file_fsync_failure(self): self.result_fault("file")
    def test_13_close_failure(self): self.result_fault("close")
    def test_14_parent_fsync_failure(self): self.result_fault("parent")
    def test_15_primary_durability_survives(self): self.result_fault("write")
    def test_16_primary_partial_survives(self): self.result_fault("write",executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
    def test_17_secondary_no_traceback_or_repr(self): self.result_fault("parent",executor.APPROVED_INPUT_STAGING_FAILED)
    def test_18_evidence_failure_no_retry(self):
        executor.durable_claim(self.fd,"a"*40,"b"*64,self.state)
        with patch.object(executor,"write_failure_result",side_effect=OSError(errno.EIO,"PRIVATE_EXCEPTION_DETAIL")), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(executor.write_result_with_secondary(self.fd,self.state,executor.APPROVED_INPUT_STAGING_FAILED),(executor.APPROVED_INPUT_STAGING_FAILED,executor.RESULT_EVIDENCE_WRITE_FAILED))
        self.assert_nonretryable()

class TemporaryOrchestrationTests(SyntheticRun):
    def test_partial_install_real_hardlinks(self):
        real_link = os.link
        linked = {}
        def link(src,dst,**kwargs):
            if dst == self.specs[1][0]: raise FileExistsError(errno.EEXIST,"synthetic collision")
            real_link(src,dst,**kwargs)
            linked[dst] = (self.parent/dst).stat().st_ino
        with patch.object(executor.os,"link",side_effect=link):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
        first = self.parent/self.specs[0][0]
        self.assertEqual(first.read_bytes(),self.payloads[0]); self.assertEqual(first.stat().st_ino,linked[first.name])
        self.assertFalse(self.states[0].approval.final_verified)
        self.assert_retry_blocked()
    def test_postverification_cleanup_real_hardlinks(self):
        real_unlink = os.unlink
        def unlink(path,*args,**kwargs):
            if str(path).startswith(".approved-input-approval.json.stage-"): raise OSError(errno.EACCES,"synthetic unlink")
            return real_unlink(path,*args,**kwargs)
        with patch.object(executor.os,"unlink",side_effect=unlink):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE)
        final = self.parent/self.specs[1][0]
        residual = list(self.parent.glob(".approved-input-approval.json.stage-*"))
        self.assertEqual(len(residual),1); self.assertEqual(final.stat().st_ino,residual[0].stat().st_ino)
        self.assertEqual(final.read_bytes(),self.payloads[1]); self.assert_retry_blocked()
    def test_prepublication_cleanup_failure(self):
        real_unlink = os.unlink
        def unlink(path,*args,**kwargs):
            if str(path).startswith(".approved-input.json.stage-"): raise OSError(errno.EACCES,"synthetic unlink")
            return real_unlink(path,*args,**kwargs)
        with patch.object(executor.os,"link",side_effect=OSError(errno.EIO,"synthetic publish")), patch.object(executor.os,"unlink",side_effect=unlink):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,PRE_CLEANUP)
        self.assertFalse((self.parent/self.specs[0][0]).exists())
        self.assertEqual(len(list(self.parent.glob(".approved-input.json.stage-*"))),1)
        self.assert_retry_blocked()
    def test_success_reverifies_pair_after_both_published(self):
        real_verify = executor.verify_file
        pair_checks = []
        def verify(fd,name,*args):
            if name in (self.specs[0][0],self.specs[1][0]) and all((self.parent/s[0]).exists() for s in self.specs): pair_checks.append(name)
            return real_verify(fd,name,*args)
        with patch.object(executor,"verify_file",side_effect=verify): self.assertEqual(executor.main(),0)
        self.assertEqual(pair_checks[-2:],[self.specs[0][0],self.specs[1][0]])
    def test_generic_staging_failure_with_successful_cleanup(self):
        with patch.object(executor,"write_all",side_effect=[None,OSError(errno.EIO,"synthetic write"),None]):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.APPROVED_INPUT_STAGING_FAILED)
        self.assertFalse(list(self.parent.glob(".*.stage-*")))
        self.assert_retry_blocked()

class AdditionalRegressionTests(SyntheticRun):
    def test_claim_write_failure_closes_writable_fd(self):
        real_open = os.open
        opened = []
        def opening(path,*args,**kwargs):
            fd = real_open(path,*args,**kwargs)
            if path == executor.MARKER: opened.append(fd)
            return fd
        try:
            with patch.object(executor.os,"open",side_effect=opening), patch.object(executor,"write_all",side_effect=OSError(errno.EIO,"private")):
                with self.assertRaises(executor.GovernedStop): executor.main()
            self.assertEqual(len(opened),1)
            with self.assertRaises(OSError): os.fstat(opened[0])
        finally:
            for fd in opened:
                try: os.close(fd)
                except OSError: pass
    def test_partial_result_records_actual_input_state(self):
        real_link = os.link
        def link(src,dst,**kwargs):
            if dst == self.specs[1][0]: raise OSError(errno.EIO,"private")
            return real_link(src,dst,**kwargs)
        with patch.object(executor.os,"link",side_effect=link):
            with self.assertRaises(executor.GovernedStop): executor.main()
        result = json.loads((self.evidence/executor.RESULT).read_bytes())
        self.assertEqual(result["classification"],executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
        self.assertEqual(set(result), executor.RESULT_KEYS)
        self.assertIsNotNone(result["parent_metadata"])
        self.assertTrue(result["approval_freshness_valid"])
        self.assertEqual(result["input_semantic_sha256"], executor.sha256(self.payloads[0][:-1]))
        self.assertEqual(result["approval_transport_bytes"], len(self.payloads[1]))
        self.assertTrue(result["input_writable_fd_closed"])
        self.assertTrue(result["input_cleanup_complete"])
        self.assertTrue(result["input_verified"]); self.assertFalse(result["approval_verified"])
    def test_input_cleanup_failure_is_cleanup_not_partial(self):
        real_unlink = os.unlink
        def unlink(path,*args,**kwargs):
            if str(path).startswith(".approved-input.json.stage-"): raise OSError(errno.EACCES,"private")
            return real_unlink(path,*args,**kwargs)
        with patch.object(executor.os,"unlink",side_effect=unlink):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE)
        self.assertEqual((self.parent/self.specs[0][0]).read_bytes(),self.payloads[0])
        self.assert_retry_blocked()

class ResultWriterRegressionTests(TempCase):
    def test_short_write_closes_result_fd(self):
        opened = []
        real_open = os.open
        def opening(*args,**kwargs):
            fd=real_open(*args,**kwargs); opened.append(fd); return fd
        try:
            with patch.object(executor.os,"open",side_effect=opening), patch.object(executor.os,"write",return_value=0), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(executor.write_result_with_secondary(self.fd,self.state,UNCERTAIN),(UNCERTAIN,executor.RESULT_EVIDENCE_WRITE_FAILED))
            with self.assertRaises(OSError): os.fstat(opened[0])
        finally:
            for fd in opened:
                try: os.close(fd)
                except OSError: pass
    def test_symlink_result_does_not_touch_target(self):
        target=self.root/'existing'; target.write_bytes(b'unchanged')
        (self.root/executor.RESULT).symlink_to(target)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(executor.write_result_with_secondary(self.fd,self.state,UNCERTAIN),(UNCERTAIN,executor.RESULT_EVIDENCE_WRITE_FAILED))
        self.assertEqual(target.read_bytes(),b'unchanged')

class IntegrationRegressionTests(SyntheticRun):
    def test_success_result_contains_policy_metadata(self):
        self.assertEqual(executor.main(), 0)
        record = json.loads((self.evidence / executor.RESULT).read_bytes())
        self.assertEqual(set(record), executor.RESULT_KEYS)
        self.assertEqual(record["classification"], SUCCESS)
        self.assertTrue(record["claim_exclusive"])
        self.assertTrue(record["durability_barrier_complete"])
        self.assertTrue(record["pre_targets_absent"])
        self.assertTrue(record["approval_freshness_valid"])
        self.assertEqual(set(record["parent_metadata"]), {"device", "inode", "uid", "gid", "mode"})
        self.assertTrue(record["pair_reverified"])
        for role, source in zip(("input", "approval"), self.payloads):
            self.assertEqual(record[f"{role}_semantic_sha256"], executor.sha256(source[:-1]))
            self.assertEqual(record[f"{role}_transport_bytes"], len(source))
            for field in ("staging_verified", "writable_fd_closed", "writable_fd_absent", "stage_device_verified", "published", "verified", "final_inode_verified", "semantic_prefix_hash_verified", "transport_bytes_verified", "cleanup_complete"):
                self.assertTrue(record[f"{role}_{field}"], (role, field))
            self.assertEqual(record[f"{role}_final_metadata"]["size"], len(source))
        for private in ("synthetic\":\"input", "synthetic\":\"approval", "supplier_name", "document_number", "candidate_material_description", "Traceback"):
            self.assertNotIn(private, json.dumps(record))
    def test_success_evidence_failure_preserves_pair_and_blocks_retry(self):
        with patch.object(executor,"write_failure_result",side_effect=OSError(errno.EIO,"PRIVATE_EXCEPTION_DETAIL")), contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(executor.main(),1)
        self.assertEqual(output.getvalue(),executor.RESULT_EVIDENCE_WRITE_FAILED+'\n')
        for spec,data in zip(self.specs,self.payloads): self.assertEqual((self.parent/spec[0]).read_bytes(),data)
        self.assert_retry_blocked()
    def test_pair_reverification_failure_never_success(self):
        real_verify=executor.verify_file
        def verify(fd,name,*args):
            if self.states and self.states[0].current_stage == 'PAIR_REVERIFY': raise OSError(errno.EIO,'PRIVATE_EXCEPTION_DETAIL')
            return real_verify(fd,name,*args)
        with patch.object(executor,'verify_file',side_effect=verify):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.APPROVED_INPUT_FINAL_VERIFICATION_FAILED)
        self.assertNotEqual(json.loads((self.evidence/executor.RESULT).read_bytes())['classification'],SUCCESS)
        self.assert_retry_blocked()
    def test_approval_final_verification_partial(self):
        real_verify=executor.verify_file
        def verify(fd,name,*args):
            if name == self.specs[1][0]: raise OSError(errno.EIO,'PRIVATE_EXCEPTION_DETAIL')
            return real_verify(fd,name,*args)
        with patch.object(executor,'verify_file',side_effect=verify):
            with self.assertRaises(executor.GovernedStop) as caught: executor.main()
        self.assertEqual(caught.exception.classification,executor.STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION)
        record=json.loads((self.evidence/executor.RESULT).read_bytes())
        self.assertEqual(record['errno_code'],errno.EIO)
        self.assertEqual(record['artifact_role'],self.specs[1][0])
        self.assertTrue(record['approval_published']); self.assertFalse(record['approval_verified'])
        self.assert_retry_blocked()

if __name__ == '__main__':
    unittest.main()
