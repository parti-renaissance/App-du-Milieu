"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Date
from datetime import date, timedelta

from typing import Optional
from app.models.models_enmarche import Adherents
from app.models.models_crm import DownloadsDpt, DownloadsReg
from app.database.database_crm import engine_crm
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
    filter_zone = {zone.type: zone.name}

    sum_ori = 0
    if zone.type == 'region':
        sum_ori = db.query(DownloadsReg) \
                .filter_by(**filter_zone) \
                .filter(DownloadsReg.date < before - timedelta(days=range)) \
                .order_by(desc(DownloadsReg.date)) \
                .first().cumsum if not None else 0

        query = db.query(DownloadsReg) \
                .filter_by(**filter_zone) \
                .filter(DownloadsReg.date < before) \
                .filter(DownloadsReg.date >= before - timedelta(days=range)) \
                .statement
    else:
        sum_ori = db.query(DownloadsDpt) \
                .filter_by(**filter_zone) \
                .filter(DownloadsDpt.date < before - timedelta(days=range)) \
                .order_by(desc(DownloadsDpt.date)) \
                .first().cumsum if not None else 0

        query = db.query(DownloadsDpt) \
                .filter_by(**filter_zone) \
                .filter(DownloadsDpt.date < before) \
                .filter(DownloadsDpt.date >= before - timedelta(days=range)) \
                .statement

    df = pd.read_sql(query, engine_crm).drop(columns=['index', zone.type])
    if not df.empty:
        df['cumsum'] = df['cumsum'].astype(int) - int(sum_ori)
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df
