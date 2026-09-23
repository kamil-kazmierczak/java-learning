# Repository language rules

Teach and review proposed lesson changes in Polish. Write repository prose in English.
Use ASD-STE100 Issue 9 for English repository prose.
The root [README](../README.md) is a Polish guide for the learner. It is outside the English prose check.
See [checker configuration](../language/policy.json) for automatic and manual coverage.
Use the [technical glossary](../language/technical-terms.json) for Java and JVM terms.

## Project rules

### STYLE-01

Use at most 25 words in each prose sentence. This project limit does not replace STE instruction rules.

### STYLE-02

Remove stock phrases and generic praise. The checker detects only its listed phrases.

### STYLE-03

Write full word forms. Do not use contractions.

### STYLE-04

Use the glossary names. The checker reports the listed avoid forms.

### STYLE-05

Give evidence for each progress claim. Remove repetition and unsupported conclusions.

### STYLE-06

Review each new technical term before you add it. State its meaning and source.

## Review limits

Automatic checks cover selected project rules in live JSON prose and repository Markdown, except the root README.
Local links in the README remain subject to document validation.
Schemas and fictional JSON examples are outside the prose check.
A successful job does not establish full STE compliance, technical accuracy, consent, or the truth of an observation.
Review approved words, word classes, meanings, and applicable writing rules against Issue 9.
Do not add ordinary English words to the technical glossary to bypass a finding.
Do not rewrite code, API names, identifiers, URLs, enum values, or exact quotations to satisfy prose rules.
Use code formatting only for exact technical text. Use block quotes only for exact source quotations.
Review these exclusions manually. Do not hide instructional prose inside excluded blocks.
