from typing import List

from sqlalchemy.orm import Session

from project.app.schemas import schemas
from project.app.models.models import User ,Contract ,Task
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_name(db: Session, user_name: str):
    return db.query(User).filter(User.user_name == user_name).first()



def create_user(db: Session,user_name:str, name: str, phone_number: str, email: str ,hashed_password: bytes, active: bool):
    new_user = User(user_name=user_name,name=name,phone_number=phone_number,email = email, hashed_password=hashed_password, active=active)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, name: str, password: str):
    user = get_user_by_name(db, name)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def user_check( db: Session ,user_name : str = None) -> bool:

    if not (user := get_user_by_name(db=db,user_name=user_name)):
        return False

    return True


# contract
def get_contract_by_id(db: Session, contract_id: int):
    try:
        return db.query(Contract).filter(Contract.contract_id == contract_id).first()
    except Exception as e:
        raise Exception(f"An error occurred while find contract by contract_id : {e}")

def get_tasks_by_ct_id(db: Session, contract_id: int):
    try:
        return db.query(Task).filter(Task.contract_id == contract_id).all()
    except Exception as e:
        raise Exception(f"An error occurred while fetching tasks by contract_id: {e}")



def create_contract(db: Session ,owner_create_id: int, name: str,description: str , date: str):
    new_contract = Contract(
        owner_create_id=owner_create_id,
        name = name,
        description = description,
        date = date,)
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract

# task
def create_task(db: Session,owner_id: int,contract_id:int, task_name: str, type:str , deadline : str ):
    new_task = Task(
        owner_id= owner_id,
        contract_id= contract_id,
        task_name= task_name,
        type = type,
        deadline=deadline,)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_all_contract(db: Session, owner_create_id: int, skip: int = 0, limit: int = 10) :
    try:
        return db.query(Contract).filter(Contract.owner_create_id == owner_create_id).offset(skip).limit(limit).all()
    except Exception as e:
        raise Exception(f"An error occurred while fetching contracts: {e}")