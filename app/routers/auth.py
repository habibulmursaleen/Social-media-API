from email import utils
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import database, schemas, models, utils 
from sqlalchemy.orm import Session  

router = APIRouter(
    tags= ['Authentication'] #documentation grp
)

@router.post('/login')
def login(users_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.email == users_credentials.email).first() 
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Invalid Credentials")
        
    if not utils.verify(users_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Invalid Credentials")
    
    #create a token
    #return token 
    return {"token":"example token"}    