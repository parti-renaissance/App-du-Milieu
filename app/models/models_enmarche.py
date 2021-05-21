"""
SQLAlchemy de notre base de données Globale
"""
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy import UniqueConstraint, ForeignKey, PrimaryKeyConstraint
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
    candidate_managed_area_id = Column(Integer, ForeignKey('candidate_managed_area.id'), nullable=True)
    candidate_managed_area = relationship('CandidateManagedArea')


class AdherentMessages(Base):
    """ Table adherent_messages """
    __tablename__ = 'adherent_messages'

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('adherents.id'), nullable=True)
    author = relationship('Adherents')
    label = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False)
    type = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=True)


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


class GeoCanton(Base):
    """ Table geo_canton """
    __tablename__ = 'geo_canton'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('geo_department.id'))
    geo_department = relationship('GeoDepartment')
    active = Column(Boolean, nullable=False)


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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region_id = Column(Integer, ForeignKey('geo_region.id'))
    geo_region = relationship('GeoRegion')


class GeoRegion(Base):
    """ Table geo_region """
    __tablename__ = 'geo_region'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


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


class MailChimpCampaign(Base):
    """ Table mailchimp_campaign """
    __tablename__ = 'mailchimp_campaign'

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey('adherent_messages.id'), nullable=True)
    message = relationship('AdherentMessages', lazy="joined")
    recipient_count = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    report_id = Column(Integer, ForeignKey('mailchimp_campaign_report.id'), nullable=True)
    report = relationship('MailChimpCampaignReport', back_populates='mailchimp_campaign')


class MailChimpCampaignReport(Base):
    """ Table mailchimp_campaign_report """
    __tablename__ = 'mailchimp_campaign_report'

    id = Column(Integer, primary_key=True, index=True)
    open_total = Column(Integer, nullable=False)
    open_unique = Column(Integer, nullable=False)
    click_total = Column(Integer, nullable=False)
    click_unique = Column(Integer, nullable=False)
    email_sent = Column(Integer, nullable=False)
    unsubscribed = Column(Integer, nullable=False)
    mailchimp_campaign = relationship("MailChimpCampaign", back_populates="report")
    #TODO define method to calculate rates ?


class Referent(Base):
    """ Table referent """
    __tablename__ = 'referent'

    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String, nullable=True)
    area_label = Column(String, nullable=False)
    status = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)


class ReferentArea(Base):
    """ Table referent_area """
    __tablename__ = 'referent_area'

    id = Column(Integer, primary_key=True, index=True)
    area_code = Column(String, nullable=False)
    area_type = Column(String, nullable=False)


class ReferentAreas(Base):
    """ Table referent_areas """
    __tablename__ = 'referent_areas'

    referent_id = Column(Integer, ForeignKey('referent.id'), nullable=True)
    referent = relationship('Referent', lazy='joined')
    area_id = Column(Integer, ForeignKey('referent_area.id'), nullable=True)
    area = relationship('ReferentArea', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('referent_id', 'area_id'),
        {},
    )


class OauthAccessTokens(Base):
    """ Table oauth_access_tokens """
    __tablename__ = 'oauth_access_tokens'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
