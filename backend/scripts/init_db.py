"""
Initialize Database Script

This script creates all database tables and initial data.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.database import Base
from app.models import *  # Import all models


async def init_database():
    """Initialize database tables"""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    # Create initial data
    await create_initial_data(engine)

    await engine.dispose()


async def create_initial_data(engine):
    """Create initial data for categories and tags"""
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create default categories
        categories_data = [
            {
                "id": "cat-deep-learning",
                "name": "深度学习",
                "slug": "deep-learning",
                "description": "深度学习相关文章",
                "icon": "Brain",
                "color": "#3B82F6",
                "sort_order": 1,
            },
            {
                "id": "cat-nlp",
                "name": "自然语言处理",
                "slug": "nlp",
                "description": "NLP技术和应用",
                "icon": "MessageSquare",
                "color": "#10B981",
                "sort_order": 2,
            },
            {
                "id": "cat-cv",
                "name": "计算机视觉",
                "slug": "computer-vision",
                "description": "CV技术和应用",
                "icon": "Camera",
                "color": "#8B5CF6",
                "sort_order": 3,
            },
            {
                "id": "cat-ml",
                "name": "机器学习",
                "slug": "machine-learning",
                "description": "机器学习基础和进阶",
                "icon": "Target",
                "color": "#F59E0B",
                "sort_order": 4,
            },
            {
                "id": "cat-rl",
                "name": "强化学习",
                "slug": "reinforcement-learning",
                "description": "强化学习和RL应用",
                "icon": "Gamepad2",
                "color": "#EF4444",
                "sort_order": 5,
            },
        ]

        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)

        # Create default tags
        tags_data = [
            {
                "id": "tag-transformer",
                "name": "Transformer",
                "slug": "transformer",
                "description": "Transformer架构相关",
                "color": "#3B82F6",
            },
            {
                "id": "tag-bert",
                "name": "BERT",
                "slug": "bert",
                "description": "BERT模型相关",
                "color": "#F59E0B",
            },
            {
                "id": "tag-gpt",
                "name": "GPT",
                "slug": "gpt",
                "description": "GPT系列模型",
                "color": "#10B981",
            },
            {
                "id": "tag-pytorch",
                "name": "PyTorch",
                "slug": "pytorch",
                "description": "PyTorch框架",
                "color": "#EE4C2C",
            },
            {
                "id": "tag-tensorflow",
                "name": "TensorFlow",
                "slug": "tensorflow",
                "description": "TensorFlow框架",
                "color": "#FF6F00",
            },
            {
                "id": "tag-langchain",
                "name": "LangChain",
                "slug": "langchain",
                "description": "LangChain框架",
                "color": "#8B5CF6",
            },
            {
                "id": "tag-llm",
                "name": "LLM",
                "slug": "llm",
                "description": "大语言模型",
                "color": "#EC4899",
            },
            {
                "id": "tag-finetuning",
                "name": "Fine-tuning",
                "slug": "fine-tuning",
                "description": "模型微调",
                "color": "#06B6D4",
            },
            {
                "id": "tag-prompt-eng",
                "name": "Prompt Engineering",
                "slug": "prompt-engineering",
                "description": "提示工程",
                "color": "#84CC16",
            },
            {
                "id": "tag-rag",
                "name": "RAG",
                "slug": "rag",
                "description": "检索增强生成",
                "color": "#F97316",
            },
        ]

        for tag_data in tags_data:
            tag = Tag(**tag_data)
            session.add(tag)

        await session.commit()
        print("Initial data created successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())
