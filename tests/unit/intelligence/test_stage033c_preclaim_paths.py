import importlib.util
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

EXECUTOR = Path(__file__).resolve().parents[3] / 'docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py'
spec = importlib.util.spec_from_file_location('stage033c_preclaim_executor', EXECUTOR)
ex = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ex
spec.loader.exec_module(ex)


class PathPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.chain = self.root / 'aios' / 'runtime' / 'intelligence' / 'production-candidate-create' / 'stage-0.33c'
        self.chain.mkdir(parents=True)
        for component in (self.root, *self.chain.parents[:-1]):
            if component == self.root or self.root in component.parents:
                component.chmod(0o755)
        self.chain.chmod(0o750)
        self.real_fstat = os.fstat
        self.real_stat = os.stat
        self.tmp_info = os.stat('/tmp')

    def metadata(self, fd):
        info = self.real_fstat(fd)
        values = list(info)
        values[4] = 0
        if (info.st_dev, info.st_ino) == (self.tmp_info.st_dev, self.tmp_info.st_ino):
            values[0] = stat.S_IFDIR | 0o755
        return os.stat_result(values)

    def check(self):
        with patch.object(ex.os, 'fstat', side_effect=self.metadata):
            return ex.open_dir(self.chain, 0, os.getgid(), 0o750, check_components=True)

    def failure(self):
        with self.assertRaises(ex.GovernedStop) as caught:
            self.check()
        self.assertEqual(caught.exception.classification, ex.PRECONDITION_FAILED)

    def test_valid_complete_chain(self):
        fd = self.check()
        self.assertEqual(self.real_fstat(fd).st_ino, self.real_stat(self.chain).st_ino)
        os.close(fd)

    def test_missing_intermediate(self):
        self.chain.rename(self.root / 'moved')
        self.failure()

    def test_symlink_intermediate(self):
        part = self.root / 'aios' / 'runtime'
        part.rename(self.root / 'real-runtime')
        part.symlink_to(self.root / 'real-runtime')
        self.failure()

    def test_regular_file_intermediate(self):
        part = self.root / 'aios' / 'runtime'
        part.rename(self.root / 'real-runtime')
        part.write_text('x')
        self.failure()

    def test_wrong_owner(self):
        original = self.metadata
        target = self.real_stat(self.root / 'aios')
        def wrong_owner(fd):
            info = original(fd)
            if (info.st_dev, info.st_ino) == (target.st_dev, target.st_ino):
                values = list(info); values[4] = 12345
                return os.stat_result(values)
            return info
        self.metadata = wrong_owner
        self.failure()

    def test_unsafe_writable_intermediate(self):
        (self.root / 'aios').chmod(0o777)
        self.failure()

    def test_final_parent_wrong_mode(self):
        self.chain.chmod(0o755)
        self.failure()

    def test_component_identity_mismatch(self):
        original = os.stat
        target = self.root / 'aios'
        def substituted(path, *args, **kwargs):
            if path == 'aios' and kwargs.get('dir_fd') is not None:
                return original(self.root, follow_symlinks=False)
            return original(path, *args, **kwargs)
        with patch.object(ex.os, 'stat', side_effect=substituted):
            self.failure()


class StagingDebrisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.fd)

    def test_clean_directory_and_unrelated_file_pass(self):
        ex.preflight_install_names(self.fd)
        (self.root / 'unrelated.txt').write_text('keep')
        ex.preflight_install_names(self.fd)

    def test_valid_and_malformed_stage_prefixes_stop_without_mutation(self):
        for final in ('approved-input.json', 'approved-input-approval.json'):
            for suffix in ('123e4567-e89b-42d3-a456-426614174000', 'broken'):
                with self.subTest(final=final, suffix=suffix):
                    name = f'.{final}.stage-{suffix}'
                    path = self.root / name
                    path.write_text('untouched')
                    with self.assertRaises(ex.GovernedStop) as caught:
                        ex.preflight_install_names(self.fd)
                    self.assertEqual(caught.exception.classification, ex.PRECONDITION_FAILED)
                    self.assertEqual(path.read_text(), 'untouched')
                    path.unlink()

    def test_final_target_absence_is_separate(self):
        (self.root / 'approved-input.json').write_text('keep')
        with self.assertRaises(ex.GovernedStop) as caught:
            ex.preflight_install_names(self.fd)
        self.assertEqual(caught.exception.classification, ex.TARGET_ALREADY_EXISTS)
