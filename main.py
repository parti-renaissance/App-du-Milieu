# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ
from typing import List

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
# profiling
#from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.crud import contact, enmarche, jemengage
from app.models.models_enmarche import GeoZone
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


async def get_uuid_zone(
    X_User_UUID: str = Header(None),
    db: Session = Depends(get_db)) -> GeoZone:
    if X_User_UUID is None:
        raise HTTPException(status_code=401, detail='You are not authenticated.')
    
    if (zone := enmarche.get_candidate_zone(db, X_User_UUID)) is None:
        raise HTTPException(status_code=203, detail='You have no candidate area affected.')

    return zone


async def get_filter_zone(zone: GeoZone = Depends(get_uuid_zone)):
    filter_zone = {'departement': zone.name} if zone.type == 'department' else {zone.type: zone.name}
    return filter_zone


@app.get("/")
async def home():
    """ Message d'accueil """
    return {
        'message': 'Welcome to building RESTful APIs with FastAPI'
    }


@app.get("/contacts", response_class=ORJSONResponse)
async def read_contacts(
    filter_zone: dict = Depends(get_filter_zone),
    db: Session = Depends(get_db)
    ):
    try:
        contacts = contact.get_contacts(db, filter_zone)
    except:
        return HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get('/adherents', response_class=ORJSONResponse)
async def get_adherents(
    filter_zone: dict = Depends(get_filter_zone),
    db: Session = Depends(get_db)
    ):
    return contact.get_number_of_contacts(db, filter_zone)


@app.get('/jemengage/downloads', response_class=ORJSONResponse)
async def jemengage_downloads(
    zone: dict = Depends(get_uuid_zone),
    db: Session = Depends(get_db)
    ):
    res = jemengage.get_downloads(db, zone)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/downloadsRatios', response_class=ORJSONResponse)
async def jemengage_downloads_ratio(
    zone: dict = Depends(get_uuid_zone),
    db: Session = Depends(get_db)
    ):
    res = jemengage.downloads_ratio(db, zone)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/users', response_class=ORJSONResponse)
async def jemengage_users(
    zone: dict = Depends(get_uuid_zone),
    db: Session = Depends(get_db)
    ):
    res = jemengage.get_users(db, zone)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'users': json.loads(res)}


@app.get('/jemengage/survey', response_model=schemas.JecouteDataSurveyOut, response_class=ORJSONResponse)
async def jemengage_survey(
    zone: dict = Depends(get_uuid_zone),
    db: Session = Depends(get_db)
    ):
    return jemengage.get_survey(db, zone)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    	)
