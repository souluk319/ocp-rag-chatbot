# derived_corpus_materialization_recovery_20260417

- kickoff: confirmed current `chunks.jsonl`, `normalized_docs.jsonl`, `playbook_documents.jsonl` all cover only `29` unique books
- finding: `topic_playbooks.py` can already generate `145` derived playbooks from the current `29` approved sources, but runtime catalog materialization never projects those into normalized/chunk rows
- decision: keep the current approved source scope and materialize derived playbooks into retrieval corpus so coverage expands without changing raw truth scope
