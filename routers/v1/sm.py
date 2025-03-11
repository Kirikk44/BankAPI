import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common import oauth2_scheme, SECRET_KEY, ALGORITHM
from database import UserRole, ContractDTO, ContractDB, UserDB, DocumentDB
from routers.v1.auth import get_db
from routers.v1.dbo import get_current_user

router = APIRouter(prefix="/v1/sm", tags=["SM"])


@router.post("/create_contract")
def create_contract(contract: ContractDTO, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.bank_employee:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    new_contract = ContractDB(name=contract.name, owner_id=user.id)
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return {"message": "Контракт создан", "contract": new_contract}


@router.post("/link_contract")
def link_document_to_contract(contract_id: int, doc_id: int, user: UserDB = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user.role != UserRole.bank_employee:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    contract = db.query(ContractDB).filter(ContractDB.id == contract_id).first()
    document = db.query(DocumentDB).filter(DocumentDB.id == doc_id).first()
    if not contract or not document:
        raise HTTPException(status_code=404, detail="Контракт или документ не найден")
    contract.documents.append(document)
    db.commit()
    return {"message": "Документ привязан к контракту"}
