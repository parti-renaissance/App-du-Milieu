# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ
from typing import List, Optional

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.crud import contact, enmarche, jemengage
from app.schemas import schemas
from app.database import SessionLocal

import uvicorn
import json

app = FastAPI(
    title="API pour le CRM de LaREM",
    description="GET uniquements pour récupérer les données des contacts de notre base",
    version="1.0.0"
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    """ Message d'accueil """
    return {
        'message': 'Welcome to building RESTful APIs with FastAPI'
    }


@app.get("/contacts")
def read_contacts(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    try:
        me = enmarche.me(db, X_User_UUID)
    except:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    try:
        contacts = contact.get_contacts(db, adherent=me)
    except:
        return HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get('/adherents')
def get_adherents(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    try:
        me = enmarche.me(db, X_User_UUID)
    except:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    return contact.get_number_of_contacts(db, me)



@app.get('/jemengage/downloads')
def jemengage_downloads(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    try:
        me = enmarche.me(db, X_User_UUID)
    except:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    res = jemengage.get_downloads(db, me)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/users')
def jemengage_users(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    try:
        me = enmarche.me(db, X_User_UUID)
    except:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    res = jemengage.get_users(db, me)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    	)
