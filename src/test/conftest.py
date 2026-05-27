from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import pytest
from datetime import datetime, timedelta

from src.auth.router import app
from src.auth.database import get_db
from src.auth.models import Url, User
from src.auth.security import get_current_user, get_password_hash

load_dotenv()

engine = create_engine(os.getenv('TEST_DATABASE_URL'))

SessionTest = sessionmaker(bind=engine)


@pytest.fixture
def session():
    with SessionTest() as session:
        yield session
        session.query(Url).delete()
        session.query(User).delete()
        session.commit()


@pytest.fixture
def client(session, test_user):
    def get_db_override():
        yield session

    
    def get_test_user_id():
        return test_user
    

    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = get_test_user_id

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def test_user(session):
    password = get_password_hash('testtest')

    user = User(
        username='test',
        email='test@test.com',
        password=password
    )

    session.add(user)
    session.commit()

    return user


@pytest.fixture
def test_url(session, test_user):

    new_url = Url(
        original_url='www.test.com',
        short_url='testtest',
        expires_date=(
            datetime.now()
            + timedelta(minutes=int(os.getenv('URL_TIME_EXPIRE')))
        ),
        click_count=0,
        is_active=True,
        user_id=test_user.id,
    )

    session.add(new_url)
    session.commit()
    
    return new_url
