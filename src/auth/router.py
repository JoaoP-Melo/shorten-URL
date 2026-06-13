from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from http import HTTPStatus
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from src.auth.database import get_db
from src.auth.models import Url, User
from src.auth.service import (
    generator_code_url,
    validate_url_exists,
    validate_url_id,
    validate_expire_time_url,
)
from src.auth.schemas import (
    ShortUrlRequest,
    PrivateUser,
    PublicUser,
)
from src.auth.security import (
    get_password_hash,
    verify_password,
    create_token,
    get_current_user,
)

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
URL_TIME_EXPIRE = int(os.getenv("URL_TIME_EXPIRE"))
app = FastAPI()


@app.post("/save_url/", status_code=HTTPStatus.CREATED)
async def shoteen_url(
    data: ShortUrlRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    short_url = generator_code_url()

    while await session.scalar(select(Url).where(Url.short_url == short_url)):
        short_url = generator_code_url()

    time_expire = datetime.now() + timedelta(minutes=int(URL_TIME_EXPIRE))

    new_url = Url(
        original_url=data.original_url,
        short_url=short_url,
        expires_date=time_expire,
        click_count=0,
        is_active=True,
        user_id=current_user.id,
    )

    session.add(new_url)
    await session.commit()
    await session.refresh(new_url)

    return {"short_url": short_url}


@app.get("/get_url/{short_url}", status_code=HTTPStatus.OK)
async def get_original_url(
    short_url: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    url_in_db = await session.scalar(select(Url).where(Url.short_url == short_url))

    validate_url_exists(url_in_db)

    await validate_expire_time_url(url_in_db, session)

    if url_in_db.is_active == False:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Short url is deactivated"
        )

    validate_url_id(url_in_db.user_id, current_user.id)

    url_in_db.click_count += 1
    await session.commit()

    return {"original_url": url_in_db.original_url}


@app.get("/statistic_url/{short_url}", status_code=HTTPStatus.OK)
async def statistic_url(
    short_url: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    url_in_db = await session.scalar(select(Url).where(Url.short_url == short_url))

    validate_url_exists(url_in_db)

    validate_url_id(url_in_db.user_id, current_user.id)

    await validate_expire_time_url(url_in_db, session)

    return {
        "number_of_clicks": url_in_db.click_count,
        "is_activate": url_in_db.is_active,
    }


@app.delete("/delete_url/{short_url}", status_code=HTTPStatus.OK)
async def delete_url(
    short_url: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    url_in_db = await session.scalar(select(Url).where(Url.short_url == short_url))

    validate_url_exists(url_in_db)

    validate_url_id(url_in_db.user_id, current_user.id)

    await session.delete(url_in_db)
    await session.commit()

    return {"short_url": url_in_db.short_url}


@app.post("/create_user/", status_code=HTTPStatus.CREATED, response_model=PublicUser)
async def create_user(user: PrivateUser, session: AsyncSession = Depends(get_db)):
    existing_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        elif existing_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"username": new_user.username, "email": new_user.email, "id": new_user.id}


@app.delete("/delete_user/{current_user.id}", status_code=HTTPStatus.OK)
async def delete_user(
    username: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    existing_user = await session.scalar(
        select(User).where((User.username == username))
    )

    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )

    if existing_user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="This profile belongs to another user.",
        )

    await session.delete(existing_user)
    await session.commit()

    return {"email": existing_user.email, "username": existing_user.username}


@app.post("/token/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    user = await session.scalar(select(User).where(User.username == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
