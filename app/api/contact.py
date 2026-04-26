from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.models import ContactMessage
from app.schemas.schemas import ContactRequest, ContactResponse

router = APIRouter(prefix="/api/contact", tags=["Contact"])


@router.post("/", response_model=ContactResponse)
async def send_message(request: ContactRequest, db: AsyncSession = Depends(get_db)):
    msg = ContactMessage(
        name=request.name,
        email=request.email,
        message=request.message
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return ContactResponse(id=msg.id)
