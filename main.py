# -*- coding: utf-8 -*-
"""A sample flask application on Cloud Run."""
from os import environ
from datetime import datetime
import json
import base64

import uvicorn
from pydantic import constr, conint
from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
# profiling
# from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.crud import contact, enmarche, jemengage, mail_campaign, elections
from app.crud import text_generator
from app.database import SessionLocal

app = FastAPI(
    title="API pour le CRM de LaREM",
    description="GET uniquements pour récupérer les données des contacts de notre base",
    version="1.0.0")
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(PyInstrumentProfilerMiddleware)

# Dependency

MAILLAGE_PATTERN = r'^(region|departement|circonscription|canton|commune|bureau)$'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_scopes(
        scope: str,
        X_Scope: str = Header(None),
        db: Session = Depends(get_db)) -> dict:
    if scope is None:
        raise HTTPException(status_code=400, detail='No scope parameter')
    if X_Scope is None:
        raise HTTPException(status_code=400, detail='No X-Scope in header')
    
    try:
        scope = enmarche.decode_scopes(db, X_Scope)
    except base64.binascii.Error as err:
        raise HTTPException(status_code=422,
                            detail=f'Could not decode scope - {err}')
    except json.decoder.JSONDecodeError as err:
        raise HTTPException(status_code=422,
                            detail=f'Could not decode scope - {err}')

    return scope


@app.get("/")
async def home():
    """Message d'accueil"""
    return {
        'message': 'Welcome to building RESTful APIs with FastAPI'
    }


@app.get("/contacts", response_class=ORJSONResponse)
async def read_contacts(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    try:
        contacts = contact.get_contacts(db, selected_scope)
    except BaseException:
        raise HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get("/contacts-v01", response_class=ORJSONResponse)
async def read_contacts_v01(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    try:
        contacts = contact.get_contacts_v01(db, selected_scope, skip, limit)
    except BaseException:
        raise HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get("/contacts-v02", response_class=ORJSONResponse)
async def read_contacts_v02(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    q: list = Query([])
):
    try:
        contacts = contact.get_contacts_v02(db, selected_scope, skip, limit, q)
    except BaseException:
        raise HTTPException(status_code=204, detail='No contact found')
    return contacts


@app.get('/adherents', response_class=ORJSONResponse)
async def get_adherents(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    return contact.get_number_of_contacts(db, selected_scope)


@app.get('/jemengage/downloads', response_class=ORJSONResponse)
async def jemengage_downloads(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = jemengage.get_downloads(db, selected_scope)
    if res.empty:
        raise HTTPException(status_code=204, detail='No content')

    total = int(res.unique_user.sum())

    res = res.to_json(orient='records')
    return {'totalDownloads': total, 'downloads': json.loads(res)}


@app.get('/jemengage/users', response_class=ORJSONResponse)
async def jemengage_users(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = jemengage.get_users(db, selected_scope)
    if res.empty:
        raise HTTPException(status_code=204, detail='No content')

    total = int(res.unique_user.sum())

    res = res.to_json(orient='records')
    return {'totalUsers': total, 'users': json.loads(res)}


@app.get('/jemengage/survey', response_class=ORJSONResponse)
async def jemengage_survey(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    return jemengage.get_survey(db, selected_scope)


@app.get('/mailCampaign/reports', response_class=ORJSONResponse)
async def mail_reports(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    since: datetime = datetime(2021, 1, 1)
):
    result = [await mail_campaign.get_campaign_reports(db, zone, since, selected_scope['code']) for zone in selected_scope['zones']]
    return result


@app.get('/mailCampaign/reportsRatios', response_class=ORJSONResponse)
async def mail_ratios(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    since: datetime = datetime(2021, 1, 1)
):
    result = await mail_campaign.get_mail_ratios(db, selected_scope, since)
    return {
        'zones': [
            zone.name for zone in selected_scope['zones']],
        'depuis': since,
        **result}


@app.get('/election/participation', response_class=ORJSONResponse)
async def election_participation(
    election: constr(min_length = 1),
    maillage: constr(regex = MAILLAGE_PATTERN),
    code_zone: constr(min_length = 1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = elections.get_participation(db, selected_scope, election, tour, maillage, code_zone)
    if res.empty:
        return []

    res = res.to_json(orient='records')
    return json.loads(res)


@app.get('/election/results', response_class=ORJSONResponse)
async def election_results(
    election: constr(min_length = 1),
    maillage: constr(regex = MAILLAGE_PATTERN),
    code_zone: constr(min_length = 1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = elections.get_results(db, selected_scope, election, tour, maillage, code_zone)
    if res.empty:
        return []

    res = res.to_json(orient='records')
    return json.loads(res)


@app.get('/election/colors', response_class=ORJSONResponse)
async def election_colors(
    election: constr(min_length = 1),
    maillage: constr(regex = MAILLAGE_PATTERN),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = elections.get_colors(db, selected_scope, election, tour, maillage)
    if res.empty:
        return []

    res = res.to_json(orient='records')
    return json.loads(res)


@app.get('/election/nuanceResults', response_class=ORJSONResponse)
async def nuanceResults(
    election: constr(min_length = 1),
    maillage: constr(regex = MAILLAGE_PATTERN),
    nuance_liste: constr(min_length = 1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = elections.get_nuance_results(db, selected_scope, election, tour, maillage, nuance_liste)
    if res.empty:
        return []

    res = res.to_json(orient='records')
    return json.loads(res)


@app.get('/textGenerator', response_class=ORJSONResponse)
async def generate_text(
    text: constr(min_length = 1),
    from_language: str = 'FR'
):
    res = text_generator.generate_text(text, from_language)
    return res['text']


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    )
