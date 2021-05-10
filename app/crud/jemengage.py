"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, Date
from datetime import date, timedelta

from typing import Optional
from app.models.models_enmarche import GeoCity, GeoDepartment, GeoRegion
from app.models.models_enmarche import Adherents, JecouteDataSurvey, JecouteSurvey
from app.models.models_crm import Downloads, Users
from app.crud.enmarche import me, get_candidate_zone
from app.database.database_crm import engine_crm

import pandas as pd


def get_downloads(
    db: Session,
    uuid: str,
    before: Date = date.today(),
    range: int = 28
    ):
    if (zone := get_candidate_zone(db, uuid)) is None:
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
    uuid: str,
    before: Date = date.today(),
    range: int = 28
    ):
    if (zone := get_candidate_zone(db, uuid)) is None:
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

def get_survey(
    db: Session,
    uuid: str
    ):
    if (zone := get_candidate_zone(db, uuid)) is None:
        return None
    
    if zone.type == 'department':
        return db.query(JecouteDataSurvey, JecouteSurvey) \
            .filter(JecouteDataSurvey.postal_code is not None) \
            .join(GeoCity, func.instr(GeoCity.postal_code, JecouteDataSurvey.postal_code)) \
            .join(GeoDepartment) \
            .join(JecouteSurvey) \
            .filter(GeoDepartment.code == zone.code) \
            .filter(JecouteDataSurvey.latitude != '') \
            .filter(JecouteDataSurvey.longitude != '') \
            .all()

    if zone.type == 'region':
        return db.query(JecouteDataSurvey) \
            .options(joinedload(JecouteDataSurvey.jecoute_survey)) \
            .filter(JecouteDataSurvey.postal_code != '') \
            .join(GeoCity, GeoCity.postal_code.like('%' + JecouteDataSurvey.postal_code + '%')) \
            .join(GeoDepartment) \
            .join(GeoRegion) \
            .filter(GeoRegion.code == zone.code) \
            .filter(JecouteDataSurvey.latitude != '') \
            .filter(JecouteDataSurvey.longitude != '') \
            .all()
