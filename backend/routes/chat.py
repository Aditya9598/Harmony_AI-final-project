from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse
from services.chat_service import generate_chat_response


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        response, provider = await generate_chat_response(payload.message)
        return ChatResponse(response=response, provider=provider)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat service error: {exc}") from exc
