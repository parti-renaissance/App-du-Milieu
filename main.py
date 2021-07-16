# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ
from datetime import datetime
import json

import uvicorn

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
# profiling
#from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


from app.crud import contact, enmarche, jemengage, mail_campaign
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
    if (scope is None):
        raise HTTPException(status_code=400, detail='No scope parameter')
    if (X_Scope is None):
        raise HTTPException(status_code=400, detail='No X-Scope in header')

    if (scope := enmarche.decode_scopes(db, X_Scope)) is None:
        raise HTTPException(status_code=203,
                            detail='You have no candidate area affected.')

    return scope


@app.get("/")
async def home():
    """ Message d'accueil """
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

    res = res.to_json(orient='records')
    return {'downloads': json.loads(res)}


@app.get('/jemengage/users', response_class=ORJSONResponse)
async def jemengage_users(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    res = jemengage.get_users(db, selected_scope)
    if res.empty:
        raise HTTPException(status_code=204, detail='No content')

    res = res.to_json(orient='records')
    return {'users': json.loads(res)}


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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    )
