from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from user_service.src.user_api import crud, schemas, security
from user_service.src.user_api.dependencies import get_db, get_user_service
from user_service.src.user_api.interfaces import UserServiceInterface

router = APIRouter(prefix="/api", tags=["Authentication"])

UserServiceDep = Annotated[UserServiceInterface, Depends(get_user_service)]


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    # This logic needs a direct DB access to get the hashed password securely
    db = next(get_db())
    try:
        db_user = crud.get_user_by_email(db, email=form_data.username)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # At this point, db_user.hashed_password is a string at runtime
        if not security.verify_password(form_data.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = security.create_access_token(data={"sub": db_user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()
