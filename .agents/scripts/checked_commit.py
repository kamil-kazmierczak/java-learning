"""Evaluate GitHub run snapshots. This module does not fetch GitHub data."""
from framework_config import load_config



def checked_commit(sha, runs, jobs_by_run_attempt, *, root=None):
    """Require the latest run attempt for this commit and workflow.

    Fetch all matching runs and the jobs for the selected attempt before use.
    Keys in jobs_by_run_attempt are (run_id, run_attempt) tuples.
    A successful result proves checks only, not learner approval.
    """
    try:
        config = load_config() if root is None else load_config(root)
    except Exception as error:
        return False, f"Invalid framework configuration: {error}"
    candidates = [run for run in runs
                  if run.get("head_sha") == sha
                  and run.get("head_branch") == config["branch"]
                  and run.get("path") == config["workflow_path"]
                  and run.get("event") in {"push", "workflow_dispatch"}
                  and ("repository" not in run or
                       run["repository"].get("html_url") == config["repository_url"])]
    if not candidates:
        return False, "No matching workflow run."
    run = max(candidates, key=lambda r: (r.get("run_number", 0), r.get("run_attempt", 0)))
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return False, "The latest run attempt has not passed."
    run_id, attempt = run.get("id"), run.get("run_attempt")
    jobs = jobs_by_run_attempt.get((run_id, attempt), [])
    for name in config["required_checks"]:
        matches = [job for job in jobs if job.get("name") == name]
        if len(matches) != 1:
            return False, f"Missing or duplicate required job: {name}"
        job = matches[0]
        if job.get("head_sha") != sha or job.get("run_id") != run_id or job.get("run_attempt") != attempt:
            return False, f"Job belongs to a different commit or run attempt: {name}"
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            return False, f"Required job has not passed: {name}"
    return True, "All required jobs passed for this commit."


def nearest_checked_ancestor(head, parents, runs, jobs_by_run_attempt, *, roots_by_sha=None):
    """Follow the recorded first-parent chain. Never select an unrelated SHA.

    The caller must separately establish that learner records were approved.
    Missing parent data and cycles stop selection. Supply roots_by_sha when
    settings differ across commits. Without it, all candidates use local settings.
    """
    seen = set()
    candidate = head
    while candidate and candidate not in seen:
        seen.add(candidate)
        # Historical configuration must come from that same candidate commit.
        root = None if roots_by_sha is None else roots_by_sha.get(candidate)
        if roots_by_sha is not None and root is None:
            return None
        if checked_commit(candidate, runs, jobs_by_run_attempt, root=root)[0]:
            return candidate
        candidate = parents.get(candidate)
    return None
