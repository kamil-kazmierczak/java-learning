# Java learning system plan

This document records requirements and design decisions. It is not a lesson input or a claim that all acceptance scenarios passed.
Operational instructions are in [AGENTS.md](../AGENTS.md), [teaching rules](../.agents/teaching.md), and [language rules](../.agents/language.md).
Current machine configuration is in [config](../.agents/config.json). Current learner facts are in [profile](../profile.json).

## Format migration

The learner approved separate formats for instructions and structured data.
Instructions, project setup, language guidance, and this plan use Markdown. Data records and machine configuration retain JSON Schema.
Language policy version `2.0.0` removes editorial instructions. The instructions now reside in the language guide.
Other learner record versions remain unchanged. Existing lessons and evidence require no migration.
Read historical commits with their own schemas and instructions. Do not combine old policy records with the new policy schema.
The plan JSON schema and plan-only validator are retired. Shared strict JSON parsing remains in the data validator.
The following learner settings record the design baseline. Read the profile for current settings.

## Date

2026-09-23

## Repository

- Url: <https://github.com/kamil-kazmierczak/java-learning>
- Branch: develop
- Pull requests: No.

## Learner

- Experience years: 6
- Role: Java Backend Developer
- Experience context: Commercial software development
- IDE: IntelliJ IDEA
- JDK distribution: Eclipse Temurin
- JDK version: 25
- Daily minutes: 30
- Practice within session: Yes.

### Goals

- Understand Java and JVM mechanisms in depth.
- Find and fill gaps in existing knowledge.


## Language

- Repository prose: en
- Lesson chat: pl
- Approval review: pl
- Standard: ASD-STE100
- Standard issue: 9
- Automated full compliance claim: No.
- Checker selection: Partial project checker selected. Full STE validation remains open.

## Progress states

### not_assessed

- Value: not_assessed
- Meaning: There is not enough evidence.

### learning

- Value: learning
- Meaning: The learner needs help or has a known gap.

### applied_independently

- Value: applied_independently
- Meaning: The learner explained the mechanism and solved a new task without LLM hints.

### retained

- Value: retained
- Meaning: The learner repeated this result after a delay.

## Requirements

### LRN-01

- Area: learning
- Basis: user_confirmed
- Text: Use one ChatGPT project for Java. Start each lesson in a new chat.
- Verification: Start a new chat and load the saved state.

### LRN-02

- Area: learning
- Basis: user_confirmed
- Text: Teach Java, the standard library, and the JVM. Use frameworks only when they help explain these subjects.
- Verification: Review the topic map and one lesson.

### LRN-03

- Area: learning
- Basis: user_confirmed
- Text: Use a short initial assessment. Assess each topic again before instruction.
- Verification: Record evidence from both types of assessment.

### LRN-04

- Area: learning
- Basis: user_confirmed
- Text: Propose the next topic and explain why it is useful. Let the learner accept, change, or defer it.
- Verification: Show the topic choice in the lesson record.

### LRN-05

- Area: learning
- Basis: user_confirmed
- Text: Use the session budget in the learner profile. Include instruction, practice, review, and closure. Adjust their duration to the task.
- Verification: Record unfinished work for a later session.

### LRN-06

- Area: learning
- Basis: user_confirmed
- Text: Teach mechanisms that apply across Java versions. State relevant version differences.
- Verification: Record the JDK version when a result depends on it.

### LRN-07

- Area: learning
- Basis: user_confirmed
- Text: Give a guiding question first. Then give a specific hint, a partial example, and a full explanation as needed.
- Verification: Record the help given. Use a new task after a full explanation.

### LRN-08

- Area: learning
- Basis: user_confirmed
- Text: Let the learner request an explanation before all hint steps are complete.
- Verification: Review the learner request and the tutor response.

### LRN-09

- Area: learning
- Basis: user_confirmed
- Text: Assess understanding, use in practice, use in a new task, and recall after a delay.
- Verification: Link each progress change to evidence.

### LRN-10

- Area: learning
- Basis: user_confirmed
- Text: Allow the IDE, tests, and documentation during independent practical tasks. Do not give LLM hints during these tasks.
- Verification: Record the resources and hints used.

### LRN-11

- Area: learning
- Basis: user_confirmed
- Text: Use the agreed progress states. Record a deferred topic separately from its progress state.
- Verification: Check that a deferred topic is not marked as mastered.

### LRN-12

