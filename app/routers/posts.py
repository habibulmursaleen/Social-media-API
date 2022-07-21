from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas # .. means upper directory
from ..database import get_db
from sqlalchemy.orm import Session  
from typing import List

router = APIRouter(
    prefix = "/posts", # /posts/{id}
    tags= ['Posts'] #documentation grp
)

#SQLalchemy test
@router.get("/")
def test_posts(db: Session = Depends(get_db)):
     posts = db.query(models.Post).all()
     return {"data": posts}

#All Post Retrive 
@router.get("/", response_model= List[schemas.Post])
def get_post(db: Session = Depends(get_db)):
    
    #cur.execute("""SELECT * FROM posts """)
    #posts = cur.fetchall()
    
    posts = db.query(models.Post).all()
    
    return posts

#Create Post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    #cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #            (post.title, post.content, post.published)) #order matters 
    #new_posts = cur.fetchone()
    #anytime we make a change to the database, we need to commit to it  
    #conn.commit() 
    
    #new_posts = models.Post(title=post.title, content=post.content, published=post.published)
    # (**) this is going to uppack the all the fields/columns so we dont have to manually type it out
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit() # #Commit to DB
    db.refresh(new_post) #retrive the data
    return new_post

#Single Post Retrive
@router.get("/{id}", response_model= schemas.Post)
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
@router.put("/{id}", response_model= schemas.Post)
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
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
