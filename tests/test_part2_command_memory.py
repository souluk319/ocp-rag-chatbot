from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.command_memory import (  # noqa: E402
    build_command_template_follow_up_answer,
    build_command_template_hints,
    build_command_template_memory,
)
from ocp_rag_part2.models import CommandTemplateMemory, ProcedureMemory, SessionContext  # noqa: E402


class CommandMemoryTests(unittest.TestCase):
    def test_build_command_template_memory_parses_serviceaccount_flag_style(self) -> None:
        template = build_command_template_memory(
            "oc adm policy add-role-to-user view -z default -n user-getting-started"
        )

        self.assertIsNotNone(template)
        assert template is not None
        self.assertEqual("rbac_add_role_to_subject", template.operation)
        self.assertEqual("serviceaccount", template.slots["subject_kind"])
        self.assertEqual("default", template.slots["subject_name"])
        self.assertEqual("user-getting-started", template.slots["namespace"])
        self.assertIn("-z {subject_name}", template.template)

    def test_build_command_template_follow_up_replays_recent_command(self) -> None:
        template = build_command_template_memory(
            "oc adm policy add-role-to-user admin alice -n joe"
        )
        assert template is not None
        context = SessionContext(recent_command_templates=[template])

        answer = build_command_template_follow_up_answer(
            "그 명령 다시",
            context,
            citations=[object()],
        )

        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("oc adm policy add-role-to-user admin alice -n joe", answer)
        self.assertIn("[1]", answer)

    def test_build_command_template_follow_up_allows_namespace_mutation(self) -> None:
        template = build_command_template_memory(
            "oc adm policy add-role-to-user admin alice -n joe"
        )
        assert template is not None
        context = SessionContext(recent_command_templates=[template])

        answer = build_command_template_follow_up_answer(
            "prod namespace 기준으로 다시",
            context,
            citations=[object()],
        )

        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("-n prod", answer)
        self.assertIn("namespace joe -> prod", answer)

    def test_build_command_template_follow_up_blocks_subject_kind_change(self) -> None:
        template = build_command_template_memory(
            "oc adm policy add-role-to-user admin alice -n joe"
        )
        assert template is not None
        context = SessionContext(recent_command_templates=[template])

        answer = build_command_template_follow_up_answer(
            "serviceaccount 기준으로 다시",
            context,
            citations=[object()],
        )

        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("user/group/serviceaccount", answer)
        self.assertNotIn("add-role-to-serviceaccount", answer)

    def test_build_command_template_hints_fail_closed_for_unsafe_kind_change(self) -> None:
        template = build_command_template_memory(
            "oc adm policy add-role-to-user admin alice -n joe"
        )
        assert template is not None
        context = SessionContext(recent_command_templates=[template])

        hints = build_command_template_hints("serviceaccount 기준으로 다시", context)

        self.assertEqual([], hints)

    def test_build_command_template_follow_up_prefers_step_template(self) -> None:
        step_one = build_command_template_memory("oc adm policy add-role-to-user admin alice -n joe")
        step_two = build_command_template_memory("oc describe rolebinding -n joe")
        recent = CommandTemplateMemory(
            operation="namespace_scoped_command",
            format="command",
            template="oc get pods -n {namespace}",
            rendered="oc get pods -n legacy",
            slots={"namespace": "legacy"},
            references=[],
        )
        context = SessionContext(
            recent_command_templates=[recent],
            procedure_memory=ProcedureMemory(
                goal="rbac verify",
                steps=["Create binding", "Verify binding"],
                active_step_index=0,
                step_commands=[
                    "oc adm policy add-role-to-user admin alice -n joe",
                    "oc describe rolebinding -n joe",
                ],
                step_command_templates=[step_one, step_two],
                references=[],
            ),
        )

        answer = build_command_template_follow_up_answer(
            "2번 단계 그 명령 다시",
            context,
            citations=[object()],
        )

        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("oc describe rolebinding -n joe", answer)
        self.assertNotIn("oc get pods -n legacy", answer)


if __name__ == "__main__":
    unittest.main()