- Area: learning
- Basis: user_confirmed
- Text: Use recall tasks and later review tasks. Put these tasks inside lesson time.
- Verification: Store review results and the next proposed review.

### LRN-13

- Area: learning
- Basis: user_confirmed
- Text: Use chat for short answers and results. Store larger exercises in the repository.
- Verification: Link each larger exercise to its lesson.

### CTX-01

- Area: context
- Basis: user_confirmed
- Text: Use AGENTS.md as the entry file. Include a link to each lesson file.
- Verification: Compare the lesson files with the lesson index.

### CTX-02

- Area: context
- Basis: user_confirmed
- Text: Store each lesson in a separate JSON file. Load only the files needed for the current task.
- Verification: Review the file list used for a lesson.

### CTX-03

- Area: context
- Basis: user_confirmed
- Text: Keep the current state small. Store detailed evidence in topic and lesson files.
- Verification: The next tutor can resume without reading all lessons.

### CTX-04

- Area: context
- Basis: derived_design
- Text: Put an explicit repository read instruction in the ChatGPT project setup.
- Verification: A new chat reads AGENTS.md before it starts instruction.

### CTX-05

- Area: context
- Basis: user_confirmed
- Text: Use repository records for the learner profile, agreed rules, and progress. Use official Java sources for technical facts.
- Verification: Keep source links with technical statements that need verification.

### DATA-01

- Area: data
- Basis: user_confirmed
- Text: Use JSON with a defined JSON Schema for structured data. Use Markdown for descriptive instructions and the system plan.
- Verification: Reject data with missing fields, unknown fields, or incorrect types.

### DATA-02

- Area: data
- Basis: user_confirmed
- Text: Define field meaning, allowed values, IDs, dates, empty values, and schema versions.
- Verification: Provide a schema and a separate valid example for each record type.

### DATA-03

- Area: data
- Basis: user_confirmed
- Text: Keep observations separate from tutor assessments. Record uncertainty when evidence is incomplete.
- Verification: Inspect a record with an uncertain assessment.

### DATA-04

- Area: data
- Basis: user_confirmed
- Text: Record tasks, errors, help, progress evidence, sources, unfinished work, and the next proposed step in each lesson.
- Verification: Validate a complete lesson record.

### DATA-05

- Area: data
- Basis: user_confirmed
- Text: Do not change a schema to make a failed lesson record pass. Request approval for format changes.
- Verification: A format change has an approved plan for old records.

### DATA-06

- Area: data
- Basis: derived_design
- Text: Keep example records separate from real learner records.
- Verification: Example results do not change learner progress.

### LANG-01

- Area: language
- Basis: user_confirmed
- Text: Write repository prose in English. Use ASD-STE100 Issue 9 as the language standard.
- Verification: Review English prose against the standard and the declared rule coverage.

### LANG-02

- Area: language
- Basis: user_confirmed
- Text: Teach in Polish. Present lesson summaries and proposed progress changes in Polish for review.
- Verification: The learner can review meaning without reading JSON.

### LANG-03

- Area: language
- Basis: user_confirmed
- Text: Use a controlled glossary for Java and JVM terms. Keep term meanings consistent.
- Verification: Report unapproved terms and inconsistent names.

### LANG-04

- Area: language
- Basis: user_confirmed
- Text: Use direct instructions and evidence-based reports. Remove generic praise, filler, slogans, and repeated statements.
- Verification: Apply the editorial rules and review meaning.

### LANG-05

- Area: language
- Basis: derived_design
- Text: Do not rewrite code, API names, IDs, or exact source quotations to satisfy prose rules.
- Verification: Keep these fields separate from prose fields.

### LANG-06

- Area: language
- Basis: user_confirmed
- Text: Report which STE rules were checked and which need human review. Do not claim full compliance from a word filter.
- Verification: The report states automated coverage and manual review limits.

### GIT-01

- Area: repository
- Basis: user_confirmed
- Text: Store approved work in kamil-kazmierczak/java-learning on develop. Do not use pull requests.
- Verification: Check the branch and the commit.

### GIT-02

- Area: repository
- Basis: user_confirmed
- Text: Show the lesson summary and all related state changes before saving them. Save only after learner approval.
- Verification: Compare the approved content with the saved content.

### GIT-03

- Area: repository
- Basis: user_confirmed
- Text: Save the lesson, its AGENTS.md link, state changes, and approved exercise changes in one commit.
- Verification: Inspect the commit file list.

### GIT-04

