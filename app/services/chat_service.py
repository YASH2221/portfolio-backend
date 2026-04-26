"""
Gemini AI Chat Service with multi-tier caching for token optimization.

Cache Strategy:
  Layer 1: FAQ cache — pre-computed answers for common questions (0 API calls)
  Layer 2: Response cache — LRU cache for recent unique queries (0 API calls)
  Layer 3: Gemini API call with sliding window (last 5 messages)
"""

from google import genai
from google.genai import types
from app.core.config import settings
from typing import Optional, Dict, List
import hashlib
import time
import re
import asyncio
from collections import OrderedDict

# Configure Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ─── Portfolio Context (compact, ~400 tokens) ───
PORTFOLIO_CONTEXT = """You are Yash Patidar's portfolio AI assistant. You help visitors learn about Yash.

ABOUT YASH:
- Senior Full Stack Developer, 4+ years experience
- Location: Indore, MP, India
- Email: yashpatidar2203@gmail.com
- LinkedIn: linkedin.com/in/yash-patidar-288412230

SKILLS:
- Languages: JavaScript, TypeScript, Python, Kotlin
- Backend: Node.js, Express.js, FastAPI, Flask
- Frontend: Angular, React.js, Next.js, Remix, HTML5, CSS3, Tailwind, Material UI
- Mobile: Ionic (Angular), Cordova, Capacitor, Android (Kotlin)
- Databases: MongoDB, PostgreSQL, Redis, Firebase
- Cloud: GCP, AWS (EC2, S3), Azure, DigitalOcean, Docker, GitHub Actions
- AI/ML: OpenAI APIs (GPT, DALL-E, TTS), LLM Engineering, GenAI

EXPERIENCE:
1. Katyayani Organics (Dec 2024-Present) - Team Lead & Full Stack Dev
   - KOMAL Portal ERP & WMS system, microservices with FastAPI+PostgreSQL+MongoDB+Redis
   - React/Remix frontends, 7+ modules, real-time inventory across 5+ warehouses
   - Integrated Zoho CRM, Shiprocket, Delhivery, QR code tracking, automated reordering

2. Quazma Techno Solutions (May-Oct 2024) - Senior Full Stack Dev
   - Shortly.io: AI content platform (text-to-image/audio/video) with Next.js+OpenAI+FFmpeg
   - Silextech: Legal doc management MS Word Add-In, deployed to Microsoft Marketplace
   - Soulpizza: Multi-panel food ordering system with WebSockets+Electron invoice printing

3. Codewise Infotech (Feb 2022-Apr 2024) - Senior Full Stack Dev
   - Consillion: Analytics platform with Angular Material UI + OIDC auth
   - TDI Suite: Hybrid+native apps with Ionic/Kotlin, NFC, AWS, Firebase, Odoo
   - Automation & scraping systems with Python (Odoo APIs, BeautifulSoup)
   - Corporate & real estate platforms with React/Redux/Angular

EDUCATION:
- MBA (IT & Marketing) - Modern Institute of Professional Studies, 2020-2022
- B.Com (Computer Application) - SJHSGICCS, 2018-2020

RULES:
- Keep answers concise (2-4 sentences max)
- Only answer questions about Yash's professional profile, skills, projects, experience
- If asked unrelated questions, politely redirect to portfolio topics
- Be friendly and professional
- If asked to contact, share email and LinkedIn
- When asked about a specific project, give detailed info about THAT project only
"""

