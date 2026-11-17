"""
User-facing translation error messages keyed by error code × UI language.

Error code table (maps to i18n key in TRANSLATIONS[lang]):
| Code          | i18n key              | When raised |
|---------------|-----------------------|-------------|
| TIMEOUT       | trans_err_timeout     | HTTP request exceeds timeout (12s default) |
| NETWORK       | trans_err_network     | ConnectionError, DNS, TLS, broken pipe |
| HTTP_400      | trans_err_400         | Bad request / invalid payload |
| HTTP_401      | trans_err_401         | Invalid or missing API key |
| HTTP_403      | trans_err_403         | Key forbidden or quota policy |
| HTTP_429      | trans_err_429         | Rate limited |
| HTTP_500      | trans_err_500         | Server error |
| HTTP_503      | trans_err_503         | Service unavailable |
| HTTP_OTHER    | trans_err_http_other  | Other HTTP status |
| BLOCKED       | trans_err_blocked     | Content safety / filter |
| NO_API_KEY    | trans_err_no_api_key  | Provider selected but key empty |
| PARSE         | trans_err_parse       | Unexpected API response shape |
| GENERIC       | trans_err_generic     | Fallback |
"""

from __future__ import annotations

import re
from typing import Any

from ui.i18n import TRANSLATIONS

ERROR_CODE_I18N_KEY: dict[str, str] = {
    "TIMEOUT": "trans_err_timeout",
    "NETWORK": "trans_err_network",
    "HTTP_400": "trans_err_400",
    "HTTP_401": "trans_err_401",
    "HTTP_403": "trans_err_403",
    "HTTP_429": "trans_err_429",
    "HTTP_500": "trans_err_500",
    "HTTP_503": "trans_err_503",
    "HTTP_OTHER": "trans_err_http_other",
    "BLOCKED": "trans_err_blocked",
    "NO_API_KEY": "trans_err_no_api_key",
    "PARSE": "trans_err_parse",
    "GENERIC": "trans_err_generic",
}

_HTTP_STATUS_RE = re.compile(r"\b(?:status\s*code\s*|=)?\s*(\d{3})\b", re.IGNORECASE)


def infer_error_code(exc: BaseException) -> str:
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code:
        return code
    text = str(exc).lower()
    if "timeout" in text or "timed out" in text:
        return "TIMEOUT"
    if "network error" in text or "connection" in text:
        return "NETWORK"
    if "api key" in text and ("not configured" in text or "missing" in text):
        return "NO_API_KEY"
    if "blocked" in text or "refused" in text or "safety" in text or "content_filter" in text:
        return "BLOCKED"
    if "unexpected" in text and "response" in text:
        return "PARSE"
    if "429" in text:
        return "HTTP_429"
    if "403" in text:
        return "HTTP_403"
    if "401" in text:
        return "HTTP_401"
    if "503" in text:
        return "HTTP_503"
    if "500" in text or "502" in text or "504" in text:
        return "HTTP_500"
    m = _HTTP_STATUS_RE.search(str(exc))
    if m:
        status = int(m.group(1))
        if status == 400:
            return "HTTP_400"
        if status == 401:
            return "HTTP_401"
        if status == 403:
            return "HTTP_403"
        if status == 429:
            return "HTTP_429"
        if status == 500:
            return "HTTP_500"
        if status == 503:
            return "HTTP_503"
        return "HTTP_OTHER"
    return "GENERIC"


def user_message_for_translation_error(exc: BaseException, ui_lang: str) -> str:
    """Return a short message for the popup, in the user's UI language."""
    code = infer_error_code(exc)
    msgs: dict[str, Any] = TRANSLATIONS.get(ui_lang, TRANSLATIONS["en"])
    key = ERROR_CODE_I18N_KEY.get(code, ERROR_CODE_I18N_KEY["GENERIC"])
    template = msgs.get(key) or TRANSLATIONS["en"].get(key, ERROR_CODE_I18N_KEY["GENERIC"])
    status = None
    if code == "HTTP_OTHER":
        m = _HTTP_STATUS_RE.search(str(exc))
        if m:
            status = m.group(1)
    if status and "{status}" in template:
        return template.format(status=status)
    if "{status}" in template:
        return template.format(status="?")
    return template


def format_translation_error_title(exc: BaseException, ui_lang: str) -> str:
    """Wrap user message with the standard translation error title."""
    msgs = TRANSLATIONS.get(ui_lang, TRANSLATIONS["en"])
    body = user_message_for_translation_error(exc, ui_lang)
    return msgs.get("err_trans_title", "Translation Error: {}").format(body)