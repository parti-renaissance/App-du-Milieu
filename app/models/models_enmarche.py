"""
SQLAlchemy de notre base de données Globale
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.database import Base

# import datetime
# 'tim': int ((self.tim - datetime.datetime (1970, 1, 1)).total_seconds ()),


class Adherents(Base):
    """ Table adherents id/uuid """
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    candidate_managed_area_id = Column(Integer)


    def get_candidate_managed_area(self):
        return self.candidate_managed_area_id


class CandidateManagedArea(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'candidate_managed_area'

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)


    def get_zone_id(self):
        return self.zone_id


class GeoZone(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'geo_zone'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    UniqueConstraint('code', 'type', name='geo_zone_code_type_unique')


    def get_code(self):
        return self.code


class GeoRegion(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'geo_region'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)


    def get_code(self):
        return self.code


    def get_name(self):
        return self.name
