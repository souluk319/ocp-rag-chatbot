# Stage 7 Runtime-Corpus Integrity Report

## Goal

Confirm that the live runtime at `localhost:8000` is serving the same corpus/profile that the project currently declares as active.

This stage verifies serving integrity only.
It does not claim retrieval quality improvement.

## Summary

- checked_at: `2026-04-01T03:21:08.958268+00:00`
- base_url: `http://127.0.0.1:8000`
- health_status: `200`
- active_profile_id: `ocp-validation-main-core`
- active_index_id: `s15c-core`
- active_manifest_path: `C:\Users\soulu\cywell\ocp-rag-chatbot\data\staging\s15c\manifests\staged-manifest.json`
- active_document_count: `1201`
- overall_pass: `True`

## Integrity checks

- current.txt matches health active_index_id: `True`
- active profile matches staged manifest source_profile: `True`
- manifest document_count matches health active_document_count: `True`
- source lineage declared/detected ref aligned: `True`
- core validation source id aligned: `True`

## User-visible checkpoint

- Open `http://127.0.0.1:8000/health`
- Confirm `active_index_id` is `s15c-core`
- Confirm `active_document_count` is `1201`
- Confirm `active_manifest_path` points to `data/staging/s15c/manifests/staged-manifest.json`

Companion direct runtime proof remains:

- [Stage 6 direct runtime report](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-direct-runtime-report.md)

## Output

- JSON: `C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-07-report.json`
