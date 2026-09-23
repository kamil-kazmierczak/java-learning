"""Evaluate GitHub run snapshots. This module does not fetch GitHub data."""
WORKFLOW = ".github/workflows/validate.yml"
REQUIRED = frozenset({"validate-data", "validate-language"})


def checked_commit(sha, runs, jobs_by_run_attempt):
    """Require the latest run attempt for this commit and workflow.

    Fetch all matching runs and the jobs for the selected attempt before use.
    Keys in jobs_by_run_attempt are (run_id, run_attempt) tuples.
    A successful result proves checks only, not learner approval.
    """
    candidates = [run for run in runs
                  if run.get("head_sha") == sha
                  and run.get("head_branch") == "develop"
                  and run.get("path") == WORKFLOW
                  and run.get("event") in {"push", "workflow_dispatch"}]
    if not candidates:
        return False, "No matching workflow run."
    run = max(candidates, key=lambda r: (r.get("run_number", 0), r.get("run_attempt", 0)))
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return False, "The latest run attempt has not passed."
    run_id, attempt = run.get("id"), run.get("run_attempt")
    jobs = jobs_by_run_attempt.get((run_id, attempt), [])
    for name in REQUIRED:
        matches = [job for job in jobs if job.get("name") == name]
        if len(matches) != 1:
            return False, f"Missing or duplicate required job: {name}"
        job = matches[0]
        if job.get("head_sha") != sha or job.get("run_id") != run_id or job.get("run_attempt") != attempt:
            return False, f"Job belongs to a different commit or run attempt: {name}"
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            return False, f"Required job has not passed: {name}"
    return True, "Both required jobs passed for this commit."


def nearest_checked_ancestor(head, parents, runs, jobs_by_run_attempt):
    """Follow the recorded first-parent chain. Never select an unrelated SHA.

    The caller must separately establish that learner records were approved.
    Missing parent data and cycles stop selection.
    """
    seen = set()
    candidate = head
    while candidate and candidate not in seen:
        seen.add(candidate)
        if checked_commit(candidate, runs, jobs_by_run_attempt)[0]:
            return candidate
        candidate = parents.get(candidate)
    return None
