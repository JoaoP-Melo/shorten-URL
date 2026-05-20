from fastapi import FastAPI, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from src.auth.database import get_db
from src.auth.models import Url
from src.auth.service import generator_code_url
from src.auth.schemas import PrivateUrl

load_dotenv()
app = FastAPI()

@app.post("/{url}/", status_code=HTTPStatus.CREATED)
def shoteen_url(original_url: str, session: Session = Depends(get_db)):
    short_url = generator_code_url()
    time_expire = datetime.now() + timedelta(
        minutes=int(os.getenv("URL_TIME_EXPIRE"))
    )

    new_url = Url(
        original_url= original_url, 
        short_url= short_url, 
        expires_date= time_expire,
        click_count= 0,
        is_active=True)
    
    session.add(new_url)
    session.commit()
    session.refresh(new_url)
    
    return short_url