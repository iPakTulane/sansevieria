from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import (
    generate_chat_response,
    ChatServiceError,
)
from app.routers.auth_router import get_current_user
from app.models.user import User
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger("CHAT_API")


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        result = generate_chat_response(payload.to_message_dicts())
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
            user_id=current_user.id,
            user_email=current_user.email,
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
            user_id=current_user.id,
            user_email=current_user.email,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected chat processing error",
        )
