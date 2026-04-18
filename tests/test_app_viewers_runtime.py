from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_viewers import AppViewersTestSupport


class TestAppViewerRuntime(unittest.TestCase):
    pass


for _name, _value in vars(AppViewersTestSupport).items():
    if not _name.startswith("__") and (not _name.startswith("test_") or _name.startswith("test_internal_viewer_html_")):
        setattr(TestAppViewerRuntime, _name, _value)
