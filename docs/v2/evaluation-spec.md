# v2 Evaluation Specification

## Purpose

This document defines how we will decide whether the v2 assistant is good enough to move beyond the initial slice.

The evaluation model is built for an OCP operations assistant that:

- uses official OCP documents as the main source of truth
- answers in Korean
- cites its evidence
- opens the cited document when a source is clicked
- runs in a closed-network operating model

## Evaluation principles

1. A fluent answer without evidence does not pass.
2. A cited answer that points to the wrong document does not pass.
3. A correct answer from the wrong product family does not pass.
4. A Korean answer that mistranslates critical technical terms does not pass.
5. A correct-looking answer that mixes incompatible OCP versions must be treated as unsafe.

## Evaluation tracks

### Track A. Grounding and retrieval

Checks:

- the retrieved documents belong to the intended OCP product line
- the answer is supported by the top retrieved material
- the retrieved chunk set contains the evidence needed to answer

Pass expectation for the first working slice:

- the correct source family appears in the retrieved set for the baseline questions
- the answer does not rely on unsupported claims

### Track A1. Retrieval benchmark

This track exists specifically to answer the "vector search quality is unproven" feedback.

Required query classes:

- install and prerequisites
- upgrade and update
- disconnected environment
- troubleshooting and recovery
- networking and node health
- version-sensitive questions
- follow-up questions rewritten from prior turns

Required metrics:

- `source_dir_hit@3`
- `source_dir_hit@5`
- `supporting_doc_hit@5`
- `supporting_doc_hit@10`
- `citation_correctness`
- `rerank_lift@5`

Required Stage 5 artifacts:

- `docs/v2/retrieval-benchmark-plan.md`
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- `eval/retrieval-benchmark-schema.yaml`
- `eval/retrieval_benchmark_report.py`

Recommended first-slice gates:

- `source_dir_hit@5 >= 0.85`
- `supporting_doc_hit@10 >= 0.75`
- `citation_correctness >= 0.90` on grounded answers
- reranking must improve or at least not regress the ambiguous-query subset

Benchmark reporting should compare:

- dense retrieval only
- retrieval plus rerank
- query class by query class results

### Track A2. Context-retention diagnostics

This track exists to make benchmark failures explainable before we widen scope.

Checks:

- expected support survives from retrieval to rerank to assembled context
- token-budget pressure and truncation are visible
- final citations still point to the grounded context that survived assembly
- follow-up turns preserve the grounded topic through query rewrite

Required diagnostics:

- `retrieval_miss`
- `rerank_loss`
- `assembly_loss`
- `citation_loss`
- `truncation_applied`
- `version_drift`
- `follow_up_rewrite_missing`

Required artifacts:

- `docs/v2/context-retention-harness.md`
- `eval/context-harness-schema.yaml`
- `eval/context_harness_report.py`

Pass expectation for the first working slice:

- benchmark failures can be localized to a pipeline stage
- follow-up trace failures are visible before answer-quality review starts

### Track B. Citation accuracy

Checks:

- every answer includes citations
- cited sources match the actual supporting document
- cited sections are narrow enough to inspect the claim

Pass expectation for the first working slice:

- no missing citations on grounded answers
- no hallucinated citations
- citations point to the same document family used for retrieval

### Track C. Citation click-through

Checks:

- clicking a citation opens a readable document view
- the opened view matches the cited document
- the user can locate the relevant section without manually searching the whole corpus

Pass expectation for the first working slice:

- every cited source opens a real HTML document path
- section-level precision is preferred, document-level precision is the minimum fallback

### Track D. Korean answer quality

Checks:

- the answer is written in Korean
- technical terms remain precise where translation would reduce accuracy
- procedural steps remain understandable to an operator

Pass expectation for the first working slice:

- the answer is clearly readable in Korean
- critical terms such as command names, API resources, and component names are not mistranslated

### Track E. Version safety

Checks:

- the answer prefers the intended OCP version
- incompatible version guidance is not mixed together without warning
- when version confidence is low, the answer says so

