from __future__ import annotations

import re
from dataclasses import dataclass

from .models import CommandTemplateMemory, SessionContext


STEP_REFERENCE_RE = re.compile(r"(?<!\d)(1[0-2]|[1-9])번(?:\s*단계)?")
PROCEDURE_NEXT_STEP_RE = re.compile(
    r"(다음(?:\s*단계)?|그 다음|이어서|다음으로|계속(?:해서)?)",
    re.IGNORECASE,
)
PROCEDURE_CURRENT_STEP_RE = re.compile(
    r"(이 단계|현재 단계|여기서|여기부터|방금 단계|해당 단계)",
    re.IGNORECASE,
)
FOLLOW_UP_COMMAND_RE = re.compile(
    r"(그\s*명령|그\s*커맨드|그\s*yaml|그\s*manifest|다시|바꿔|바꿔서|변경|대신|"
    r"serviceaccount|서비스어카운트|서비스\s*계정|group|그룹|user|사용자|"
    r"namespace|네임스페이스|프로젝트|yaml|manifest|매니페스트)",
    re.IGNORECASE,
)
YAML_REQUEST_RE = re.compile(r"(yaml|manifest|매니페스트)", re.IGNORECASE)
SERVICEACCOUNT_RE = re.compile(
    r"(serviceaccount|서비스어카운트|서비스\s*계정)",
    re.IGNORECASE,
)
GROUP_RE = re.compile(r"(\bgroup\b|그룹)", re.IGNORECASE)
USER_RE = re.compile(r"(\buser\b|사용자)", re.IGNORECASE)
NAMESPACE_VALUE_RE = re.compile(
    r"(?P<value>[A-Za-z0-9][-A-Za-z0-9_.]*)\s*"
    r"(?:namespace|네임스페이스|프로젝트)\s*(?:기준(?:으로)?|으로|에서|는|은)?",
    re.IGNORECASE,
)
SUBJECT_SWAP_RE = re.compile(
    r"(?P<current>[A-Za-z0-9:_-]+)\s+대신\s+(?P<new>[A-Za-z0-9:_-]+)",
    re.IGNORECASE,
)
ROLE_TO_SUBJECT_RE = re.compile(
    r"^oc\s+adm\s+policy\s+add-role-to-(?P<subject_kind>user|group|serviceaccount)\s+"
    r"(?P<role>\S+)\s+(?P<subject>\S+)\s+(?:-n|--namespace)\s+(?P<namespace>\S+)\s*$",
    re.IGNORECASE,
)
ROLE_TO_SERVICEACCOUNT_FLAG_RE = re.compile(
    r"^oc\s+adm\s+policy\s+add-role-to-user\s+(?P<role>\S+)\s+-z\s+(?P<subject>\S+)\s+"
    r"(?:-n|--namespace)\s+(?P<namespace>\S+)\s*$",
    re.IGNORECASE,
)
DESCRIBE_ROLEBINDING_RE = re.compile(
    r"^(?P<prefix>oc\s+describe\s+rolebinding(?:\s+\S+)?)\s+"
    r"(?:-n|--namespace)\s+(?P<namespace>\S+)\s*$",
    re.IGNORECASE,
)
CAN_I_RE = re.compile(
    r"^(?P<prefix>oc\s+auth\s+can-i\b.*?)(?:\s+(?:-n|--namespace)\s+(?P<namespace>\S+))?"
    r"(?:\s+--as\s+(?P<subject>\S+))?\s*$",
    re.IGNORECASE,
)
NAMESPACE_FLAG_RE = re.compile(r"(?P<flag>--namespace|-n)\s+\S+")
NAMESPACE_PATH_RE = re.compile(r"(?P<prefix>/namespaces/)(?P<namespace>[^/\s]+)")
ROLEBINDING_YAML_SUBJECT_RE = re.compile(
    r"subjects:\s*-\s*kind:\s*(?P<kind>User|Group|ServiceAccount)"
    r"\s*(?:\n\s*apiGroup:\s*[^\n]+)?\s*\n\s*name:\s*(?P<subject>[^\n#]+)",
    re.IGNORECASE | re.DOTALL,
)
ROLEBINDING_YAML_ROLE_RE = re.compile(
    r"roleRef:\s*(?:.*?\n)*?\s*name:\s*(?P<role>[^\n#]+)",
    re.IGNORECASE | re.DOTALL,
)
YAML_NAMESPACE_LINE_RE = re.compile(r"(?m)^(\s*namespace:\s*)([^\n#]+)")
YAML_SUBJECT_KIND_LINE_RE = re.compile(
    r"(?ms)(subjects:\s*-\s*kind:\s*)(User|Group|ServiceAccount)"
)
YAML_SUBJECT_NAME_LINE_RE = re.compile(
    r"(?ms)(subjects:\s*-\s*kind:\s*(?:User|Group|ServiceAccount)"
    r"\s*(?:\n\s*apiGroup:\s*[^\n]+)?\s*\n\s*name:\s*)([^\n#]+)"
)