# ─── Project-specific FAQ entries (detailed, for specific project questions) ───
PROJECT_DETAILS: Dict[str, str] = {
    "komal": "**KOMAL Portal** (Katyayani Organics Manufacturing And Logistics) is Yash's current flagship project as **Team Lead & System Architect** at Katyayani Organics (Dec 2024 - Present).\n\n**What it does:** A comprehensive ERP & WMS replacing manual operations with an integrated digital solution.\n\n**Key Modules:**\n- Inventory & Warehouse Management (real-time stock, bin management, multi-store)\n- Production Control (BOM, work orders, planning, routing)\n- Quality Assurance (QC inspections, compliance, quality reporting)\n- Purchase & Sales Management (end-to-end order/procurement)\n- Logistics & Dispatch (driver management, route planning, shipment tracking, manifests)\n- Approval Workflows (configurable multi-level approvals)\n\n**Tech Stack:** FastAPI, PostgreSQL, MongoDB, Redis, Celery, React/Remix, Tailwind CSS, AG Grid, Socket.io, Docker, AWS S3\n\n**Integrations:** Google Sheets API, Zoho CRM, Shiprocket, Delhivery, AWS S3\n\n**Impact:**\n- Reduced manual data entry errors by 85%\n- Real-time inventory across 5+ warehouse locations\n- Automated material requirement calculations\n- Optimized pick-pack-ship workflows\n- Digital audit trails for quality compliance",

    "shortly": "**Shortly.io** is an **AI-Powered Content Generator** Yash built at Quazma Techno Solutions (Jun 2024 - Present).\n\n**What it does:** Transforms text into dynamic media - images, audio, and video using AI.\n\n**Key Features:**\n- Text-to-Image: Generate visuals from prompts using DALL-E\n- Text-to-Audio: Convert text into natural-sounding speech via TTS\n- Text-to-Video: Create short videos automatically using AI + FFmpeg\n\n**Tech Stack:** Next.js (frontend), Node.js (backend), OpenAI APIs (GPT, DALL-E, TTS), FFmpeg\n\n**Live Demo:** [shorts-ai-olive.vercel.app](https://shorts-ai-olive.vercel.app/)\n\nThis was a deep dive into multimodal AI capabilities, performance optimization, and seamless UX.",

    "silextech": "**Silextech CLM Add-in** is a **legal document management system for Microsoft Word** built at Quazma (May 2024 - Present). Successfully published to the **Microsoft Marketplace**.\n\n**Key Features:**\n- **Clause Management:** Centralized clause library with version control, search, and metadata\n- **Template Management:** Machine-readable templates (NDA, Service Agreements), customization, and import\n- **Collaboration:** Real-time editing, commenting, change tracking, workflow approvals\n- **Compliance:** Automated compliance verification and legal guidance database\n- **AI Features:** Automated clause extraction, risky clause identification, missing element detection\n\n**Tech Stack:** React.js, Office.js, Next.js, PostgreSQL, Microsoft Azure\n\nPassed Microsoft's strict marketplace review process.",

    "soulpizza": "**Soulpizza** is a **multi-panel food ordering e-commerce system** with three panels: User (ordering), Admin (management), and Store (order processing).\n\n**Tech Stack:** React.js, WebSockets, Electron, Node.js, DigitalOcean\n\n**Features:**\n- Real-time order state sync across 3 panels via WebSockets\n- Automated thermal printer invoice generation via Electron\n- Complete ordering ecosystem from customer to kitchen",

    "tdi": "**TDI Suite** (Team Duurzaam Installatietechniek) is a collection of **enterprise productivity apps** Yash built at Codewise Infotech. It includes:\n\n**1. TDI Timesheet** - Task/timesheet management for employees & laborers\n- Built with Ionic/Angular, Odoo ERP, Firebase, Google Cloud Functions\n\n**2. TDI Member** - User dashboard showing assigned tasks, tools, progress charts, leave requests, help support\n- Built with Android Kotlin, Charts, ViewPager2, AWS S3\n\n**3. TDI Data Entry** - Native data entry app for firm members\n- Built with Android Kotlin, NFC Tag Reader, ViewPager2, AWS S3\n\n**4. TDI Backend** - Backend for Member & Data Entry apps\n- Node.js, Express, MongoDB, Amazon Pinpoint, Passport-JWT, Twilio\n- Role-based access control, dynamic route resolution",

    "consillion": "**Consillion** is a **dynamic reporting and analytics admin platform** Yash built at Codewise Infotech.\n\n**Tech Stack:** Angular, RxJS, Material UI, Node.js, OIDC\n\n**Features:**\n- Generates dynamic reports from large datasets as charts\n- Tree-structured data management with nested/advanced filters\n- OIDC-based token management and enterprise SSO",

    "scraper": "Yash built **two scraping projects** at Codewise Infotech:\n\n**1. Scraper App** - Angular hybrid app (Ionic framework) that scrapes orders from the web and displays them with multi-color validation cards and advanced filters.\n\n**2. Scraper Script** - Python dynamic scripts for scraping orders and writing to Excel files and Odoo ERP. Used Odoo APIs, BeautifulSoup, and .bat automation.\n\n**3. Backend Scraper** - Python Flask backend with MongoDB clusters, Odoo ERP integration, generic middlewares, token-based auth, and schema-based validators.",

    "codewise": "**Codewise Infotech Website** (codewiseinfotech.com) and **Admin Dashboard** - corporate website and admin panel Yash built at Codewise.\n\n**Tech Stack:** React.js, MUI, Formik, Yup, Redux, Redux-Saga\n\n**Also built:** Assignment-hub (Mapbox integration), Yuzee (Quickblox communication), and multiple real estate platforms.",
}