- Area: repository
- Basis: derived_design
- Text: Read the branch before writing. Preserve other changes. Do not force-push.
- Verification: Check the parent commit and update the branch without force.

### GIT-05

- Area: repository
- Basis: user_confirmed
- Text: When the learner says 'kończymy', stop new instruction and prepare the lesson record.
- Verification: Close a lesson with an unfinished exercise.

### GIT-06

- Area: repository
- Basis: user_confirmed
- Text: After an interrupted chat, resume from the last approved saved state and ask for missing context.
- Verification: Start a new chat after an unapproved draft.

### VAL-01

- Area: validation
- Basis: user_confirmed
- Text: Run automatic checks after each push to develop, including file additions and updates.
- Verification: Inspect a workflow run for the saved commit.

### VAL-02

- Area: validation
- Basis: user_confirmed
- Text: Check JSON syntax, duplicate keys, schemas, IDs, references, Markdown links, and the lesson index.
- Verification: Run valid and invalid fixtures.

### VAL-03

- Area: validation
- Basis: user_confirmed
- Text: Run language checks with explicit rule coverage. Keep language results separate from data results.
- Verification: A data check cannot produce a full STE compliance claim.

### VAL-04

- Area: validation
- Basis: user_confirmed
- Text: Read the required check results for the exact saved commit. Missing, skipped, or pending checks are not success.
- Verification: Match each required check to the commit SHA.

### VAL-05

- Area: validation
- Basis: derived_design
- Text: Use one checked commit for all reads in a lesson. Report unchecked changes and use the last approved passing ancestor.
- Verification: Start a lesson after a failed push.

### VAL-06

- Area: validation
- Basis: derived_design
- Text: Report each error with its file, rule ID, and message. Include a JSON pointer or Markdown location when applicable.
- Verification: Inspect a failed validation report.

### VAL-07

- Area: validation
- Basis: user_confirmed
- Text: Do not claim that tests ran without execution evidence. Identify results supplied by the learner.
- Verification: Keep code review and test execution as separate evidence.

### VAL-08

- Area: validation
- Basis: derived_design
- Text: If a correction changes approved meaning or progress, obtain new approval before saving it.
- Verification: Review a correction after a failed check.

### LRN-14

- Area: learning
- Basis: derived_design
- Text: Agree on a short session plan with a clear end point. Announce the final task and start closure after it.
- Verification: The learner knows the remaining stages. The tutor closes without requiring the closure command.

### VAL-09

- Area: validation
- Basis: derived_design
- Text: Check complete runnable tutor examples and each changed variant before use. Identify unverified code and tutor defects explicitly.
- Verification: Compilation and runtime claims have matching execution evidence. Tutor defects do not count as learner gaps.

## File layout

### AGENTS.md

- Path: AGENTS.md
- Schema: None.
- Purpose: Entry instructions and a link to each lesson.
- Load when: At the start of each chat.

### profile.json

- Path: `profile.json`
- Schema: `.agents/schemas/profile.schema.json`
- Purpose: Learner goals, experience, tools, and preferences.
- Load when: At the start of each chat.

### .agents/teaching.md

- Path: `.agents/teaching.md`
- Schema: None.
- Purpose: Teaching, help, assessment, source, and approval rules.
- Load when: At the start of each chat.

### state/current.json

- Path: `state/current.json`
- Schema: `.agents/schemas/current-state.schema.json`
- Purpose: Current work, unfinished tasks, and next proposed topics.
- Load when: At the start of each chat.

### curriculum.json

- Path: `curriculum.json`
- Schema: `.agents/schemas/curriculum.schema.json`
- Purpose: Topic map and prerequisites.
- Load when: During assessment or a change of learning direction.

### topics/<topic-id>.json

- Path: `topics/<topic-id>.json`
- Schema: `.agents/schemas/topic.schema.json`
- Purpose: Topic progress, evidence, gaps, and reviews.
- Load when: When the current lesson needs this topic.

### lessons/<lesson-id>.json

- Path: `lessons/<lesson-id>.json`
- Schema: `.agents/schemas/lesson.schema.json`
- Purpose: One approved lesson record.
- Load when: Read the last lesson. Read older lessons only when needed.

### exercises/<exercise-id>/exercise.json

- Path: `exercises/<exercise-id>/exercise.json`
- Schema: `.agents/schemas/exercise.schema.json`
- Purpose: Task, constraints, expected checks, and code paths.
- Load when: When the learner works on this exercise.

### exercises/<exercise-id>/*.java

