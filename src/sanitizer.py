"""공개 가능한 코퍼스로 만들기 위한 민감정보 치환기."""
from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass

# 내부 도메인 패턴은 .env에서 로드 (소스코드에 회사명 노출 방지)
# .env 예시: SANITIZE_INTERNAL_DOMAIN=my-company
_INTERNAL_DOMAIN = os.getenv("SANITIZE_INTERNAL_DOMAIN", "example-corp")

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PRIVATE_URL_RE = re.compile(
    r"\bhttps?://(?:"
    r"(?:10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|(?:172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})"
    r"|(?:192\.168\.\d{1,3}\.\d{1,3})"
    r"|(?:100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3})"
    r"|(?:[A-Za-z0-9-]+\.)*(?:" + re.escape(_INTERNAL_DOMAIN) + r")(?:\.[A-Za-z0-9.-]+)+"
    r")(?::\d+)?(?:/[^\s\"'<>)]*)?",
    re.IGNORECASE,
)
_PRIVATE_IP_RE = re.compile(
    r"\b(?:"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|127\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}"
    r")\b"
)
_INTERNAL_HOST_RE = re.compile(
    r"\b(?:[A-Za-z0-9-]+\.)*(?:" + re.escape(_INTERNAL_DOMAIN) + r")(?:\.[A-Za-z0-9.-]+)+\b",
    re.IGNORECASE,
)
_SECRET_KEY_VALUE_RE = re.compile(
    r"(?P<prefix>\b(?:password|passwd|pwd|pass|db_password|db_pass|secret|token|api[_-]?key|access[_-]?token)\b\s*[:=]\s*)"
    r"(?P<quote>[\"']?)"
    r"(?P<value>[^\s\"']+)"
    r"(?P=quote)",
    re.IGNORECASE,
)
_ACCOUNT_KEY_VALUE_RE = re.compile(
    r"(?P<prefix>\b(?:username|user|userid|user_id|account|email|db_username|db_user)\b\s*[:=]\s*)"
    r"(?P<quote>[\"']?)"
    r"(?P<value>[^\s\"']+)"
    r"(?P=quote)",
    re.IGNORECASE,
)
_CLI_PASSWORD_RE = re.compile(
    r"(?P<prefix>--(?:password|pass|passwd|token|api-key)=)(?P<value>[^\s]+)",
    re.IGNORECASE,
)
_CLI_ACCOUNT_RE = re.compile(
    r"(?P<prefix>--(?:username|user|email|docker-username|docker-email)=)(?P<value>[^\s]+)",
    re.IGNORECASE,
)
_FROM_LITERAL_SECRET_RE = re.compile(
    r"(?P<prefix>--from-literal=(?:[^=\s]*(?:PASSWORD|PASSWD|PASS|SECRET|TOKEN|API_KEY))=)"
    r"(?P<value>[^\s]+)",
    re.IGNORECASE,
)
_FROM_LITERAL_ACCOUNT_RE = re.compile(
    r"(?P<prefix>--from-literal=(?:[^=\s]*(?:USERNAME|USER|EMAIL|ACCOUNT))=)"
    r"(?P<value>[^\s]+)",
    re.IGNORECASE,
)


@dataclass
class SanitizeResult:
    text: str
    counts: dict[str, int]


class TextSanitizer:
    """민감한 값만 치환하고 개념어는 남긴다."""

    def sanitize(self, text: str) -> SanitizeResult:
        counts: Counter[str] = Counter()

        def replace_email(match: re.Match[str]) -> str:
            counts["email"] += 1
            return "[REDACTED_EMAIL]"

        def replace_private_url(match: re.Match[str]) -> str:
            counts["internal_url"] += 1
            return "[REDACTED_INTERNAL_URL]"

        def replace_private_ip(match: re.Match[str]) -> str:
            counts["private_ip"] += 1
            return "[REDACTED_PRIVATE_IP]"

        def replace_internal_host(match: re.Match[str]) -> str:
            counts["internal_host"] += 1
            return "[REDACTED_INTERNAL_HOST]"

        def replace_secret_value(match: re.Match[str]) -> str:
            counts["secret_value"] += 1
            return f"{match.group('prefix')}{match.group('quote')}[REDACTED_SECRET]{match.group('quote')}"

        def replace_account_value(match: re.Match[str]) -> str:
            counts["account_value"] += 1
            return f"{match.group('prefix')}{match.group('quote')}[REDACTED_ACCOUNT]{match.group('quote')}"

        def replace_cli_secret(match: re.Match[str]) -> str:
            counts["secret_value"] += 1
            return f"{match.group('prefix')}[REDACTED_SECRET]"

        def replace_cli_account(match: re.Match[str]) -> str:
            counts["account_value"] += 1
            return f"{match.group('prefix')}[REDACTED_ACCOUNT]"

        text = _PRIVATE_URL_RE.sub(replace_private_url, text)
        text = _EMAIL_RE.sub(replace_email, text)
        text = _SECRET_KEY_VALUE_RE.sub(replace_secret_value, text)
        text = _ACCOUNT_KEY_VALUE_RE.sub(replace_account_value, text)
        text = _CLI_PASSWORD_RE.sub(replace_cli_secret, text)
        text = _CLI_ACCOUNT_RE.sub(replace_cli_account, text)
        text = _FROM_LITERAL_SECRET_RE.sub(replace_cli_secret, text)
        text = _FROM_LITERAL_ACCOUNT_RE.sub(replace_cli_account, text)
        text = _INTERNAL_HOST_RE.sub(replace_internal_host, text)
        text = _PRIVATE_IP_RE.sub(replace_private_ip, text)

        return SanitizeResult(text=text, counts=dict(counts))
