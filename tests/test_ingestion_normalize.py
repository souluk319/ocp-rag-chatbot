from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.normalize import extract_document_ast, extract_sections

class NormalizeTests(unittest.TestCase):
    def test_extract_sections_populates_operational_metadata(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>머신 구성</h1>
                <h2 id="recover">장애 복구</h2>
                <p>Machine Config Operator 가 NotReady Pod 와 ImagePullBackOff 증상을 진단합니다.</p>
                <p>검증: oc get pods -n openshift-machine-config-operator</p>
                <pre><code>oc get pods -n openshift-machine-config-operator</code></pre>
                <p>Deployment 와 MachineConfigPool 상태를 점검합니다.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="machine_configuration",
            title="머신 구성",
            source_url="https://example.com/machine_configuration",
            viewer_path="/docs/machine_configuration/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        section = sections[0]
        self.assertEqual(
            ("oc get pods -n openshift-machine-config-operator",),
            section.cli_commands,
        )
        self.assertEqual(("NotReady", "ImagePullBackOff"), section.error_strings)
        self.assertEqual(
            ("Pod", "Deployment", "MachineConfigPool"),
            section.k8s_objects,
        )
        self.assertEqual(("Machine Config Operator",), section.operator_names)
        self.assertEqual(
            (
                "검증: oc get pods -n openshift-machine-config-operator",
                "oc get pods -n openshift-machine-config-operator",
            ),
            section.verification_hints,
        )

    def test_extract_sections_skips_noise_headings(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>테스트 문서</h1>
                <h2 id="intro">소개</h2>
                <p>한국어 설명입니다.</p>
                <h2 id="legal">Legal Notice</h2>
                <p>Copyright 2026 Red Hat</p>
                <h3 id="fallback">이 콘텐츠는 선택한 언어로 제공되지 않습니다.</h3>
                <p>OpenShift Container Platform 4.20</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="test_book",
            title="테스트 문서",
            source_url="https://example.com/test",
            viewer_path="/docs/test/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        self.assertEqual("소개", sections[0].heading)
        self.assertIn("한국어 설명", sections[0].text)

    def test_extract_sections_trims_legal_notice_prefix_from_section_text(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>테스트 문서</h1>
                <h2 id="intro">소개</h2>
                <p>Red Hat OpenShift Documentation Team 법적 공지 초록</p>
                <p>이 문서는 OpenShift의 기본 개념을 설명합니다.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="test_book",
            title="테스트 문서",
            source_url="https://example.com/test",
            viewer_path="/docs/test/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        self.assertNotIn("법적 공지 초록", sections[0].text)
        self.assertIn("기본 개념을 설명", sections[0].text)

    def test_extract_sections_preserves_code_blocks_and_inline_literals(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>노드 문서</h1>
                <h2 id="drain">노드 비우기</h2>
                <p>상태가 <code>Ready,SchedulingDisabled</code> 인지 확인합니다.</p>
                <pre><code><span>$</span> <span>oc adm cordon </span><span>&lt;</span>node<span>1</span><span>&gt;</span></code></pre>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="nodes",
            title="노드 문서",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        self.assertIn("상태가 `Ready,SchedulingDisabled` 인지 확인합니다.", sections[0].text)
        self.assertIn("[CODE]\n$ oc adm cordon <node1>\n[/CODE]", sections[0].text)
        self.assertEqual("nodes:drain", sections[0].section_id)
        self.assertIn("code", sections[0].block_kinds)

    def test_extract_sections_extracts_operational_metadata(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Ingress troubleshooting</h1>
                <h2 id="router-check">Router check</h2>
                <p>확인: Route 상태를 점검합니다.</p>
                <p>ImagePullBackOff 가 발생하면 Deployment 상태도 함께 확인합니다.</p>
                <p>Machine Config Operator 와 Ingress Operator 로그를 검토합니다.</p>
                <pre><code>$ oc get pods -n openshift-ingress
kubectl describe deployment router-default -n openshift-ingress</code></pre>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="ingress",
            title="Ingress troubleshooting",
            source_url="https://example.com/ingress",
            viewer_path="/docs/ingress/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        self.assertEqual(
            ("oc get pods -n openshift-ingress", "kubectl describe deployment router-default -n openshift-ingress"),
            sections[0].cli_commands,
        )
        self.assertIn("ImagePullBackOff", sections[0].error_strings)
        self.assertIn("Route", sections[0].k8s_objects)
        self.assertIn("Deployment", sections[0].k8s_objects)
        self.assertIn("Machine Config Operator", sections[0].operator_names)
        self.assertIn("확인: Route 상태를 점검합니다.", sections[0].verification_hints)
        self.assertIn("oc get pods -n openshift-ingress", sections[0].verification_hints)

    def test_extract_document_ast_builds_typed_blocks(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>클러스터 리소스</h1>
                <h2 id="interact">리소스와 상호 작용</h2>
                <p>사전 요구 사항: cluster-admin 권한 - oc CLI 설치</p>
                <p>1. 리소스 목록을 확인합니다.</p>
                <pre><code>$ oc api-resources</code></pre>
                <p>주의: 운영 클러스터에서는 변경 전에 영향을 확인합니다.</p>
                <table>
                  <tr><th>이름</th><th>역할</th></tr>
                  <tr><td>master-0</td><td>control-plane</td></tr>
                </table>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="resources",
            title="클러스터 리소스",
            source_url="https://example.com/resources",
            viewer_path="/docs/resources/index.html",
            content_status="approved_ko",
            source_fingerprint="fp-1",
        )

        document = extract_document_ast(html, entry)

        self.assertEqual("resources", document.book_slug)
        self.assertEqual("approved_ko", document.translation_status)
        self.assertEqual("approved_ko", document.provenance.translation_stage)
        self.assertEqual("ko", document.provenance.translation_source_language)
        self.assertEqual(1, len(document.sections))
        self.assertEqual(
            ("prerequisite", "procedure", "code", "note", "table"),
            document.sections[0].block_kinds,
        )
        self.assertEqual("procedure", document.sections[0].semantic_role)

    def test_extract_document_ast_preserves_rh_code_block_metadata(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>클러스터 리소스</h1>
                <h2 id="interact">리소스와 상호 작용</h2>
                <rh-code-block actions="copy wrap" full-height="true" language="yaml">
                  <pre><code>kind: Pod
metadata:
  name: example</code></pre>
                </rh-code-block>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="resources",
            title="클러스터 리소스",
            source_url="https://example.com/resources",
            viewer_path="/docs/resources/index.html",
            content_status="approved_ko",
            source_fingerprint="fp-2",
        )

        document = extract_document_ast(html, entry)

        code_block = document.sections[0].blocks[0]
        self.assertEqual("code", code_block.kind)
        self.assertEqual("yaml", code_block.language)
        self.assertTrue(code_block.wrap_hint)
        self.assertEqual("toggle", code_block.overflow_hint)
        self.assertEqual("kind: Pod\nmetadata:\n  name: example", code_block.copy_text)

    def test_extract_document_ast_preserves_indentation_and_drops_callout_badges(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>노드 문서</h1>
                <h2 id="example">Pod 구성의 예</h2>
                <p>Red Hat OpenShift Documentation Team 법적 공지 초록</p>
                <rh-code-block actions="copy wrap" full-height="true" language="yaml">
                  <pre><code>spec:
  restartPolicy: Always</code></pre>
                  <rh-badge id="CO1-1" state="info">1</rh-badge>
                  <pre><code>  securityContext:
    runAsNonRoot: true</code></pre>
                </rh-code-block>
                <p>설명 단락입니다.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="nodes",
            title="노드 문서",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes/index.html",
            content_status="approved_ko",
            source_fingerprint="fp-4",
        )

        document = extract_document_ast(html, entry)

        self.assertEqual("code", document.sections[0].blocks[0].kind)
        self.assertEqual(
            "spec:\n  restartPolicy: Always\n  securityContext:\n    runAsNonRoot: true",
            document.sections[0].blocks[0].code,
        )
        self.assertFalse(
            any(
                getattr(block, "text", "").strip() == "Red Hat OpenShift Documentation Team 법적 공지 초록"
                for block in document.sections[0].blocks
            )
        )

    def test_extract_document_ast_promotes_code_caption_and_merges_numeric_callouts(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>노드 문서</h1>
                <h2 id="example">Pod 구성의 예</h2>
                <p>Pod 오브젝트 정의(YAML)</p>
                <rh-code-block actions="copy wrap" full-height="true" language="yaml">
                  <pre><code>kind: Pod
spec:
  restartPolicy: Always</code></pre>
                  <rh-badge id="CO1-1" state="info">1</rh-badge>
                  <pre><code>  securityContext:
    runAsNonRoot: true</code></pre>
                </rh-code-block>
                <p>1</p>
                <p>Pod는 단일 작업에서 선택할 수 있는 라벨을 사용합니다.</p>
                <p>2</p>
                <p>spec는 보안 컨텍스트 같은 실행 구성을 포함합니다.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="nodes",
            title="노드 문서",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes/index.html",
            content_status="approved_ko",
            source_fingerprint="fp-5",
        )

        document = extract_document_ast(html, entry)

        self.assertEqual("code", document.sections[0].blocks[0].kind)
        self.assertEqual("Pod 오브젝트 정의(YAML)", document.sections[0].blocks[0].caption)
        self.assertEqual("paragraph", document.sections[0].blocks[1].kind)
        self.assertEqual(
            "1. Pod는 단일 작업에서 선택할 수 있는 라벨을 사용합니다.",
            document.sections[0].blocks[1].text,
        )
        self.assertEqual(
            "2. spec는 보안 컨텍스트 같은 실행 구성을 포함합니다.",
            document.sections[0].blocks[2].text,
        )

    def test_extract_document_ast_deduplicates_duplicate_anchors(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>클러스터 리소스</h1>
                <h2 id="dup">개요</h2>
                <p>첫 번째 설명</p>
                <h2 id="dup">개요</h2>
                <p>두 번째 설명</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="resources",
            title="클러스터 리소스",
            source_url="https://example.com/resources",
            viewer_path="/docs/resources/index.html",
            content_status="approved_ko",
            source_fingerprint="fp-3",
        )

        document = extract_document_ast(html, entry)

        self.assertEqual(["dup", "dup-2"], [section.anchor for section in document.sections])
        self.assertEqual(
            ["resources:dup", "resources:dup-2"],
            [section.section_id for section in document.sections],
        )

    def test_extract_document_ast_translates_draft_entries_when_settings_present(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Machine configuration</h1>
                <h2 id="overview">Overview</h2>
                <p>The Machine Config Operator manages node configuration.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="machine_configuration",
            title="Machine configuration",
            source_url="https://example.com/machine_configuration",
            viewer_path="/docs/machine_configuration/index.html",
            content_status="translated_ko_draft",
            resolved_language="en",
            source_fingerprint="fp-draft",
        )
        settings = object()

        def fake_translate(document, provided_settings):
            self.assertIs(provided_settings, settings)
            return replace(
                document,
                title="머신 구성",
                display_language="ko",
                translation_status="translated_ko_draft",
            )

        with patch(
            "play_book_studio.ingestion.normalize.translate_document_ast",
            side_effect=fake_translate,
        ) as translate_mock:
            document = extract_document_ast(html, entry, settings=settings)

        translate_mock.assert_called_once()
        self.assertEqual("머신 구성", document.title)
        self.assertEqual("translated_ko_draft", document.translation_status)
        self.assertEqual("ko", document.display_language)

    def test_extract_document_ast_filters_noise_sections_from_translated_draft_document(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Monitoring</h1>
                <h2 id="fallback">This content is not available in selected language.</h2>
                <p>OpenShift Container Platform 4.20</p>
                <h2 id="about">About monitoring</h2>
                <p>Monitor the cluster.</p>
                <h2 id="legal">Legal Notice</h2>
                <p>Copyright 2026 Red Hat</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="monitoring",
            title="Monitoring",
            source_url="https://example.com/monitoring",
            viewer_path="/docs/monitoring/index.html",
            content_status="translated_ko_draft",
            resolved_language="en",
            source_fingerprint="fp-monitoring",
        )
        settings = object()

        def fake_translate(document, provided_settings):
            self.assertIs(provided_settings, settings)
            translated_sections = []
            for section in document.sections:
                heading = section.heading
                if heading == "This content is not available in selected language.":
                    heading = "이 콘텐츠는 선택한 언어로 제공되지 않습니다."
                elif heading == "About monitoring":
                    heading = "모니터링 소개"
                elif heading == "Legal Notice":
                    heading = "법적 고지"
                translated_sections.append(replace(section, heading=heading))
            return replace(
                document,
                title="모니터링",
                display_language="ko",
                translation_status="translated_ko_draft",
                sections=tuple(translated_sections),
            )

        with patch(
            "play_book_studio.ingestion.normalize.translate_document_ast",
            side_effect=fake_translate,
        ):
            document = extract_document_ast(html, entry, settings=settings)

        self.assertEqual(["모니터링 소개"], [section.heading for section in document.sections])

    def test_extract_document_ast_infers_semantic_role_from_english_headings_before_translation(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Monitoring</h1>
                <h2 id="configuring">Configuring and using the monitoring stack</h2>
                <p>Monitor the cluster.</p>
                <h2 id="about">About monitoring</h2>
                <p>Understand monitoring concepts.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="monitoring",
            title="Monitoring",
            source_url="https://example.com/monitoring",
            viewer_path="/docs/monitoring/index.html",
            content_status="translated_ko_draft",
            resolved_language="en",
            source_fingerprint="fp-monitoring",
        )
        settings = object()

        def fake_translate(document, provided_settings):
            self.assertIs(provided_settings, settings)
            return replace(
                document,
                title="모니터링",
                display_language="ko",
                translation_status="translated_ko_draft",
            )

        with patch(
            "play_book_studio.ingestion.normalize.translate_document_ast",
            side_effect=fake_translate,
        ):
            document = extract_document_ast(html, entry, settings=settings)

        roles = {section.anchor: section.semantic_role for section in document.sections}
        self.assertEqual("procedure", roles["configuring"])
        self.assertEqual("overview", roles["about"])

    def test_extract_document_ast_marks_overview_book_sections_as_concepts_when_no_other_signal(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Observability overview</h1>
                <h2 id="chapter">Observability information</h2>
                <p>Understand observability capabilities.</p>
                <h3 id="monitoring">Monitoring</h3>
                <p>Monitor the cluster.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="observability_overview",
            title="Observability overview",
            source_url="https://example.com/observability_overview",
            viewer_path="/docs/observability_overview/index.html",
            content_status="translated_ko_draft",
            resolved_language="en",
            source_fingerprint="fp-observability",
        )

        document = extract_document_ast(
            html,
            entry,
            settings=object(),
            translate=False,
        )

        roles = {section.anchor: section.semantic_role for section in document.sections}
        self.assertEqual("concept", roles["chapter"])
        self.assertEqual("concept", roles["monitoring"])

    def test_extract_document_ast_can_skip_translation_for_diagnostics(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>Backup and restore</h1>
                <h2 id="overview">About backup and restore</h2>
                <p>Back up the cluster state before upgrades.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="backup_and_restore",
            title="Backup and restore",
            source_url="https://example.com/backup_and_restore",
            viewer_path="/docs/backup_and_restore/index.html",
            content_status="translated_ko_draft",
            resolved_language="en",
            source_fingerprint="fp-backup",
        )

        with patch(
            "play_book_studio.ingestion.normalize.translate_document_ast",
            side_effect=AssertionError("translation must be skipped"),
        ):
            document = extract_document_ast(
                html,
                entry,
                settings=object(),
                translate=False,
            )

        self.assertEqual("Backup and restore", document.title)
        self.assertEqual("translated_ko_draft", document.translation_status)
        self.assertEqual("ko", document.display_language)
        self.assertEqual("About backup and restore", document.sections[0].heading)

    def test_extract_document_ast_supports_product_hub_pages_without_article(self) -> None:
        html = """
        <html>
          <head>
            <title>Power monitoring for Red Hat OpenShift | 0.5 | Red Hat Documentation</title>
          </head>
          <body>
            <main id="main-content">
              <div class="product-hub-header"><h1>Power monitoring for Red Hat OpenShift 0.5</h1></div>
              <div class="product-main-container">
                <div class="product-main-body">
                  <div class="right-section">
                    <section class="category" id="About">
                      <h2 class="category-title">About</h2>
                      <rh-tile compact>
                        <h3 slot="headline"><a href="/ko/documentation/power_monitoring_for_red_hat_openshift/0.5/html/about_power_monitoring">전원 모니터링 정보</a></h3>
                        <p>Red Hat OpenShift의 전원 모니터링 소개.</p>
                      </rh-tile>
                    </section>
                    <section class="category" id="Installing">
                      <h2 class="category-title">Installing</h2>
                      <rh-tile compact>
                        <h3 slot="headline"><a href="/ko/documentation/power_monitoring_for_red_hat_openshift/0.5/html/installing_power_monitoring">전원 모니터링 설치</a></h3>
                        <p>Power Monitoring Operator 설치 및 PowerMonitor 사용자 정의 리소스 배포.</p>
                      </rh-tile>
                    </section>
                  </div>
                </div>
              </div>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="power_monitoring",
            title="전원 모니터링",
            source_url="https://example.com/power_monitoring",
            viewer_path="/docs/power_monitoring/index.html",
            content_status="approved_ko",
            resolved_language="ko",
            source_fingerprint="fp-power-monitoring",
        )

        document = extract_document_ast(
            html,
            entry,
            settings=object(),
            translate=False,
        )

        roles = {section.anchor: section.semantic_role for section in document.sections}
        self.assertEqual("전원 모니터링", document.title)
        self.assertGreaterEqual(len(document.sections), 2)
        self.assertEqual("overview", roles["전원-모니터링-정보"])
        self.assertEqual("procedure", roles["전원-모니터링-설치"])

    def test_extract_document_ast_rescues_handoff_sections_into_known_roles(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>OpenShift 샌드박스 컨테이너</h1>
                <h2 id="guide">OpenShift 샌드박스 컨테이너 가이드</h2>
                <p>OpenShift Container Platform의 OpenShift 샌드박스형 컨테이너 지원은 추가 옵션 런타임으로 Kata Containers를 실행하는 데 대한 기본 지원을 제공합니다.</p>
                <h2 id="handoff">1장. OpenShift 샌드박스 컨테이너 정보</h2>
                <p>참고</p>
                <p>OpenShift 샌드박스 컨테이너는 OpenShift Container Platform과 다른 주기로 릴리스되므로 이제 Red Hat OpenShift 샌드박스 컨테이너에 설정된 별도의 문서로 문서를 사용할 수 있습니다.</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="openshift_sandboxed_containers",
            title="OpenShift 샌드박스 컨테이너",
            source_url="https://example.com/openshift_sandboxed_containers",
            viewer_path="/docs/openshift_sandboxed_containers/index.html",
            content_status="approved_ko",
            resolved_language="ko",
            source_fingerprint="fp-osc",
        )

        document = extract_document_ast(
            html,
            entry,
            settings=object(),
            translate=False,
        )

        roles = {section.anchor: section.semantic_role for section in document.sections}
        self.assertEqual("overview", roles["guide"])
        self.assertEqual("procedure", roles["handoff"])


if __name__ == "__main__":
    unittest.main()
