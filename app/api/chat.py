from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from app.core.database import get_db
from app.models.models import ChatSession, ChatMessage
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.chat_service import generate_chat_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Fetch chat history for context
    history = []
    if request.session_id:
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        messages = result.scalars().all()
        history = [{"role": m.role, "content": m.content} for m in messages]
    
    # Generate response
    reply, was_cached = await generate_chat_response(request.message, history)
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.message,
        cached_response=False
    )
    db.add(user_msg)
    
    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=reply,
        cached_response=was_cached
    )
    db.add(assistant_msg)
    
    # Update or create session
    existing = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = existing.scalar_one_or_none()
    if not session:
        session = ChatSession(id=session_id, message_count=1)
        db.add(session)
    else:
        session.message_count += 1
    
    await db.commit()
    
    return ChatResponse(reply=reply, session_id=session_id, cached=was_cached)
