import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import logger

def send_real_email(recipient_email: str, subject: str, html_content: str) -> None:
    """
    Sends a email using SMTP configuration.
    Runs inside FastAPI's BackgroundTasks to prevent blocking the main event loop.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning("SMTP settings are incomplete. Skipping email delivery.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = recipient_email

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, recipient_email, message.as_string())
        logger.info(f"Email successfully sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email} due to error: {e}")
