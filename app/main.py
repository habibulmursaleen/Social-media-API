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
    rating: Optional[int] = None 

#Connection with existing Databases
while True:
    try: 
        conn = psycopg2.connect(host='localhost', database= 'FastAPI', user= 'postgres', password='password', cursor_factory=RealDictCursor)

    #Open a cursor to perform database operations (SQL statement)
        cur = conn.cursor()
        print("Database Connection successful")
        break
    except Exception as error: 
        print("Database Connection Failed")
        print("Error : ", error) 
        time.sleep(2) #for break for 2 seconds and re-try to connect database in the while loop until is finds the connection and break the while loop. 

#Static Database
myPosts = [
    {
    "id": 1,
    "title": "title of post 1",
    "content": "content of post 1",
    "published": True,
    "rating": 4 
    },

    {
    "id": 2,
    "title": "title of post 2",
    "content": "content of post 2", 
    "published": True,
    "rating": 3
    }
]

def find_post(id): 
    for p in myPosts: 
        if p["id"] == id: 
            return p

def find_index_post(id): 
    for i, p in enumerate(myPosts): 
        if p["id"] == id: 
            return i

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
def get_post():
    cur.execute("""SELECT * FROM posts """)
    posts = cur.fetchall()
    return {"data": posts}

#Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published)) #order matters 
    new_posts = cur.fetchone()

    #anytime we make a change to the database, we need to commit to it  
    conn.commit()
    return {"Data": new_posts}

#Latest Post Retrive
@app.get("/posts/latest")
def get_latest_post():
    post = myPosts[len(myPosts)-1]
    return {"Post Details": post} 

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

    cur.execute("""UPDATE posts SET title = %s, content= %s, published= %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id))) #order matters 
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