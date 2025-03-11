from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, UserDB, UserRole, DocumentDB, ContractDB
from routers.v1.dbo import get_current_user

router = APIRouter(prefix="/v1/abs", tags=["ABS"])


# Эндпоинты ABS

@router.get("/documents")
def get_all_documents(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.bank_employee:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    documents = db.query(DocumentDB).all()
    return documents

@router.get("/documents/{user_id}")
def get_documents_for_user(user_id: int, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.bank_employee:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    documents = db.query(DocumentDB).filter(DocumentDB.owner_id == user_id).all()
    return documents


