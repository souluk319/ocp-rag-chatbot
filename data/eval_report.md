# OCP RAG Evaluation Report

- Generated at: `2026-03-26T13:53:51.168184+00:00`
- Endpoint: `http://127.0.0.1:8021`
- Transport: `api`
- Fixtures: `8/8` passed
- Pass rate: `100.0%`
- Rewrite pass rate: `100.0%`
- Retrieval pass rate: `100.0%`
- Answer pass rate: `100.0%`
- Total runtime: `211208ms`

## Fixture Results

| ID | Mode | Class | Pass | Time | Top sources |
| --- | --- | --- | --- | --- | --- |
| `overview-ocp-001` | `education` | `overview` | PASS | `13528ms` | ocp-basics.md, ocp-etcd-overview-ko.md, ocp-route-ingress-ko.md |
| `overview-k8s-control-plane-001` | `education` | `overview` | PASS | `16684ms` | ocp-etcd-overview-ko.md, ocp-monitoring-ko.md, ocp_control_plane.md |
| `education-workload-diff-001` | `education` | `education` | PASS | `19150ms` | k8s-workload-types-ko.md, k8s_deployment_detail.md, k8s_statefulset_detail.md |
| `education-configmap-secret-001` | `education` | `education` | PASS | `29521ms` | 변수.pdf, k8s_task_configmap.md, k8s_task_secret.md |
| `operations-resource-limits-001` | `operations` | `operations` | PASS | `29119ms` | ocp-resource-management-ko.md, k8s-resource-limits-ko.md, k8s_task_cpu_resource.md |
| `operations-oc-login-001` | `operations` | `operations` | PASS | `22724ms` | ocp-troubleshooting-advanced-ko.md, ocp-commands.md, ocp-debug-tools-ko.md |
| `troubleshooting-image-pull-001` | `operations` | `troubleshooting` | PASS | `22541ms` | ocp-image-pull-troubleshooting-ko.md, ocp_troubleshooting_os.md, ocp_troubleshooting_pods.md |
| `troubleshooting-pending-followup-001` | `operations` | `troubleshooting` | PASS | `57933ms` | ocp-pending-pod-troubleshooting-ko.md, k8s_task_cpu_resource.md, k8s_task_memory_resource.md |
