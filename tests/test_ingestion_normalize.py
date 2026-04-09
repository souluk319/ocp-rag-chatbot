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


if __name__ == "__main__":
    unittest.main()
