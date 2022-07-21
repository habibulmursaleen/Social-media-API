from passlib.context import CryptContext 

#telling passlib what is the default hashing algorithm which is bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str): 
    return pwd_context.hash(password)