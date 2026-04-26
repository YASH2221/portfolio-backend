from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.models import Project
from app.schemas.schemas import ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Project).order_by(Project.display_order, Project.id)
    if category:
        query = query.where(Project.category == category)
    if featured is not None:
        query = query.where(Project.featured == featured)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{slug}", response_model=ProjectResponse)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
