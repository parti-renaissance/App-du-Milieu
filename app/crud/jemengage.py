"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, Date
from datetime import date, timedelta

from app.crud.enmarche import scope2dict, get_child
from app.database.database_crm import engine_crm
from app.models.models_enmarche import GeoZone, GeoCity, GeoDepartment, GeoRegion
from app.models.models_enmarche import JecouteDataSurvey
from app.models.models_crm import Downloads, Users

import pandas as pd


def get_downloads(
    db: Session,
    scope: dict,
    before: Date = date.today(),
    range: int = 28
    ):
    after = before - timedelta(days=range)

    # series of all date from min to max
    s_date = pd.date_range(after, before - timedelta(days=1))

    empty = pd.DataFrame(s_date, columns=['date'])
    empty['unique_user'] = 0
    df_list = [empty]

    for k, v in scope2dict(scope, True).items():
        query = db.query(Downloads.date, Downloads.unique_user) \
                .filter(Downloads.zone_type == k) \
                .filter(Downloads.zone_name.in_(v)) \
                .filter(Downloads.date < before) \
                .filter(Downloads.date >= after) \
                .statement

        df = pd.read_sql(query, engine_crm)
        if not df.empty:
            # fill missing date
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            df = df.groupby('date').sum().reindex(s_date).rename_axis('date')
            # fill unique user to 0
            df['unique_user'] = df['unique_user'].fillna(0).astype(int)

            df.reset_index(inplace=True)
            df_list = [*df_list, df]

    big_df = pd.concat(df_list)
    big_df = big_df.groupby(['date']).sum().reset_index()
    big_df['date'] = big_df['date'].dt.strftime('%d/%m')

    return big_df


'''
    Deprecated

def downloads_ratio(
    db: Session,
    scope: dict,
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
'''


def get_users(
    db: Session,
    scope: dict,
    before: Date = date.today(),
    range: int = 28
    ):
    after = before - timedelta(days=range)

    # series of all date from min to max
    s_date = pd.date_range(after - timedelta(7), before - timedelta(days=1))

    empty = pd.DataFrame(s_date, columns=['date'])
    empty['unique_user'] = 0
    df_list = [empty]

    for k, v in scope2dict(scope, True).items():
        query = db.query(Users.date, Users.unique_user) \
                .filter(Users.zone_type == k) \
                .filter(Users.zone_name.in_(v)) \
                .filter(Users.date < before) \
                .filter(Users.date >= after - timedelta(7)) \
                .statement

        df = pd.read_sql(query, engine_crm)
        if not df.empty:
            # fill missing date
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            df = df.groupby('date').sum().reindex(s_date).rename_axis('date')
            # fill unique user to 0
            df['unique_user'] = df['unique_user'].fillna(0).astype(int)
            # fill cumulative to previous value
            df['rolling_seven_users'] = df.rolling(7).sum().fillna(0).astype(int)
            
            df.reset_index(inplace=True)
            df = df[df.date >= pd.to_datetime(after)]
            df_list = [*df_list, df]
    
    big_df = pd.concat(df_list)
    big_df = big_df.groupby(['date']).sum().reset_index()
    big_df['date'] = big_df['date'].dt.strftime('%d/%m')

    return big_df


def get_survey(
    db: Session,
    scope: dict
    ):

    city_codes = []
    for zone in scope['zones']:
        city_codes += [zone.code for zone in get_child(db, zone, 'city')]

    survey_datas = db.query(JecouteDataSurvey) \
        .options(joinedload(JecouteDataSurvey.author)) \
        .options(joinedload(JecouteDataSurvey.survey)) \
        .filter(JecouteDataSurvey.postal_code != '') \
        .join(GeoCity, GeoCity.postal_code.like('%' + JecouteDataSurvey.postal_code + '%')) \
        .filter(GeoCity.code.in_(city_codes)) \
        .filter(JecouteDataSurvey.latitude != '') \
        .filter(JecouteDataSurvey.longitude != '') \
        .all()
    

    returned_zone = scope2dict(scope, True)
    res = {}
    if 'region' in returned_zone.keys():
        geo_reg =  db.query(GeoRegion) \
            .filter(GeoRegion.name == returned_zone['region'][0]) \
            .first()
        res['zone_name'] = geo_reg.name
        res['latitude'] = geo_reg.latitude
        res['longitude'] = geo_reg.longitude
    elif 'departement' in returned_zone.keys():
        geo_dpt = db.query(GeoDepartment) \
            .filter(GeoDepartment.name == returned_zone['departement'][0]) \
            .first()
        res['zone_name'] = geo_dpt.name
        res['latitude'] = geo_dpt.latitude
        res['longitude'] = geo_dpt.longitude
    else:
        res['zone_name'] = next(iter(returned_zone.values()))[0]
        # Chez Xavier
        res['latitude'] = 48.835633
        res['longitude'] =  2.323433

    res['survey_datas'] = survey_datas
    return res