# ─── Generic projects question (only matches when no specific project is named) ───
GENERIC_PROJECTS_RESPONSE = "Yash has built 15+ projects across his career. Here are the highlights:\n\n**KOMAL Portal** - Enterprise ERP & WMS (FastAPI + React) [Current]\n**Shortly.io** - AI content generator (Next.js + OpenAI) [Live Demo](https://shorts-ai-olive.vercel.app/)\n**Silextech** - Legal doc management MS Word Add-In (Published on Microsoft Marketplace)\n**Soulpizza** - Multi-panel food ordering with WebSockets + Electron\n**TDI Suite** - 4 enterprise apps (Timesheet, Member, Data Entry, Backend)\n**Consillion** - Analytics platform with dynamic reporting\n**Scraper Suite** - Web scraping apps + Python automation scripts\n**Codewise Website** - Corporate site (codewiseinfotech.com)\n\nAsk me about any specific project for details!"

def check_specific_skill(message: str) -> Optional[str]:
    match = re.search(r"(?:experience|skills?|proficient) (?:in|with|for|on|using) ([a-zA-Z0-9.\-\+]+)", message.lower())
    if match:
        tech = match.group(1).strip()
        exp = {
            "react": "4+", "reactjs": "4+", "react.js": "4+",
            "angular": "3+", "node": "4+", "nodejs": "4+", "node.js": "4+",
            "python": "3+", "fastapi": "2+", "flask": "2+",
            "aws": "3+", "docker": "2.5+", "mongodb": "4+", "postgres": "3+",
            "postgresql": "3+", "javascript": "4.5+", "typescript": "3+",
            "ionic": "2.5+", "kotlin": "1.5+", "android": "2+", "nextjs": "2.5+", "next.js": "2.5+",
            "sql": "2+", "firebase": "3+", "gcp": "2+", "azure": "1.5+", "redis": "2+",
            "html": "4.5+", "css": "4.5+", "tailwind": "2.5+", "mui": "2+"
        }
        if tech in exp:
            return f"Yash has {exp[tech]} years of professional experience with {tech.title()}."
        else:
            return f"Yash has experience with {tech.title()} across various projects. You can check the Skills section of this portfolio for a complete breakdown!"
    return None

def check_projects_by_skill(message: str) -> Optional[str]:
    match = re.search(r"projects?.*(?:in|with|using|use)\s+([a-zA-Z0-9.\-\+]+)", message.lower())
    if match:
        tech = match.group(1).strip()
        matched_projects = []
        for key, detail in PROJECT_DETAILS.items():
            if tech.lower() in detail.lower():
                name_match = re.search(r"\*\*(.*?)\*\*", detail)
                if name_match:
                    matched_projects.append(name_match.group(1))
        
        if matched_projects:
            return f"Yash has used {tech.title()} in the following projects: **{', '.join(matched_projects)}**. Ask me about any of them for more details!"
        else:
            return f"I couldn't find specific portfolio projects highlighting {tech.title()}, but Yash has a broad tech stack. Check the Projects section for more details!"
    return None

