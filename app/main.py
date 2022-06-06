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
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session  
from passlib.context import CryptContext

#telling passlib what is the default  hasing algorithm is. 
pwd_context = CryptContext(schemes=["bcrypy"], deprecated = "auto") 

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

#path operation/route 
@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI!!"}

#SQLalchemy test
# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     post = db.query(models.Post).all()
#     return {"data": post}

#All Post Retrive 
@app.get("/posts", response_model= List[schemas.Post])
def get_post(db: Session = Depends(get_db)):
    
    #cur.execute("""SELECT * FROM posts """)
    #posts = cur.fetchall()
    
    posts = db.query(models.Post).all()
    
    return posts

#Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    #cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #            (post.title, post.content, post.published)) #order matters 
    #new_posts = cur.fetchone()
    #anytime we make a change to the database, we need to commit to it  
    #conn.commit() 
    
    #new_posts = models.Post(title=post.title, content=post.content, published=post.published)
    # (**) this is going to uppack the all the fields/columns so we dont have to manually type it out
    new_posts = models.Post(**post.dict())
    db.add(new_posts)
    db.commit() # #Commit to DB
    db.refresh(new_posts) #retrive the data
    return new_posts

#Single Post Retrive
@app.get("/posts/{id}", response_model= schemas.Post)
def get_one_post(id: int, db: Session = Depends(get_db)):
    # cur.execute("""SELECT * FROM posts WHERE id = %s """, (str(id))) # this is to avoid SQL injection
    # post = cur.fetchone() 
    
    post = db.query(models.Post).filter(models.Post.id == id).first() #works like SQL WHERE. 
                                                            #.first() bring the first found result instead of all()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} not found")
        
    return post

#Update
@app.put("/posts/{id}", response_model= schemas.Post)
def update_post(id: int, post:schemas.PostCreate, db: Session = Depends(get_db)):

    # # cur.execute("""UPDATE posts SET title = %s, content= %s, published= %s WHERE id = %s RETURNING * """, 
    # #             (post.title, post.content, post.published, str(id))) #order matters 
    # # updated_post = cur.fetchone()
    # #anytime we make a change to the database, we need to commit to it  
    # conn.commit()
    
    updated_post_query = db.query(models.Post).filter(models.Post.id == id) 
    updated_post=updated_post_query.first()

    if updated_post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} not found")
    updated_post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    db.refresh(updated_post_query.first()) #retrive the data
    
    return updated_post_query.first()

#Delete
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    # cur.execute("""DELETe FROM posts WHERE id = %s RETURNING * """, (str(id))) # this is to avoid SQL injection
    # deleted_post = cur.fetchone()
    
    post = db.query(models.Post).filter(models.Post.id == id) 
    if post.first() == None: #checking if the first found result is none
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit() #Commit to DB
    db.refresh(new_user) #retrive the data
    return new_user 

#Create User
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model= schemas.UserOut)
def create_User(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
     #hash the password before putting into DB 
     #hash the password - hash.password 
     
    hased_password = pwd_context.hash(user.password)
    user.password = hased_password 
    
    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit() # #Commit to DB
    db.refresh(new_user) #retrive the data
    return new_user