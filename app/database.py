from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@postgresserver_ipaddress/db"
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password@localhost/FastAPI'

#responsible to SQLALchamy with Postgres DB 
engine = create_engine(SQLALCHEMY_DATABASE_URL) #for SQLlite this needs to add ", connect_args={"check_same_thread": False}"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal() #session object is responsive for talking with DB 
    try:
        yield db
    finally:
        db.close()
