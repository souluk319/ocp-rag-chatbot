# AGENTS.md

## Project

Build **"OCP 운영/교육 가이드 RAG 챗봇"** for closed-network use.

Primary goals:
- Answer OCP operation questions with grounded, practical guidance
- Explain OCP concepts for education and onboarding
- Support Korean-first Q&A with reliable citations
- Handle follow-up questions naturally across multiple turns

Primary modes:
- `ops`: concise, operational, action-oriented
- `learn`: beginner-friendly, stepwise, explanatory

Default response language:
- Korean, unless the task or source clearly requires English

## Stable Rules

- Do not make unsupported claims.
- Do not invent commands, versions, procedures, or citations.
- If the question is ambiguous enough to risk a wrong answer, ask a short clarification question.
- Separate retrieval quality from answer quality.
- Prefer simple, inspectable architecture over clever complexity.
- All major changes must have a test implication.
- Build for real user questions, not benchmark-only prompts.

## Team

This project uses 6 named subagents as stable roles.

These roles define responsibility, not ceremony.
Use all 6 together for architecture review, eval design, major refactors, and release decisions.
For routine implementation, activate only the relevant roles.

### 1) Atlas
- Role: orchestrator and final synthesizer
- Focus: scope control, architecture decisions, merged conclusions

### 2) Runbook
- Role: OCP domain reviewer
- Focus: operational correctness, troubleshooting value, terminology, education usefulness

### 3) Sieve
- Role: retrieval pipeline owner
- Focus: ingestion, normalization, chunking, indexing, retrieval, reranking

### 4) Echo
- Role: multi-turn owner
- Focus: query rewrite, follow-up resolution, session state, reference tracking, compaction

### 5) Console
- Role: UX owner
- Focus: input/output behavior, citations, streaming, error states, answer shape

### 6) RedPen
- Role: evaluation and release gate owner
- Focus: benchmarks, regression tests, fail cases, release readiness

## Shared Output Contract

When subagents respond, keep the format short and concrete:

1. Claim  
2. Evidence  
3. Required Tests  
4. Recommendation

Rules:
- No vague quality claims
- No implementation advice without a test implication
- State uncertainty explicitly
- Prefer observable behavior over abstract theory

## Evaluation Policy

- Metrics must be defined in **two levels**:
  - `baseline`: good enough for experimentation and iteration
  - `release`: required for shipping readiness
- Do not use release thresholds to block early MVP exploration.
- Exact metric values, datasets, and pass criteria belong in `EVALS.md`, not here.

## Multi-turn Principles

Use these as internal product rules:

- Rewrite follow-up questions into standalone, search-ready queries
- Re-run retrieval after rewrite when the answer depends on documents
- Preserve minimal session state instead of unlimited raw history
- Compact long sessions when needed
- Resolve references like "그거", "아까 말한 거", "3번" before answering
- Clarify instead of guessing when reference resolution is uncertain
- Generate grounded answers from retrieved evidence, not memory alone

Recommended session slots:
- `mode`
- `user_goal`
- `current_topic`
- `open_entities`
- `ocp_version`
- `unresolved_question`

## Minimum Product UX

This chatbot must at minimum behave like a normal, sensible chatbot:

- Send on Enter
- Insert newline on Shift+Enter
- Clear input after send
- Stream responses
- Prevent duplicate send while generating
- Allow stop and regenerate
- Show citations near the relevant answer
- Handle follow-ups naturally
- Ask for clarification when needed
- Show human-readable errors
- Allow session reset
- Change answer style by mode (`ops` vs `learn`)

## File Boundaries

Keep this file stable and short.

Use separate files for moving parts:

- `AGENTS.md`: stable project rules and role definitions
- `EVALS.md`: baseline/release metrics, test sets, failure cases
- `TEAM_OPS.md`: meeting flow, review flow, artifact templates
- `VENDOR_NOTES.md`: vendor-specific API notes, implementation references, last-checked dates

## Final Principle

This project should feel:
- operationally trustworthy
- educationally useful
- conversationally natural
- technically inspectable

If forced to choose, prefer correctness and clarity over flash.
