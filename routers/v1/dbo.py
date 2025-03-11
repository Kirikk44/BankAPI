import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common import oauth2_scheme, SECRET_KEY, ALGORITHM
from database import DocumentDTO, DocumentDB, UserDB
from routers.v1.auth import get_db

router = APIRouter(prefix="/v1/dbo", tags=["DBO"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/dbo/upload")
def upload_document(doc: DocumentDTO, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    new_doc = DocumentDB(name=doc.name, content=doc.content, owner_id=user.id)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return {"message": "Документ загружен", "document": new_doc}


@router.get("/dbo/download/{doc_id}")
def download_document(doc_id: int, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(DocumentDB).filter(DocumentDB.id == doc_id, DocumentDB.owner_id == user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document


@router.get("/dbo/getdocuments")
def get_user_documents(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    documents = db.query(DocumentDB).filter(DocumentDB.owner_id == user.id).all()
    return documents
