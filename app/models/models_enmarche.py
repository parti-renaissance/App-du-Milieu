"""
SQLAlchemy de notre base de données Globale
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

# import datetime
# 'tim': int ((self.tim - datetime.datetime (1970, 1, 1)).total_seconds ()),


class Adherents(Base):
    """ Table adherents id/uuid """
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    candidate_managed_area_id = Column(Integer, ForeignKey('candidate_managed_area.id'))
    candidate_managed_area = relationship('CandidateManagedArea')


class CandidateManagedArea(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'candidate_managed_area'

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey('geo_zone.id'))
    candidate_managed_zone = relationship('GeoZone')

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

    def get_type(self):
        return self.type


class GeoCity(Base):
    """ Table geo_city """
    __tablename__ = 'geo_city'

    id = Column(Integer, primary_key=True, index=True)
    postal_code = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('geo_department.id'))
    geo_department = relationship('GeoDepartment')


class GeoDepartment(Base):
    """ Table geo_department """
    __tablename__ = 'geo_department'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('geo_region.id'))
    geo_region = relationship('GeoRegion')


class GeoRegion(Base):
    """ Table geo_region """
    __tablename__ = 'geo_region'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)


class OauthAccessTokens(Base):
    """ Table oauth_access_tokens """
    __tablename__ = 'oauth_access_tokens'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, nullable=False, index=True)


class JecouteDataSurvey(Base):
    """ Table jecoute_data_survey """
    __tablename__ = 'jecoute_data_survey'

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('adherents.id'), nullable=True)
    author = relationship('Adherents', lazy='joined')
    posted_at = Column(DateTime, nullable=False)
    postal_code = Column(String, nullable=True)
    age_range = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    survey_id = Column(Integer, ForeignKey('jecoute_survey.id'))
    survey = relationship('JecouteSurvey', lazy='joined')


class JecouteSurvey(Base):
    """ Table jecoute_data_survey """
    __tablename__ = 'jecoute_survey'

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('adherents.id'), nullable=True)
    author = relationship('Adherents', lazy='joined')
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    zone_id = Column(Integer, ForeignKey('geo_zone.id'))
    geo_zone_relation = relationship('GeoZone')