from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.backend import schemas, models, oauth2
from app.backend.database import get_db
from .document import rag_pipeline

router = APIRouter(tags=['Queries'])

@router.post("/ask", response_model=schemas.Query)
async def ask_question(req: schemas.QueryRequest, 
                       db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_current_user)):
    """Query the RAG pipeline with a question."""
    document = db.query(models.Document).filter(
            models.Document.id == req.document_id,
            models.Document.user_id == current_user.id
        ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    rag_pipeline.create_chain(persist_dir=document.persist_path)
    print("The chain is created")
    chunks = [chunk for chunk in rag_pipeline.query(req.question)]
    result = ''.join(chunks)

    new_query = models.Query(
        question=req.question,
        answer=result,
        document_id=req.document_id
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    return new_query