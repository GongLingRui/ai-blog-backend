"""
Utility functions
"""
import re
import uuid
from typing import Optional


def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from text
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')

    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    return slug


def generate_unique_slug(text: str, existing_slugs: list[str] = None) -> str:
    """
    Generate a unique slug, appending a number if necessary
    """
    base_slug = generate_slug(text)
    slug = base_slug

    if existing_slugs:
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1

    return slug


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes
    """
    # Remove markdown syntax and count words
    words = len(re.findall(r'\w+', content))
    minutes = max(1, round(words / words_per_minute))
    return minutes


def generate_uuid() -> str:
    """
    Generate a unique UUID
    """
    return str(uuid.uuid4())


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_html(html: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks
    """
    # Basic sanitization - remove script tags and event handlers
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'on\w+="[^"]*"', '', html, flags=re.IGNORECASE)
    return html
