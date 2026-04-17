# Local Worklog

- task_id: `chat_runtime_grounding_recovery_20260417`
- lane_id: `main`
- role: `main`
- active source manifest confirms `29` approved official books, but runtime corpus still materializes `26657` chunks.
- real chatbot failures were reproduced locally: retrieval and context assembly succeeded, then `grounding_guard` downgraded the answer to `no_answer` because the LLM omitted inline citations.
- fix strategy: keep the strict learn-mode block, but preserve runtime/ops answers when multiple grounded hits already exist by injecting fallback inline citations instead of discarding the answer.
- live smoke queries after the patch returned `rag` with citations for RBAC and project Terminating questions.
