"""Reject stale, skipped, incomplete, and unrelated GitHub check results."""
import copy
import unittest

from checked_commit import checked_commit, nearest_checked_ancestor
from framework_config import load_config


class CheckedCommitTests(unittest.TestCase):
    def setUp(self):
        self.run = {"id": 10, "run_number": 7, "run_attempt": 1,
                    "head_sha": "a" * 40, "head_branch": "develop", "path": load_config()["workflow_path"],
                    "event": "push", "status": "completed", "conclusion": "success"}
        self.jobs = {(10, 1): [dict(name=name, head_sha="a" * 40, run_id=10,
                                   run_attempt=1, status="completed", conclusion="success")
                               for name in ("validate-data", "validate-language")]}

    def test_exact_commit_success(self):
        self.assertTrue(checked_commit("a" * 40, [self.run], self.jobs)[0])

    def test_reject_wrong_sha_branch_workflow_or_event(self):
        for field, value in [("head_sha", "b" * 40), ("head_branch", "main"),
                             ("path", ".github/workflows/other.yml"), ("event", "pull_request")]:
            with self.subTest(field=field):
                changed = dict(self.run, **{field: value})
                self.assertFalse(checked_commit("a" * 40, [changed], self.jobs)[0])

    def test_missing_and_non_success_jobs(self):
        for conclusion in (None, "skipped", "cancelled", "failure", "neutral", "timed_out"):
            with self.subTest(conclusion=conclusion):
                jobs = copy.deepcopy(self.jobs)
                jobs[(10, 1)][1]["conclusion"] = conclusion
                self.assertFalse(checked_commit("a" * 40, [self.run], jobs)[0])
        self.assertFalse(checked_commit("a" * 40, [self.run], {})[0])

    def test_job_must_match_commit_run_and_attempt(self):
        for field, value in [("head_sha", "b" * 40), ("run_id", 11), ("run_attempt", 2)]:
            with self.subTest(field=field):
                jobs = copy.deepcopy(self.jobs)
                jobs[(10, 1)][0][field] = value
                self.assertFalse(checked_commit("a" * 40, [self.run], jobs)[0])

    def test_pending_rerun_does_not_reuse_previous_success(self):
        pending = dict(self.run, run_attempt=2, status="in_progress", conclusion=None)
        self.assertFalse(checked_commit("a" * 40, [self.run, pending], self.jobs)[0])

    def test_newer_failed_run_does_not_reuse_previous_success(self):
        failed = dict(self.run, id=11, run_number=8, conclusion="failure")
        self.assertFalse(checked_commit("a" * 40, [failed, self.run], self.jobs)[0])

    def test_ancestor_fallback_is_one_sha_and_not_an_unrelated_success(self):
        head, parent = "b" * 40, "a" * 40
        self.assertEqual(nearest_checked_ancestor(head, {head: parent}, [self.run], self.jobs), parent)
        self.assertIsNone(nearest_checked_ancestor(head, {}, [self.run], self.jobs))

    def test_no_success_and_cycle_stop_without_state(self):
        self.assertIsNone(nearest_checked_ancestor("a", {"a": "b", "b": "a"}, [], {}))


if __name__ == "__main__":
    unittest.main()
