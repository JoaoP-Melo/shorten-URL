from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from src.auth.router import app
from src.auth.database import get_db
from src.auth.models import Url, User
from src.auth.security import get_current_user, get_password_hash

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
SessionTest = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

transport = ASGITransport(app=app)


@pytest_asyncio.fixture
async def session():
    async with SessionTest() as session:
        yield session
        await session.execute(delete(Url))
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def test_user(session):
    password = get_password_hash("testtest")

    new_user = User(username="test", email="test@test.com", password=password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@pytest_asyncio.fixture
async def test_url(test_user, session):
    new_url = Url(
        original_url="www.test.com",
        short_url="testtest",
        expires_date=(
            datetime.now() + timedelta(minutes=int(os.getenv("URL_TIME_EXPIRE")))
        ),
        click_count=0,
        is_active=True,
        user_id=test_user.id,
    )
    session.add(new_url)
    await session.commit()
    await session.refresh(new_url)

    return new_url


@pytest_asyncio.fixture
async def client(test_user):
    async def get_db_override():
        async with SessionTest() as session:
            yield session

    async def get_test_user():
        return test_user

    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = get_test_user

    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
