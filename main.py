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

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.dependencies import CommonQueryParams

import uvicorn

models.Base.metadata.create_all(bind=engine)

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
    commons: CommonQueryParams = Depends(CommonQueryParams),
    X_User_UUID: Optional[str] = Header(None)
    ):
    if X_User_UUID is None:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    me = crud.me(db, X_User_UUID)
    if me is None:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    contacts = crud.get_contacts(db, commons, adherent=me)
    if contacts is None:
        raise HTTPException(status_code=404, detail='No contact found')
    return contacts


@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int,
    db: Session = Depends(get_db),
    uuid: Optional[str] = Header(None)
    ):
    if uuid is None:
        return HTTPException(status_code=401, detail='You are not authenticated.')

    me = crud.me(db, uuid)
    if me is None:
        return HTTPException(status_code=403, detail='You are not allowed to access these datas.')

    contact = crud.get_contact(db, id=contact_id, adherent=me)
    if contact is None:
        raise HTTPException(status_code=404, detail='Contact not found')
    return contact


if __name__ == "__main__":
    uvicorn.run(
        app,
    	debug=True,
    	host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    	)
