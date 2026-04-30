from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User

async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(
    db: AsyncSession, 
    user_id: str, 
    email: str, 
    name: str, 
    role: str,
    phone: str | None = None,
    address_city: str | None = None,
    address_province: str | None = None,
    address_detail: str | None = None
) -> User:
    db_user = User(
        id=user_id,
        email=email,
        name=name,
        role=role,
        phone=phone,
        address_city=address_city,
        address_province=address_province,
        address_detail=address_detail
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
