"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Date
from datetime import date, timedelta

from typing import Optional
from app.models.models_enmarche import Adherents
from app.models.models_crm import Downloads, Users
from app.crud.enmarche import me, get_candidate_zone

import pandas as pd


def get_downloads(
    db: Session,
    adherent: Adherents,
    before: Date = date.today(),
    range: int = 28
    ):
    zone = get_candidate_zone(db, adherent)
    if zone is None:
        return None

    # We first add filter by geo_zone
    filter_zone = {'zone_type': zone.type, 'zone_name': zone.name}

    after = before - timedelta(days=range)

    query = db.query(Downloads) \
            .filter_by(**filter_zone) \
            .filter(Downloads.date < before) \
            .filter(Downloads.date >= after) \
            .statement

    df = pd.read_sql(query, engine_crm).drop(columns=['index', 'zone_type', 'zone_name'])
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(after, before - timedelta(days=1))
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date')
        # fill unique user to 0
        df['unique_user'] = df['unique_user'].fillna(0).astype(int)
        # fill cumulative to previous value
        df['cumsum'] = df.cumsum()

        df.reset_index(inplace=True)
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df


def get_users(
    db: Session,
    adherent: Adherents,
    before: Date = date.today(),
    range: int = 28
    ):
    zone = get_candidate_zone(db, adherent)
    if zone is None:
        return None

    # We first add filter by geo_zone
    filter_zone = {'zone_type': zone.type, 'zone_name': zone.name}

    after = before - timedelta(days=range)

    query = db.query(Users) \
            .filter_by(**filter_zone) \
            .filter(Users.date < before) \
            .filter(Users.date >= after - timedelta(7)) \
            .statement

    df = pd.read_sql(query, engine_crm).drop(columns=['index', 'zone_type', 'zone_name'])
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(after - timedelta(7), before - timedelta(days=1))
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date')
        # fill unique user to 0
        df['unique_user'] = df['unique_user'].fillna(0).astype(int)
        # fill cumulative to previous value
        df['7days_users'] = df.rolling(7).sum().fillna(0).astype(int)
        
        df.reset_index(inplace=True)
        df = df[df.date >= pd.to_datetime(after)]
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df
