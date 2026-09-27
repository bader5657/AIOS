import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
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
        "approval_id": executor.RECOVERY_APPROVAL_ID,
        "package_payload_sha256": executor.RECOVERY_PAYLOAD_SHA256,
        "expected_runtime_head": head,
        "executor_sha256": executor_sha,
        "policy_reference": str(executor.REL_POLICY),
        "activated_at_utc": "2026-09-20T00:00:00.000000Z",
    }


class ZeroSideEffectProof:
    def assert_main_precondition_without_side_effects(self):
        with patch.object(executor, "durable_claim") as claim, \
             patch.object(executor, "stage_and_publish") as staging, \
             patch.object(executor.os, "link") as publication:
            with self.assertRaises(executor.GovernedStop) as caught:
                executor.main()
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
        self.assertEqual(claim.call_count, 0, "claim count")
        self.assertEqual(staging.call_count, 0, "staging count")
        self.assertEqual(publication.call_count, 0, "publication count")


# Git-graph preclaim regressions now exercise recovery evidence in
# test_stage033c_recovery_reader.py; the legacy activation format is rejected.

class GitSafeDirectoryTests(unittest.TestCase):
    def test_both_helpers_freeze_exact_path_and_minimal_environment(self):
        self.assertEqual(executor.REPOSITORY, Path("/opt/aios-src"))
        for helper, output in ((executor.run_git, "head\n"), (executor._git_bytes, b"head\n")):
            with self.subTest(helper=helper.__name__), \
                 patch.object(executor.subprocess, "run", return_value=SimpleNamespace(stdout=output)) as run:
                helper("rev-parse", "HEAD")
                expected = dict(check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"})
                if helper is executor.run_git:
                    expected["text"] = True
                run.assert_called_once_with(
                    ("/usr/bin/git", "-c", "safe.directory=/opt/aios-src", "-C",
                     "/opt/aios-src", "rev-parse", "HEAD"), **expected,
                )

    def test_wrong_owned_repository_is_not_added_to_trust(self):
        # Git's test hook exercises the ownership guard without root/chown.
        real_run = subprocess.run

        def different_owner(command, **kwargs):
            self.assertEqual(kwargs["env"], {"PATH": "/usr/bin:/bin"})
            kwargs["env"] = {**kwargs["env"], "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
            return real_run(command, **kwargs)

        with tempfile.TemporaryDirectory() as directory:
            git(directory, "init")
            with patch.object(executor, "REPOSITORY", Path(directory)), \
                 patch.object(executor.subprocess, "run", side_effect=different_owner):
                for helper in (executor.run_git, executor._git_bytes):
                    with self.subTest(helper=helper.__name__), self.assertRaises(executor.GovernedStop) as caught:
                        helper("rev-parse", "--git-dir")
                    self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
                    self.assertEqual(caught.exception.stage, "RUNTIME_REPOSITORY")
                    self.assertEqual(caught.exception.__cause__.returncode, 128)

    def test_exact_governed_repository_ownership_and_no_config_mutation(self):
        # Read-only host proof. Portable CI still checks exact argv above.
        if not Path("/opt/aios-src/.git").exists():
            self.skipTest("governed host repository is not installed")
        configs = (Path("/etc/gitconfig"), Path.home() / ".gitconfig",
                   Path.home() / ".config/git/config", Path("/opt/aios-src/.git/config"))

        def snapshot():
            return {str(path): (path.read_bytes(), path.stat().st_mtime_ns)
                    if path.exists() else None for path in configs}

        before = snapshot()
        env = {"PATH": "/usr/bin:/bin", "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
        command = ("/usr/bin/git", "-C", "/opt/aios-src", "rev-parse", "HEAD")
        rejected = subprocess.run(command, env=env, capture_output=True)
        self.assertEqual(rejected.returncode, 128)
        self.assertIn(b"detected dubious ownership", rejected.stderr)
        real_run = subprocess.run

        def different_owner(command, **kwargs):
            self.assertEqual(kwargs["env"], {"PATH": "/usr/bin:/bin"})
            return real_run(command, **{**kwargs, "env": env})

        with patch.object(executor.subprocess, "run", side_effect=different_owner):
            head = executor.run_git("rev-parse", "HEAD")
            self.assertRegex(head, r"^[0-9a-f]{40}$")
            self.assertEqual(executor._git_bytes("rev-parse", "HEAD"), head.encode() + b"\n")
        # A subsequent unamended process still rejects this same repository.
        self.assertEqual(subprocess.run(command, env=env, capture_output=True).returncode, 128)
        self.assertEqual(snapshot(), before)

    def test_policy_digest_matches_executor_bytes(self):
        import re
        policy = (ROOT / executor.REL_POLICY).read_text()
        match = re.search(r"\| executor SHA-256 \| `([0-9a-f]{64})` \|", policy)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), hashlib.sha256(EXECUTOR.read_bytes()).hexdigest())


class ActivationSchemaTests(ZeroSideEffectProof, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        (self.repo / "fixture-executor.py").write_bytes(b"fixture executor")
        self.sha = hashlib.sha256((self.repo / "fixture-executor.py").read_bytes()).hexdigest()
        self.valid = activation(self.sha, "b" * 40, "c" * 40)
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(executor, "REPOSITORY", self.repo))
        self.stack.enter_context(patch.object(executor, "REL_EXECUTOR", Path("fixture-executor.py")))
        self.stack.enter_context(patch.object(executor, "check_no_args_root"))
        self.stack.enter_context(patch.object(executor, "verify_actual_interpreter"))

    def run_activation(self, value):
        with patch.object(executor, "read_activation_record", return_value=value):
            self.assert_main_precondition_without_side_effects()

    def test_valid_schema_accepted(self):
        executor.validate_activation_schema(self.valid, self.sha)

    def test_wrong_pr_number_rejected(self):
        self.run_activation({**self.valid, "pr_number": 288})

    def test_wrong_reviewed_head_rejected(self):
        self.run_activation({**self.valid, "reviewed_head_sha": "d" * 40})

    def test_wrong_executor_sha_rejected(self):
        self.run_activation({**self.valid, "executor_sha256": "e" * 64})

    def test_malformed_and_unknown_schema_rejected(self):
        self.run_activation({**self.valid, "unknown": True})

    def test_activation_absent_stops_main_before_claim(self):
        real_read = executor.read_activation_record
        missing = self.repo / "activation-record-does-not-exist.json"
        with patch.object(executor, "ACTIVATION_RECORD", missing), patch.object(executor, "read_activation_record", side_effect=lambda: real_read()):
            self.assert_main_precondition_without_side_effects()


class InterpreterTests(ZeroSideEffectProof, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.python = Path(self.tmp.name) / "python"
        self.python.symlink_to(Path(os.__file__).resolve())
        (Path(self.tmp.name) / "fixture-executor.py").write_bytes(b"fixture executor")
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(executor, "REPOSITORY", Path(self.tmp.name)))
        self.stack.enter_context(patch.object(executor, "REL_EXECUTOR", Path("fixture-executor.py")))
        self.stack.enter_context(patch.object(executor, "check_no_args_root"))
        self.stack.enter_context(patch.object(executor, "read_activation_record", return_value={}))
        self.stack.enter_context(patch.object(executor, "verify_merged_authority", return_value="a" * 40))

    def test_correct_path_and_version_accepted(self):
        with patch.object(executor, "EXPECTED_INTERPRETER", str(self.python)):
            executor.verify_actual_interpreter(str(self.python), (3, 12, 3, "final"))

    def test_wrong_interpreter_path_rejected(self):
        with patch.object(executor, "EXPECTED_INTERPRETER", str(self.python)):
            self.assert_main_precondition_without_side_effects()

    def test_wrong_python_version_rejected(self):
        wrong = tuple(sys.version_info[:2]) + (sys.version_info.micro + 1,)
        with patch.object(executor, "EXPECTED_INTERPRETER", sys.executable), \
             patch.object(executor, "EXPECTED_PYTHON_VERSION", wrong):
            self.assert_main_precondition_without_side_effects()


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


    def test_multiple_links_main_path_has_zero_side_effects(self):
        (self.root / "fixture-executor.py").write_bytes(b"fixture executor")
        parent = self.root / "parent"; parent.mkdir()
        (parent / executor.EVIDENCE_DIR).mkdir()
        real_fstat = os.fstat

        def metadata(fd):
            value = real_fstat(fd)
            if stat.S_ISREG(value.st_mode):
                values = list(value); values[3] = 2; values[4] = 0; values[5] = 0
                return os.stat_result(values)
            return value

        def open_fixture(path, *args, **kwargs):
            return os.open(path, os.O_RDONLY | os.O_DIRECTORY)

        with ExitStack() as stack:
            stack.enter_context(patch.object(executor, "REPOSITORY", self.root))
            stack.enter_context(patch.object(executor, "REL_EXECUTOR", Path("fixture-executor.py")))
            stack.enter_context(patch.object(executor, "RUNTIME_PARENT", parent))
            stack.enter_context(patch.object(executor, "INPUT_SOURCE_PARENT", self.root))
            stack.enter_context(patch.object(executor, "APPROVAL_SOURCE_PARENT", self.root))
            stack.enter_context(patch.object(executor, "FILES", tuple(item[:4] for item in self.specs)))
            stack.enter_context(patch.object(executor, "check_no_args_root"))
            stack.enter_context(patch.object(executor, "read_activation_record", return_value={}))
            stack.enter_context(patch.object(executor, "verify_merged_authority", return_value="a" * 40))
            stack.enter_context(patch.object(executor, "verify_actual_interpreter"))
            stack.enter_context(patch.object(executor, "open_dir", side_effect=open_fixture))
            stack.enter_context(patch.object(executor.pwd, "getpwnam", return_value=SimpleNamespace(pw_uid=os.geteuid(), pw_gid=os.getegid())))
            stack.enter_context(patch.object(executor.os, "fstat", side_effect=metadata))
            ZeroSideEffectProof.assert_main_precondition_without_side_effects(self)


if __name__ == "__main__":
    unittest.main()