SUBJECT_KIND_TITLE = {
    "user": "User",
    "group": "Group",
    "serviceaccount": "ServiceAccount",
}
SUBJECT_NAME_PLACEHOLDERS = {
    "user": "<user-name>",
    "group": "<group-name>",
    "serviceaccount": "<serviceaccount-name>",
}


@dataclass(slots=True)
class CommandMutationResult:
    memory: CommandTemplateMemory
    rendered: str
    changes: list[str]
    requested_format: str


def build_command_template_memory(
    command_text: str,
    *,
    references: list[str] | None = None,
    block_format: str = "",
) -> CommandTemplateMemory | None:
    text = (command_text or "").strip()
    if not text:
        return None

    normalized_format = (block_format or "").strip().lower()
    refs = list(references or [])

    if normalized_format in {"yaml", "yml"} or _looks_like_rolebinding_yaml(text):
        subject_match = ROLEBINDING_YAML_SUBJECT_RE.search(text)
        namespace_match = YAML_NAMESPACE_LINE_RE.search(text)
        role_match = ROLEBINDING_YAML_ROLE_RE.search(text)
        if subject_match and namespace_match:
            subject_kind = _canonical_subject_kind(subject_match.group("kind"))
            subject_name = subject_match.group("subject").strip()
            namespace = namespace_match.group(2).strip()
            slots = {
                "namespace": namespace,
                "subject_kind": subject_kind,
                "subject_name": subject_name,
            }
            if role_match:
                slots["role"] = role_match.group("role").strip()
            return CommandTemplateMemory(
                operation="rbac_rolebinding_yaml",
                format="yaml",
                template=text,
                rendered=text,
                slots=slots,
                references=refs,
            )

    role_match = ROLE_TO_SUBJECT_RE.match(text)
    if role_match:
        subject_kind = _canonical_subject_kind(role_match.group("subject_kind"))
        return CommandTemplateMemory(
            operation="rbac_add_role_to_subject",
            format="command",
            template=f"oc adm policy add-role-to-{subject_kind} {{role}} {{subject_name}} -n {{namespace}}",
            rendered=text,
            slots={
                "role": role_match.group("role"),
                "namespace": role_match.group("namespace"),
                "subject_kind": subject_kind,
                "subject_name": role_match.group("subject"),
            },
            references=refs,
        )

    serviceaccount_flag_match = ROLE_TO_SERVICEACCOUNT_FLAG_RE.match(text)
    if serviceaccount_flag_match:
        return CommandTemplateMemory(
            operation="rbac_add_role_to_subject",
            format="command",
            template="oc adm policy add-role-to-user {role} -z {subject_name} -n {namespace}",
            rendered=text,
            slots={
                "role": serviceaccount_flag_match.group("role"),
                "namespace": serviceaccount_flag_match.group("namespace"),
                "subject_kind": "serviceaccount",
                "subject_name": serviceaccount_flag_match.group("subject"),
            },
            references=refs,
        )

    describe_match = DESCRIBE_ROLEBINDING_RE.match(text)
    if describe_match:
        return CommandTemplateMemory(
            operation="rbac_describe_rolebinding",
            format="command",
            template=describe_match.group("prefix") + " -n {namespace}",
            rendered=text,
            slots={"namespace": describe_match.group("namespace")},
            references=refs,
        )

    can_i_match = CAN_I_RE.match(text)
    if can_i_match and (can_i_match.group("namespace") or can_i_match.group("subject")):
        namespace = can_i_match.group("namespace") or ""
        subject = can_i_match.group("subject") or ""
        subject_kind, subject_name = _normalize_as_subject(subject, namespace)
        template = can_i_match.group("prefix").strip()
        if namespace:
            template += " -n {namespace}"
        if subject:
            template += " --as {subject_ref}"
        return CommandTemplateMemory(
            operation="rbac_can_i",
            format="command",
            template=template,
            rendered=text,
            slots={
                "namespace": namespace,
                "subject_kind": subject_kind,
                "subject_name": subject_name,
            },
            references=refs,
        )

    namespace_flag_match = NAMESPACE_FLAG_RE.search(text)
    if namespace_flag_match:
        namespace = namespace_flag_match.group(0).split()[-1]
        template = NAMESPACE_FLAG_RE.sub(r"\g<flag> {namespace}", text, count=1)
        return CommandTemplateMemory(
            operation="namespace_scoped_command",
            format="command",
            template=template,
            rendered=text,
            slots={"namespace": namespace},
            references=refs,
        )

    namespace_path_match = NAMESPACE_PATH_RE.search(text)
    if namespace_path_match:
        namespace = namespace_path_match.group("namespace")
        template = NAMESPACE_PATH_RE.sub(r"\g<prefix>{namespace}", text, count=1)
        return CommandTemplateMemory(
            operation="namespace_scoped_command",
            format="command",
            template=template,
            rendered=text,
            slots={"namespace": namespace},
            references=refs,
        )

    return None


