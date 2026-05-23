from fastapi import FastAPI, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from src.auth.database import get_db
from src.auth.models import Url
from src.auth.service import generator_code_url
from src.auth.schemas import StatisticUrl, ShortUrlRequest, OriginalUrlRequest

load_dotenv()
app = FastAPI()


@app.post('/save_url/', status_code=HTTPStatus.CREATED)
def shoteen_url(data: ShortUrlRequest, session: Session = Depends(get_db)):

    short_url = generator_code_url()

    if session.scalar(select(Url).where(Url.short_url == short_url)):
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    time_expire = datetime.now() + timedelta(
        minutes=int(os.getenv('URL_TIME_EXPIRE'))
    )

    new_url = Url(
        original_url=data.original_url,
        short_url=short_url,
        expires_date=time_expire,
        click_count=0,
        is_active=True,
    )

    session.add(new_url)
    session.commit()
    session.refresh(new_url)

    return {'short_url': short_url}


@app.get('/get_url/{short_url}', status_code=HTTPStatus.OK)
def get_short_url(short_url: str, session: Session = Depends(get_db)):

    url_in_db = session.scalar(select(Url).where(Url.short_url == short_url))

    if url_in_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Short url not found'
        )

    if datetime.now() > url_in_db.expires_date:
        session.execute(
            update(Url)
            .where(Url.short_url == short_url)
            .values(is_active=False)
        )
        session.commit()

        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Short url is deactivated'
        )

    session.execute(
        update(Url)
        .where(Url.short_url == short_url)
        .values(click_count=url_in_db.click_count + 1)
    )
    session.commit()
    return {'original_url': url_in_db.original_url}


@app.get('/statistic_url/{short_url}', status_code=HTTPStatus.OK)
def statistic_url(short_url: str, session: Session = Depends(get_db)):

    url_in_db = session.scalar(select(Url).where(Url.short_url == short_url))

    if url_in_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Short url not found'
        )

    return {
        'number_of_clicks': url_in_db.click_count,
        'status': url_in_db.is_active,
    }


@app.delete('/delete_url/{short_url}', status_code=HTTPStatus.OK)
def delete_url(short_url: str, session: Session = Depends(get_db)):

    url_in_db = session.scalar(select(Url).where(Url.short_url == short_url))

    if url_in_db is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Short url not found'
        )

    session.delete(url_in_db)
    session.commit()

    return {'short_url': url_in_db.short_url}
