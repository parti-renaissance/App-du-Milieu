"""Endpoints de notre api."""
from datetime import date, timedelta

import pandas as pd
from app.crud.enmarche import get_child, scope2dict
from app.database.database_crm import engine_crm
from app.models.models_crm import Downloads, Users
from app.models.models_enmarche import (
    Adherents,
    GeoBorough,
    GeoCity,
    GeoCountry,
    GeoDepartment,
    GeoDistrict,
    GeoRegion,
    JemarcheDataSurvey,
    JecouteDataSurvey,
)
from sqlalchemy import Date, func, and_, or_
from sqlalchemy.orm import Session


def get_downloads(
    db: Session, scope: dict, before: Date = date.today(), range_days: int = 28
):
    after = before - timedelta(days=range_days)

    # series of all date from min to max
    s_date = pd.date_range(after, before - timedelta(days=1))

    empty = pd.DataFrame(s_date, columns=["date"])
    empty["unique_user"] = 0
    df_list = [empty]

    for k, v in scope2dict(scope, True).items():
        query = (
            db.query(Downloads.date, Downloads.unique_user)
            .filter(Downloads.zone_type == k)
            .filter(Downloads.zone_name.in_(v))
            .filter(Downloads.date < before)
            .filter(Downloads.date >= after)
            .statement
        )

        df = pd.read_sql(query, engine_crm)
        if not df.empty:
            # fill missing date
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
            df = df.groupby("date").sum().reindex(s_date).rename_axis("date")
            # fill unique user to 0
            df["unique_user"] = df["unique_user"].fillna(0).astype(int)

            df.reset_index(inplace=True)
            df_list = [*df_list, df]

    big_df = pd.concat(df_list)
    big_df = big_df.groupby(["date"]).sum().reset_index()
    big_df["date"] = big_df["date"].dt.strftime("%d/%m")

    return big_df


def get_users(
    db: Session, scope: dict, before: Date = date.today(), range_days: int = 28
):
    after = before - timedelta(days=range_days)

    # series of all date from min to max
    s_date = pd.date_range(after - timedelta(7), before - timedelta(days=1))

    empty = pd.DataFrame(s_date, columns=["date"])
    empty["unique_user"] = 0
    df_list = [empty]

    for k, v in scope2dict(scope, True).items():
        query = (
            db.query(Users.date, Users.unique_user)
            .filter(Users.zone_type == k)
            .filter(Users.zone_name.in_(v))
            .filter(Users.date < before)
            .filter(Users.date >= after - timedelta(7))
            .statement
        )

        df = pd.read_sql(query, engine_crm)
        if not df.empty:
            # fill missing date
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
            df = df.groupby("date").sum().reindex(s_date).rename_axis("date")
            # fill unique user to 0
            df["unique_user"] = df["unique_user"].fillna(0).astype(int)
            # fill cumulative to previous value
            df["rolling_seven_users"] = df.rolling(7).sum().fillna(0).astype(int)

            df.reset_index(inplace=True)
            df_list = [*df_list, df]

    big_df = pd.concat(df_list)
    big_df = big_df.groupby(["date"]).sum().reset_index()
    big_df = big_df[big_df.date >= pd.to_datetime(after)]
    big_df["date"] = big_df["date"].dt.strftime("%d/%m")

    return big_df


def survey_datas_export(query):
    return {
        "total_surveys": query.count(),
        "survey_datas": (
            query
            .filter(JemarcheDataSurvey.latitude != "")
            .filter(JemarcheDataSurvey.longitude != "")
            .all()
        )
    }


def get_survey_datas(db: Session, scope: dict, survey_id):
    query = (
        db.query(JemarcheDataSurvey)
        .join(JemarcheDataSurvey.data_survey, JecouteDataSurvey.author, isouter=True)
    )

    if survey_id:
        query = query.filter(JecouteDataSurvey.survey_id == survey_id)

    if scope['code'] == 'national':
        return survey_datas_export(query)

    city_codes = []
    for zone in scope["zones"]:
        city_codes += [zone.code for zone in get_child(db, zone, "city")]
        city_codes += [zone.code for zone in get_child(db, zone, "borough")]

    query = (
        query
        .join(GeoCity,
            and_(GeoCity.postal_code.like("%" +
                func.IF(JemarcheDataSurvey.postal_code != '', JemarcheDataSurvey.postal_code, Adherents.address_postal_code) + 
                "%"
                ), or_(JemarcheDataSurvey.postal_code != '', Adherents.address_postal_code)
            )
        )
        .filter(GeoCity.code.in_(city_codes))
    )

    return survey_datas_export(query)


def get_geo_matched_zone(db: Session, zones: dict):
    if "pays" in zones.keys():
        return (
            db.query(GeoCountry)
            .filter(GeoCountry.name == zones["pays"][0])
        )
    if "region" in zones.keys():
        return (
            db.query(GeoRegion)
            .filter(GeoRegion.name == zones["region"][0])
        )
    if "departement" in zones.keys():
        return (
            db.query(GeoDepartment)
            .filter(GeoDepartment.name == zones["departement"][0])
        )
    if "circonscription" in zones.keys():
        return (
            db.query(GeoDistrict)
            .filter(GeoDistrict.name == zones["circonscription"][0])
        )
    if "arrondissement_commune" in zones.keys():
        return (
            db.query(GeoBorough)
            .filter(GeoBorough.name == zones["arrondissement_commune"][0])
        )
    return None


def get_survey(db: Session, scope: dict, survey_id):
    returned_zones = scope2dict(scope, True)
    if (query := get_geo_matched_zone(db, returned_zones)):
        geo_matched_zone = query.first()
        res = {
            "zone_name": geo_matched_zone.name,
            "latitude": geo_matched_zone.latitude if geo_matched_zone.latitude else 47.260834, # not nullable
            "longitude": geo_matched_zone.longitude if geo_matched_zone.longitude else 2.418889 # not nullable
        }
        return dict(get_survey_datas(db, scope, survey_id), **res)

    return {
        "zone_name": "Zone non implémentée", #next(iter(returned_zones.values()))[0],
        "latitude": 47.260834,
        "longitude": 2.418889,
        "total_surveys": 0,
        "survey_datas": []
    }

