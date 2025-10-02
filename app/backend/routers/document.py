from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, status, Response
from app.core.ollama_rag import OllamaRAG
from sqlalchemy.orm import Session
from app.backend import schemas, models, oauth2
from app.backend.database import get_db
import os, shutil

MODEL='mistral:latest'

rag_pipeline = OllamaRAG(model=MODEL)
router = APIRouter(
        prefix='/documents',
        tags=['Documents']
    )

@router.post("/upload", response_model=schemas.Document)
async def upload_pdf(
    file: UploadFile,
    chunk_size: int = Form(1000),
    current_user = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a PDF, store it, process with RAG, and save metadata in DB."""
    existing_doc = db.query(models.Document).filter(
                models.Document.name == file.filename
            ).first()

    if existing_doc:
        raise HTTPException(status_code=400, detail="File already uploaded")
    
    file.filename = f'{current_user.id}_' + file.filename
    
    save_path = os.path.join("uploads", file.filename)
    print(save_path)
    os.makedirs("uploads", exist_ok=True)
    

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        rag_pipeline.load_pdf(path="uploads", name=file.filename, chunk_size=chunk_size)
        rag_pipeline.create_chain()

        persist_dir = rag_pipeline.persist_dir

        new_doc = models.Document(
            name=file.filename,
            file_path=save_path,
            persist_path=persist_dir,
            user_id = current_user.id
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        return new_doc

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.get('/')
def get_pdf(db: Session = Depends(get_db),
            current_user = Depends(oauth2.get_current_user)):
    documents = db.query(models.Document).filter(
            models.Document.user_id == current_user.id
        ).all()
    if not documents:
        return {'message': 'no pdf uploaded'}
    return documents

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(id: int,
                db: Session = Depends(get_db),
                current_user = Depends(oauth2.get_current_user)):
    document_query = db.query(models.Document).filter(
            models.Document.id == id,
            models.Document.user_id == current_user.id
        )
    document = document_query.first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No Document Found!'
        )

    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)

    if document.persist_path and os.path.exists(document.persist_path):
        shutil.rmtree(document.persist_path, ignore_errors=True)

    document_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