- Path: `exercises/<exercise-id>/*.java`
- Schema: None.
- Purpose: Exercise code and tests.
- Load when: When the current task needs the code.

### language/policy.json

- Path: `language/policy.json`
- Schema: `.agents/schemas/language-policy.schema.json`
- Purpose: STE issue, checker configuration, and rule coverage.
- Load when: When the tutor writes or reviews prose.

### language/technical-terms.json

- Path: `language/technical-terms.json`
- Schema: `.agents/schemas/technical-terms.schema.json`
- Purpose: Approved Java and JVM terms with meanings and uses.
- Load when: When the tutor needs a domain term.

### .agents/project-instructions.md

- Path: `.agents/project-instructions.md`
- Schema: None.
- Purpose: Setup text for the ChatGPT project and the start procedure.
- Load when: When the project is configured.

### .agents/examples/<record-type>.json

- Path: `.agents/examples/<record-type>.json`
- Schema: `.agents/schemas/<record-type>.schema.json`
- Purpose: Valid example data, separate from learner evidence.
- Load when: When the tutor creates a record of this type.

### .github/workflows/validate.yml

- Path: `.github/workflows/validate.yml`
- Schema: None.
- Purpose: Checks after each push to develop.
- Load when: GitHub Actions runs this file.

### .agents/config.json

- Path: `.agents/config.json`
- Schema: `.agents/schemas/config.schema.json`
- Purpose: Repository routing and required checks.
- Load when: At session start and during check selection.

### .agents/language.md

- Path: `.agents/language.md`
- Schema: None.
- Purpose: Writing rules and manual review requirements.
- Load when: Before writing repository prose.

### planning/system-plan.md

- Path: `planning/system-plan.md`
- Schema: None.
- Purpose: Requirements, design decisions, and acceptance scenarios.
- Load when: When changing the framework.

## Session flow

### START

- Instruction: Load the checked entry file, profile, teaching rules, current state, and last lesson.

### SELECT

- Instruction: Propose a topic and ask the learner to accept or change it.

### ASSESS

- Instruction: Load the needed topic records. Assess prerequisites and current understanding.

### TEACH

- Instruction: Explain the mechanism and guide practice. Adjust the time used for each task.

### CHECK

- Instruction: Use an independent task and ask the learner to explain the result.

### CLOSE

- Instruction: Prepare the lesson record and state changes. Show their meaning in Polish.

### APPROVE

- Instruction: Apply requested edits and obtain approval for the final content.

### SAVE

- Instruction: Save one commit to develop. Read the automatic check results for that commit.

## Write protocol

- Build all proposed changes from one known branch commit.
- Validate the draft before writing when an execution tool is available.
- Present the complete proposed meaning in Polish and obtain learner approval.
- Read develop again. Resolve concurrent changes without dropping approved or existing data.
- Ask for new approval if the content meaning changed.
- Write one commit without a force update.
- Wait for the required post-push checks for this commit.
- If checks pass, return the commit and lesson links.
- If checks fail, report the errors and prepare a correction.
- If checks remain pending or unavailable, report that validation is incomplete.

## Validation

- Workflow event: push
- Branch: develop
- Exact commit required: Yes.
### Checks

#### DATA

- Scope: JSON syntax, duplicate keys, JSON Schema, and format versions.
- Mode: automatic

#### LINKS

- Scope: Unique IDs, file references, lesson index, and state evidence links.
- Mode: automatic

#### LANGUAGE

- Scope: Declared STE and editorial rules for English prose.
- Mode: automatic_with_manual_review

#### MEANING

- Scope: Technical accuracy and the match between evidence and learner progress.
- Mode: manual_review

### Report fields

- commit_sha
- check_id
- rule_id
- file
- json_pointer
- severity
- message
- coverage

- Bootstrap scope: The initial plan-only validator is retired. Current validation covers structured records, their references, required documents, and Markdown links.
- Failure policy: A failed or unchecked commit is not the accepted state for the next lesson. No automatic history rewrite is allowed.

## Acceptance tests

### AT-01

#### Requirement ids

- CTX-01
- CTX-02
- CTX-03
- CTX-04

- Scenario: Start a new chat after a saved lesson.
- Expected: The tutor loads only the needed files and identifies the unfinished task.

### AT-02

#### Requirement ids

- LRN-03
- LRN-04

- Scenario: Complete the initial assessment.
- Expected: The tutor proposes a topic order and waits for the learner choice.

