# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
# profiling
#from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from datetime import datetime

from app.crud import contact, enmarche, jemengage, mail_campaign, elections
from app.models.models_enmarche import GeoZone
from app.schemas import schemas
from app.database import SessionLocal

from typing import List

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


async def get_scopes(
    X_Scope: str = Header(None),
    db: Session = Depends(get_db)) -> dict:
    if X_Scope is None:
        raise HTTPException(status_code=401, detail='You are not authenticated.')
    
    if (scopes := enmarche.decode_scopes(db, X_Scope)) is None:
        raise HTTPException(status_code=203, detail='You have no candidate area affected.')

    return scopes

# TODO DELETE
@app.get("/testScopes", response_class=ORJSONResponse, response_model=schemas.ScopesOut)
def testScopes(
    X_Scope: str = Header(None),
    db: Session = Depends(get_db)) -> dict:
    return enmarche.decode_scopes(db, X_Scope)


@app.get("/")
async def home():
    """ Message d'accueil """
    return {
        'message': 'Welcome to building RESTful APIs with FastAPI'
    }


@app.get("/contacts", response_class=ORJSONResponse)
async def read_contacts(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    print(f'get /contacts: {scope}')
    contacts = contact.get_contacts(db, scope)
    '''
    try:
        contacts = contact.get_contacts(db, scope)
    except:
        return HTTPException(status_code=204, detail='No contact found')
    '''
    return contacts


@app.get('/adherents', response_class=ORJSONResponse)
async def get_adherents(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    return contact.get_number_of_contacts(db, scope)


@app.get('/jemengage/downloads', response_class=ORJSONResponse)
async def jemengage_downloads(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    res = jemengage.get_downloads(db, scope)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/downloadsRatios', response_class=ORJSONResponse)
async def jemengage_downloads_ratio(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    res = jemengage.downloads_ratio(db, scope)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/users', response_class=ORJSONResponse)
async def jemengage_users(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    res = jemengage.get_users(db, scope)
    if res.empty:
        return HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'users': json.loads(res)}


@app.get('/jemengage/survey', response_model=schemas.JecouteDataSurveyOut, response_class=ORJSONResponse)
async def jemengage_survey(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    return jemengage.get_survey(db, scope)


@app.get('/mailCampaign/reports', response_model=schemas.MailReportOut, response_class=ORJSONResponse)
async def mail_reports(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    since: datetime = datetime(2021, 1, 1)
    ):
    result = await mail_campaign.get_candidate_reports(db, scope, since)
    return result


@app.get('/mailCampaign/reportsRatios', response_model=schemas.MailRatiosOut, response_class=ORJSONResponse)
async def mail_ratios(
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    since: datetime = datetime(2021, 1, 1)
    ):
    result = await mail_campaign.get_mail_ratios(db, scope, since)
    return {'zones': [zone.name for zone in scope['zones']], 'depuis': since, **result}


@app.get('/elections', response_class=ORJSONResponse, response_model_exclude_unset=True)
async def get_elections(
    election: str,
    tour: int = 1,
    scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
    ):
    if election not in elections.available_elections:
        return HTTPException(status_code=422, detail="The election is not available yet")
    if tour not in [1,2]:
        return HTTPException(status_code=422, detail="parameter 'tour' must be 1 or 2")

    result = elections.get_elections(election, tour, scope, db)
    return result


@app.get('/availableElections')
def get_available_elections():
    return {'availableElections': elections.available_elections}


if __name__ == "__main__":
    uvicorn.run(
        app='main:app',
        reload=True,
        port=8080
        #host="0.0.0.0",
        #port=int(environ.get("PORT", 8080))
    	)
