# Java learning

## Project state

The record schemas and data checks are implemented.
The teaching setup and language checks still need implementation.
No live learner state, lesson, or assessment result exists.
All files in `examples/` are fictional. Do not copy their results into learner state.

## Read order

1. Read [the system plan](planning/system-plan.json) for setup work.
2. Read [the plan schema](schemas/system-plan.schema.json) before you change the plan.
3. For a record change, read only its schema and required definitions from [common fields](schemas/common.schema.json).
4. Read the `validate-data` check for the exact commit you use.
5. Do not treat this data check as a full STE check or as proof that lessons are ready.

Write repository prose in English. Use ASD-STE100 Issue 9.
Teach and review proposed changes with the learner in Polish.
Use `develop`. Do not create pull requests.
Ask the learner to approve lesson records and related state changes before you save them.
Keep observations separate from assessments. Do not invent learner evidence.
Do not change schemas to bypass failed checks.

## Record contracts

| Record | Schema | Fictional example |
| --- | --- | --- |
| Learner profile | [profile](schemas/profile.schema.json) | [profile](examples/profile.json) |
| Tutor rules | [teaching](schemas/teaching.schema.json) | [teaching](examples/teaching.json) |
| Topic map | [curriculum](schemas/curriculum.schema.json) | [curriculum](examples/curriculum.json) |
| Current state | [current-state](schemas/current-state.schema.json) | [current-state](examples/current-state.json) |
| Topic state | [topic](schemas/topic.schema.json) | [topic](examples/topic.json) |
| Lesson | [lesson](schemas/lesson.schema.json) | [lesson](examples/lesson.json) |
| Exercise | [exercise](schemas/exercise.schema.json) | [exercise](examples/exercise.json) |
| Language policy | [language-policy](schemas/language-policy.schema.json) | [language-policy](examples/language-policy.json) |
| Technical terms | [technical-terms](schemas/technical-terms.schema.json) | [technical-terms](examples/technical-terms.json) |
| Project setup | [project-instructions](schemas/project-instructions.schema.json) | [project-instructions](examples/project-instructions.json) |

Use `schema_version: "1.0.0"` for these records.
Use `record_kind: "live"` only for actual learner data.
Use an empty list when no items exist. Use `null` only where the schema permits it.
Do not omit required fields. Do not add fields or infer missing facts.
An ID must match its file name. IDs remain stable after a title change.
Keep topic choice separate from progress. A deferred topic can keep its existing progress.
Use evidence references to link topic state to observations in approved lessons.
Keep observations and tutor assessments separate.

## Data checks

Install `requirements-validation.txt`, then run:

```sh
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/validate_plan.py
python scripts/validate_records.py
```

GitHub Actions runs the same commands after each push to `develop`.
The report states data errors and the limits of these checks.
It cannot prove that a learner gave approval or that an observation is true.
It does not check STE vocabulary or certify language compliance.
Before adding another JSON record type, add its schema, route, example, and tests.

## Lesson index

No lessons have been saved.
Add one relative link for each lesson when the lesson is saved.
Keep summaries in their own JSON files.
