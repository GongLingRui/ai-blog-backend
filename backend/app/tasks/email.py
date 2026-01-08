"""
Email Tasks
"""
import logging
from typing import Dict, Any

from app.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.email.send_email")
def send_email_task(
    email_to: str,
    subject: str,
    html_content: str,
    text_content: str = None,
) -> Dict[str, Any]:
    """
    Send email task

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML email content
        text_content: Plain text email content (optional)

    Returns:
        Dict with status and message
    """
    try:
        # TODO: Implement actual email sending logic
        # For now, just log the email details
        logger.info(f"Sending email to {email_to}")
        logger.info(f"Subject: {subject}")

        # Example implementation with SMTP:
        # import smtplib
        # from email.mime.text import MIMEText
        # from email.mime.multipart import MIMEMultipart
        #
        # msg = MIMEMultipart("alternative")
        # msg["Subject"] = subject
        # msg["From"] = settings.EMAILS_FROM_EMAIL
        # msg["To"] = email_to
        #
        # if text_content:
        #     part1 = MIMEText(text_content, "plain")
        #     msg.attach(part1)
        #
        # part2 = MIMEText(html_content, "html")
        # msg.attach(part2)
        #
        # with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        #     server.send_message(msg)

        return {
            "status": "success",
            "message": "Email sent successfully",
            "email_to": email_to,
        }

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {
            "status": "failed",
            "message": str(e),
            "email_to": email_to,
        }


@celery_app.task(name="app.tasks.email.send_welcome_email")
def send_welcome_email(user_email: str, user_name: str) -> Dict[str, Any]:
    """
    Send welcome email to new user

    Args:
        user_email: User's email address
        user_name: User's name
    """
    subject = "Welcome to AI Muse Blog!"
    html_content = f"""
    <html>
        <body>
            <h1>Welcome, {user_name}!</h1>
            <p>Thank you for joining AI Muse Blog. We're excited to have you!</p>
            <p>Start exploring and sharing your thoughts with our community.</p>
        </body>
    </html>
    """
    text_content = f"Welcome, {user_name}! Thank you for joining AI Muse Blog."

    return send_email_task(user_email, subject, html_content, text_content)


@celery_app.task(name="app.tasks.email.send_verification_email")
def send_verification_email(user_email: str, verification_url: str) -> Dict[str, Any]:
    """
    Send email verification link

    Args:
        user_email: User's email address
        verification_url: Email verification URL
    """
    subject = "Verify Your Email Address"
    html_content = f"""
    <html>
        <body>
            <h1>Verify Your Email</h1>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
        </body>
    </html>
    """
    text_content = f"Please verify your email by visiting: {verification_url}"

    return send_email_task(user_email, subject, html_content, text_content)


@celery_app.task(name="app.tasks.email.send_password_reset_email")
def send_password_reset_email(user_email: str, reset_url: str) -> Dict[str, Any]:
    """
    Send password reset link

    Args:
        user_email: User's email address
        reset_url: Password reset URL
    """
    subject = "Reset Your Password"
    html_content = f"""
    <html>
        <body>
            <h1>Reset Your Password</h1>
            <p>Please click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    text_content = f"Reset your password by visiting: {reset_url}"

    return send_email_task(user_email, subject, html_content, text_content)
