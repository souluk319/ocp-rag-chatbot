# PART4_PLAN.md

## Goal

Wrap the retrieval and answer pipeline in a minimum usable chatbot interface and prepare a demo flow.

## Inputs

- retrieval pipeline
- answer pipeline
- citation viewer mapping

## Outputs

- minimum chat UI
- demo question set
- end-to-end runnable flow

## Steps

### Step 1. Build minimum chat interface

- input box
- message list
- send behavior
- loading or streaming state

### Step 2. Add answer rendering

- show Korean answer cleanly
- separate answer body from citation area

### Step 3. Add citation interaction

- make citations visible and clickable
- open internal Korean document view at the right location

### Step 4. Add basic controls

- session reset
- stop generation if supported
- regenerate if supported

### Step 5. Add error handling

- show human-readable errors
- avoid raw stack traces in the user-facing UI

### Step 6. Prepare demo scenarios

- define minimum core questions
- define expected behavior for each
- verify end-to-end flow before presentation

## Exit Criteria

Part 4 is ready when:

- a user can ask a Korean question
- the system returns a Korean answer
- citations are visible
- citation click opens the intended Korean document target

## Notes

- Keep the demo simple.
- A stable minimum flow is better than a wide but fragile UI.