def has_command_template_follow_up(query: str, context: SessionContext | None) -> bool:
    if context is None:
        return False
    if not _select_template_for_follow_up(query, context):
        return False
    return bool(FOLLOW_UP_COMMAND_RE.search(query or ""))


def build_command_template_hints(query: str, context: SessionContext | None) -> list[str]:
    template = _select_template_for_follow_up(query, context)
    if template is None or not has_command_template_follow_up(query, context):
        return []

    mutation = mutate_command_template(template, query)
    if mutation is None or mutation.requested_format != template.format:
        return []

    slots = mutation.memory.slots
    slot_items = [f"{key}={value}" for key, value in sorted(slots.items()) if value]
    hints = [
        f"recent command template operation={template.operation}",
        f"recent command format={template.format}",
    ]
    if slot_items:
        hints.append("recent command slots " + " | ".join(slot_items))
    return hints


def build_command_template_follow_up_answer(
    query: str,
    context: SessionContext | None,
    citations: list[object],
) -> str | None:
    template = _select_template_for_follow_up(query, context)
    if template is None or not has_command_template_follow_up(query, context):
        return None

    mutation = mutate_command_template(template, query)
    if mutation is None:
        return None
    if mutation.requested_format != template.format:
        return None

    citation_mark = " [1]" if citations else ""
    label = "YAML" if mutation.memory.format == "yaml" else "명령"
    if mutation.changes:
        lines = [f"답변: 최근 {label}을 요청한 기준으로 다시 정리했습니다{citation_mark}."]
        lines.extend(["", "변경: " + " / ".join(mutation.changes)])
    else:
        lines = [f"답변: 최근 {label}을 다시 보여드립니다{citation_mark}."]

    fence = "yaml" if mutation.memory.format == "yaml" else "bash"
    lines.extend(["", f"```{fence}", mutation.rendered, "```"])
    return "\n".join(lines)


