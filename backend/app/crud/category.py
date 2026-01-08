"""
Category CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.utils import generate_slug, generate_unique_slug


async def get_category(db: AsyncSession, category_id: str) -> Optional[Category]:
    """Get category by ID"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_category_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
    """Get category by slug"""
    result = await db.execute(
        select(Category).where(Category.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[Category]:
    """Get list of categories"""
    query = select(Category)

    if active_only:
        query = query.where(Category.is_active == True)

    query = query.order_by(Category.sort_order).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_categories(db: AsyncSession, active_only: bool = True) -> int:
    """Count categories"""
    from sqlalchemy import func

    query = select(func.count(Category.id))

    if active_only:
        query = query.where(Category.is_active == True)

    result = await db.execute(query)
    return result.scalar() or 0


async def create_category(
    db: AsyncSession,
    category_in: CategoryCreate,
) -> Category:
    """Create new category"""
    import uuid

    category = Category(
        id=str(uuid.uuid4()),
        name=category_in.name,
        slug=generate_slug(category_in.name),
        description=category_in.description,
        icon=category_in.icon,
        color=category_in.color,
        parent_id=category_in.parent_id,
        sort_order=category_in.sort_order,
    )

    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    category: Category,
    category_in: CategoryUpdate,
) -> Category:
    """Update category"""
    update_data = category_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category: Category) -> None:
    """Delete category (soft delete by setting is_active=False)"""
    category.is_active = False
    await db.flush()
