from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── Projects ───
class ProjectBase(BaseModel):
    title: str
    slug: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    problem_statement: Optional[str] = None
    challenges: Optional[str] = None
    tech_stack: Optional[List[str]] = []
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    screenshots: Optional[List[str]] = []
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    featured: Optional[bool] = False
    display_order: Optional[int] = 0

class ProjectResponse(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Skills ───
class SkillBase(BaseModel):
    name: str
    category: str
    proficiency: Optional[int] = 50
    years_experience: Optional[float] = 0
    icon_name: Optional[str] = None
    display_order: Optional[int] = 0

class SkillResponse(SkillBase):
    id: int

    class Config:
        from_attributes = True


# ─── Journey ───
class JourneyBase(BaseModel):
    type: str
    title: str
    organization: Optional[str] = None
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[List[str]] = []
    tech_used: Optional[List[str]] = []
    icon_name: Optional[str] = None
    display_order: Optional[int] = 0

class JourneyResponse(JourneyBase):
    id: int

    class Config:
        from_attributes = True


# ─── Chat ───
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    cached: bool = False

class ChatHistoryItem(BaseModel):
    role: str
    content: str
    created_at: Optional[datetime] = None


# ─── Contact ───
class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

class ContactResponse(BaseModel):
    id: int
    success: bool = True
    message: str = "Message sent successfully!"


# ─── Analytics ───
class PageViewRequest(BaseModel):
    page: str
    referrer: Optional[str] = None
