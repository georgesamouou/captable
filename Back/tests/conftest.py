import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole, ShareholderProfile
from app.auth import get_password_hash
import factory
from factory.fuzzy import FuzzyText, FuzzyInteger


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Test client fixture"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Database session fixture"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# Factory classes for test data
class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = factory.LazyFunction(lambda: get_password_hash("testpassword"))
    role = UserRole.SHAREHOLDER
    is_active = True


class AdminUserFactory(UserFactory):
    role = UserRole.ADMIN


class ShareholderProfileFactory(factory.Factory):
    class Meta:
        model = ShareholderProfile
    
    first_name = FuzzyText(length=10)
    last_name = FuzzyText(length=10)
    phone = factory.Sequence(lambda n: f"+1234567890{n}")
    address = factory.Faker('address')
    tax_id = factory.Sequence(lambda n: f"TAX{n:06d}")


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    user = AdminUserFactory()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def shareholder_user(db_session):
    """Create shareholder user for testing"""
    user = UserFactory()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    profile = ShareholderProfileFactory(user_id=user.id)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Get admin authentication token"""
    response = client.post("/api/token/", data={
        "username": admin_user.email,
        "password": "testpassword"
    })
    return response.json()["access_token"]


@pytest.fixture
def shareholder_token(client, shareholder_user):
    """Get shareholder authentication token"""
    response = client.post("/api/token/", data={
        "username": shareholder_user.email,
        "password": "testpassword"
    })
    return response.json()["access_token"] 