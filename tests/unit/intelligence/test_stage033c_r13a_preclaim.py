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
        "pr_number": 289,
        "reviewed_head_sha": executor.R13_REVIEWED_HEAD,
        "authority_merge_sha": merge,
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


class GitGraphCase(ZeroSideEffectProof, unittest.TestCase):
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
        self.main_patches = (
            patch.object(executor, "check_no_args_root"),
            patch.object(executor, "read_activation_record", return_value=self.activation),
            patch.object(executor, "verify_actual_interpreter"),
        )
        for item in self.main_patches:
            item.start(); self.addCleanup(item.stop)

    def assert_precondition(self):
        with self.assertRaises(executor.GovernedStop) as caught:
            executor.verify_merged_authority(self.digest, self.activation)
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)

    def test_exact_expected_head_and_valid_activation_accepted(self):
        self.assertEqual(executor.verify_merged_authority(self.digest, self.activation), self.merge)

    def test_wrong_head_rejected(self):
        self.activation["expected_runtime_head"] = self.merge
        self.assert_main_precondition_without_side_effects()

    def test_modified_tracked_file_rejected(self):
        (self.repo / "runtime-proof").write_text("dirty\n")
        self.assert_main_precondition_without_side_effects()

    def test_staged_change_rejected(self):
        (self.repo / "runtime-proof").write_text("staged\n")
        git(self.repo, "add", "runtime-proof")
        self.assert_main_precondition_without_side_effects()

    def test_untracked_file_rejected(self):
        (self.repo / "untracked").write_text("dirt\n")
        self.assert_main_precondition_without_side_effects()

    def test_repository_resolution_failure_rejected(self):
        # Prove readable prerequisites and repository truth before fault injection.
        self.assertEqual(hashlib.sha256(self.exec_path.read_bytes()).hexdigest(), self.digest)
        self.assertEqual(executor.verify_merged_authority(self.digest, self.activation), self.merge)
        command = ("/usr/bin/git", "-c", "safe.directory=/opt/aios-src", "-C", str(self.repo), "cat-file", "-e", f"{self.merge}^{{commit}}")
        git_failure = subprocess.CalledProcessError(128, command)
        with ExitStack() as stack:
            git_path = stack.enter_context(patch.object(executor, "run_git", wraps=executor.run_git))
            git_command = stack.enter_context(patch.object(executor.subprocess, "run", side_effect=git_failure))
            claim = stack.enter_context(patch.object(executor, "durable_claim"))
            staging = stack.enter_context(patch.object(executor, "stage_and_publish"))
            publication = stack.enter_context(patch.object(executor.os, "link"))
            with self.assertRaises(executor.GovernedStop) as caught:
                executor.main()
        git_path.assert_called_once_with("cat-file", "-e", f"{self.merge}^{{commit}}")
        git_command.assert_called_once_with(
            command, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, env={"PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(caught.exception.classification, executor.PRECONDITION_FAILED)
        self.assertEqual(caught.exception.stage, "RUNTIME_REPOSITORY")
        self.assertIs(caught.exception.__cause__, git_failure)
        self.assertEqual(claim.call_count, 0, "claim count")
        self.assertEqual(staging.call_count, 0, "staging count")
        self.assertEqual(publication.call_count, 0, "publication count")

    def test_invalid_merge_sha_rejected(self):
        self.activation["authority_merge_sha"] = "f" * 40
        self.assert_main_precondition_without_side_effects()

    def test_byte_git_failure_stops_before_claim(self):
        real_run = subprocess.run

        def fail_show(command, **kwargs):
            if "show" in command:
                raise subprocess.CalledProcessError(128, command)
            return real_run(command, **kwargs)

        self.assertEqual(executor.verify_merged_authority(self.digest, self.activation), self.merge)
        with patch.object(executor.subprocess, "run", side_effect=fail_show), \
             patch.object(executor, "_git_bytes", wraps=executor._git_bytes) as byte_git:
            self.assert_main_precondition_without_side_effects()
        byte_git.assert_called_once_with("show", f"{self.reviewed}:{executor.REL_R13_AUTHORITY}")

    def test_executor_head_mismatch_even_when_status_is_clean(self):
        # Git's assume-unchanged bit can hide a local executor edit from status.
        git(self.repo, "update-index", "--assume-unchanged", str(executor.REL_EXECUTOR))
        self.exec_path.write_bytes(b"locally replaced executor\n")
        self.digest = hashlib.sha256(self.exec_path.read_bytes()).hexdigest()
        self.policy_path.write_text(
            f"{executor.AUTHORITY_ID}\nP4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW\n"
            f"| executor SHA-256 | `{self.digest}` |\n"
        )
        git(self.repo, "add", str(executor.REL_POLICY))
        git(self.repo, "commit", "-m", "bind local executor digest")
        self.activation["executor_sha256"] = self.digest
        self.activation["expected_runtime_head"] = git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(executor.run_git("status", "--porcelain=v1", "--untracked-files=all"), "")
        with self.assertRaises(executor.GovernedStop) as caught:
            executor.verify_merged_authority(self.digest, self.activation)
        self.assertEqual(caught.exception.stage, "EXECUTOR_HEAD")
        self.assert_main_precondition_without_side_effects()

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
        self.assert_main_precondition_without_side_effects()

    def test_reviewed_authority_document_must_match_merge_lineage(self):
        self.activation["authority_merge_sha"] = self.head
        self.authority_path.write_text("changed authority\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "changed authority")
        changed = git(self.repo, "rev-parse", "HEAD")
        self.activation["authority_merge_sha"] = changed
        self.activation["expected_runtime_head"] = changed
        self.assert_main_precondition_without_side_effects()


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
        with patch.object(executor, "read_activation_record", side_effect=lambda: real_read(missing)):
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
            stack.enter_context(patch.object(executor, "SOURCE_PARENT", self.root))
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