Pass expectation for the first working slice:

- no silent version mixing on baseline questions
- uncertain version matches are disclosed

### Track F. Operations usefulness

Checks:

- the answer helps with real operator tasks
- the answer preserves step order when the source is procedural
- the answer surfaces escalation clues when the source is troubleshooting-focused
- the answer includes risk warnings for high-impact changes when the source implies them

Pass expectation for the first working slice:

- install, update, disconnected, and troubleshooting questions receive actionable answers

### Track G. Source priority and policy safety

Checks:

- official OCP documents outrank unrelated or lower-trust content
- approved internal guidance can supplement official guidance without silently replacing it
- when evidence is incomplete, the system stays conservative

Pass expectation for the first working slice:

- no answer is primarily grounded in the wrong product family
- weakly grounded questions do not receive overconfident answers

### Track H. Closed-network update safety

Checks:

- the corpus can be refreshed through a bundle flow
- manifest and checksum outputs are reproducible
- index activation can be rolled forward and back

Pass expectation for the first working slice:

- one approved refresh cycle can be repeated without ambiguous state

### Track I. Multi-turn continuity

This track exists specifically to answer the "multi-turn behavior is weak" feedback.

Checks:

- at least 5 turns remain on the same grounded topic unless the user changes it
- follow-up questions can be rewritten into retrieval-ready standalone questions
- version context remains stable across turns
- citation continuity is preserved across related follow-up turns
- the system admits when prior turns are insufficient to ground the next answer

Pass expectation for the first working slice:

- 5-turn scenarios stay grounded
- version drift does not occur silently
- follow-up turns still produce valid citations

Required Stage 7 artifacts:

- `docs/v2/multiturn-memory-plan.md`
- `app/multiturn_memory.py`
- `eval/benchmarks/p0_multiturn_scenarios.json`
- `eval/multiturn-scenario-schema.yaml`
- `eval/multiturn_rewrite_report.py`

## Baseline scenario groups

The first baseline dataset must include at least these groups:

1. installation and prerequisites
2. post-install configuration
3. disconnected environment procedures
4. updating and upgrade preparation
5. networking, storage, and node health
6. troubleshooting and operator recovery
7. version-sensitive follow-up questions
8. citation click-through checks
9. retrieval benchmark queries by class
10. 5-turn multi-turn scenarios

## Baseline question format

Each evaluation item should record:

- `id`
- `group`
- `question_ko`
- `expected_source_dirs`
- `expected_category`
- `expected_version_behavior`
- `expected_query_class`
- `expected_memory_behavior`
- `must_include_terms`
- `must_not_include_terms`
- `citation_required`
- `click_through_required`
- `turn_index`
- `notes`
- `context_harness_required`
- `expected_document_paths`
- `scenario_id`
- `turn_type`

## Minimum release gate for the first working slice

The first working slice is acceptable only if all of the following are true:

1. the normalized P0 corpus can be regenerated reproducibly
2. the system answers Korean questions using the normalized OCP corpus
3. every grounded answer includes citations
4. every citation opens a real document path
5. the baseline questions do not show obvious OSD, ROSA, or MicroShift contamination
6. the system does not silently mix incompatible OCP version guidance
7. retrieval benchmark meets the first-slice gate
8. 5-turn multi-turn scenarios stay grounded
9. failing benchmark cases can be traced through the context-retention harness

## Red-team checks

The initial red-team set should include:

- vague questions with no clear evidence in the corpus
- mixed-version questions
- questions that tempt the system to use non-OCP product guidance
- questions that ask for unsafe certainty when the source is incomplete
- follow-up questions that rely on previous context
- high-risk change questions that should trigger caution language
- follow-up questions that intentionally try to cause topic drift

## Ownership

- QA / Evaluation / Red Team owns the checklist structure
- OCP Operations SME owns the operational validity of baseline questions
- RAG / Search Engineer owns grounding and ranking diagnostics
- LLM Serving / Backend Engineer owns Korean answer behavior and streaming correctness
