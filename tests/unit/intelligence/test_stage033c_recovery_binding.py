"""R32 recovery gates. All bytes, markers, and publication paths are temporary."""
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from tests.unit.intelligence import test_stage033c_registry_manifest_matrix as matrix
from tests.unit.intelligence import test_stage033c_orchestration as orchestration
from tests.unit.intelligence.test_stage033c_r13a_preclaim import activation

m = matrix.m
OLD_AUTHORITY = "9d29c855-0f23-4539-a9b9-2e17dc89c49d"
OLD_APPROVAL = "122625d8-d3fd-42a7-b9c6-c54fc1f367bf"


class RecoveryPackageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.f = matrix.fixture(temp.name)
        p = self.f["approval"]["package_payload"]
        p.update(approval_id=m.RECOVERY_APPROVAL_ID,
                 approved_at_utc=m.RECOVERY_APPROVED_AT,
                 not_after_utc=m.RECOVERY_NOT_AFTER)
        self.approval_bytes = matrix.rehash(self.f)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(m, "utc_now", return_value=m.parse_utc(m.RECOVERY_APPROVED_AT)))
        # Synthetic facts/evidence are deliberately not private production bytes.
        # Freeze their initial hashes; mutations never refresh the active bindings.
        self.stack.enter_context(patch.object(m, "RECOVERY_PAYLOAD_SHA256", self.f["approval"]["package_payload_sha256"]))
        self.stack.enter_context(patch.object(m, "RECOVERY_TF_A", p["trusted_facts_sha256"]))
        specs = tuple((name, len(data)-1, len(data), m.sha256(data[:-1])) for name, data in zip(
            ("approved-input.json", "approved-input-approval.json"),
            (self.f["input_transport"], self.approval_bytes)))
        self.stack.enter_context(patch.object(m, "FILES", specs))

    def validate(self, approval_bytes=None):
        return m.validate_frozen_package(self.f["input_transport"], approval_bytes or matrix.rehash(self.f),
                                         manifest_root=self.f["manifest_root"], retained_root=self.f["retained"])

    def reject(self, stage=None):
        with patch.object(m, "durable_claim") as claim, patch.object(m, "stage_and_publish") as stage_publish, patch.object(m.os, "link") as publish:
            with self.assertRaises(m.GovernedStop) as caught:
                self.validate()
            if stage:
                self.assertEqual(caught.exception.stage, stage)
            claim.assert_not_called(); stage_publish.assert_not_called(); publish.assert_not_called()

    def test_unchanged_input_and_fresh_approval_accepted(self):
        before = self.f["input_transport"]
        i, a, _ = self.validate()
        self.assertEqual(before, self.f["input_transport"])
        self.assertEqual(a["package_payload"]["approval_id"], m.RECOVERY_APPROVAL_ID)
        self.assertIsNone(i["ingestion_result"]["registry_record_id"])
        self.assertIs(i["ingestion_result"]["registration_succeeded"], False)

    def test_historical_approval_rejected_even_before_historical_expiry(self):
        p = self.f["approval"]["package_payload"]
        p.update(approval_id=OLD_APPROVAL, approved_at_utc="2026-09-19T21:24:52.273127Z", not_after_utc="2026-09-26T21:24:52.273127Z")
        with patch.object(m, "utc_now", return_value=m.parse_utc(p["approved_at_utc"])):
            self.reject("RECOVERY_APPROVAL_ID")

    def test_wrong_approval_id(self):
        self.f["approval"]["package_payload"]["approval_id"] = OLD_APPROVAL
        self.reject("RECOVERY_APPROVAL_ID")

    def test_wrong_exact_timestamps(self):
        p = self.f["approval"]["package_payload"]
        for key in ("approved_at_utc", "not_after_utc"):
            old = p[key]
            p[key] = old.replace("093093", "093094")
            self.reject("RECOVERY_APPROVAL_TIME")
            p[key] = old

    def test_self_consistent_unreviewed_payload_rejected(self):
        self.f["approval"]["package_payload"]["project_owner_approval_reference"] = "UNREVIEWED"
        self.reject("RECOVERY_PAYLOAD_HASH")

    def test_wrong_outer_payload_hash(self):
        self.f["approval"]["package_payload_sha256"] = "0" * 64
        with self.assertRaises(m.GovernedStop) as caught:
            self.validate(matrix.canon(self.f["approval"]) + b"\n")
        self.assertEqual(caught.exception.stage, "PAYLOAD_HASH")

    def test_historical_payload_digest_cannot_bind_recovery(self):
        with patch.object(m, "RECOVERY_PAYLOAD_SHA256", "3b25029b1015bd67eddab2557cfef8202a48fff546ffc79fc3ab708c144de1f4"):
            self.reject("RECOVERY_PAYLOAD_HASH")

    def test_wrong_tf_a(self):
        with patch.object(m, "RECOVERY_TF_A", "0" * 64):
            self.reject("RECOVERY_TRUSTED_FACTS_HASH")

    def test_wrong_approval_semantic_hash(self):
        specs = (m.FILES[0], (*m.FILES[1][:3], "0" * 64))
        with patch.object(m, "FILES", specs):
            self.reject("RECOVERY_SOURCE_BINDING")

    def test_model_b_is_mandatory_even_for_consistent_registry(self):
        self.f["input"]["ingestion_result"].update(registration_succeeded=True, registry_record_id=42)
        self.f["approval"]["package_payload"]["evidence"]["registry_record_id"] = 42
        matrix.refresh(self.f)
        with patch.object(m, "RECOVERY_PAYLOAD_SHA256", self.f["approval"]["package_payload_sha256"]):
            self.reject("RECOVERY_MODEL_B")

    def test_expiry_boundary_no_renewal(self):
        expiry = m.parse_utc(m.RECOVERY_NOT_AFTER)
        import datetime as dt
        with patch.object(m, "utc_now", return_value=expiry-dt.timedelta(microseconds=1)):
            self.validate()
        with patch.object(m, "utc_now", return_value=expiry):
            self.reject("APPROVAL_TIME")


