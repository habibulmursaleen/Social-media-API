from email.policy import default
from xmlrpc.client import boolean
from markupsafe import string
from sqlalchemy import TIMESTAMP, Column, Integer,String,Boolean
from sqlalchemy.sql.expression import null, text 
from .database import Base 

#model represents tables
class Post(Base): 
    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String, nullable = False)
    published = Column(Boolean, server_default= 'True')
    cretaed_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))
    
