from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Journey
from app.schemas.schemas import JourneyResponse

router = APIRouter(prefix="/api/journey", tags=["Journey"])


@router.get("/", response_model=List[JourneyResponse])
async def get_journey(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Journey).order_by(Journey.display_order))
    return result.scalars().all()