class RecoveryOrchestrationTests(orchestration.SyntheticRun):
    def setUp(self):
        super().setUp()
        self.m = orchestration.executor
        self.recovery = self.root / "recovery"
        self.recovery.mkdir(mode=0o700)
        (self.source / self.specs[1][0]).rename(self.recovery / self.specs[1][0])
        self.stack.enter_context(patch.object(self.m, "APPROVAL_SOURCE_PARENT", self.recovery))
        self.opened = []
        def opening(path, *args, **kwargs):
            self.opened.append((path, args))
            self.assertIn(path, (self.parent, self.source, self.recovery))
            return os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        self.stack.enter_context(patch.object(self.m, "open_dir", side_effect=opening))

    def no_effect(self, expected=None):
        with patch.object(self.m, "durable_claim") as claim, patch.object(self.m, "stage_and_publish") as staging, patch.object(self.m.os, "link") as publication:
            with self.assertRaises((self.m.GovernedStop, OSError)) as caught:
                self.m.main()
            if expected:
                self.assertEqual(caught.exception.classification, expected)
            self.assertEqual((claim.call_count, staging.call_count, publication.call_count), (0, 0, 0))
        self.assertFalse((self.evidence / self.m.MARKER).exists())

    def test_split_sources_no_duplicate_input_or_shared_parent(self):
        self.assertFalse((self.recovery / self.specs[0][0]).exists())
        self.assertFalse((self.source / self.specs[1][0]).exists())
        self.assertEqual(self.m.main(), 0)
        self.assertEqual(self.opened[1:], [(self.source, (0, 0, 0o700)), (self.recovery, (0, 0, 0o700))])

    def test_both_parent_checks_precede_any_source_read(self):
        with patch.object(self.m, "read_source", side_effect=self.m.Stop(self.m.PRECONDITION_FAILED)) as reading:
            self.no_effect()
            self.assertEqual(reading.call_count, 1)
            self.assertEqual([p for p, _ in self.opened], [self.parent, self.source, self.recovery])

    def test_either_source_parent_failure_stops_before_reads(self):
        real = self.m.open_dir.side_effect
        for bad in (self.source, self.recovery):
            def opening(path, *args, **kwargs):
                if path == bad:
                    raise self.m.Stop(self.m.PRECONDITION_FAILED, "PATH_PREFLIGHT")
                return real(path, *args, **kwargs)
            with patch.object(self.m, "open_dir", side_effect=opening), patch.object(self.m, "read_source") as reading:
                self.no_effect()
                reading.assert_not_called()

    def test_historical_source_input_required(self):
        (self.source / self.specs[0][0]).unlink()
        self.no_effect()

    def test_source_hash_or_lf_failure_zero_effects(self):
        path = self.recovery / self.specs[1][0]
        for data in (b"wrong\n", self.payloads[1][:-1] + b" "):
            path.chmod(0o600); path.write_bytes(data); path.chmod(0o400)
            self.no_effect(self.m.APPROVED_BYTES_INVALID)

    def test_either_source_hardlink_rejected(self):
        for parent, spec in zip((self.source, self.recovery), self.specs):
            alias = self.root / "alias"
            os.link(parent / spec[0], alias)
            self.no_effect(self.m.PRECONDITION_FAILED)
            alias.unlink()

    def test_old_marker_and_result_do_not_consume_recovery(self):
        old = f"step4-install-authority-{OLD_AUTHORITY}.json"
        for name in (old, old + ".result.json"):
            (self.evidence / name).write_bytes(b"immutable history")
        self.assertEqual(self.m.ExecutionState().consumption_state, "UNUSED")
        self.assertEqual(self.m.main(), 0)
        for name in (old, old + ".result.json"):
            self.assertEqual((self.evidence / name).read_bytes(), b"immutable history")
        self.assert_retry_blocked()

    def test_historical_activation_cannot_authorize_main(self):
        value = activation("a"*64, "b"*40, "c"*40)
        value["authority_id"] = OLD_AUTHORITY
        def verify(digest, record):
            self.m.validate_activation_schema(record, digest)
            self.fail("historical activation passed")
        with patch.object(self.m, "read_activation_record", return_value=value), patch.object(self.m, "verify_merged_authority", side_effect=verify):
            self.no_effect(self.m.PRECONDITION_FAILED)
        self.assertEqual(self.opened, [])

    def test_new_marker_means_consumed_without_staging(self):
        marker = self.evidence / self.m.MARKER
        marker.write_bytes(b"ambiguous recovery claim")
        with patch.object(self.m, "durable_claim") as claim, patch.object(self.m, "stage_and_publish") as staging, patch.object(self.m.os, "link") as publication:
            with self.assertRaises(self.m.GovernedStop) as caught:
                self.m.main()
            self.assertEqual(caught.exception.classification, self.m.AUTHORITY_CONSUMED)
            self.assertEqual((claim.call_count, staging.call_count, publication.call_count), (0, 0, 0))
        self.assertEqual(marker.read_bytes(), b"ambiguous recovery claim")

    def test_source_symlink_and_mode_rejected(self):
        path = self.recovery / self.specs[1][0]
        path.chmod(0o600)
        self.no_effect(self.m.PRECONDITION_FAILED)
        path.chmod(0o400)
        renamed = self.recovery / "untouched"
        path.rename(renamed)
        path.symlink_to(renamed)
        self.no_effect()
        self.assertEqual(renamed.read_bytes(), self.payloads[1])

    def test_new_result_alone_consumes_recovery(self):
        (self.evidence / self.m.RESULT).write_bytes(b"ambiguous")
        self.no_effect(self.m.AUTHORITY_CONSUMED)

    def test_package_failures_zero_effects(self):
        for stage in ("RECOVERY_APPROVAL_ID", "RECOVERY_APPROVAL_TIME", "RECOVERY_PAYLOAD_HASH", "RECOVERY_TRUSTED_FACTS_HASH", "RECOVERY_MODEL_B", "RECOVERY_SOURCE_BINDING", "MANIFEST_BINDING"):
            with patch.object(self.m, "validate_frozen_package", side_effect=self.m.Stop(self.m.APPROVED_BYTES_INVALID, stage)):
                self.no_effect(self.m.APPROVED_BYTES_INVALID)


