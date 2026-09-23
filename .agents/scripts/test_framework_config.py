"""Verify that commit selection consumes configured routing and job names."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from checked_commit import checked_commit, nearest_checked_ancestor
from framework_config import load_config
from validation_common import ROOT


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='java-config-tests-', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.agents/schemas').mkdir(parents=True)
        shutil.copy(ROOT / '.agents/schemas/config.schema.json', self.root / '.agents/schemas/config.schema.json')
        self.config = load_config()
        self.config.update(branch='study', workflow_path='.github/workflows/study.yml', required_checks=['check-records'])
        self.write_config()
        self.run = dict(id=20, run_number=1, run_attempt=1, head_sha='a'*40, head_branch='study',
                        path=self.config['workflow_path'], event='push', status='completed', conclusion='success',
                        repository={'html_url': self.config['repository_url']})
        self.jobs = {(20, 1): [dict(name='check-records', run_id=20, run_attempt=1, head_sha='a'*40,
                                  status='completed', conclusion='success')]}

    def write_config(self):
        (self.root / '.agents/config.json').write_text(json.dumps(self.config))

    def test_custom_branch_workflow_and_job_names(self):
        self.assertTrue(checked_commit('a'*40, [self.run], self.jobs, root=self.root)[0])
        self.assertFalse(checked_commit('a'*40, [self.run], self.jobs)[0])

    def test_missing_new_required_job_fails(self):
        self.config['required_checks'].append('check-language')
        self.write_config()
        self.assertFalse(checked_commit('a'*40, [self.run], self.jobs, root=self.root)[0])

    def test_invalid_config_fails_closed(self):
        for value in ([], ['check-records', 'check-records']):
            self.config['required_checks'] = value
            self.write_config()
            self.assertFalse(checked_commit('a'*40, [self.run], self.jobs, root=self.root)[0])

    def test_wrong_repository_is_rejected(self):
        self.run['repository']['html_url'] = 'https://github.com/other/repository'
        self.assertFalse(checked_commit('a'*40, [self.run], self.jobs, root=self.root)[0])

    def test_ancestor_uses_its_own_configuration(self):
        head, parent = 'b'*40, 'a'*40
        self.assertEqual(nearest_checked_ancestor(head, {head: parent}, [self.run], self.jobs,
                         roots_by_sha={head: ROOT, parent: self.root}), parent)
        self.assertIsNone(nearest_checked_ancestor(head, {head: parent}, [self.run], self.jobs,
                          roots_by_sha={head: ROOT}))


if __name__ == '__main__':
    unittest.main()
