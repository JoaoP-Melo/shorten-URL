from nanoid import generate
from fastapi import HTTPException
from http import HTTPStatus
from datetime import datetime
from src.auth.models import Url
from sqlalchemy import update


def generator_code_url():
    return generate(size=8)


def validate_url_exists(query_result_url):
    if query_result_url is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Short url not found"
        )


def validate_url_id(id_url, id_current_user):
    if id_url != id_current_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="This URL belongs to another user.",
        )


async def validate_expire_time_url(query_result_url, session):
    if datetime.now() > query_result_url.expires_date:
        await session.execute(
            update(Url)
            .where(Url.short_url == query_result_url.short_url)
            .values(is_active=False)
        )

        await session.commit()
