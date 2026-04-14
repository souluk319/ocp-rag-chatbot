# OCP 4.20 Source Mirror Catalog

## 목적

이 문서는 Wave 1 Gold Corpus 구축에 사용하는 OpenShift 4.20 공식 source mirror 기준을 고정한다.

핵심 목표는 단순하다.

- 어떤 공식 repo 를 기준 입력으로 쓰는지
- 어떤 branch 와 commit 을 기준으로 보는지
- 어떤 문서 slug 가 어떤 source path 와 연결되는지

를 한 번에 잠그는 것이다.

## 현재 판단

Wave 1의 기준 입력은 `openshift/openshift-docs` 공식 저장소의 `enterprise-4.20` branch 다.

`html-single`는 버리는 게 아니라 fallback 으로 유지한다.

## Source Mirror Baseline

- repo:
  - `https://github.com/openshift/openshift-docs`
- branch:
  - `enterprise-4.20`
- mirrored path:
  - [tmp_source/openshift-docs-enterprise-4.20](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20)
- current local mirror commit:
  - `37c1c821426c6ca60e701689ce1aef7c86e05574`

## Source Authority Rule

- `openshift-docs` AsciiDoc source
  - first-class input
- `docs.redhat.com html-single`
  - fallback / coverage safety net
- community repo / ops repo
  - 보강 자료

즉, Wave 1은 source-first 로 가되, html-single 를 coverage fallback 으로 유지한다.

## Wave 1 Source Mapping

### W1-1. `backup_and_restore`

- source repo path:
  - [backup_and_restore/index.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/backup_and_restore/index.adoc:1)
- key module paths:
  - [backup-etcd.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/backup-etcd.adoc:1)
  - [dr-restoring-cluster-state-about.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/dr-restoring-cluster-state-about.adoc:1)
  - [manually-restoring-cluster-etcd-backup.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/manually-restoring-cluster-etcd-backup.adoc:1)
- html-single fallback:
  - [docs.redhat backup_and_restore](https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/backup_and_restore/index)

### W1-2. `installing_on_any_platform`

- source repo path:
  - [installing/overview/index.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/installing/overview/index.adoc:1)
- expected extraction focus:
  - install overview
  - infrastructure preparation
  - install-config
  - manifests / ignition
  - bootstrap / verify
- html-single fallback:
  - [docs.redhat installing_on_any_platform](https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index)

### W1-3. `machine_configuration`

- source repo path:
  - [machine_configuration/index.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/machine_configuration/index.adoc:1)
- key module paths:
  - [understanding-machine-config-operator.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/understanding-machine-config-operator.adoc:1)
  - [machine-config-overview.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/machine-config-overview.adoc:1)
  - [checking-mco-node-status.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/modules/checking-mco-node-status.adoc:1)
- html-single fallback:
  - [docs.redhat machine_configuration](https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/machine_configuration/index)

### W1-4. `monitoring`

- source repo root:
  - [observability/monitoring](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring)
- representative source paths:
  - [about-ocp-monitoring.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/about-ocp-monitoring.adoc:1)
  - [configuring-alerts-and-notifications.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/configuring-core-platform-monitoring/configuring-alerts-and-notifications.adoc:1)
  - [configuring-metrics.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/configuring-core-platform-monitoring/configuring-metrics.adoc:1)
  - [managing-alerts-as-an-administrator.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/managing-alerts/managing-alerts-as-an-administrator.adoc:1)
  - [troubleshooting-monitoring-issues.adoc](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/troubleshooting-monitoring-issues.adoc:1)
- html-single fallback:
  - [docs.redhat monitoring](https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/monitoring/index)

## Catalog Rule

Wave 1 문서를 새로 승격할 때는 아래 4개를 함께 남긴다.

1. repo
2. branch or commit
3. relative source path
4. html-single fallback URL

이 4개가 없으면 source provenance 가 닫히지 않은 것으로 본다.

## Current Conclusion

Wave 1은 이제 막연한 `공식 문서 수집`이 아니다.

지금부터는 이 catalog 기준으로

- source-first 입력을 읽고
- fallback 을 같이 보존하고
- reader-grade gold book 을 만든다.
