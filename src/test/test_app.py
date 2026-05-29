from http import HTTPStatus
from sqlalchemy import select
from src.auth.models import Url, User
from src.auth.security import get_current_user
from src.auth.router import app
import pytest

@pytest.mark.asyncio
async def test_shoteen_url_success(client, session):
    url = 'www.test.com.br'

    response = await client.post('/save_url/', json={'original_url': url})

    url_in_db = await session.scalar(select(Url).where(Url.original_url == url))

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'short_url': url_in_db.short_url}


@pytest.mark.asyncio
async def test_get_original_url_success(client, session, test_url):
    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.get(f'/get_url/{short_url_db}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'original_url': url_db.original_url}



@pytest.mark.asyncio
async def test_get_original_url_short_url_not_found(client):
    short_url_db = 'ksnafjibsf'

    response = await client.get(f'/get_url/{short_url_db}')

    assert response.status_code == HTTPStatus.NOT_FOUND



@pytest.mark.asyncio
async def test_get_original_url_short_url_deactivated(client, session, test_url):
    url_db = await session.scalar(select(Url))
    url_db.is_active = False
    await session.commit()

    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.get(f'/get_url/{short_url_db}')

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_original_url_short_url_user_unauthorized(client, session, test_url):
    async def get_another_user():
        user = User(
            username='testtest',
            email='testtest@test.com',
            password='testtest'
        )

        session.add(user)
        await session.commit()

        return user

    app.dependency_overrides[get_current_user] = get_another_user

    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.get(f'/get_url/{short_url_db}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_statistic_url_success(client, session, test_url):
    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.get(f'/statistic_url/{short_url_db}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'number_of_clicks': url_db.click_count,
        'is_activate': url_db.is_active,
    }


@pytest.mark.asyncio
async def test_statistic_url_success_shorturl_not_found(client, session, test_url):
    short_url = 'ksnafjibsf'

    response = await client.get(f'/statistic_url/{short_url}')

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_statistic_url_short_url_user_unauthorized(client, session, test_url):
    async def get_another_user():
        user = User(
            username='testtest',
            email='testtest@test.com',
            password='testtest'
        )

        session.add(user)
        await session.commit()

        return user

    app.dependency_overrides[get_current_user] = get_another_user

    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.get(f'/statistic_url/{short_url_db}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_url_success(client, session, test_url):
    url_db = await session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = await client.delete(f'/delete_url/{short_url_db}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'short_url': short_url_db}


@pytest.mark.asyncio
async def test_delete_url_success_shorturl_not_found(client, session, test_url):
    short_url = 'ksnafjibsf'

    response = await client.delete(f'/delete_url/{short_url}')

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_url_short_url_user_unauthorized(client, session, test_url):
    async def get_another_user():
        user = User(
            username='testtest',
            email='testtest@test.com',
            password='testtest'
        )

        session.add(user)
        await session.commit()

        return user


    app.dependency_overrides[get_current_user] = get_another_user

    url_db = await session.scalar(select(Url))
    short_url = str(url_db.short_url)

    response = await client.delete(f'/delete_url/{short_url}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_user_success(client, session):
    response = await client.post( "/create_user/", 
        json={
        'username': 'testtest',
        'email': 'testtest@test.com',
        'password': 'testtest'
        }
    )

    user_db = await session.scalar(select(User).where(
        (User.email == 'testtest@test.com')
        )
    )
       

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': user_db.username,
        'email': user_db.email,
        'id': user_db.id
    }


@pytest.mark.asyncio
async def test_create_user_username_conflict(client, session, test_user):
    response = await client.post( "/create_user/", 
        json={
        'username': test_user.username,
        'email': 'testtest@test.com',
        'password': 'testtest'
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_create_user_email_conflict(client, session, test_user):
    response = await client.post( "/create_user/", 
        json={
        'username': 'testtest',
        'email': test_user.email,
        'password': 'testtest'
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_delete_success(client, session, test_user):
    response = await client.delete(f'/delete_user/{test_user.username}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'email': test_user.email,
        'username': test_user.username
    }


@pytest.mark.asyncio
async def test_delete_success(client, session):
    response = await client.delete(f'/delete_user/{'testtest'}')

    assert response.status_code == HTTPStatus.NOT_FOUND
