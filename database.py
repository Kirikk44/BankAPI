import enum
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from sqlalchemy import Table

DATABASE_URL = "postgresql://postgres:1235@localhost:5432/apibank"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

contract_document = Table(
    'contract_document',
    Base.metadata,
    Column('contract_id', Integer, ForeignKey('contracts.id')),
    Column('document_id', Integer, ForeignKey('documents.id'))
)


# Роли пользователей
class UserRole(str, enum.Enum):
    user = "user"
    bank_employee = "bank_employee"


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("DocumentDB", back_populates="owner")


class DocumentDB(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("UserDB", back_populates="documents")
    contracts = relationship("ContractDB", secondary=contract_document, back_populates="documents")


class ContractDB(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))  # владелец контракта (bank_employee)
    owner = relationship("UserDB", back_populates="contracts")
    documents = relationship("DocumentDB", secondary=contract_document, back_populates="contracts")

    # DTO (Data Transfer Object)


class UserDTO(BaseModel):
    username: str
    password: str


class DocumentDTO(BaseModel):
    name: str
    content: str


class ContractDTO(BaseModel):
    name: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
