"""
Test utility functions
"""
import pytest
from app.core.utils import (
    generate_slug,
    generate_unique_slug,
    calculate_reading_time,
    generate_uuid,
    truncate_text,
    sanitize_html
)


def test_generate_slug_basic():
    """Test basic slug generation"""
    slug = generate_slug("Hello World")
    assert slug == "hello-world"


def test_generate_slug_with_special_chars():
    """Test slug generation with special characters"""
    slug = generate_slug("Hello @#$% World!")
    assert slug == "hello-world"


def test_generate_slug_with_multiple_spaces():
    """Test slug generation with multiple spaces"""
    slug = generate_slug("Hello    World    Test")
    assert slug == "hello-world-test"


def test_generate_slug_with_underscores():
    """Test slug generation with underscores"""
    slug = generate_slug("hello_world_test")
    assert slug == "hello-world-test"


def test_generate_slug_with_numbers():
    """Test slug generation with numbers"""
    slug = generate_slug("Test 123 Article")
    assert slug == "test-123-article"


def test_generate_slug_empty_string():
    """Test slug generation with empty string"""
    slug = generate_slug("")
    assert slug == ""


def test_generate_slug_leading_trailing_hyphens():
    """Test that leading and trailing hyphens are removed"""
    slug = generate_slug("---Hello World---")
    assert slug == "hello-world"


def test_generate_slug_consecutive_hyphens():
    """Test that consecutive hyphens are reduced to single hyphen"""
    slug = generate_slug("Hello---World")
    assert slug == "hello-world"


def test_generate_unique_slug_no_duplicates():
    """Test unique slug generation when no duplicates exist"""
    slug = generate_unique_slug("Test Article", [])
    assert slug == "test-article"


def test_generate_unique_slug_with_duplicates():
    """Test unique slug generation with duplicates"""
    existing_slugs = ["test-article", "test-article-2"]
    slug = generate_unique_slug("Test Article", existing_slugs)
    assert slug == "test-article-3"


def test_generate_unique_slug_multiple_duplicates():
    """Test unique slug generation with multiple duplicates"""
    existing_slugs = ["test-article", "test-article-1", "test-article-2", "test-article-3"]
    slug = generate_unique_slug("Test Article", existing_slugs)
    assert slug == "test-article-4"


def test_calculate_reading_time_short():
    """Test reading time calculation for short content"""
    content = "This is a short article."
    time = calculate_reading_time(content)
    assert time == 1  # Minimum 1 minute


def test_calculate_reading_time_medium():
    """Test reading time calculation for medium content"""
    # Create content with ~400 words
    content = "word " * 400
    time = calculate_reading_time(content)
    assert time == 2  # ~2 minutes


def test_calculate_reading_time_long():
    """Test reading time calculation for long content"""
    # Create content with ~1000 words
    content = "word " * 1000
    time = calculate_reading_time(content)
    assert time == 5  # ~5 minutes


def test_calculate_reading_time_with_markdown():
    """Test reading time calculation with markdown content"""
    content = """
    # Title

    This is an article with **bold** and *italic* text.

    - List item 1
    - List item 2
    - List item 3

    [Link](https://example.com)
    """
    time = calculate_reading_time(content)
    assert time >= 1


def test_calculate_reading_time_empty():
    """Test reading time calculation for empty content"""
    content = ""
    time = calculate_reading_time(content)
    assert time == 1  # Minimum 1 minute


def test_calculate_reading_time_custom_wpm():
    """Test reading time calculation with custom words per minute"""
    content = "word " * 100  # 100 words
    time = calculate_reading_time(content, words_per_minute=50)
    assert time == 2  # 100 words / 50 wpm = 2 minutes


def test_generate_uuid():
    """Test UUID generation"""
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()

    assert uuid1 != uuid2
    assert len(uuid1) == 36  # Standard UUID length
    assert "-" in uuid1


def test_truncate_text_short():
    """Test truncating short text (no truncation needed)"""
    text = "Short text"
    result = truncate_text(text, max_length=20)
    assert result == "Short text"


def test_truncate_text_exact_length():
    """Test truncating text at exact length"""
    text = "Exact length"
    result = truncate_text(text, max_length=11)
    assert result == "Exact length"


def test_truncate_text_long():
    """Test truncating long text"""
    text = "This is a very long text that needs to be truncated"
    result = truncate_text(text, max_length=20)
    assert len(result) == 20
    assert result.endswith("...")


def test_truncate_text_custom_suffix():
    """Test truncating with custom suffix"""
    text = "This is a very long text that needs to be truncated"
    result = truncate_text(text, max_length=20, suffix=" [more]")
    assert len(result) == 20
    assert result.endswith("[more]")


def test_truncate_text_empty():
    """Test truncating empty text"""
    text = ""
    result = truncate_text(text, max_length=10)
    assert result == ""


def test_sanitize_html_script_tags():
    """Test sanitizing HTML with script tags"""
    html = '<p>Valid content</p><script>alert("XSS")</script>'
    result = sanitize_html(html)
    assert "<script>" not in result
    assert "Valid content" in result


def test_sanitize_html_event_handlers():
    """Test sanitizing HTML with event handlers"""
    html = '<p onclick="malicious()">Content</p>'
    result = sanitize_html(html)
    assert "onclick=" not in result
    assert "Content" in result


def test_sanitize_html_complex():
    """Test sanitizing complex HTML"""
    html = '''
    <div>
        <p>Valid paragraph</p>
        <script>alert("XSS")</script>
        <a href="#" onmouseover="bad()">Link</a>
        <img src="x" onerror="alert(1)">
    </div>
    '''
    result = sanitize_html(html)
    assert "<script>" not in result
    assert "onmouseover=" not in result
    assert "onerror=" not in result
    assert "Valid paragraph" in result


def test_sanitize_html_clean():
    """Test that clean HTML is preserved"""
    html = '<p>This is <strong>clean</strong> HTML</p>'
    result = sanitize_html(html)
    assert "<p>" in result
    assert "<strong>" in result
    assert "clean" in result


def test_sanitize_html_empty():
    """Test sanitizing empty HTML"""
    html = ""
    result = sanitize_html(html)
    assert result == ""


def test_slug_with_unicode():
    """Test slug generation with unicode characters"""
    slug = generate_slug("Café résumé naïve")
    assert "cafe" in slug
    assert "resume" in slug


def test_slug_with_mixed_case():
    """Test slug generation with mixed case"""
    slug = generate_slug("HeLLo WoRLD")
    assert slug == "hello-world"


def test_truncate_unicode():
    """Test truncating text with unicode characters"""
    text = "This is text with emoji 🎉 and special chars"
    result = truncate_text(text, max_length=20)
    assert len(result) == 20
    assert result.endswith("...")
