from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical.command_split import split_inline_commands
from play_book_studio.canonical.html import _postprocess_blocks
from play_book_studio.canonical.models import CodeBlock, ParagraphBlock


class CanonicalCommandSplitTests(unittest.TestCase):
    def test_split_inline_commands_extracts_shell_command_from_paragraph(self) -> None:
        split = split_inline_commands(
            "그런 다음 `oc apply -f install-config.yaml` 명령을 실행하여 클러스터에 적용합니다."
        )

        assert split is not None
        self.assertEqual(("oc apply -f install-config.yaml",), split.commands)
        self.assertEqual("그런 다음 아래 명령을 실행하여 클러스터에 적용합니다.", split.narrative_text)

    def test_split_inline_commands_handles_script_command_at_sentence_start(self) -> None:
        split = split_inline_commands(
            "`cluster-restore.sh` 로 이전 백업에서 클러스터 상태를 복원합니다."
        )

        assert split is not None
        self.assertEqual(("cluster-restore.sh",), split.commands)
        self.assertEqual("다음 명령으로 이전 백업에서 클러스터 상태를 복원합니다.", split.narrative_text)

    def test_postprocess_blocks_promotes_inline_command_paragraph_to_code_block(self) -> None:
        blocks = _postprocess_blocks(
            (
                ParagraphBlock(
                    "태그를 추가한 뒤 `podman push quay.io/example/app:latest` 명령을 실행하여 레지스트리에 이미지를 푸시합니다."
                ),
            )
        )

        self.assertEqual(2, len(blocks))
        self.assertIsInstance(blocks[0], ParagraphBlock)
        self.assertIsInstance(blocks[1], CodeBlock)
        self.assertEqual(
            "태그를 추가한 뒤 아래 명령을 실행하여 레지스트리에 이미지를 푸시합니다.",
            blocks[0].text,
        )
        self.assertEqual("podman push quay.io/example/app:latest", blocks[1].code)


if __name__ == "__main__":
    unittest.main()
