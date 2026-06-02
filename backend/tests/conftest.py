import pytest
from typing import AsyncGenerator, Tuple
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from main import app
from core.database import Base, get_db
from resource.models import Resource
from resource.crud import create_resource
from resource.schemas import ResourceCreate

from user_module.user_repository import UserRepository
from user_module.admin_level import AdminLevel
from user_module.schemas import UserRequest, CreatorRequest
from user_module.user import User
from user_module.user_service import UserService
from core.config import settings


# TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres:5432/test_db"

# @pytest.fixture(scope="session")
# def event_loop():
#     """Создает один цикл событий на всю сессию тестов"""
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Создает движок и таблицы """
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
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            yield session
        await transaction.rollback()


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
    user_data = UserRequest(username="testuser", password="TestPass123")
    token_response = await  UserService.create(user_data, db_session,AdminLevel.user)
    user = await UserRepository.get_by_username("testuser", db_session)
    return user, token_response.access_token


@pytest.fixture(scope="function")
async def test_admin(db_session) -> Tuple[User, str]:
    admin_data = UserRequest(username="adminuser", password="AdminPass123")
    token_response = await UserService.create(admin_data, db_session, AdminLevel.admin)
    admin = await UserRepository.get_by_username("adminuser", db_session)
    return admin, token_response.access_token


@pytest.fixture(scope="function")
async def test_creator(db_session) -> Tuple[User, str]:
    """Создает creator пользователя для тестов"""
    creator_data = CreatorRequest(
        username="creatoruser",
        password="CreatorPass123",
        creator_registration_key=settings.CREATOR_REGISTRATION_KEY
    )
    token_response = await UserService.create_creator(creator_data, db_session)
    creator = await UserRepository.get_by_username("creatoruser", db_session)
    return creator, token_response.access_token


@pytest.fixture(scope="function")
async def creator_token_headers(test_creator):
    _, token = test_creator
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
async def test_resource(db_session) -> Resource:
    """Создает тестовый ресурс"""
    resource_data = ResourceCreate(
        name="Test Room",
        type="room",
        description="Test Desc",
        is_active=True
    )
    return await create_resource(db_session, resource_data)

@pytest.fixture(scope="function")
async def created_resource(test_resource):
    return test_resource

@pytest.fixture(scope="function")
async def admin_token_headers(test_admin):
    _, token = test_admin
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
async def user_token_headers(test_user):
    _, token = test_user
    return {"Authorization": f"Bearer {token}"}