# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ
from typing import List, Optional

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
# profiling
#from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.add_middleware(PyInstrumentProfilerMiddleware)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home():
    """ Message d'accueil """
    return {
        'message': 'Welcome to building RESTful APIs with FastAPI'
    }


@app.get("/contacts", response_class=ORJSONResponse)
async def read_contacts(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    try:
        contacts = contact.get_contacts(db, X_User_UUID)
    except:
        return HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get('/adherents', response_class=ORJSONResponse)
async def get_adherents(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    return contact.get_number_of_contacts(db, X_User_UUID)



@app.get('/jemengage/downloads', response_class=ORJSONResponse)
async def jemengage_downloads(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    res = jemengage.get_downloads(db, X_User_UUID)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/users', response_class=ORJSONResponse)
async def jemengage_users(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    res = jemengage.get_users(db, X_User_UUID)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'users': json.loads(res)}


@app.get('/jemengage/survey', response_model=List[schemas.JecouteDataSurvey], response_class=ORJSONResponse)
async def jemengage_survey(
    db: Session = Depends(get_db),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if not X_User_UUID:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    return jemengage.get_survey(db, X_User_UUID)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    	)
