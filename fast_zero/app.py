from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema, Token
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello, World!"}


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="User already exists",
        )
    # db_user = User(**user.model_dump())
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    skip: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    users = session.scalars(select(User).limit(limit).offset(skip))
    return {"users": users}


@app.put(
    "/users/{user_id}/", status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="User can only update their own account",
        )
    current_user = session.scalar(select(User).where(User.id == user_id))
    if not current_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )
    # current_user.update(**user.model_dump())
    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)
    session.commit()
    session.refresh(current_user)
    return current_user


@app.delete("/users/{user_id}/", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="User can only delete their own account",
        )
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )
    session.delete(db_user)
    session.commit()


@app.get(
    "/users/{user_id}/", status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )
    return db_user


@app.post("/token/", status_code=HTTPStatus.OK, response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    db_user = session.scalar(
        select(User).where(User.username == form_data.username)
    )
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username",
        )
    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect password",
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "Bearer"}
