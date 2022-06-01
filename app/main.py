from ast import While
from curses import newwin
from random import randrange
from sqlite3 import Cursor
from turtle import title
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor 
import time 
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session  

#This is going to create all the models and tables 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel): 
    title: str
    content: str 
    published: bool  = True 
    
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
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    post = db.query(models.Post).all()
    return {"data": post}

#All Post Retrive 
@app.get("/posts")
def get_post(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    #cur.execute("""SELECT * FROM posts """)
    #posts = cur.fetchall()
    return {"data": posts}

#Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    
    
    #cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #            (post.title, post.content, post.published)) #order matters 
    #new_posts = cur.fetchone()
    #anytime we make a change to the database, we need to commit to it  
    #conn.commit() 
    
    #new_posts = models.Post(title=post.title, content=post.content, published=post.published)
    
    #this is going to uppack the all the fields/columns so we dont have to manually type it out
    new_posts = models.Post(**post.dict())
    #anytime we make a change to the database, we need to commit to it 
    db.add(new_posts)
    db.commit()
    db.refresh(new_posts) #retrive the data
    return {"Data": new_posts}

#Single Post Retrive
@app.get("/posts/{id}")
def get_one_post(id: int):
    cur.execute("""SELECT * FROM posts WHERE id = %s """, (str(id))) # this is to avoid SQL injection
    post = cur.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} not found")
    return {"Post Details": post} 

#Update
@app.put("/posts/{id}")
def update_post(id: int, post:Post):

    cur.execute("""UPDATE posts SET title = %s, content= %s, published= %s WHERE id = %s RETURNING * """, 
                (post.title, post.content, post.published, str(id))) #order matters 
    updated_post = cur.fetchone()
    #anytime we make a change to the database, we need to commit to it  
    conn.commit()

    if updated_post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} not found")
    return {"Data": updated_post}

#Delete
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cur.execute("""DELETe FROM posts WHERE id = %s RETURNING * """, (str(id))) # this is to avoid SQL injection
    deleted_post = cur.fetchone()
    #anytime we make a change to the database, we need to commit to it  
    conn.commit()

    if deleted_post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with Id:{id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)