# ─── FAQ Cache (zero API cost) ───
FAQ_PATTERNS: Dict[str, str] = {
    r"^(hi|hello|hey|greetings|yo|sup)\b": "Hey there! I'm Yash's portfolio AI assistant. I can tell you about his skills, projects, experience, or education. What would you like to know?",

    r"(who is yash|about yash|introduce yourself|who are you)": "Yash Patidar is a Senior Full Stack Developer with 4+ years of experience, currently leading development at Katyayani Organics. He specializes in React, FastAPI, Node.js, and has strong expertise in AI/ML with OpenAI APIs. He's built everything from enterprise ERP systems to AI content platforms!",

    r"(what are .* skills|list .* skills|tell me about .* skills|what tech|your stack|your technologies)": "Yash's tech stack spans the full spectrum:\n\n**Frontend:** React, Next.js, Angular, Remix, Tailwind CSS\n**Backend:** FastAPI, Node.js, Express, Flask\n**Mobile:** Ionic, Kotlin (Android)\n**Databases:** PostgreSQL, MongoDB, Redis, Firebase\n**Cloud:** AWS, GCP, Azure, Docker\n**AI/ML:** OpenAI APIs, LLM Engineering, GenAI",

    r"(what is .* experience|work history|career path|where have you worked|past roles|jobs)": "Yash has worked at 3 companies:\n\n**Katyayani Organics** (Dec 2024-Present) - Team Lead, building ERP/WMS systems\n**Quazma Techno** (May-Oct 2024) - AI platforms, MS Add-ins, e-commerce\n**Codewise Infotech** (Feb 2022-Apr 2024) - Enterprise apps, analytics, mobile dev",

    r"(best|favorite|top|most).*project|sab se (jada|zyada).*project": "Yash's flagship project is currently the **KOMAL Portal** - an enterprise ERP & WMS system he architected from scratch at Katyayani Organics. Another highly notable project is **Shortly.io**, an AI-powered content platform, and the **Silextech Add-in**, which is officially published on the Microsoft Marketplace!",

    r"(education|degree|college|university|study|studied|qualification)": "Yash holds an **MBA in IT & Marketing** from Modern Institute of Professional Studies (2020-2022) and a **B.Com in Computer Application** from SJHSGICCS Indore (2018-2020).",

    r"(contact|reach|email|hire|connect|how.*(reach|contact|hire))": "You can reach Yash at:\n\n**Email:** yashpatidar2203@gmail.com\n**LinkedIn:** [linkedin.com/in/yash-patidar-288412230](https://linkedin.com/in/yash-patidar-288412230)\n\nOr use the contact form on this portfolio!",

    r"(resume|cv|download)": "You can download Yash's resume using the download button in the hero section of this portfolio, or feel free to reach out via email at yashpatidar2203@gmail.com!",

    r"(current|now|present|working on|latest|where.*(work|now))": "Yash is currently the **Team Lead & Full Stack Developer** at Katyayani Organics, where he's spearheading the KOMAL Portal - a comprehensive ERP & WMS system built with FastAPI, PostgreSQL, MongoDB, Redis, and React/Remix. It handles real-time inventory across 5+ warehouse locations!",
}

# ─── Generic projects question (only matches when no specific project is named) ───
GENERIC_PROJECTS_RESPONSE = "Yash has built impressive projects:\n\n**KOMAL Portal** - Full ERP & WMS with real-time inventory (FastAPI + React)\n**Shortly.io** - AI content platform for text-to-image/video (Next.js + OpenAI)\n**Silextech** - Legal doc management for MS Word (React + Azure)\n**Soulpizza** - Multi-panel food ordering with WebSockets\n**TDI Suite** - Enterprise mobile apps with NFC + Kotlin\n\nAsk me about any specific project for more details!"


