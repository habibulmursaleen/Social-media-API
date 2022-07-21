import email
from email.mime import base
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
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, 
                        server_default=text('now()'))
    
class Users(Base): 
     __tablename__ = "users"
     
     id = Column(Integer, primary_key = True, nullable = False)
     email = Column(String, nullable = False, unique= True)
     password = Column(String, nullable = False)
     created_at = Column(TIMESTAMP(timezone=True), nullable = False, 
                         server_default=text('now()')) 