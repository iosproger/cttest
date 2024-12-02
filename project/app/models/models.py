from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from project.app.schemas.schemas import TaskType

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# contract
class Contract(Base):
    __tablename__ = "contract"
    contract_id = Column(Integer, primary_key=True, index=True)
    owner_create_id = Column(Integer, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship("Task", back_populates="contract")



# Tasks
class Task(Base):
    __tablename__ = "task"  # Correct table name
    task_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contract.contract_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    deadline = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    contract = relationship("Contract", back_populates="tasks")

    @validates("type")
    def validate_type(self, key, value):
        if value not in TaskType._value2member_map_:  # Validate against TaskType values
            raise ValueError(f"Invalid task type: {value}")
        return value