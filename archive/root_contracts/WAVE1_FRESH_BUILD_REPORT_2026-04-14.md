# Wave 1 Fresh Build Report (2026-04-14)

## 현재 판단

`openshift-docs enterprise-4.20` full mirror 기준으로 Wave 1 refresh build 는 정상적으로 다시 태워졌다.  
다만 `현재 자동 final md`와 `현재 채택 gold candidate md`는 여전히 구분해서 봐야 한다.

## Build Scope

- source mirror:
  - `tmp_source/openshift-docs-enterprise-4.20`
- branch:
  - `enterprise-4.20`
- mirror commit:
  - `37c1c821426c6ca60e701689ce1aef7c86e05574`

## Executed Refresh

### 1. Wave 1 Trial Refresh

실행 결과:

- `backup_and_restore`
- `installing_on_any_platform`
- `machine_configuration`
- `monitoring`

각 slug 에 대해 `01~10` trial 을 다시 생성했다.

기준 위치:

- [backup_and_restore trials](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/backup_and_restore/README.md:1)
- [installing_on_any_platform trials](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/installing_on_any_platform/README.md:1)
- [machine_configuration trials](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/machine_configuration/README.md:1)
- [monitoring trials](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/README.md:1)

### 2. Current Automatic Final MD Refresh

자동 final md 는 현재 지원 slug 기준으로 다시 생성했다.

- [backup_and_restore.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/data/reader_grade_books/backup_and_restore.md:1)
- [installing_on_any_platform.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/data/reader_grade_books/installing_on_any_platform.md:1)

## Current Gold Candidate Baseline

Wave 1에서 지금 채택한 gold candidate 는 아래 기준선을 따른다.

### W1-1 `backup_and_restore`

- [14_asciidoc_plus_12_tone/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/backup_and_restore/14_asciidoc_plus_12_tone/output.md:1)

판단 이유:

- `12`보다 critical restore flag 보존이 좋다
- `--skip-hash-check=true`가 살아 있다
- tone/structure 도 reader-grade 수준을 유지한다

### W1-2 `installing_on_any_platform`

- [14_asciidoc_plus_12_tone/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/installing_on_any_platform/14_asciidoc_plus_12_tone/output.md:1)

판단 이유:

- source-first 입력으로 install path 를 더 안정적으로 보존한다
- `install-config / manifests / ignition / bootstrap / verify` 축을 유지한다

### W1-3 `machine_configuration`

- [14_asciidoc_plus_12_tone/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/machine_configuration/14_asciidoc_plus_12_tone/output.md:1)

판단 이유:

- MCO 역할, pool 규칙, verify/failure 축이 reader-grade 구조로 정리된다

### W1-4 `monitoring`

통문서가 아니라 작업 단위 북 기준으로 본다.

- [14_alerts_admin_book/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/14_alerts_admin_book/output.md:1)
- [15_metrics_admin_book/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/15_metrics_admin_book/output.md:1)
- [16_troubleshooting_book/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/16_troubleshooting_book/output.md:1)

판단 이유:

- 기존 통문서 trial 은 내용이 비거나 대표성이 약했다
- monitoring 은 `alerts / metrics / troubleshooting` 분리가 맞다

## Important Separation

### Current Automatic Final MD

이 결과는 현재 코드 경로가 자동으로 뽑는 final md 다.

- [backup_and_restore.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/data/reader_grade_books/backup_and_restore.md:1)
- [installing_on_any_platform.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/data/reader_grade_books/installing_on_any_platform.md:1)

### Current Gold Candidate MD

이 결과는 지금까지 실험을 통해 더 낫다고 채택한 candidate 다.

- [backup_and_restore 14](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/backup_and_restore/14_asciidoc_plus_12_tone/output.md:1)
- [installing_on_any_platform 14](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/installing_on_any_platform/14_asciidoc_plus_12_tone/output.md:1)
- [machine_configuration 14](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/machine_configuration/14_asciidoc_plus_12_tone/output.md:1)
- [monitoring alerts 14](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/14_alerts_admin_book/output.md:1)
- [monitoring metrics 15](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/15_metrics_admin_book/output.md:1)
- [monitoring troubleshooting 16](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/monitoring/16_troubleshooting_book/output.md:1)

## Current Conclusion

Wave 1 refresh 는 성공했다.

하지만 `지금 코드가 자동으로 뽑는 final md`가 곧바로 `gold candidate`는 아니다.

지금 단계의 truth 는 다음과 같다.

- 입력 source 는 `GitHub source-first`로 고정됐다
- trial refresh 는 다시 돌았다
- gold candidate baseline 도 문서별로 다시 확인됐다
- 다음 일은 `gold candidate baseline`을 실제 promotion path 로 바꾸는 것이다
