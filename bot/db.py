from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

from models import *

Base.metadata.create_all(bind=engine)
