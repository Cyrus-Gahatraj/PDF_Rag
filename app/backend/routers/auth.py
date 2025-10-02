from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.backend.database import get_db
from sqlalchemy.orm import Session
from app.backend import models, oauth2, schemas
from app.backend.utils import verify, hash

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post('/log-in', response_model=schemas.Token)
def user_login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user  = db.query(models.User).filter(
        models.User.email == user_credentials.username ).first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail='Invalid Email.'
        )
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail='Invalid Password.'
        )
    
    access_token = oauth2.create_access_token(data={
         'user_id': str(user.id)
        })
    
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post('/sign-up', status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user.password = hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
