from ast import While
from curses import newwin
from multiprocessing.sharedctypes import synchronized
from random import randrange
from sqlite3 import Cursor
from turtle import title
from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor 
import time 
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session  
from .routers import posts, users, auth 

#This is going to create all the models and tables 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
    
#Connection with existing Database 
while True:
    try: 
        conn = psycopg2.connect(host='localhost', database= 'FastAPI', user= 'postgres', 
                                password='password', cursor_factory=RealDictCursor)

    #Open a cursor to perform database operations (SQL statement)
        cur = conn.cursor()
        print("Database Connection successful")
        break
    except Exception as error: 
        print("Database Connection Failed")
        print("Error : ", error) 
        time.sleep(2) #for break for 2 seconds and re-try to connect database in the-
                        #-while loop until is finds the connection and break the while loop. 

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

#path operation/route 
@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI!!"}

