import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import asyncio

def _send_email_sync(name: str, email: str, message: str):
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("Warning: SMTP_USER or SMTP_PASSWORD not configured. Email not sent.")
        return False

    sender = settings.SMTP_USER
    receiver = settings.SMTP_RECEIVER if settings.SMTP_RECEIVER else settings.SMTP_USER
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"New Contact Message from {name} (Digital Resume)"

    body = f"""
    You have received a new contact message from your portfolio website:

    Name: {name}
    Email: {email}

    Message:
    {message}
    """
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Using Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

async def send_contact_email(name: str, email: str, message: str):
    """
    Send an email asynchronously so it doesn't block the API request.
    """
    await asyncio.to_thread(_send_email_sync, name, email, message)