def mutate_command_template(
    template: CommandTemplateMemory,
    query: str,
) -> CommandMutationResult | None:
    if not template.operation:
        return None

    requested_format = "yaml" if YAML_REQUEST_RE.search(query or "") else template.format
    if requested_format != template.format:
        return CommandMutationResult(
            memory=template,
            rendered=template.rendered,
            changes=[],
            requested_format=requested_format,
        )

    slots = dict(template.slots)
    changes: list[str] = []

    namespace = _resolve_namespace_value(query, slots.get("namespace", ""))
    if namespace != slots.get("namespace", ""):
        changes.append(f"namespace {slots.get('namespace', '-') } -> {namespace}")
        slots["namespace"] = namespace

    subject_kind, subject_name = _resolve_subject_update_v2(query, slots)
    if subject_kind != slots.get("subject_kind", ""):
        changes.append(f"subject {slots.get('subject_kind', '-') } -> {subject_kind}")
        slots["subject_kind"] = subject_kind
    if subject_name != slots.get("subject_name", ""):
        changes.append(f"name {slots.get('subject_name', '-') } -> {subject_name}")
        slots["subject_name"] = subject_name

    rendered = _render_command_template(template, slots)
    if not rendered:
        return None

    updated = CommandTemplateMemory(
        operation=template.operation,
        format=template.format,
        template=template.template,
        rendered=rendered,
        slots=slots,
        references=list(template.references),
    )
    return CommandMutationResult(
        memory=updated,
        rendered=rendered,
        changes=changes,
        requested_format=requested_format,
    )


def _render_command_template(template: CommandTemplateMemory, slots: dict[str, str]) -> str:
    if template.operation == "rbac_add_role_to_subject":
        subject_kind = slots.get("subject_kind") or "user"
        namespace = slots.get("namespace") or "<namespace-name>"
        role = slots.get("role") or "<role-name>"
        subject_name = slots.get("subject_name") or SUBJECT_NAME_PLACEHOLDERS.get(
            subject_kind,
            "<subject-name>",
        )
        return (
            f"oc adm policy add-role-to-{subject_kind} {role} {subject_name} -n {namespace}"
        ).strip()

    if template.operation == "rbac_describe_rolebinding":
        namespace = slots.get("namespace") or "<namespace-name>"
        return template.template.format(namespace=namespace).strip()

    if template.operation == "rbac_can_i":
        namespace = slots.get("namespace") or "<namespace-name>"
        subject_ref = _render_as_subject_ref(
            slots.get("subject_kind") or "user",
            slots.get("subject_name") or "",
            namespace,
        )
        payload = {"namespace": namespace, "subject_ref": subject_ref}
        return template.template.format(**payload).strip()

    if template.operation == "namespace_scoped_command":
        namespace = slots.get("namespace") or "<namespace-name>"
        return template.template.format(namespace=namespace).strip()

    if template.operation == "rbac_rolebinding_yaml":
        return _render_rolebinding_yaml(template.template, slots)

    return template.rendered


def _render_rolebinding_yaml(template_text: str, slots: dict[str, str]) -> str:
    rendered = template_text
    namespace = slots.get("namespace") or "<namespace-name>"
    subject_kind = SUBJECT_KIND_TITLE.get(
        slots.get("subject_kind") or "user",
        "User",
    )
    subject_name = slots.get("subject_name") or SUBJECT_NAME_PLACEHOLDERS.get(
        slots.get("subject_kind") or "user",
        "<subject-name>",
    )

    rendered = YAML_NAMESPACE_LINE_RE.sub(rf"\1{namespace}", rendered, count=1)
    rendered = YAML_SUBJECT_KIND_LINE_RE.sub(
        lambda match: match.group(1) + subject_kind,
        rendered,
        count=1,
    )
    rendered = YAML_SUBJECT_NAME_LINE_RE.sub(
        lambda match: match.group(1) + subject_name,
        rendered,
        count=1,
    )
    return rendered.strip()


def _resolve_namespace_value(query: str, current_namespace: str) -> str:
    match = NAMESPACE_VALUE_RE.search(query or "")
    if match:
        return match.group("value")
    lowered = (query or "").lower()
    if "namespace" in lowered or "네임스페이스" in (query or "") or "프로젝트" in (query or ""):
        return current_namespace or "<namespace-name>"
    return current_namespace


