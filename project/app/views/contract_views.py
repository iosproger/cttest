from fastapi import APIRouter, Depends, HTTPException, Form,status
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError

from typing import List

from project.app.schemas import schemas
from project.app.crud import crud
from project.dependencies import get_db
from project.app.utils import utils as auth_utils
from sqlalchemy.exc import SQLAlchemyError

from fastapi.security import (
    # HTTPBearer,
    # HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="jwt/login/",
)

router = APIRouter(prefix='/contract', tags=["Contract"])

def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_scheme),
) -> dict:
    # token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> schemas.UserBase:
    user_name: str | None = payload.get("sub")
    if user := crud.get_user_by_name(db= db, user_name= user_name):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )

def get_current_active_auth_user(
    user: schemas.UserBase = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )

# contract
def validate_and_get_ct(
    name : str = Form(),
    date : str = Form(),
) -> schemas.ContractBase:

    ct = schemas.ContractBase(name=name, date=date)


    return ct

@router.post("/offer", response_model=dict)
async def offer_contart(
    contract: schemas.PostCTWT,
    user: schemas.User = Depends(get_current_active_auth_user),
    db: Session = Depends(get_db),
):
    try:



        # Create the contract
        new_contract = crud.create_contract(
            db=db,
            owner_create_id=user.id,
            name=contract.name_ct,
            description=contract.description,
            date=contract.date,
        )

        # Create tasks for the contract
        for t in contract.task:
            crud.create_task(
                db=db,
                owner_id=user.id,
                contract_id=new_contract.contract_id,
                task_name=t.task_name,
                type=t.type,
                deadline=t.deadline,
            )


        return {"message": f"Successful add {new_contract.name}"}

    except Exception as e:
        # Roll back the transaction explicitly if something goes wrong
        print(f"Error occurred: {e}")  # Optional logging
        raise HTTPException(status_code=400, detail="Failed to add contract")



@router.post("/accept",response_model=dict)
async def accept_controct(
    contract_id: int = Form(),
    user: schemas.User = Depends(get_current_active_auth_user),
    db: Session = Depends(get_db),
):



    return {"message": "successful test"}


@router.get("/all_contract_owner_id", response_model=List[schemas.Contract], status_code=200)
async def history_of_contract(
    res: schemas.GetAllCt = Depends(),
    user: schemas.User = Depends(get_current_active_auth_user),
    db: Session = Depends(get_db),
):

    try:
        response = crud.get_all_contract(db=db, owner_create_id=user.id, skip=res.skip, limit=res.limit)
        if not response:
            raise HTTPException(status_code=404, detail="No contracts found")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An unexpected error occurred: {str(e)}")
    return response


@router.get("/task_contract", response_model=schemas.PostCtwT)
async def taskIdCt(
    contract_id: schemas.CTID,
    user: schemas.User = Depends(get_current_active_auth_user),
    db: Session = Depends(get_db),
):
    try:

        ct = crud.get_contract_by_id(db=db, contract_id=contract_id.contract_id)
        if not ct:
            raise HTTPException(status_code=404, detail="No contracts found")


        if user.id != ct.owner_create_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not own the contract {ct.name}"
            )


        tasks = crud.get_tasks_by_ct_id(db=db, contract_id=ct.contract_id)


        response = schemas.PostCtwT(
            name_ct=ct.name,
            task=tasks,
            description=ct.description,
            date=ct.date,
        )
        return response

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An unexpected error occurred: {str(e)}")



# @router.post("/ofer",response_model=dict)
# def offer(
#         db: Session = Depends(get_db)
# ):
#
#     return {'message':'test'}