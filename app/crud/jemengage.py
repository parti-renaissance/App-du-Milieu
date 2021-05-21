"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, Date
from datetime import date, timedelta

from app.models.models_enmarche import GeoZone, GeoCity, GeoDepartment, GeoRegion
from app.models.models_enmarche import JecouteDataSurvey
from app.models.models_crm import Downloads, Users
from app.database.database_crm import engine_crm

import pandas as pd


def get_downloads(
    db: Session,
    zone: GeoZone,
    before: Date = date.today(),
    range: int = 28
    ):
    after = before - timedelta(days=range)

    query = db.query(Downloads.date, Downloads.unique_user) \
            .filter(Downloads.zone_type == zone.type) \
            .filter(Downloads.zone_name == zone.name) \
            .filter(Downloads.date < before) \
            .filter(Downloads.date >= after) \
            .statement

    df = pd.read_sql(query, engine_crm)
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(after, before - timedelta(days=1))
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date')
        # fill unique user to 0
        df['unique_user'] = df['unique_user'].fillna(0).astype(int)
        # fill cumulative to previous value
        df['cumsum'] = df['unique_user'].cumsum()

        df.reset_index(inplace=True)
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df


def downloads_ratio(
    db: Session,
    zone: GeoZone,
    before: Date = date.today(),
    range: int = 28
    ):
    after = before - timedelta(days=range)

    query = db.query(Downloads.date, Downloads.downloadsPer1000) \
            .filter(Downloads.zone_type == zone.type) \
            .filter(Downloads.zone_name == zone.name) \
            .filter(Downloads.date < before) \
            .filter(Downloads.date >= after) \
            .statement

    filter_nat = {'zone_type': 'pays', 'zone_name': 'France'}
    query_nat = db.query(Downloads.date, Downloads.downloadsPer1000) \
            .filter_by(**filter_nat) \
            .filter(Downloads.date < before) \
            .filter(Downloads.date >= after) \
            .statement

    df_nat = pd.read_sql(query_nat, engine_crm)
    df_nat.rename(columns={'downloadsPer1000': 'nationalPer1000'}, inplace=True)
    df_nat['date'] = pd.to_datetime(df_nat['date'], format='%Y-%m-%d')

    df = pd.read_sql(query, engine_crm)
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(after, before - timedelta(days=1))
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date')
        # fill unique user to 0
        df['downloadsPer1000'] = df['downloadsPer1000'].fillna(method='ffill').round(3)
        df_nat['nationalPer1000'] = df_nat['nationalPer1000'].fillna(method='ffill').round(3)

        df.reset_index(inplace=True)
        df = df.merge(df_nat)
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df


def get_users(
    db: Session,
    zone: GeoZone,
    before: Date = date.today(),
    range: int = 28
    ):
    after = before - timedelta(days=range)

    query = db.query(Users.date, Users.unique_user) \
            .filter(Users.zone_type == zone.type) \
            .filter(Users.zone_name == zone.name) \
            .filter(Users.date < before) \
            .filter(Users.date >= after - timedelta(7)) \
            .statement

    df = pd.read_sql(query, engine_crm)
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(after - timedelta(7), before - timedelta(days=1))
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date')
        # fill unique user to 0
        df['unique_user'] = df['unique_user'].fillna(0).astype(int)
        # fill cumulative to previous value
        df['rolling_seven_users'] = df.rolling(7).sum().fillna(0).astype(int)
        
        df.reset_index(inplace=True)
        df = df[df.date >= pd.to_datetime(after)]
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df


def get_survey(
    db: Session,
    zone: GeoZone
    ):    
    if zone.type == 'department':
        geo_dpt = db.query(GeoDepartment) \
            .filter(GeoDepartment.code == zone.code) \
            .first()
        return {
            "zone_name": zone.name,
            "latitude": geo_dpt.latitude,
            "longitude": geo_dpt.longitude,
            "survey_datas": db.query(JecouteDataSurvey) \
            .options(joinedload(JecouteDataSurvey.author)) \
            .options(joinedload(JecouteDataSurvey.survey)) \
            .filter(JecouteDataSurvey.postal_code != '') \
            .join(GeoCity, func.instr(GeoCity.postal_code, JecouteDataSurvey.postal_code)) \
            .join(GeoDepartment) \
            .filter(GeoDepartment.code == zone.code) \
            .filter(JecouteDataSurvey.latitude != '') \
            .filter(JecouteDataSurvey.longitude != '') \
            .all()
        }

    if zone.type == 'region':
        geo_reg =  db.query(GeoRegion) \
            .filter(GeoRegion.code == zone.code) \
            .first()
        return {
            "zone_name": zone.name,
            "latitude": geo_reg.latitude,
            "longitude": geo_reg.longitude,
            "survey_datas": db.query(JecouteDataSurvey) \
                .options(joinedload(JecouteDataSurvey.author)) \
                .options(joinedload(JecouteDataSurvey.survey)) \
                .filter(JecouteDataSurvey.postal_code != '') \
                .join(GeoCity, GeoCity.postal_code.like('%' + JecouteDataSurvey.postal_code + '%')) \
                .join(GeoDepartment) \
                .join(GeoRegion) \
                .filter(GeoRegion.code == zone.code) \
                .filter(JecouteDataSurvey.latitude != '') \
                .filter(JecouteDataSurvey.longitude != '') \
                .all()
        }
