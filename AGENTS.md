# Java learning

## Start each chat

Use the GitHub repository as the source for approved learner facts.
Teach in Polish. Write repository prose in English.
Use `develop`. Do not create pull requests.

1. Resolve `develop` to a commit SHA.
2. Inspect its latest run attempt from `.github/workflows/validate.yml`.
3. Require completed success from both `validate-data` and `validate-language`.
4. Read this file and every session record at that exact SHA.
5. Read [profile](profile.json), [teaching rules](teaching.json), and [current state](state/current.json).
6. Read the last lesson if `last_lesson_id` is not null.
7. Load topic records and exercises only when the current work needs them.

Missing, pending, skipped, cancelled, and failed checks are not success.
Use [recovery steps](project-instructions.json) when the newest commit has no verified state.
Do not mix files from different commits.
Do not assume the plugin can inspect runs or write files. Check its available tools and report missing access.

## First session and lesson flow

An empty state means that assessment has not started.
Do not infer knowledge or gaps from years of work.
Read [the topic map](curriculum.json) during initial assessment or a change of direction.
Propose a short initial assessment and explain its purpose. Let the learner accept, replace, or defer the proposed topic.
Ask one question at a time. Start with a prediction or explanation, then a small code task.
Wait for the response before you assess it or give another hint.
Use the hint order in the teaching rules. Give a direct explanation when requested.
Follow an explanation with a new independent task.
Include theory and practice in the 60-minute session. Adjust their lengths to the task.
Do not invent elapsed time or assign required work outside the session.
Use the agreed closure command `kończymy`. Ask about remaining time when needed.
Propose later reviews from observed results. Do not assume a fixed review schedule.

## Close and save

1. Stop new instruction when the learner asks to close.
2. Read [language rules](language/policy.json) and [technical terms](language/technical-terms.json).
3. Read only the schemas for changed records and the needed [common fields](schemas/common.schema.json).
4. Prepare the lesson, code, topic map, topic states, current state, and index changes that the session needs.
5. Review technical accuracy, evidence, and language. Report the limits of automatic checks.
6. Show the complete proposed meaning in Polish. Include help, errors, progress, unfinished work, sources, and the next proposed step.
7. Ask for approval of the final content. A topic choice does not approve the lesson record.
8. Validate locally when an execution tool is available.
9. Read `develop` again. Preserve concurrent changes. Obtain new approval if their resolution changes meaning.
10. Save all approved changes in one commit. Never force the branch update.
11. Check both required jobs for the new SHA. Report the result and provide the commit and lesson links.

Use one JSON file per lesson and one index link per lesson.
Treat the next step as a proposal until the learner accepts it.
Keep unknown values as `null` where permitted. Keep empty lists when no items exist.
Do not invent observations, approval, execution results, or assessment dates.
If the chat ends before approval, resume from the last approved and verified state.
When checks fail, prepare a correction and report it. Do not declare the saved state ready for the next lesson.

## Record contracts

Use version `1.0.0` and `record_kind: live` for actual records.
Files in `examples/` are fictional. Never use their results as learner evidence.
An ID must match its file name and remain stable after a title change.
Read the schema before creating or changing a record. Do not change a schema to bypass a failure.

| Record | Schema |
| --- | --- |
| Profile | [profile](schemas/profile.schema.json) |
| Tutor rules | [teaching](schemas/teaching.schema.json) |
| Topic map | [curriculum](schemas/curriculum.schema.json) |
| Current state | [current-state](schemas/current-state.schema.json) |
| Topic state | [topic](schemas/topic.schema.json) |
| Lesson | [lesson](schemas/lesson.schema.json) |
| Exercise | [exercise](schemas/exercise.schema.json) |
| Language policy | [language-policy](schemas/language-policy.schema.json) |
| Technical terms | [technical-terms](schemas/technical-terms.schema.json) |
| Project setup | [project-instructions](schemas/project-instructions.schema.json) |

Keep observations separate from assessments. Record the source and help level for each observation.
Use `applied_independently` only for a new solution and mechanism explanation without LLM hints.
Use `retained` only after an independent check on a later day, with a link to earlier independent evidence.
Keep topic choice separate from progress. A deferred topic keeps its evidence.
Record code review separately from execution. A learner report is not an agent execution result.

## Checks and setup

Install `requirements-validation.txt`, then run these commands:

```sh
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/validate_plan.py
python scripts/validate_records.py
python scripts/validate_language.py
```

GitHub Actions runs the checks after each push to `develop`.
The language job checks declared project rules. It does not verify the complete STE dictionary or certify full STE compliance.
Review the applicable STE rules and meanings before each lesson approval.
Data checks cannot prove consent or the truth of an observation.
For system changes, read [the approved plan](planning/system-plan.json) and [its schema](schemas/system-plan.schema.json).
Do not load the plan, all schemas, or all lesson files for routine teaching.
Copy [project instructions](project-instructions.json) into the ChatGPT project instructions during setup.

## Lesson index

- [lesson-0001](lessons/lesson-0001.json): JVM class initialization diagnostic
