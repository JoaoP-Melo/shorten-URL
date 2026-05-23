from http import HTTPStatus
from sqlalchemy import select
from src.auth.models import Url


def test_shoteen_url_success(client, session):
    url = 'www.test.com.br'

    response = client.post('/save/', json={'original_url': url})

    url_in_db = session.scalar(select(Url).where(Url.original_url == url))

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'short_url': url_in_db.short_url}


def test_get_short_url_success(client, session, add_url_in_db):
    url_db = session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = client.get(f"/get_url/{short_url_db}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'original_url': url_db.original_url}


def test_statistic_url_success(client, session, add_url_in_db):
    url_db = session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = client.get(f"/statistic_url/{short_url_db}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'number_of_clicks': url_db.click_count,
        'status': url_db.is_active,
        }


def test_delete_url_success(client, session, add_url_in_db):
    url_db = session.scalar(select(Url))
    short_url_db = str(url_db.short_url)

    response = client.delete(f"/delete_url/{short_url_db}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'short_url': short_url_db}