# Java learning

## Start each chat

Use this repository for approved learner facts. Teach in Polish. Write repository prose in English.
Read [configuration](.agents/config.json) for the repository, branch, entry file, workflow, and required job names.
Use the configured branch. Do not create pull requests.

1. Resolve the branch to a commit SHA. Read this file and the configuration at that SHA.
2. Inspect the latest matching workflow run and its latest attempt for that exact SHA and branch.
3. Require completed success from the workflow and every configured job. Each job must match the SHA, run, and attempt.
4. Read [profile](profile.json), [teaching rules](.agents/teaching.md), and [current state](state/current.json) at the verified SHA.
5. Read the last lesson when `last_lesson_id` is not null. Use the lesson index below.
6. Load the needed topic and exercise records. Read [the topic map](curriculum.json) during assessment or a change of direction.

Missing, pending, skipped, cancelled, and failed checks are not success.
Do not mix files from different commits. Do not use fictional examples as learner evidence.
The [check selector](.agents/scripts/checked_commit.py) evaluates supplied run snapshots. It does not fetch GitHub results or prove learner approval.

## Recovery

If the newest state has no verified checks, report this and inspect its nearest earlier ancestors.
Use the nearest ancestor with approved learner records and successful required checks. Read its configuration, instructions, and data together.
If none exists, pause lesson state changes and explain the setup problem.
If the plugin cannot read exact commits, inspect jobs, or write files, report the missing capability.
Never claim that an unavailable read or save succeeded. Do not substitute chat memory for verified state.

## Save protocol

Follow [teaching rules](.agents/teaching.md) for lesson planning, evidence, closure, and approval.

1. Read [language rules](.agents/language.md), [coverage](language/policy.json), and [technical terms](language/technical-terms.json).
2. Read the schemas for changed records and [common fields](.agents/schemas/common.schema.json). Use the matching fictional examples only as format guides.
3. Prepare one lesson file, its index link, and the related state, topic, curriculum, and exercise changes.
4. Review technical accuracy, evidence, and language. Show the complete proposed meaning in Polish and obtain approval.
5. Validate locally when execution tools are available. Do not change a schema to bypass an error.
6. Read the branch again. Preserve concurrent changes. Obtain new approval if resolving them changes the proposed meaning.
7. Save all approved changes in one commit. Never force the branch update.
8. Check every required job for the new SHA. Report the result and return the commit and lesson links.

A topic choice does not approve a lesson record. An interrupted chat resumes from the last approved and verified state.
If checks fail, report the failure and prepare a correction. A change of meaning requires new approval.
If checks remain pending or unavailable, report that validation is incomplete.

## File contracts

Instructions use Markdown. Structured data use JSON with the schema version required for that record type.
Use `record_kind: live` for actual records. IDs must match file names and remain stable after title changes.

| Record | Schema |
| --- | --- |
| Configuration | [config](.agents/schemas/config.schema.json) |
| Profile | [profile](.agents/schemas/profile.schema.json) |
| Topic map | [curriculum](.agents/schemas/curriculum.schema.json) |
| Current state | [current-state](.agents/schemas/current-state.schema.json) |
| Topic state | [topic](.agents/schemas/topic.schema.json) |
| Lesson | [lesson](.agents/schemas/lesson.schema.json) |
| Exercise | [exercise](.agents/schemas/exercise.schema.json) |
| Language policy | [language-policy](.agents/schemas/language-policy.schema.json) |
| Technical terms | [technical-terms](.agents/schemas/technical-terms.schema.json) |

## Checks and setup

Install `requirements-validation.txt`, then run:

```sh
python -m unittest discover -s .agents/scripts -p 'test_*.py' -v
python .agents/scripts/validate_records.py
python .agents/scripts/validate_language.py
```

GitHub Actions runs these checks after each push to the configured branch.
Data checks cover record contracts and Markdown links. They cannot establish consent or factual truth.
The language job checks declared project rules. It does not certify full STE compliance. Manual review remains required.
For framework changes, read [the system plan](planning/system-plan.md). Do not load the plan or all lesson files for routine teaching.
During setup, paste the complete [project instructions](.agents/project-instructions.md) into the ChatGPT project instructions field.

## Lesson index

- [lesson-0001](lessons/lesson-0001.json): JVM class initialization diagnostic
