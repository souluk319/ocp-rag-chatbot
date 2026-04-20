from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - validation helper bootstrap
    raise SystemExit(
        "playwright is required for this smoke. Install it in the active venv with "
        "`python -m pip install playwright`."
    ) from exc


DEFAULT_BROWSER_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEFAULT_APP_BASE = "http://127.0.0.1:5173"
DEFAULT_RUNTIME_BASE = "http://127.0.0.1:8765"
DEFAULT_USER_ID = "kugnus@cywell.co.kr"
DEFAULT_SOURCE_TITLE = "에이전트 기반 설치 관리자를 사용하여 온프레미스 클러스터 설치"


@dataclass(frozen=True)
class SmokeConfig:
    app_base: str
    runtime_base: str
    browser_path: str
    source_title: str
    user_id: str
    keep_overlay: bool
    report_path: str


class WorkspaceCardEditSmoke:
    def __init__(self, config: SmokeConfig):
        self.config = config
        self.note_text = f"[workspace-card-smoke] {int(time.time())}"
        self.result: dict[str, Any] = {
            "app_base": config.app_base,
            "runtime_base": config.runtime_base,
            "source_title": config.source_title,
            "note_text": self.note_text,
            "cleanup_removed": 0,
            "pass": False,
        }

    def run(self) -> dict[str, Any]:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                    executable_path=self.config.browser_path,
                )
                page = browser.new_page(viewport={"width": 1600, "height": 1100})
                try:
                    self._exercise(page)
                finally:
                    browser.close()
            self.result["pass"] = True
            return self.result
        finally:
            if not self.config.keep_overlay:
                self.result["cleanup_removed"] = self._cleanup_saved_overlay()
            self._write_report()

    def _exercise(self, page) -> None:
        page.goto(f"{self.config.app_base}/studio", wait_until="domcontentloaded")
        source_count = self._wait_for_sources(page)
        self.result["source_count"] = source_count

        self._open_source(page)
        page.select_option(".viewer-mode-select", "multi")
        page.wait_for_timeout(2500)

        quick_nav_titles = self._quick_nav_titles(page)
        if len(quick_nav_titles) < 3:
            raise RuntimeError(f"expected at least 3 quick-nav entries, found {len(quick_nav_titles)}")
        self.result["quick_nav_titles"] = quick_nav_titles[:5]

        save_section_title = self._open_quick_nav_item(page, 1)
        compare_section_title = self._open_quick_nav_item(page, 2)
        self.result["save_section_title"] = save_section_title
        self.result["compare_section_title"] = compare_section_title

        self._open_quick_nav_item(page, 1)
        current_target_title = self._save_note(page, self.note_text)
        self.result["saved_target_title"] = current_target_title
        if current_target_title != save_section_title:
            raise RuntimeError(
                f"saved target mismatch: expected {save_section_title!r}, got {current_target_title!r}"
            )

        compare_visible = self._verify_other_section_is_clean(page, 2, compare_section_title)
        self.result["compare_section_has_saved_note"] = compare_visible
        if compare_visible:
            raise RuntimeError("saved edited card leaked into a different quick-nav section")

        restored_text = self._restore_saved_section(page, 1, save_section_title)
        self.result["restored_text_before_reload"] = restored_text
        if restored_text != self.note_text:
            raise RuntimeError("saved note did not restore when returning to the saved section")

        page.reload(wait_until="domcontentloaded")
        self._wait_for_sources(page)
        self._open_source(page)
        page.select_option(".viewer-mode-select", "multi")
        page.wait_for_timeout(2500)
        restored_after_reload = self._restore_saved_section(page, 1, save_section_title)
        self.result["restored_text_after_reload"] = restored_after_reload
        if restored_after_reload != self.note_text:
            raise RuntimeError("saved note did not restore after full page reload")

        signals_titles = self._verify_signals_filter(page)
        self.result["signals_titles"] = signals_titles
        if not signals_titles:
            raise RuntimeError("saved edited card did not appear in Signals > 수정한 것")

    def _wait_for_sources(self, page) -> int:
        page.wait_for_function(
            """
            () => {
              const btn = document.querySelector('button.viewer-utility-btn');
              if (!btn) return false;
              const match = btn.innerText.match(/Sources \\((\\d+)\\)/);
              return Boolean(match && Number(match[1]) > 0);
            }
            """,
            timeout=120000,
        )
        raw = page.locator("button.viewer-utility-btn").first.inner_text()
        count = int(raw.split("(", 1)[1].split(")", 1)[0])
        return count

    def _open_source(self, page) -> None:
        sources_button = page.locator("button.viewer-utility-btn").first
        if "active" not in (sources_button.get_attribute("class") or ""):
            sources_button.click()
            page.wait_for_timeout(400)

        source_section = page.locator(".source-section").first
        if "collapsed" in (source_section.get_attribute("class") or ""):
            page.locator(".section-header-btn").first.click()
            page.wait_for_timeout(400)

        page.locator(".source-item", has_text=self.config.source_title).click()
        page.wait_for_function(
            "() => document.querySelector('.viewer-mode-select') !== null",
            timeout=120000,
        )
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

    def _quick_nav_titles(self, page) -> list[str]:
        self._open_quick_nav(page)
        titles = page.locator(".viewer-quick-nav-item-heading").all_inner_texts()
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        return titles

    def _open_quick_nav_item(self, page, index: int) -> str:
        self._open_quick_nav(page)
        heading = page.locator(".viewer-quick-nav-item-heading").nth(index)
        heading.wait_for(state="visible", timeout=30000)
        label = heading.inner_text()
        page.locator(".viewer-quick-nav-item").nth(index).click()
        page.wait_for_timeout(2500)
        return label

    def _open_quick_nav(self, page) -> None:
        trigger = page.locator("button.viewer-quick-nav-trigger")
        popover = page.locator(".viewer-quick-nav-popover")
        trigger.wait_for(state="visible", timeout=30000)
        for _ in range(3):
            if popover.count() > 0 and popover.first.is_visible():
                return
            trigger.click()
            try:
                popover.wait_for(state="visible", timeout=5000)
                return
            except PlaywrightTimeoutError:
                page.wait_for_timeout(300)
        popover.wait_for(state="visible", timeout=30000)

    def _save_note(self, page, note_text: str) -> str:
        note_toggle = page.locator("button.wiki-overlay-action[title*='텍스트']")
        note_toggle.click()
        page.wait_for_function(
            "() => document.querySelector('.viewer-note-panel-target') !== null",
            timeout=30000,
        )
        current_target_title = page.locator(".viewer-note-panel-target").inner_text().strip()
        page.locator(".wiki-note-input").fill(note_text)
        page.locator(".viewer-note-style-btn", has_text="Teal").click()
        page.locator(".viewer-note-style-btn", has_text="Bold").click()
        page.locator(".viewer-note-actions .outline-btn", has_text="저장").click()
        page.wait_for_function(
            """(expected) => {
              const node = document.querySelector('.viewer-added-text-body');
              return Boolean(node && (node.textContent || '').trim() === expected);
            }""",
            arg=note_text,
            timeout=30000,
        )
        visible_note = page.locator(".viewer-added-text-body").inner_text().strip()
        if visible_note != note_text:
            raise RuntimeError("saved note body did not render in the viewer stage rail")
        return current_target_title

    def _verify_other_section_is_clean(self, page, index: int, expected_title: str) -> bool:
        target = self._open_quick_nav_item(page, index)
        self.result["compare_section_title_after_nav"] = target
        if target != expected_title:
            raise RuntimeError(
                f"compare section mismatch: expected {expected_title!r}, got {target!r}"
            )
        return page.locator(".viewer-added-text-card").count() > 0

    def _restore_saved_section(self, page, index: int, expected_title: str) -> str:
        target = self._open_quick_nav_item(page, index)
        if target != expected_title:
            raise RuntimeError(
                f"restore section mismatch: expected {expected_title!r}, got {target!r}"
            )
        return page.locator(".viewer-added-text-body").inner_text().strip()

    def _verify_signals_filter(self, page) -> list[str]:
        page.get_by_role("button", name="Signals").click()
        page.wait_for_timeout(500)
        page.locator(".signals-filter-btn", has_text="수정한 것").click()
        page.wait_for_timeout(1000)
        return page.locator(".signals-card").nth(1).locator(".signals-chip").all_inner_texts()

    def _cleanup_saved_overlay(self) -> int:
        try:
            response = requests.get(
                f"{self.config.runtime_base}/api/wiki-overlays",
                params={"user_id": self.config.user_id},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return 0

        removed = 0
        for item in payload.get("items", []):
            if item.get("kind") != "edited_card":
                continue
            if (item.get("body") or "").strip() != self.note_text:
                continue
            remove_response = requests.post(
                f"{self.config.runtime_base}/api/wiki-overlays/remove",
                json={
                    "user_id": self.config.user_id,
                    "overlay_id": item.get("overlay_id"),
                },
                timeout=60,
            )
            if remove_response.ok:
                removed += 1
        return removed

    def _write_report(self) -> None:
        if not self.config.report_path:
            return
        report_path = Path(self.config.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(self.result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def parse_args() -> SmokeConfig:
    parser = argparse.ArgumentParser(description="Run the Workspace card-edit browser smoke.")
    parser.add_argument("--app-base", default=DEFAULT_APP_BASE)
    parser.add_argument("--runtime-base", default=DEFAULT_RUNTIME_BASE)
    parser.add_argument("--browser-path", default=DEFAULT_BROWSER_PATH)
    parser.add_argument("--source-title", default=DEFAULT_SOURCE_TITLE)
    parser.add_argument("--user-id", default=DEFAULT_USER_ID)
    parser.add_argument("--keep-overlay", action="store_true")
    parser.add_argument("--report-path", default="")
    args = parser.parse_args()
    return SmokeConfig(
        app_base=args.app_base.rstrip("/"),
        runtime_base=args.runtime_base.rstrip("/"),
        browser_path=args.browser_path,
        source_title=args.source_title,
        user_id=args.user_id,
        keep_overlay=bool(args.keep_overlay),
        report_path=args.report_path,
    )


def main() -> int:
    config = parse_args()
    smoke = WorkspaceCardEditSmoke(config)
    try:
        result = smoke.run()
    except PlaywrightTimeoutError as exc:
        smoke.result["error"] = f"playwright timeout: {exc}"
        smoke._write_report()
        print(json.dumps(smoke.result, ensure_ascii=False, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover - operational closeout path
        smoke.result["error"] = str(exc)
        smoke._write_report()
        print(json.dumps(smoke.result, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
