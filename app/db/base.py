from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from ..configs import SQLALCHEMY_DATABASE_URL
import json


# create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
)
# session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base
Base: DeclarativeMeta = declarative_base()