class ChatCacheManager:
    """Multi-tier LRU cache for chat responses."""

    def __init__(self, max_size: int = 200):
        self.cache: OrderedDict[str, tuple] = OrderedDict()
        self.max_size = max_size

    def _normalize_query(self, query: str) -> str:
        """Normalize query for better cache hits."""
        return re.sub(r'[^\w\s]', '', query.lower().strip())

    def _hash_query(self, query: str) -> str:
        return hashlib.md5(self._normalize_query(query).encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        key = self._hash_query(query)
        if key in self.cache:
            response, timestamp = self.cache[key]
            # Cache valid for 1 hour
            if time.time() - timestamp < 3600:
                self.cache.move_to_end(key)
                return response
            else:
                del self.cache[key]
        return None

    def set(self, query: str, response: str):
        key = self._hash_query(query)
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = (response, time.time())


# Global cache instance
cache_manager = ChatCacheManager()

# Model configuration
MODEL_NAME = "gemini-3-flash-preview"
GENERATION_CONFIG = types.GenerateContentConfig(
    max_output_tokens=350,
    temperature=0.7,
    top_p=0.9,
    system_instruction=PORTFOLIO_CONTEXT,
)


def check_project_specific(message: str) -> Optional[str]:
    """Check if the message asks about a specific project."""
    msg_lower = message.lower()
    for key, detail in PROJECT_DETAILS.items():
        if key in msg_lower:
            return detail
    return None


def check_faq(message: str) -> Optional[str]:
    """Check if message matches a FAQ pattern."""
    msg_lower = message.lower().strip()

    # First, check project-specific questions
    project_answer = check_project_specific(msg_lower)
    if project_answer:
        return project_answer

    # Next, check for specific skill experience questions
    skill_exp = check_specific_skill(msg_lower)
    if skill_exp:
        return skill_exp

    # Check for projects using specific skills
    project_skill = check_projects_by_skill(msg_lower)
    if project_skill:
        return project_skill

    # Then check general FAQ patterns
    for pattern, response in FAQ_PATTERNS.items():
        if re.search(pattern, msg_lower):
            return response

    # Generic "projects" / "what has he built" question (no specific project named)
    if re.search(r"(all )?projects|what.*(built|made|created|developed)|portfolio|show.*(work|projects)", msg_lower):
        return GENERIC_PROJECTS_RESPONSE

    return None


async def generate_chat_response(
    message: str,
    history: List[Dict[str, str]] = None
) -> tuple[str, bool]:
    """
    Generate a chat response with multi-tier caching.
    Returns (response_text, was_cached).
    """
    # Layer 1: FAQ cache
    faq_response = check_faq(message)
    if faq_response:
        return faq_response, True

    # Layer 2: Response cache
    cached = cache_manager.get(message)
    if cached:
        return cached, True

    # Layer 3: Call Gemini API with sliding window (last 5 messages)
    try:
        contents = []

        if history:
            # Only keep last 5 exchanges for token efficiency
            recent = history[-10:]  # 5 user + 5 assistant messages
            for msg in recent:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

        # Add current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        ))

        # Call Gemini with retry
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=contents,
            config=GENERATION_CONFIG,
        )

        reply = response.text

        # Store in response cache
        cache_manager.set(message, reply)

        return reply, False

    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API error: {error_msg}")

        # If rate limited, wait and retry once
        if "429" in error_msg or "quota" in error_msg.lower():
            try:
                await asyncio.sleep(3)
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=MODEL_NAME,
                    contents=[types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=message)]
                    )],
                    config=GENERATION_CONFIG,
                )
                reply = response.text
                cache_manager.set(message, reply)
                return reply, False
            except Exception as retry_err:
                print(f"Gemini retry failed: {retry_err}")

        # Instead of throwing a connection error, return a comprehensive fallback summary
        fallback_msg = (
            "I'm currently operating in offline mode due to high traffic, but here is a quick summary of Yash:\n\n"
            "🚀 **Role:** Senior Full Stack Developer & Team Lead\n"
            "💻 **Top Tech:** React, Node.js, Python, FastAPI, AWS, AI/ML\n"
            "💼 **Current:** Building enterprise ERP/WMS at Katyayani Organics\n"
            "🏆 **Key Projects:** KOMAL Portal, Shortly.io (AI), Silextech (Microsoft Marketplace)\n\n"
            "Try asking me specifically about **skills**, **experience**, or a **specific project name** to search my offline database!"
        )
        return fallback_msg, False
