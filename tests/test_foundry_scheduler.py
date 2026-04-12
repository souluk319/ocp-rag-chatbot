from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.foundry_scheduler import (
    build_foundry_schedule_tasks,
    register_foundry_schedule_tasks,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class FoundrySchedulerTests(unittest.TestCase):
    def test_build_foundry_schedule_tasks_maps_profiles_to_schtasks_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "pipelines" / "foundry_routines.json",
                {
                    "timezone": "Asia/Seoul",
                    "jobs": {},
                    "profiles": [
                        {
                            "id": "runtime_smoke_hourly",
                            "name": "Runtime Smoke Hourly",
                            "description": "runtime checks",
                            "schedule": {"cadence": "hourly", "minute": 15, "interval_hours": 1},
                            "jobs": ["runtime_smoke"],
                        },
                        {
                            "id": "morning_gate",
                            "name": "Morning Gate",
                            "description": "weekday gate",
                            "schedule": {
                                "cadence": "daily",
                                "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                                "time": "08:30",
                            },
                            "jobs": ["source_approval"],
                        },
                    ],
                },
            )
            settings = Settings(root_dir=root)

            tasks = build_foundry_schedule_tasks(settings)

            self.assertEqual(2, len(tasks))
            hourly = next(task for task in tasks if task.profile_id == "runtime_smoke_hourly")
            weekday = next(task for task in tasks if task.profile_id == "morning_gate")
            self.assertEqual(
                ("/SC", "HOURLY", "/MO", "1", "/ST", "00:15"),
                hourly.schedule_args,
            )
            self.assertEqual(
                ("/SC", "WEEKLY", "/D", "MON,TUE,WED,THU,FRI", "/ST", "08:30"),
                weekday.schedule_args,
            )
            self.assertIn("pwsh.exe", hourly.command)
            self.assertIn("run_foundry_task.ps1", hourly.command)
            self.assertNotIn("-LogPath", hourly.command)
            self.assertNotIn("-ReportDir", hourly.command)
            self.assertIn("-Retries 2", hourly.command)
            self.assertIn("-RetryDelaySeconds 900", hourly.command)
            self.assertLess(len(hourly.command), 261)
            self.assertTrue(weekday.task_name.endswith("\\morning_gate"))

    def test_register_foundry_schedule_tasks_invokes_schtasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root / "pipelines" / "foundry_routines.json",
                {
                    "timezone": "Asia/Seoul",
                    "jobs": {},
                    "profiles": [
                        {
                            "id": "nightly_refresh",
                            "name": "Nightly Refresh",
                            "description": "nightly run",
                            "schedule": {
                                "cadence": "daily",
                                "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                                "time": "01:30",
                            },
                            "jobs": ["source_approval"],
                        }
                    ],
                },
            )
            settings = Settings(root_dir=root)
            tasks = build_foundry_schedule_tasks(settings)

            with patch("play_book_studio.ingestion.foundry_scheduler.subprocess.run") as run_mock:
                results = register_foundry_schedule_tasks(tasks)

            self.assertEqual(1, len(results))
            run_mock.assert_called_once_with(
                tasks[0].schtasks_args,
                check=True,
                capture_output=True,
                text=True,
            )


if __name__ == "__main__":
    unittest.main()
