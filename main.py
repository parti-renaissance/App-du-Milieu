# -*- coding: utf-8 -*-
"""
A sample flask application on Cloud Run. Version 1
"""
from os import environ
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.dependencies import CommonQueryParams

import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
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
def read_contacts(db: Session = Depends(get_db), commons: CommonQueryParams = Depends(CommonQueryParams)):
    return crud.get_contacts(db, commons)


@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


if __name__ == "__main__":
    uvicorn.run(
        app,
    	debug=True,
    	host="0.0.0.0",
        port=int(environ.get("PORT", 8080))
    	)
