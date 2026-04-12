from __future__ import annotations

from dataclasses import dataclass
import requests

from app.config import settings
from app.utils.logger import get_logger


logger = get_logger("LM_STUDIO")


class ChatServiceError(Exception):
    def __init__(self, detail: str, status_code: int = 503):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class LMStudioUnavailableError(ChatServiceError):
    pass


class LMStudioBadResponseError(ChatServiceError):
    pass


class ChatValidationError(ChatServiceError):
    pass


@dataclass
class ChatResult:
    response: str
    provider: str
    model: str | None = None


def _extract_error_detail(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return "LM Studio returned an unexpected error payload"
    err = payload.get("error")
    if isinstance(err, dict):
        return str(err.get("message") or "LM Studio error")
    if isinstance(err, str):
        return err
    return str(payload.get("message") or "LM Studio request failed")


def _extract_assistant_content(payload: dict) -> tuple[str, str | None]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LMStudioBadResponseError("LM Studio returned no chat choices", status_code=502)

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise LMStudioBadResponseError("LM Studio returned malformed chat message", status_code=502)

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise LMStudioBadResponseError("LM Studio returned empty assistant content", status_code=502)

    model = payload.get("model")
    return content.strip(), (model if isinstance(model, str) else None)


def _normalize_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(messages, list):
        raise ChatValidationError("messages must be a list", status_code=400)

    normalized: list[dict[str, str]] = []

    for item in messages:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"}:
            continue
        if not isinstance(content, str):
            continue

        cleaned = content.strip()
        if not cleaned:
            continue

        normalized.append({"role": role, "content": cleaned})

    if not normalized:
        raise ChatValidationError("No valid messages were provided", status_code=400)
    if not any(item["role"] == "user" for item in normalized):
        raise ChatValidationError("At least one user message is required", status_code=400)

    system_message = {"role": "system", "content": settings.CHATBOT_SYSTEM_PROMPT}
    conversation = normalized
    conversation = conversation[-8:]  # Keep only the most recent lightweight context window.

    return [system_message, *conversation]


def generate_chat_response(messages: list[dict[str, str]]) -> ChatResult:
    prepared_messages = _normalize_messages(messages)

    body = {
        "model": settings.LM_STUDIO_MODEL,
        "messages": prepared_messages,
        "temperature": 0.4,
    }
    url = settings.lm_studio_chat_url

    try:
        response = requests.post(url, json=body, timeout=settings.LM_STUDIO_TIMEOUT)
    except requests.exceptions.Timeout:
        logger.error("chat", "lm_studio", "LM Studio request timed out", url=url, timeout=settings.LM_STUDIO_TIMEOUT)
        raise LMStudioUnavailableError("LM Studio request timed out", status_code=504)
    except requests.exceptions.ConnectionError:
        logger.error("chat", "lm_studio", "LM Studio connection failed", url=url)
        raise LMStudioUnavailableError(
            "LM Studio is unreachable. Ensure the local server is running on the configured URL.",
            status_code=503,
        )
    except requests.RequestException as e:
        logger.error("chat", "lm_studio", "LM Studio request failed", url=url, error=str(e))
        raise LMStudioUnavailableError("Failed to reach LM Studio", status_code=503)

    payload = None
    try:
        payload = response.json()
    except ValueError:
        if not response.ok:
            logger.error(
                "chat",
                "lm_studio",
                "LM Studio returned non-JSON error",
                status_code=response.status_code,
                response_preview=(response.text or "")[:160],
            )
            raise LMStudioBadResponseError("LM Studio returned a non-JSON error response", status_code=502)
        logger.error("chat", "lm_studio", "LM Studio returned non-JSON success", status_code=response.status_code)
        raise LMStudioBadResponseError("LM Studio returned a non-JSON response", status_code=502)

    if not response.ok:
        detail = _extract_error_detail(payload)
        logger.warning(
            "chat",
            "lm_studio",
            "LM Studio returned request error",
            status_code=response.status_code,
            detail=detail,
        )
        if response.status_code in (400, 404, 422):
            raise LMStudioUnavailableError(
                f"LM Studio could not process the chat request. {detail}",
                status_code=503,
            )
        raise LMStudioBadResponseError(f"LM Studio returned an error: {detail}", status_code=502)

    answer, model = _extract_assistant_content(payload)
    return ChatResult(response=answer, provider="lm_studio", model=model or settings.LM_STUDIO_MODEL)
