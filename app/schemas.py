from datetime import datetime
import email
from pydantic import BaseModel, EmailStr 
 
class PostBase(BaseModel): 
    title: str
    content: str 
    published: bool  = True 
    
#User to Backend 
class PostCreate(PostBase): 
    pass #inhairte from postcreate 

#Backend to user (Response) 
class Post(PostBase): 
    id: int 
    created_at: datetime 
    
    class Config:   #Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model
        orm_mode = True
        
class UserCreate(BaseModel): 
    email: EmailStr 
    password: str 
    
class UserOut(BaseModel): #response model for not retriving password 
    id: int 
    email: EmailStr
    created_at: datetime 
    
    class Config:   
        orm_mode = True
        
class UserLogin(BaseModel):  
    email: EmailStr 
    password: str 
