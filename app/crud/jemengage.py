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

    if zone.type == 'region':
        try:
            sum_ori = int(db.query(DownloadsReg) \
                            .filter_by(**filter_zone) \
                            .filter(DownloadsReg.date < before - timedelta(days=range)) \
                            .order_by(desc(DownloadsReg.date)) \
                            .first().cumsum)
        except:
            sum_ori = 0

        query = db.query(DownloadsReg) \
                .filter_by(**filter_zone) \
                .filter(DownloadsReg.date < before) \
                .filter(DownloadsReg.date >= before - timedelta(days=range)) \
                .statement
    else:
        try:
            sum_ori = int(db.query(DownloadsDpt) \
                            .filter_by(**filter_zone) \
                            .filter(DownloadsDpt.date < before - timedelta(days=range)) \
                            .order_by(desc(DownloadsDpt.date)) \
                            .first().cumsum)
        except:
            sum_ori = 0

        query = db.query(DownloadsDpt) \
                .filter_by(**filter_zone) \
                .filter(DownloadsDpt.date < before) \
                .filter(DownloadsDpt.date >= before - timedelta(days=range)) \
                .statement

    df = pd.read_sql(query, engine_crm).drop(columns=['index', zone.type])
    if not df.empty:
        # series of all date from min to max
        s_date = pd.date_range(df.date.min(), df.date.max())
        # fill missing date
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date').reindex(s_date).rename_axis('date').reset_index()
        # fill unique user to 0
        df['unique_user'] = df['unique_user'].fillna(0).astype(int)
        # fill cumulative to previous value (minus first value)
        df['cumsum'] = df['cumsum'].fillna(method='ffill').astype(int)
        df['cumsum'] = df['cumsum'] - sum_ori
        df['date'] = df['date'].dt.strftime('%d/%m')
    return df
