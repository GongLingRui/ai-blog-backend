"""
Celery Tasks Package
"""
from app.tasks.email import (
    send_email_task,
    send_welcome_email,
    send_password_reset_email,
    send_verification_email,
)
from app.tasks.notifications import (
    create_notification_task,
    send_push_notification_task,
    send_bulk_notifications,
)
from app.tasks.analytics import (
    track_page_view,
    track_article_view,
    track_user_action,
    generate_analytics_report,
)

__all__ = [
    # Email tasks
    "send_email_task",
    "send_welcome_email",
    "send_password_reset_email",
    "send_verification_email",
    # Notification tasks
    "create_notification_task",
    "send_push_notification_task",
    "send_bulk_notifications",
    # Analytics tasks
    "track_page_view",
    "track_article_view",
    "track_user_action",
    "generate_analytics_report",
]
