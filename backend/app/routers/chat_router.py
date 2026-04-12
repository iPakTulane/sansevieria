from fastapi import APIRouter, HTTPException, status

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import (
    generate_chat_response,
    ChatServiceError,
)
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger("CHAT_API")


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        result = generate_chat_response(payload.message)
        return ChatResponse(
            response=result.response,
            provider=result.provider,
            model=result.model,
        )
    except ChatServiceError as e:
        logger.warning(
            "chat",
            "chat_endpoint",
            "Chat request failed",
            status_code=e.status_code,
            detail=e.detail,
        )
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except Exception as e:
        logger.error(
            "chat",
            "chat_endpoint",
            "Unexpected chat endpoint error",
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected chat processing error",
        )
