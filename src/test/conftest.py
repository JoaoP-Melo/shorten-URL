from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import pytest
from datetime import datetime, timedelta

from src.auth.router import app
from src.auth.database import get_db
from src.auth.models import Url

load_dotenv()

engine = create_engine(os.getenv('TEST_DATABASE_URL'))

SessionTest = sessionmaker(bind=engine)


@pytest.fixture
def session():
    with SessionTest() as session:
        yield session
        session.query(Url).delete()
        session.commit()


@pytest.fixture
def client(session):
    def get_db_override():
        yield session

    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def add_url_in_db(session):
    new_url = Url(
        original_url= "www.test.com",
        short_url= "testtest",
        expires_date= (
            datetime.now() + timedelta(
                minutes=int(os.getenv('URL_TIME_EXPIRE'))
            )
        ),
        click_count=0,
        is_active=True
    )

    session.add(new_url)
    session.commit
