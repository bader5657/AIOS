import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
EXECUTOR = ROOT / "docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py"
spec = importlib.util.spec_from_file_location("stage033c_r13a_executor", EXECUTOR)
executor = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = executor
spec.loader.exec_module(executor)


def git(repo, *args):
    return subprocess.run(("git", "-C", str(repo), *args), check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def activation(executor_sha, merge, head):
    return {
        "schema_version": executor.ACTIVATION_SCHEMA_VERSION,
        "authority_id": executor.AUTHORITY_ID,
        "pr_number": 289,
        "reviewed_head_sha": executor.R13_REVIEWED_HEAD,
        "authority_merge_sha": merge,
        "expected_runtime_head": head,
        "executor_sha256": executor_sha,
        "policy_reference": str(executor.REL_POLICY),
        "activated_at_utc": "2026-09-20T00:00:00.000000Z",
    }


class GitGraphCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init")
        git(self.repo, "config", "user.email", "r13a@example.invalid")
        git(self.repo, "config", "user.name", "R13A Test")
        self.exec_path = self.repo / executor.REL_EXECUTOR
        self.policy_path = self.repo / executor.REL_POLICY
        self.authority_path = self.repo / executor.REL_R13_AUTHORITY
        self.exec_path.parent.mkdir(parents=True)
        self.authority_path.parent.mkdir(parents=True)
        self.exec_path.write_bytes(b"reviewed executor\n")
        digest = hashlib.sha256(self.exec_path.read_bytes()).hexdigest()
        self.policy_path.write_text(
            f"{executor.AUTHORITY_ID}\nP4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW\n"
            f"| executor SHA-256 | `{digest}` |\n"
        )
        self.authority_path.write_text("reviewed PR 289 authority\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "reviewed")
        self.reviewed = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "merge-proof").write_text("human merge\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "authority merge")
        self.merge = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "runtime-proof").write_text("runtime head\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "runtime head")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.digest = digest
        self.activation = activation(digest, self.merge, self.head)
        self.activation["reviewed_head_sha"] = self.reviewed
        self.patches = (
            patch.object(executor, "REPOSITORY", self.repo),
            patch.object(executor, "R13_REVIEWED_HEAD", self.reviewed),
        )
        for item in self.patches:
            item.start(); self.addCleanup(item.stop)

    def assert_precondition(self):
        with self.assertRaises(executor.GovernedStop) as caught:
            executor.verify_merged_authority(self.digest, self.activation)
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)

    def test_exact_expected_head_and_valid_activation_accepted(self):
        self.assertEqual(executor.verify_merged_authority(self.digest, self.activation), self.merge)

    def test_wrong_head_rejected(self):
        self.activation["expected_runtime_head"] = self.merge
        self.assert_precondition()

    def test_modified_tracked_file_rejected(self):
        (self.repo / "runtime-proof").write_text("dirty\n")
        self.assert_precondition()

    def test_staged_change_rejected(self):
        (self.repo / "runtime-proof").write_text("staged\n")
        git(self.repo, "add", "runtime-proof")
        self.assert_precondition()

    def test_untracked_file_rejected(self):
        (self.repo / "untracked").write_text("dirt\n")
        self.assert_precondition()

    def test_repository_resolution_failure_rejected(self):
        with patch.object(executor, "REPOSITORY", self.repo / "missing"):
            self.assert_precondition()

    def test_invalid_merge_sha_rejected(self):
        self.activation["authority_merge_sha"] = "f" * 40
        self.assert_precondition()

    def test_merge_not_ancestor_rejected(self):
        git(self.repo, "checkout", "--orphan", "unrelated")
        for child in self.repo.iterdir():
            if child.name != ".git" and child.is_file():
                child.unlink()
        (self.repo / "orphan").write_text("unrelated\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "unrelated")
        unrelated = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", self.head)
        self.activation["authority_merge_sha"] = unrelated
        self.assert_precondition()

    def test_reviewed_authority_document_must_match_merge_lineage(self):
        self.activation["authority_merge_sha"] = self.head
        self.authority_path.write_text("changed authority\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "changed authority")
        changed = git(self.repo, "rev-parse", "HEAD")
        self.activation["authority_merge_sha"] = changed
        self.activation["expected_runtime_head"] = changed
        self.assert_precondition()


class ActivationSchemaTests(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 64
        self.valid = activation(self.sha, "b" * 40, "c" * 40)

    def reject(self, changed):
        value = dict(self.valid); value.update(changed)
        with self.assertRaises(executor.GovernedStop) as caught:
            executor.validate_activation_schema(value, self.sha)
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)

    def test_valid_schema_accepted(self):
        executor.validate_activation_schema(self.valid, self.sha)

    def test_wrong_pr_number_rejected(self):
        self.reject({"pr_number": 288})

    def test_wrong_reviewed_head_rejected(self):
        self.reject({"reviewed_head_sha": "d" * 40})

    def test_wrong_executor_sha_rejected(self):
        self.reject({"executor_sha256": "e" * 64})

    def test_malformed_and_unknown_schema_rejected(self):
        for value in ({}, {**self.valid, "unknown": True}):
            with self.subTest(value=value):
                with self.assertRaises(executor.GovernedStop):
                    executor.validate_activation_schema(value, self.sha)

    def test_activation_absent_stops_main_before_claim(self):
        with patch.object(executor, "check_no_args_root"), \
             patch.object(executor, "read_activation_record", side_effect=executor.Stop(executor.PRECONDITION_FAILED, "ACTIVATION")), \
             patch.object(executor, "durable_claim") as claim:
            with self.assertRaises(executor.GovernedStop): executor.main()
        claim.assert_not_called()


class InterpreterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.python = Path(self.tmp.name) / "python"
        self.python.symlink_to(Path(os.__file__).resolve())

    def test_correct_path_and_version_accepted(self):
        with patch.object(executor, "EXPECTED_INTERPRETER", str(self.python)):
            executor.verify_actual_interpreter(str(self.python), (3, 12, 3, "final"))

    def test_wrong_interpreter_path_rejected(self):
        with patch.object(executor, "EXPECTED_INTERPRETER", str(self.python)):
            with self.assertRaises(executor.GovernedStop):
                executor.verify_actual_interpreter(str(self.python) + "-other", (3, 12, 3))

    def test_wrong_python_version_rejected(self):
        with patch.object(executor, "EXPECTED_INTERPRETER", str(self.python)):
            with self.assertRaises(executor.GovernedStop):
                executor.verify_actual_interpreter(str(self.python), (3, 12, 4))


class SourceLinkCountTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY); self.addCleanup(os.close, self.fd)
        self.specs = []
        for name in ("approved-input.json", "approved-input-approval.json"):
            data = json.dumps({"role": name}, separators=(",", ":")).encode() + b"\n"
            (self.root / name).write_bytes(data); (self.root / name).chmod(0o400)
            self.specs.append((name, len(data)-1, len(data), hashlib.sha256(data[:-1]).hexdigest(), data))

    def metadata(self, real, links):
        def fake(fd):
            value = real(fd); values = list(value)
            values[3] = links; values[4] = 0; values[5] = 0; values[0] = stat.S_IFREG | 0o400
            return os.stat_result(values)
        return fake

    def test_single_link_accepted_for_both_roles(self):
        real = os.fstat
        with patch.object(executor.os, "fstat", side_effect=self.metadata(real, 1)):
            for name, semantic, transport, digest, data in self.specs:
                with self.subTest(role=name):
                    self.assertEqual(executor.read_source(self.fd, name, semantic, transport, digest), data)

    def test_multiple_links_rejected_for_both_roles_before_claim(self):
        real = os.fstat
        with patch.object(executor.os, "fstat", side_effect=self.metadata(real, 2)):
            for name, semantic, transport, digest, _ in self.specs:
                with self.subTest(role=name):
                    with self.assertRaises(executor.GovernedStop) as caught:
                        executor.read_source(self.fd, name, semantic, transport, digest)
                    self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)


if __name__ == "__main__":
    unittest.main()
