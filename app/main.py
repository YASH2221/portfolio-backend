"""
Portfolio Backend — FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import init_db, async_session
from app.models.models import Project, Skill, Journey
from app.api import projects, skills, journey, chat, contact


async def seed_data():
    """Seed the database with Yash's portfolio data if empty."""
    async with async_session() as db:
        # Check if data needs updating (count mismatch = reseed needed)
        result = await db.execute(select(func.count()).select_from(Project))
        project_count = result.scalar()
        
        skill_result = await db.execute(select(func.count()).select_from(Skill))
        skill_count = skill_result.scalar()

        if project_count == 8 and skill_count >= 70:
            return  # Already has correct data

        # Clear old data if exists (reseed with updated content)
        if project_count > 0:
            from sqlalchemy import delete
            await db.execute(delete(Project))
            await db.execute(delete(Skill))
            await db.execute(delete(Journey))
            await db.commit()

        # ─── Projects ───
        projects_data = [
            Project(
                title="KOMAL Portal — Enterprise ERP & WMS",
                slug="komal-portal",
                short_description="Comprehensive ERP & Warehouse Management System — a digital transformation initiative replacing manual operations.",
                full_description="KOMAL (Katyayani Organics Manufacturing And Logistics) Portal is a sophisticated ERP/WMS solution featuring Inventory & Warehouse Management, Production Control (BOM), Quality Assurance, Purchase & Sales Management, Logistics & Dispatch, and configurable multi-level Approval Workflows.",
                problem_statement="Katyayani Organics relied on spreadsheets and manual operations to manage their entire supply chain across multiple warehouses, leading to inventory discrepancies, data entry errors, and operational inefficiency.",
                challenges="Designing microservices handling real-time inventory sync across 5+ locations. Implementing BOM for production control with multi-level approvals. Integrating QR tracking, DWS scanning, and rate calculation engines. Reduced manual data entry errors by 85%.",
                tech_stack=["Python", "FastAPI", "PostgreSQL", "MongoDB", "Redis", "Celery", "React", "Remix", "Tailwind CSS", "Socket.io", "AG Grid", "Docker", "AWS S3"],
                category="enterprise",
                live_url=None,
                featured=True,
                display_order=1
            ),
            Project(
                title="Shortly.io — AI Content Platform",
                slug="shortly-io",
                short_description="AI-Powered Content Generator: Text-to-Image, Audio & Video using OpenAI APIs.",
                full_description="An AI-powered content creation platform supporting text-to-image (DALL-E), text-to-audio (TTS), and text-to-video generation (FFmpeg). Built to transform text into dynamic media with a seamless user experience.",
                problem_statement="Content creators needed a unified platform to generate multiple media formats from simple text prompts without switching between different tools.",
                challenges="Handling large media file processing with FFmpeg on the server, managing async generation queues, and optimizing OpenAI API usage for cost efficiency.",
                tech_stack=["Next.js", "Node.js", "OpenAI API", "FFmpeg", "GPT", "DALL-E", "TTS"],
                category="ai_ml",
                live_url="https://shorts-ai-olive.vercel.app/",
                featured=True,
                display_order=2
            ),
            Project(
                title="Silextech CLM — Legal Document Management",
                slug="silextech",
                short_description="Microsoft Word Add-In for legal document management with AI-powered clause extraction. Published on Microsoft Marketplace.",
                full_description="Silex CLM integrates legal document management into Microsoft Word. Features clause library with version control, template management (NDA, Service Agreements), real-time collaboration, AI-powered clause extraction and risk identification, and compliance verification.",
                problem_statement="Legal professionals needed an integrated tool within Microsoft Word to manage clauses, templates, and collaborate on legal documents without leaving their workflow.",
                challenges="Navigating Office.js SDK limitations, building AI-powered clause extraction and risk identification, and passing Microsoft's strict marketplace review process.",
                tech_stack=["React.js", "Office.js", "Next.js", "PostgreSQL", "Microsoft Azure"],
                category="web",
                featured=True,
                display_order=3
            ),
            Project(
                title="Soulpizza — E-commerce Platform",
                slug="soulpizza",
                short_description="Multi-panel food ordering system with real-time WebSocket updates and automated invoice printing.",
                full_description="A complete food ordering ecosystem with three panels: User (ordering), Admin (management), and Store (order processing). Features real-time WebSocket communication and Electron-based automated invoice printing.",
                problem_statement="A pizza chain needed a unified system connecting customers, store staff, and administrators with real-time order tracking and automated printing.",
                challenges="Synchronizing real-time order states across three different panels using WebSockets, and integrating Electron for automated thermal printer invoice generation.",
                tech_stack=["React.js", "WebSockets", "Electron", "Node.js", "DigitalOcean"],
                category="web",
                featured=True,
                display_order=4
            ),
            Project(
                title="TDI Suite — Enterprise Mobile Apps",
                slug="tdi-suite",
                short_description="Suite of 4 enterprise apps: Timesheet, Member Dashboard, Data Entry (NFC), and Backend services.",
                full_description="Built a suite of productivity apps for Team Duurzaam Installatietechniek: Timesheet management (Ionic/Angular + Odoo ERP + Firebase), Member dashboard with progress charts and leave requests (Kotlin), Data Entry with NFC Tag Reader (Kotlin), and a Node.js backend with role-based access control and dynamic route resolution.",
                problem_statement="Enterprise workers needed mobile solutions for time tracking and field data entry that worked both online and offline, with hardware integrations like NFC.",
                challenges="Building cross-platform hybrid apps that seamlessly integrate with native hardware (NFC readers), sync with Odoo ERP, and work reliably in offline-first scenarios.",
                tech_stack=["Ionic", "Angular", "Kotlin", "Android", "NFC", "AWS S3", "Firebase", "Odoo ERP", "Node.js", "MongoDB"],
                category="mobile",
                featured=False,
                display_order=5
            ),
            Project(
                title="Consillion — Analytics Platform",
                slug="consillion",
                short_description="Dynamic reporting admin platform generating charts from large datasets with tree-structured data.",
                full_description="Dynamic reporting platform handling large datasets with hierarchical tree-structured data organization. Features nested/advanced filters and OIDC-based token management for enterprise SSO.",
                problem_statement="Businesses needed a flexible analytics dashboard that could handle complex, hierarchically organized datasets with enterprise-grade authentication.",
                challenges="Rendering and navigating deeply nested tree-structured data efficiently with Angular Material, and implementing OIDC refresh token management.",
                tech_stack=["Angular", "RxJS", "Material UI", "Node.js", "Express", "OIDC"],
                category="web",
                featured=False,
                display_order=6
            ),
            Project(
                title="Scraper Suite — Automation Tools",
                slug="scraper-suite",
                short_description="Web scraping applications and Python automation scripts with Odoo ERP integration.",
                full_description="Built multiple scraping tools: an Angular/Ionic hybrid app displaying scraped orders with color-coded validation cards, Python scripts for scraping orders to Excel/Odoo ERP using BeautifulSoup, and a Flask backend with MongoDB clusters and token-based authentication.",
                problem_statement="The company needed automated tools to extract live web order data, validate it, and sync it with their Odoo ERP system without manual intervention.",
                challenges="Building reliable web scrapers that handle dynamic web content, implementing generic helper methods and middleware patterns, and automating the entire pipeline with .bat scripts.",
                tech_stack=["Python", "Flask", "Angular", "Ionic", "MongoDB", "Odoo ERP", "BeautifulSoup"],
                category="web",
                featured=False,
                display_order=7
            ),
            Project(
                title="Codewise Infotech — Corporate Website",
                slug="codewise-website",
                short_description="Corporate website and Admin Dashboard with React, Redux, and MUI component library.",
                full_description="Built the official Codewise Infotech corporate website and its admin dashboard. Also developed Assignment-hub (Mapbox integration), Yuzee (Quickblox communication), and multiple real estate platforms.",
                problem_statement="Codewise Infotech needed a modern corporate web presence and internal admin tools to manage their business operations.",
                challenges="Implementing complex form handling with Formik/Yup validation, managing application state with Redux-Saga, and building a scalable component architecture with Material UI.",
                tech_stack=["React.js", "Redux", "Redux-Saga", "MUI", "Formik", "Yup"],
                category="web",
                live_url="https://codewiseinfotech.com/",
                featured=False,
                display_order=8
            ),
        ]

        # ─── Skills ───
        skills_data = [
            # Languages
            Skill(name="JavaScript", category="languages", proficiency=95, years_experience=4.5, icon_name="code-2", display_order=1),
            Skill(name="TypeScript", category="languages", proficiency=90, years_experience=3.0, icon_name="file-code", display_order=2),
            Skill(name="Python", category="languages", proficiency=88, years_experience=3.0, icon_name="terminal", display_order=3),
            Skill(name="Kotlin", category="languages", proficiency=70, years_experience=1.5, icon_name="smartphone", display_order=4),
            # Frontend
            Skill(name="React.js", category="frontend", proficiency=95, years_experience=4.0, icon_name="layout", display_order=1),
            Skill(name="Next.js", category="frontend", proficiency=88, years_experience=2.5, icon_name="globe", display_order=2),
            Skill(name="Angular", category="frontend", proficiency=85, years_experience=3.0, icon_name="compass", display_order=3),
            Skill(name="Remix", category="frontend", proficiency=80, years_experience=1.0, icon_name="zap", display_order=4),
            Skill(name="Tailwind CSS", category="frontend", proficiency=90, years_experience=2.5, icon_name="palette", display_order=5),
            Skill(name="HTML5/CSS3", category="frontend", proficiency=95, years_experience=4.5, icon_name="code", display_order=6),
            # Backend
            Skill(name="Node.js", category="backend", proficiency=92, years_experience=4.0, icon_name="server", display_order=1),
            Skill(name="Express.js", category="backend", proficiency=90, years_experience=4.0, icon_name="route", display_order=2),
            Skill(name="FastAPI", category="backend", proficiency=88, years_experience=2.0, icon_name="zap", display_order=3),
            Skill(name="Flask", category="backend", proficiency=78, years_experience=2.0, icon_name="flask-conical", display_order=4),
            # Database
            Skill(name="PostgreSQL", category="database", proficiency=88, years_experience=3.0, icon_name="database", display_order=1),
            Skill(name="MongoDB", category="database", proficiency=90, years_experience=4.0, icon_name="leaf", display_order=2),
            Skill(name="Redis", category="database", proficiency=80, years_experience=2.0, icon_name="hard-drive", display_order=3),
            Skill(name="Firebase", category="database", proficiency=82, years_experience=3.0, icon_name="flame", display_order=4),
            # Cloud & DevOps
            Skill(name="AWS", category="cloud", proficiency=82, years_experience=3.0, icon_name="cloud", display_order=1),
            Skill(name="GCP", category="cloud", proficiency=78, years_experience=2.0, icon_name="cloud", display_order=2),
            Skill(name="Azure", category="cloud", proficiency=75, years_experience=1.5, icon_name="cloud", display_order=3),
            Skill(name="Docker", category="cloud", proficiency=85, years_experience=2.5, icon_name="container", display_order=4),
            Skill(name="GitHub Actions", category="cloud", proficiency=82, years_experience=2.0, icon_name="git-branch", display_order=5),
            # AI/ML
            Skill(name="OpenAI APIs", category="ai_ml", proficiency=88, years_experience=2.0, icon_name="brain", display_order=1),
            Skill(name="LLM Engineering", category="ai_ml", proficiency=85, years_experience=1.5, icon_name="cpu", display_order=2),
            Skill(name="GenAI", category="ai_ml", proficiency=82, years_experience=1.5, icon_name="sparkles", display_order=3),
            
            # Additional Skills from LinkedIn
            Skill(name="MCP (Multi Agent Protocol)", category="ai_ml", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="REST APIs", category="backend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="WebSocket", category="backend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="AG Grid", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Delhivery API's", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Shiprocket API's", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Zoho Books", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Apache Drill", category="database", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Ffmpeg", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="GCP VM", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Microsoft Power BI", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="AWS Lambda", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="DigitalOcean", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Office Js", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Prisma ORM", category="database", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Microsoft Azure", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Google API Services", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Appium", category="mobile", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="CI/CD", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="RxJS", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="MUI", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Redux.js", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Saga", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Yup", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Formik", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="JSON Web Token (JWT)", category="other", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Amazon S3", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="XML", category="languages", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="MVVM", category="other", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="NFC", category="mobile", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Web Scraping", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Twilio", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Chart.js", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="HTML", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="CSS", category="frontend", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Amazon EC2", category="cloud", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Android Development", category="mobile", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Ionic Framework", category="mobile", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Odoo", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Full-Stack Development", category="other", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Mean Stack", category="other", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="MERN Stack", category="other", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Git", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Jira", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Bitbucket", category="tools", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="SQL", category="languages", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
            Skill(name="Oracle Database", category="database", proficiency=80, years_experience=2.0, icon_name="check", display_order=10),
        ]

        # ─── Journey ───
        journey_data = [
            Journey(
                type="work",
                title="Team Lead & Full Stack Developer",
                organization="Katyayani Organics Pvt Ltd",
                location="Bhopal, Madhya Pradesh",
                start_date="Dec 2024",
                end_date=None,
                description="Leading the architecture and development of the KOMAL Portal (ERP & WMS), a comprehensive digital transformation initiative.",
                highlights=[
                    "Architect microservices backend with FastAPI + PostgreSQL + MongoDB + Redis",
                    "Build React/Remix SPAs with real-time inventory across 5+ warehouses",
                    "Design 7+ core modules: Inventory, Production, QA, Logistics, Approvals",
                    "Integrate Zoho CRM, Shiprocket, Delhivery + QR tracking"
                ],
                tech_used=["FastAPI", "React", "Remix", "PostgreSQL", "MongoDB", "Redis", "Socket.io"],
                icon_name="briefcase",
                display_order=1
            ),
            Journey(
                type="work",
                title="Senior Full Stack Developer",
                organization="Quazma Techno Solutions Pvt Ltd",
                location="Indore, Madhya Pradesh",
                start_date="May 2024",
                end_date="Oct 2024",
                description="Delivered three major products: an AI content platform, a Microsoft marketplace add-in, and a multi-panel e-commerce system.",
                highlights=[
                    "Shortly.io: AI platform for text-to-image/audio/video with OpenAI APIs",
                    "Silextech: Legal doc management MS Word Add-In, deployed to MS Marketplace",
                    "Soulpizza: Multi-panel food ordering with WebSockets + Electron printing"
                ],
                tech_used=["Next.js", "React", "Node.js", "OpenAI", "Office.js", "WebSockets", "Electron"],
                icon_name="rocket",
                display_order=2
            ),
            Journey(
                type="work",
                title="Senior Full Stack Developer",
                organization="Codewise Infotech",
                location="Indore, Madhya Pradesh",
                start_date="Feb 2022",
                end_date="Apr 2024",
                description="Built enterprise applications spanning analytics, mobile productivity, and real-estate platforms.",
                highlights=[
                    "Consillion: Dynamic reporting platform with tree-structured data + OIDC auth",
                    "TDI Suite: Hybrid + native Android apps with NFC, AWS S3, Firebase, Odoo",
                    "Automation & scraping systems with Python + Odoo APIs",
                    "Corporate & real estate platforms with React, Redux, Angular"
                ],
                tech_used=["Angular", "React", "Node.js", "Python", "Ionic", "Kotlin", "AWS"],
                icon_name="code",
                display_order=3
            ),
            Journey(
                type="education",
                title="MBA — IT & Marketing",
                organization="Modern Institute of Professional Studies",
                location="Indore, Madhya Pradesh",
                start_date="2020",
                end_date="2022",
                description="Master of Business Administration specializing in Information Technology and Marketing, combining technical expertise with business acumen.",
                highlights=[
                    "IT & Marketing specialization",
                    "Strong foundation in business strategy and technology management"
                ],
                tech_used=[],
                icon_name="graduation-cap",
                display_order=4
            ),
            Journey(
                type="education",
                title="B.Com — Computer Application",
                organization="SJHSGICCS",
                location="Indore, Madhya Pradesh",
                start_date="2018",
                end_date="2020",
                description="Bachelor of Commerce with Computer Application, building the foundational programming and business skills.",
                highlights=[
                    "Computer Application specialization",
                    "Foundation in programming and commerce"
                ],
                tech_used=[],
                icon_name="book-open",
                display_order=5
            ),
        ]

        db.add_all(projects_data)
        db.add_all(skills_data)
        db.add_all(journey_data)
        await db.commit()
        print("[OK] Database seeded successfully!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB and seed data on startup."""
    await init_db()
    await seed_data()
    yield


app = FastAPI(
    title="Yash Patidar — Portfolio API",
    description="Backend API for Yash Patidar's developer portfolio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(journey.router)
app.include_router(chat.router)
app.include_router(contact.router)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/profile")
async def get_profile():
    """Return Yash's profile information."""
    return {
        "name": "Yash Patidar",
        "title": "Senior Full Stack Developer",
        "tagline": "Building scalable solutions with modern tech",
        "bio": "Results-driven Software Engineer with 4+ years of experience in full-stack development, specializing in web applications, mobile apps, and cloud-based solutions. Proven expertise in MEAN/MERN stacks, Python (FastAPI/Flask), and mobile development. Strong background in microservices architecture, AI integration, and end-to-end cloud deployment.",
        "location": "Indore, MP, India",
        "email": "yashpatidar2203@gmail.com",
        "phone": "+91 6260859544",
        "linkedin": "https://linkedin.com/in/yash-patidar-288412230",
        "github": "https://github.com/yashpatidar",
        "rotating_titles": [
            "Senior Full Stack Developer",
            "AI/ML Engineer",
            "Team Lead",
            "Cloud Architect",
            "Problem Solver"
        ],
        "years_experience": 4,
        "projects_delivered": 15,
        "technologies_used": 30,
    }
