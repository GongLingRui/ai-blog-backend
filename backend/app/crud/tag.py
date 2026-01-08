"""
Tag CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.core.utils import generate_slug


async def get_tag(db: AsyncSession, tag_id: str) -> Optional[Tag]:
    """Get tag by ID"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_tag_by_name(db: AsyncSession, name: str) -> Optional[Tag]:
    """Get tag by name"""
    result = await db.execute(select(Tag).where(Tag.name == name))
    return result.scalar_one_or_none()


async def get_tag_by_slug(db: AsyncSession, slug: str) -> Optional[Tag]:
    """Get tag by slug"""
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    return result.scalar_one_or_none()


async def get_tags(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    sort: str = "usage_count",
    order: str = "desc",
) -> List[Tag]:
    """Get list of tags"""
    query = select(Tag)

    # Sorting
    sort_column = getattr(Tag, sort, Tag.usage_count)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def search_tags(
    db: AsyncSession,
    query: str,
    limit: int = 20,
) -> List[Tag]:
    """Search tags by name"""
    result = await db.execute(
        select(Tag)
        .where(Tag.name.ilike(f"%{query}%"))
        .order_by(Tag.usage_count.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_tags(db: AsyncSession) -> int:
    """Count tags"""
    from sqlalchemy import func

    result = await db.execute(select(func.count(Tag.id)))
    return result.scalar() or 0


async def create_tag(
    db: AsyncSession,
    tag_in: TagCreate,
) -> Tag:
    """Create new tag"""
    import uuid

    tag = Tag(
        id=str(uuid.uuid4()),
        name=tag_in.name,
        slug=generate_slug(tag_in.name),
        description=tag_in.description,
        color=tag_in.color,
    )

    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def update_tag(
    db: AsyncSession,
    tag: Tag,
    tag_in: TagUpdate,
) -> Tag:
    """Update tag"""
    update_data = tag_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.flush()
    await db.refresh(tag)
    return tag


async def get_or_create_tag(
    db: AsyncSession,
    name: str,
) -> Tag:
    """Get existing tag or create new one"""
    tag = await get_tag_by_name(db, name)

    if not tag:
        import uuid

        tag = Tag(
            id=str(uuid.uuid4()),
            name=name,
            slug=generate_slug(name),
        )
        db.add(tag)
        await db.flush()

    return tag
