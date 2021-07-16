from sqlalchemy.orm import sessionmaker
from app.database.database_crm import CRM, engine_crm
from app.database.database_enmarche import Base, engine_read_only

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    binds={CRM: engine_crm, Base: engine_read_only})
