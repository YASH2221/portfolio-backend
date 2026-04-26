from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.models import ContactMessage
from app.schemas.schemas import ContactRequest, ContactResponse
from app.services.email_service import send_contact_email

router = APIRouter(prefix="/api/contact", tags=["Contact"])


@router.post("/", response_model=ContactResponse)
async def send_message(
    request: ContactRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    msg = ContactMessage(
        name=request.name,
        email=request.email,
        message=request.message
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    
    # Send email in background so the API responds instantly
    background_tasks.add_task(
        send_contact_email,
        name=request.name,
        email=request.email,
        message=request.message
    )
    
    return ContactResponse(id=msg.id)
