from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Skill
from app.schemas.schemas import SkillResponse

router = APIRouter(prefix="/api/skills", tags=["Skills"])


@router.get("/", response_model=List[SkillResponse])
async def get_skills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).order_by(Skill.category, Skill.display_order))
    return result.scalars().all()
