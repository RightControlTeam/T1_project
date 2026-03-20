import pytest
import asyncio
from typing import AsyncGenerator, Tuple
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from core.database import Base, get_db
from user.models import User
from user.crud import register_user
from user.schemas import RegisterUser
from resource.models import Resource
from resource.crud import create_resource
from resource.schemas import ResourceCreate

# Убедись, что БД test_db существует в Postgres
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Создает один цикл событий на всю сессию тестов"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Создает движок и таблицы (один раз на сессию)"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    """ Обеспечивает изоляцию тестов"""

    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )

    async with async_session() as session:
        yield session
        await session.close()

    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator:
    """Клиент с подменой зависимости БД"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db_session) -> Tuple[User, str]:
    """Создает пользователя testuser"""
    user_data = RegisterUser(
        username="testuser",
        password="TestPass123",
        is_admin=False
    )
    token_response = await register_user(user_data, db_session)
    from user.crud import get_user_by_username
    user = await get_user_by_username("testuser", db_session)
    return user, token_response.access_token


@pytest.fixture(scope="function")
async def test_admin(db_session) -> Tuple[User, str]:
    """Создает админа adminuser"""
    admin_data = RegisterUser(
        username="adminuser",
        password="AdminPass123",
        is_admin=True
    )
    token_response = await register_user(admin_data, db_session)
    from user.crud import get_user_by_username
    admin = await get_user_by_username("adminuser", db_session)
    return admin, token_response.access_token


@pytest.fixture(scope="function")
async def test_resource(db_session, test_admin) -> Resource:
    """Создает тестовый ресурс"""
    resource_data = ResourceCreate(
        name="Test Room",
        type="room",
        description="Test Desc",
        is_active=True
    )
    return await create_resource(db_session, resource_data)