### AT-03

#### Requirement ids

- LRN-07
- LRN-09
- LRN-10
- LRN-11

- Scenario: Solve a task with two hints, then solve a different task without hints.
- Expected: The record keeps the two results separate and does not mark the topic as retained.

### AT-04

#### Requirement ids

- DATA-01
- DATA-02
- VAL-02

- Scenario: Supply a missing field, an extra field, a duplicate key, and an unknown topic ID.
- Expected: Each invalid record fails with a specific error.

### AT-05

#### Requirement ids

- GIT-02
- GIT-03

- Scenario: Approve a lesson with state and exercise changes.
- Expected: One commit contains the approved files and the lesson index entry.

### AT-06

#### Requirement ids

- VAL-01
- VAL-03
- VAL-04
- VAL-05

- Scenario: Push invalid data to develop in an isolated acceptance fixture.
- Expected: The workflow fails. The next tutor uses the previous passing ancestor and reports the newer failure.

### AT-07

#### Requirement ids

- LANG-01
- LANG-02
- LANG-06

- Scenario: Write and review a lesson record.
- Expected: Repository prose is English. Review is Polish. The report states the limits of automated STE checks.

### AT-08

#### Requirement ids

- GIT-05
- GIT-06

- Scenario: End a lesson with unfinished work, then simulate an interrupted unapproved chat.
- Expected: The next chat uses approved saved evidence and asks for missing context.

### AT-09

#### Requirement ids

- VAL-04
- VAL-07

- Scenario: A workflow is missing, skipped, or still running; code has not been run.
- Expected: The tutor claims neither successful validation nor successful test execution.

### AT-10

#### Requirement ids

- LRN-05
- LRN-14

- Scenario: Start a session with the 30-minute budget, then reach the final planned task without a closure command.
- Expected: The tutor states the plan, announces the last task, and starts review. Extra work remains a proposal.

### AT-11

#### Requirement ids

- VAL-07
- VAL-09

- Scenario: A changed tutor example fails compilation, or no execution tool is available.
- Expected: The tutor corrects and rechecks faulty code or labels it unverified. A prediction is not execution evidence.

## Implementation steps

### BUILD-01

- Text: Create the record schemas, valid examples, and invalid test fixtures.

### BUILD-02

- Text: Create the learner profile, teaching rules, language policy, and project setup instructions.

### BUILD-03

- Text: Create an empty learning state. Do not invent assessment results or lesson history.

### BUILD-04

- Text: Build data, reference, and language checks. Test the exact commit read procedure.

### BUILD-05

- Text: Run the acceptance tests with isolated fixtures.

### BUILD-06

- Text: Run the first diagnostic lesson and test continuation in a new chat.

## Open decisions

### OPEN-01

- Question: Which STE checking tool and rule set will be used?
- Resolution: Compare tool coverage, official reference access, CI use, and any cost. Ask before a paid service is used.
- Blocks: A claim of complete automated STE validation.

### OPEN-02

- Question: What is the review interval for each topic?
- Resolution: Propose dates from assessment evidence and the learner session pattern. Do not assume one fixed schedule.
- Blocks: A fixed spaced-review schedule.

### OPEN-03

- Question: How does the tutor track the remaining session time?
- Resolution: Use the profile budget and an explicit session plan. Ask about remaining time when no reliable clock is available. Keep exact timing open.
- Blocks: A claim that the tutor enforces an exact wall-clock limit.

## Sources

### SRC-STE

- Url: <https://www.asd-ste100.org/STE_faq.html>
- Use: STE rules, dictionary scope, and domain terms.

### SRC-STE-AI

- Url: <https://www.asd-ste100.org/STE_downloads.html>
- Use: Limits of AI claims about STE compliance.

### SRC-SCHEMA

- Url: <https://json-schema.org/understanding-json-schema/reference/object>
- Use: Required fields and closed objects.

### SRC-ACTIONS

- Url: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>
- Use: Automatic checks after a push.

### SRC-RECALL

- Url: <https://link.springer.com/article/10.1186/s41235-024-00598-y>
- Use: Evidence for recall and transfer. This study is not specific to Java developers.

### SRC-SPACING

- Url: <https://www.mdpi.com/2076-328X/15/6/771>
- Use: Evidence for spaced practice. Apply it as a design hypothesis for this learner.

### SRC-TUTOR

- Url: <https://doi.org/10.1073/pnas.2422633122>
- Use: Separate supported practice from independent skill assessment.