def _resolve_subject_update(query: str, slots: dict[str, str]) -> tuple[str, str]:
    current_kind = slots.get("subject_kind", "")
    current_name = slots.get("subject_name", "")
    requested_kind = current_kind
    normalized = query or ""

    if SERVICEACCOUNT_RE.search(normalized):
        requested_kind = "serviceaccount"
    elif GROUP_RE.search(normalized):
        requested_kind = "group"
    elif USER_RE.search(normalized):
        requested_kind = "user"

    swap_match = SUBJECT_SWAP_RE.search(normalized)
    if swap_match:
        current_token = swap_match.group("current")
        new_token = swap_match.group("new")
        if current_token == current_name:
            canonical_new_kind = _canonical_subject_kind(new_token)
            if canonical_new_kind != new_token:
                return canonical_new_kind, SUBJECT_NAME_PLACEHOLDERS.get(
                    canonical_new_kind,
                    current_name,
                )
            return requested_kind or current_kind, new_token
        if _canonical_subject_kind(current_token) != current_token:
            return _canonical_subject_kind(new_token), SUBJECT_NAME_PLACEHOLDERS.get(
                _canonical_subject_kind(new_token),
                current_name,
            )

    if requested_kind != current_kind:
        return requested_kind, SUBJECT_NAME_PLACEHOLDERS.get(requested_kind, current_name)
    return current_kind, current_name


def _select_template_for_follow_up(
    query: str,
    context: SessionContext | None,
) -> CommandTemplateMemory | None:
    if context is None:
        return None

    procedure = context.procedure_memory
    if procedure is not None and procedure.step_command_templates:
        step_index = _resolve_procedure_step_index(query, context)
        if step_index is not None:
            template = procedure.command_template_for(step_index)
            if template is not None:
                return template
        if procedure.active_step_index is not None:
            template = procedure.command_template_for(procedure.active_step_index)
            if template is not None:
                return template

    return context.recent_command_templates[0] if context.recent_command_templates else None


def _resolve_procedure_step_index(query: str, context: SessionContext) -> int | None:
    procedure = context.procedure_memory
    if procedure is None or not procedure.steps:
        return None

    normalized = query or ""
    match = STEP_REFERENCE_RE.search(normalized)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(procedure.steps):
            return index

    if PROCEDURE_CURRENT_STEP_RE.search(normalized):
        return procedure.active_step_index

    if PROCEDURE_NEXT_STEP_RE.search(normalized):
        if procedure.active_step_index is None:
            return 0 if procedure.steps else None
        return min(procedure.active_step_index + 1, len(procedure.steps) - 1)
    return None


