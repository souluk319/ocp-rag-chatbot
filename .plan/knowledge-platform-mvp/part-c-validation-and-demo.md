# Part C. Validation And Demo

## 1. Goal

Prove that the MVP is demo-usable with real OCP-style questions and real current data.

## 2. Chapter C1. Validation Categories

Validate across these categories:

1. chatbot answer quality
2. source tag rendering
3. source panel opening behavior
4. study readability of the source panel
5. grounding realism

## 3. Chapter C2. Required Query Themes

Test at least 5 real examples covering:

- Pod Pending troubleshooting
- CrashLoopBackOff troubleshooting
- `oc login` or CLI usage
- concept question about Pod lifecycle
- procedure question from OCP docs

## 4. Chapter C3. Validation Checklist Per Query

For each query, verify:

1. the chatbot still answers coherently
2. source tags appear under the answer
3. clicking a source tag opens a relevant document/section
4. the source panel is readable enough for study
5. the content is grounded in real existing data, not placeholders

## 5. Chapter C4. Evidence To Capture

Collect:

- query text
- response kind
- source tag count
- opened source title / section
- any readability limitation
- pass/fail note

## 6. Chapter C5. Release Gate For This Slice

This MVP can be called demo-ready only if:

- all 5 validation themes work without product-identity drift
- no raw ugly chunk dump is shown as the main study view unless clearly unavoidable
- the right panel helps study rather than confusing the answer flow

## 7. Part C Output

Produce:

- a compact validation table
- known limitations
- run/test instructions for tomorrow morning demo use
