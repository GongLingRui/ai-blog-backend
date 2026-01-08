"""
Seed Data Script

This script populates the database with sample data for development.
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import User, Article, Category, Tag, ArticleTag
from app.core.security import get_password_hash


async def seed_database():
    """Seed database with sample data"""
    print("Seeding database with sample data...")

    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create sample users
        users = [
            User(
                id="user-admin-001",
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("Admin123!"),
                full_name="Admin User",
                role="admin",
                is_verified=True,
            ),
            User(
                id="user-author-001",
                email="author@example.com",
                username="johndoe",
                hashed_password=get_password_hash("Author123!"),
                full_name="John Doe",
                bio="AI enthusiast and ML engineer",
                role="author",
                is_verified=True,
            ),
            User(
                id="user-reader-001",
                email="reader@example.com",
                username="janedoe",
                hashed_password=get_password_hash("Reader123!"),
                full_name="Jane Doe",
                bio="AI learner",
                role="reader",
            ),
        ]

        for user in users:
            session.add(user)

        # Get existing categories and tags
        categories_result = await session.execute(
            select(Category).where(Category.slug == "deep-learning")
        )
        dl_category = categories_result.scalar_one_or_none()

        tags_result = await session.execute(
            select(Tag).where(Tag.slug.in_(["transformer", "bert", "llm"]))
        )
        tags = list(tags_result.scalars().all())

        # Create sample articles
        articles = [
            Article(
                id="article-001",
                title="Introduction to Transformers",
                slug="introduction-to-transformers",
                content="""# Introduction to Transformers

Transformers have revolutionized the field of natural language processing (NLP)...

## Architecture Overview

The Transformer architecture was introduced in the paper "Attention Is All You Need"...

## Key Components

1. Self-Attention Mechanism
2. Multi-Head Attention
3. Position-wise Feed-Forward Networks
4. Positional Encoding

## Applications

- Machine Translation
- Text Generation
- Question Answering
- And many more...
""",
                excerpt="Transformers have revolutionized NLP. Learn about the architecture and applications.",
                author_id="user-author-001",
                category_id=dl_category.id if dl_category else None,
                status="published",
                published_at=datetime.utcnow(),
                reading_time=15,
            ),
            Article(
                id="article-002",
                title="Understanding BERT",
                slug="understanding-bert",
                content="""# Understanding BERT

BERT (Bidirectional Encoder Representations from Transformers) is a pre-trained language model...

## Pre-training

BERT is pre-trained on two tasks:
1. Masked Language Modeling (MLM)
2. Next Sentence Prediction (NSP)

## Fine-tuning

Fine-tuning BERT for specific tasks...
""",
                excerpt="Learn about BERT, one of the most influential NLP models.",
                author_id="user-author-001",
                category_id=dl_category.id if dl_category else None,
                status="published",
                published_at=datetime.utcnow(),
                reading_time=12,
            ),
            Article(
                id="article-003",
                title="Getting Started with Large Language Models",
                slug="getting-started-with-llms",
                content="""# Getting Started with LLMs

Large Language Models have taken the world by storm...

## Popular LLMs

- GPT-4
- Claude
- LLaMA
- Mistral

## How to Use LLMs

1. Prompt Engineering
2. Fine-tuning
3. RAG (Retrieval-Augmented Generation)
""",
                excerpt="A beginner's guide to understanding and using Large Language Models.",
                author_id="user-author-001",
                category_id=dl_category.id if dl_category else None,
                status="published",
                published_at=datetime.utcnow(),
                reading_time=10,
            ),
        ]

        for article in articles:
            session.add(article)

        await session.flush()

        # Add tags to articles
        for article in articles:
            for tag in tags[:2]:  # Add first 2 tags to each article
                article_tag = ArticleTag(
                    id=f"at-{article.id}-{tag.id}", article_id=article.id, tag_id=tag.id
                )
                session.add(article_tag)

        await session.commit()

        print(f"Created {len(users)} users")
        print(f"Created {len(articles)} articles")

    await engine.dispose()
    print("Database seeded successfully!")


if __name__ == "__main__":
    from sqlalchemy import select

    asyncio.run(seed_database())