def _canonical_subject_kind(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized in {"serviceaccount", "service-account", "sa"}:
        return "serviceaccount"
    if normalized == "group":
        return "group"
    if normalized == "user":
        return "user"
    title_normalized = normalized.title()
    if title_normalized == "Serviceaccount":
        return "serviceaccount"
    if title_normalized in {"Group", "User"}:
        return title_normalized.lower()
    return normalized


def _normalize_as_subject(subject: str, namespace: str) -> tuple[str, str]:
    cleaned = (subject or "").strip()
    if cleaned.startswith("system:serviceaccount:"):
        parts = cleaned.split(":", 3)
        if len(parts) == 4:
            return "serviceaccount", parts[3]
        return "serviceaccount", SUBJECT_NAME_PLACEHOLDERS["serviceaccount"]
    if ":" not in cleaned:
        return "user", cleaned
    return "group", cleaned


def _render_as_subject_ref(subject_kind: str, subject_name: str, namespace: str) -> str:
    name = subject_name or SUBJECT_NAME_PLACEHOLDERS.get(subject_kind, "<subject-name>")
    if subject_kind == "serviceaccount":
        scoped_namespace = namespace or "<namespace-name>"
        return f"system:serviceaccount:{scoped_namespace}:{name}"
    return name


def _looks_like_rolebinding_yaml(text: str) -> bool:
    lowered = text.lower()
    return "kind: rolebinding" in lowered and "subjects:" in lowered and "roleref:" in lowered


# Canonical command-template path: keep parsing, safe mutation, and replay in one module.
def build_command_template_memory(
    command_text: str,
    *,
    references: list[str] | None = None,
    block_format: str = "",
) -> CommandTemplateMemory | None:
    text = (command_text or "").strip()
    if not text:
        return None

    normalized_format = (block_format or "").strip().lower()
    refs = list(references or [])

    if normalized_format in {"yaml", "yml"} or _looks_like_rolebinding_yaml(text):
        subject_match = ROLEBINDING_YAML_SUBJECT_RE.search(text)
        namespace_match = YAML_NAMESPACE_LINE_RE.search(text)
        role_match = ROLEBINDING_YAML_ROLE_RE.search(text)
        if subject_match and namespace_match:
            subject_kind = _canonical_subject_kind(subject_match.group("kind"))
            subject_name = subject_match.group("subject").strip()
            namespace = namespace_match.group(2).strip()
            slots = {
                "namespace": namespace,
                "subject_kind": subject_kind,
                "subject_name": subject_name,
            }
            if role_match:
                slots["role"] = role_match.group("role").strip()
            return CommandTemplateMemory(
                operation="rbac_rolebinding_yaml",
                format="yaml",
                template=text,
                rendered=text,
                slots=slots,
                references=refs,
            )

    role_match = ROLE_TO_SUBJECT_RE.match(text)
    if role_match:
        subject_kind = _canonical_subject_kind(role_match.group("subject_kind"))
        return CommandTemplateMemory(
            operation="rbac_add_role_to_subject",
            format="command",
            template=f"oc adm policy add-role-to-{subject_kind} {{role}} {{subject_name}} -n {{namespace}}",
            rendered=text,
            slots={
                "role": role_match.group("role"),
                "namespace": role_match.group("namespace"),
                "subject_kind": subject_kind,
                "subject_name": role_match.group("subject"),
            },
            references=refs,
        )

    serviceaccount_flag_match = ROLE_TO_SERVICEACCOUNT_FLAG_RE.match(text)
    if serviceaccount_flag_match:
        return CommandTemplateMemory(
            operation="rbac_add_role_to_subject",
            format="command",
            template="oc adm policy add-role-to-user {role} -z {subject_name} -n {namespace}",
            rendered=text,
            slots={
                "role": serviceaccount_flag_match.group("role"),
                "namespace": serviceaccount_flag_match.group("namespace"),
                "subject_kind": "serviceaccount",
                "subject_name": serviceaccount_flag_match.group("subject"),
            },
            references=refs,
        )

    describe_match = DESCRIBE_ROLEBINDING_RE.match(text)
    if describe_match:
        return CommandTemplateMemory(
            operation="rbac_describe_rolebinding",
            format="command",
            template=describe_match.group("prefix") + " -n {namespace}",
            rendered=text,
            slots={"namespace": describe_match.group("namespace")},
            references=refs,
        )

    can_i_match = CAN_I_RE.match(text)
    if can_i_match and (can_i_match.group("namespace") or can_i_match.group("subject")):
        namespace = can_i_match.group("namespace") or ""
        subject = can_i_match.group("subject") or ""
        subject_kind, subject_name = _normalize_as_subject(subject, namespace)
        template = can_i_match.group("prefix").strip()
        if namespace:
            template += " -n {namespace}"
        if subject:
            template += " --as {subject_ref}"
        return CommandTemplateMemory(
            operation="rbac_can_i",
            format="command",
            template=template,
            rendered=text,
            slots={
                "namespace": namespace,
                "subject_kind": subject_kind,
                "subject_name": subject_name,
            },
            references=refs,
        )

    namespace_flag_match = NAMESPACE_FLAG_RE.search(text)
    if namespace_flag_match:
        namespace = namespace_flag_match.group(0).split()[-1]
        template = NAMESPACE_FLAG_RE.sub(r"\g<flag> {namespace}", text, count=1)
        return CommandTemplateMemory(
            operation="namespace_scoped_command",
            format="command",
            template=template,
            rendered=text,
            slots={"namespace": namespace},
            references=refs,
        )

    namespace_path_match = NAMESPACE_PATH_RE.search(text)
    if namespace_path_match:
        namespace = namespace_path_match.group("namespace")
        template = NAMESPACE_PATH_RE.sub(r"\g<prefix>{namespace}", text, count=1)
        return CommandTemplateMemory(
            operation="namespace_scoped_command",
            format="command",
            template=template,
            rendered=text,
            slots={"namespace": namespace},
            references=refs,
        )

    return None


def build_command_template_hints(query: str, context: SessionContext | None) -> list[str]:
    template = _select_template_for_follow_up(query, context)
    if template is None or not has_command_template_follow_up(query, context):
        return []

    mutation = mutate_command_template(template, query)
    if mutation is None or mutation.requested_format != template.format:
        return []

    slot_items = [
        f"{key}={value}"
        for key, value in sorted(mutation.memory.slots.items())
        if value
    ]
    hints = [
        f"recent command template operation={template.operation}",
        f"recent command format={template.format}",
    ]
    if slot_items:
        hints.append("recent command slots " + " | ".join(slot_items))
    return hints


def build_command_template_follow_up_answer(
    query: str,
    context: SessionContext | None,
    citations: list[object],
) -> str | None:
    template = _select_template_for_follow_up(query, context)
    if template is None or not has_command_template_follow_up(query, context):
        return None

    mutation = mutate_command_template(template, query)
    if mutation is None:
        reason = _classify_unsupported_mutation(query, template)
        return _build_command_template_clarification(reason, citations)
    if mutation.requested_format != template.format:
        return _build_command_template_clarification("format", citations)

    citation_mark = " [1]" if citations else ""
    label = "YAML" if mutation.memory.format == "yaml" else "명령"
    if mutation.changes:
        lines = [f"답변: 최근 {label}에서 요청한 값만 안전하게 바꿔 다시 적었습니다{citation_mark}."]
        lines.extend(["", "변경 사항: " + " / ".join(mutation.changes)])
    else:
        lines = [f"답변: 최근 {label}을 그대로 다시 보여드립니다{citation_mark}."]

    fence = "yaml" if mutation.memory.format == "yaml" else "bash"
    lines.extend(["", f"```{fence}", mutation.rendered, "```"])
    return "\n".join(lines)


def mutate_command_template(
    template: CommandTemplateMemory,
    query: str,
) -> CommandMutationResult | None:
    if not template.operation:
        return None

    requested_format = "yaml" if YAML_REQUEST_RE.search(query or "") else template.format
    if requested_format != template.format:
        return CommandMutationResult(
            memory=template,
            rendered=template.rendered,
            changes=[],
            requested_format=requested_format,
        )

    slots = dict(template.slots)
    changes: list[str] = []

    namespace = _resolve_namespace_value(query, slots.get("namespace", ""))
    if namespace != slots.get("namespace", ""):
        changes.append(f"namespace {slots.get('namespace', '-')} -> {namespace}")
        slots["namespace"] = namespace

    if _has_role_change_request(query, slots):
        return None

    subject_update = _resolve_subject_update_safe(query, slots)
    if subject_update is None:
        return None

    subject_kind, subject_name = subject_update
    if subject_kind != slots.get("subject_kind", ""):
        changes.append(f"subject {slots.get('subject_kind', '-')} -> {subject_kind}")
        slots["subject_kind"] = subject_kind
    if subject_name != slots.get("subject_name", ""):
        changes.append(f"name {slots.get('subject_name', '-')} -> {subject_name}")
        slots["subject_name"] = subject_name

    rendered = _render_command_template(template, slots)
    if not rendered:
        return None

    updated = CommandTemplateMemory(
        operation=template.operation,
        format=template.format,
        template=template.template,
        rendered=rendered,
        slots=slots,
        references=list(template.references),
    )
    return CommandMutationResult(
        memory=updated,
        rendered=rendered,
        changes=changes,
        requested_format=requested_format,
    )


def _render_command_template(template: CommandTemplateMemory, slots: dict[str, str]) -> str:
    if template.operation == "rbac_add_role_to_subject":
        subject_kind = slots.get("subject_kind") or "user"
        namespace = slots.get("namespace") or "<namespace-name>"
        role = slots.get("role") or "<role-name>"
        subject_name = slots.get("subject_name") or SUBJECT_NAME_PLACEHOLDERS.get(
            subject_kind,
            "<subject-name>",
        )
        return template.template.format(
            role=role,
            subject_name=subject_name,
            namespace=namespace,
        ).strip()

    if template.operation == "rbac_describe_rolebinding":
        namespace = slots.get("namespace") or "<namespace-name>"
        return template.template.format(namespace=namespace).strip()

    if template.operation == "rbac_can_i":
        namespace = slots.get("namespace") or "<namespace-name>"
        subject_ref = _render_as_subject_ref(
            slots.get("subject_kind") or "user",
            slots.get("subject_name") or "",
            namespace,
        )
        payload = {"namespace": namespace, "subject_ref": subject_ref}
        return template.template.format(**payload).strip()

    if template.operation == "namespace_scoped_command":
        namespace = slots.get("namespace") or "<namespace-name>"
        return template.template.format(namespace=namespace).strip()

    if template.operation == "rbac_rolebinding_yaml":
        return _render_rolebinding_yaml(template.template, slots)

    return template.rendered


def _resolve_subject_update_safe(query: str, slots: dict[str, str]) -> tuple[str, str] | None:
    current_kind = slots.get("subject_kind", "")
    current_name = slots.get("subject_name", "")
    requested_kind = current_kind
    normalized = query or ""

    if SERVICEACCOUNT_RE.search(normalized):
        requested_kind = "serviceaccount"
    elif GROUP_RE.search(normalized):
        requested_kind = "group"
    elif USER_RE.search(normalized):
        requested_kind = "user"

    if requested_kind != current_kind:
        return None

    swap_match = SUBJECT_SWAP_RE.search(normalized)
    if swap_match:
        current_token = swap_match.group("current").strip()
        new_token = swap_match.group("new").strip()
        if current_token == current_name:
            canonical_new_kind = _canonical_subject_kind(new_token)
            if canonical_new_kind != new_token:
                return None
            return current_kind, new_token
        if _canonical_subject_kind(current_token) != current_token:
            return None

    return current_kind, current_name


def _has_role_change_request(query: str, slots: dict[str, str]) -> bool:
    current_role = (slots.get("role") or "").strip()
    if not current_role:
        return False

    swap_match = SUBJECT_SWAP_RE.search(query or "")
    if not swap_match:
        return False

    return swap_match.group("current").strip() == current_role


def _requested_subject_kind(query: str) -> str:
    normalized = query or ""
    if SERVICEACCOUNT_RE.search(normalized):
        return "serviceaccount"
    if GROUP_RE.search(normalized):
        return "group"
    if USER_RE.search(normalized):
        return "user"
    return ""


def _classify_unsupported_mutation(query: str, template: CommandTemplateMemory) -> str:
    if YAML_REQUEST_RE.search(query or "") and template.format != "yaml":
        return "format"

    requested_kind = _requested_subject_kind(query)
    current_kind = (template.slots.get("subject_kind") or "").strip()
    if requested_kind and current_kind and requested_kind != current_kind:
        return "subject_kind"

    if _has_role_change_request(query, template.slots):
        return "role"

    return "ambiguous"


def _build_command_template_clarification(reason: str, citations: list[object]) -> str:
    citation_mark = " [1]" if citations else ""
    if reason == "format":
        return (
            "답변: 최근 근거 기준으로는 같은 형식의 명령만 안전하게 다시 보여드릴 수 있습니다"
            f"{citation_mark}. 명령과 YAML 전환은 새 근거로 다시 확인해야 합니다."
        )
    if reason in {"subject_kind", "role"}:
        return (
            "답변: 최근 근거 기준으로는 namespace 또는 같은 대상 종류의 이름만 안전하게 바꿔 다시 보여드릴 수 있습니다"
            f"{citation_mark}. user/group/serviceaccount 전환이나 역할 변경은 새 근거로 다시 확인해야 합니다."
        )
    return (
        "답변: 어느 값을 바꿀지 불분명합니다"
        f"{citation_mark}. namespace 또는 같은 대상 종류의 이름을 짧게 지정해 주세요."
    )