class RecoveryGovernanceTests(unittest.TestCase):
    def test_production_constants(self):
        self.assertEqual(m.AUTHORITY_ID, "7bc638e2-e1f4-4e87-a54a-4d0df031b130")
        self.assertEqual(m.MARKER, f"step4-install-authority-{m.AUTHORITY_ID}.json")
        self.assertEqual(m.RESULT, m.MARKER + ".result.json")
        self.assertEqual(str(m.INPUT_SOURCE_PARENT), "/run/aios/stage-0.33c-p4s5-source")
        self.assertEqual(str(m.APPROVAL_SOURCE_PARENT), "/run/aios/stage-0.33c-p4s5-recovery-source")
        self.assertEqual(m.FILES, (
            ("approved-input.json", 1327, 1328, "e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d"),
            ("approved-input-approval.json", 3579, 3580, "6ea5fc118e375ac035f321110198eb43811fb5b991a095554c15d0a6cbeb16c9")))
        self.assertEqual(m.RECOVERY_APPROVAL_ID, "3a478d87-5c4f-4778-9f88-2228f4d7167f")
        self.assertEqual(m.RECOVERY_APPROVED_AT, "2026-09-26T23:24:12.093093Z")
        self.assertEqual(m.RECOVERY_NOT_AFTER, "2026-10-03T23:24:12.093093Z")
        self.assertEqual(m.RECOVERY_PAYLOAD_SHA256, "be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e")
        self.assertEqual(m.RECOVERY_TF_A, "c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065")
        self.assertEqual(m.ACTIVATION_RECORD, m.RUNTIME_PARENT / "p4s7-recovery-activation.json")

    def test_historical_activation_schema_rejected(self):
        value = activation("a"*64, "b"*40, "c"*40)
        value["authority_id"] = OLD_AUTHORITY
        with self.assertRaises(m.GovernedStop):
            m.validate_activation_schema(value, "a"*64)

    def test_main_cannot_open_historical_activation_or_create_any_state(self):
        with ExitStack() as stack:
            stack.enter_context(patch.object(m, "check_no_args_root"))
            stack.enter_context(patch.object(m, "_protected_record", side_effect=m.Stop(m.PRECONDITION_FAILED, "ACTIVATION")))
            spies = [stack.enter_context(patch.object(m, name)) for name in
                     ("_read_regular_nofollow", "verify_merged_authority", "open_dir", "durable_claim", "stage_and_publish", "write_failure_result")]
            with self.assertRaises(m.GovernedStop) as caught:
                m.main()
            self.assertEqual(caught.exception.stage, "ACTIVATION")
            for spy in spies:
                spy.assert_not_called()

    def test_private_parent_metadata_and_nofollow(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp) / "private"
            parent.mkdir(mode=0o700)
            real = os.fstat
            def root_owner(fd):
                fields = list(real(fd)); fields[4] = fields[5] = 0
                return os.stat_result(fields)
            with patch.object(m.os, "fstat", side_effect=root_owner):
                fd = m.open_dir(parent, 0, 0, 0o700); os.close(fd)
                for mode in (0o755, 0o770, 0o777):
                    parent.chmod(mode)
                    with self.assertRaises(m.GovernedStop): m.open_dir(parent, 0, 0, 0o700)
                parent.chmod(0o700)
                alias = Path(temp) / "alias"; alias.symlink_to(parent)
                with self.assertRaises(m.GovernedStop): m.open_dir(alias, 0, 0, 0o700)
                with self.assertRaises(m.GovernedStop): m.open_dir(Path(temp)/"missing", 0, 0, 0o700)
            for uid, gid in ((1, 0), (0, 1)):
                def wrong_owner(fd):
                    fields = list(real(fd)); fields[4] = uid; fields[5] = gid
                    return os.stat_result(fields)
                with patch.object(m.os, "fstat", side_effect=wrong_owner):
                    with self.assertRaises(m.GovernedStop): m.open_dir(parent, 0, 0, 0o700)
