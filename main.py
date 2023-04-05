# -*- coding: utf-8 -*-

# Standard library imports
from os import environ
from datetime import date, timedelta
import base64
import json

# Third-party imports
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import conint, constr
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from typing import Optional

# Local application imports
from app.database import SessionLocal
from app.resources.strings import NO_CONTENT, NO_CONTACT, NO_SCOPE, NO_X_SCOPE
from app.schemas import schemas
from app.crud import (
    contact,
    elections,
    enmarche,
    jemengage,
    mail_campaign,
)

# Sentry error tracking setup
sentry_sdk.init(dsn="https://3c3c435fe4f245a3ba551475ff8dfa53@o62282.ingest.sentry.io/5890683")

# FastAPI app setup
app = FastAPI(
    title="API pour le CRM de LaREM",
    description="GET uniquements pour récupérer les données des contacts de notre base",
    version="1.0.0",
)

# Middleware setup
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SentryAsgiMiddleware)

# Constant variables
MAX_HISTORY = 30

# API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# define scope dependency
async def get_scopes(
    scope: str, X_Scope: str = Header(None), db: Session = Depends(get_db)
) -> dict:
    if scope is None:
        raise HTTPException(status_code=400, detail=NO_SCOPE)
    if X_Scope is None:
        raise HTTPException(status_code=400, detail=NO_X_SCOPE)

    try:
        return enmarche.decode_scopes(db, X_Scope)
    except (base64.binascii.Error, json.decoder.JSONDecodeError) as err:
        raise HTTPException(status_code=422, detail=f"Could not decode scope - {err}")

@app.get("/")
async def home():
    """Message d'accueil"""
    return {"message": "Welcome to building RESTful APIs with FastAPI"}


@app.get("/contacts", response_class=ORJSONResponse)
async def read_contacts(
    selected_scope: dict = Depends(get_scopes), db: Session = Depends(get_db)
):
    try:
        contacts = contact.get_contacts(db, selected_scope)
    except BaseException:
        raise HTTPException(status_code=204, detail=NO_CONTACT)
    return contacts


@app.get("/contacts-v01", response_class=ORJSONResponse)
async def read_contacts_v01(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    try:
        contacts = contact.get_contacts_v01(db, selected_scope, skip, limit)
    except BaseException:
        raise HTTPException(status_code=204, detail=NO_CONTACT)
    return contacts


@app.get("/contacts-v02", response_class=ORJSONResponse)
async def read_contacts_v02(
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    q: list = Query([]),
):
    try:
        contacts = contact.get_contacts_v02(db, selected_scope, skip, limit, q)
    except BaseException:
        raise HTTPException(status_code=204, detail=NO_CONTACT)
    return contacts


@app.get("/adherents", response_class=ORJSONResponse)
async def get_adherents(
    selected_scope: dict = Depends(get_scopes), db: Session = Depends(get_db)
):
    return contact.get_number_of_contacts(db, selected_scope)


@app.get("/jemengage/downloads", response_class=ORJSONResponse)
async def jemengage_downloads(
    selected_scope: dict = Depends(get_scopes), db: Session = Depends(get_db)
):
    res = jemengage.get_downloads(db, selected_scope)
    if res.empty:
        raise HTTPException(status_code=204, detail=NO_CONTENT)

    total = int(res.unique_user.sum())

    res = res.to_json(orient="records")
    return {"totalDownloads": total, "downloads": json.loads(res)}


@app.get("/jemengage/users", response_class=ORJSONResponse)
async def jemengage_users(
    selected_scope: dict = Depends(get_scopes), db: Session = Depends(get_db)
):
    res = jemengage.get_users(db, selected_scope)
    if res.empty:
        raise HTTPException(status_code=204, detail=NO_CONTENT)

    total = int(res.unique_user.sum())

    res = res.to_json(orient="records")
    return {"totalUsers": total, "users": json.loads(res)}


@app.get("/jemengage/survey", response_class=ORJSONResponse, response_model=schemas.JemarcheDataSurveyOut)
async def jemengage_survey(
    max_history: Optional[conint(ge=1)] = MAX_HISTORY,
    survey_uuid: Optional[constr(min_length=36, max_length=36)] = None,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    return jemengage.get_survey(db, selected_scope, max_history, survey_uuid)


@app.get("/mailCampaign/reports", response_class=ORJSONResponse)
async def mail_reports(
    max_history: Optional[conint(ge=1)] = MAX_HISTORY,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    return [
        await mail_campaign.get_campaign_reports(
            db, zone, max_history, selected_scope["code"]
        )
        for zone in selected_scope["zones"]
    ]


@app.get("/mailCampaign/reportsRatios", response_class=ORJSONResponse)
async def mail_ratios(
    max_history: Optional[conint(ge=1)] = MAX_HISTORY,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db)
):
    result = await mail_campaign.get_mail_ratios(
        db, selected_scope['zones'], max_history, selected_scope['code']
    )
    return {
        "zones": [zone.name for zone in selected_scope["zones"]],
        "since": (date.today() - timedelta(days=max_history)).strftime("%Y-%m-%dT%H:%M:%S"),
        **result,
    }


@app.get("/election/participation", response_class=ORJSONResponse)
async def election_participation(
    election: elections.ELECTION,
    maillage: elections.DIVISION,
    code_zone: constr(min_length=1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
):
    res = elections.get_participation(
        db, selected_scope, election, tour, maillage, code_zone
    )
    if res.empty:
        return []

    res = res.to_json(orient="records")
    return json.loads(res)


@app.get("/election/results", response_class=ORJSONResponse)
async def election_results(
    election: elections.ELECTION,
    maillage: elections.DIVISION,
    code_zone: constr(min_length=1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
):
    res = elections.get_results(db, selected_scope, election, tour, maillage, code_zone)
    if res.empty:
        return []

    res = res.to_json(orient="records")
    return json.loads(res)


@app.get("/election/density", response_class=ORJSONResponse)
async def nuanceResults(
    election: elections.ELECTION,
    maillage: elections.DIVISION,
    nuance_liste: constr(min_length=1),
    tour: conint(ge=1, le=2) = 1,
    selected_scope: dict = Depends(get_scopes),
    db: Session = Depends(get_db),
):
    res = elections.get_density(
        db, selected_scope, election, tour, maillage, nuance_liste
    )
    if res.empty:
        return []

    res = res.to_json(orient="records")
    return json.loads(res)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(environ.get("PORT", 8080)))
