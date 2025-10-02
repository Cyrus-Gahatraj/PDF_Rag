# PDF_Rag 📚

PDF_Rag is a **FastAPI + Streamlit** application for **document-based Question Answering (RAG)**.  
It allows users to **upload PDFs**, split them into chunks, store embeddings, and query the content using a language model (Ollama by default).  

---

## Features

- Upload and manage PDF documents.
- Split PDFs into chunks and store embeddings in a vector database.
- RAG (Retrieval-Augmented Generation) for PDF content using **Ollama LLM**.
- Query PDFs via API with user authentication.
- Streamlit frontend for easy file upload and interaction.
- Multi-user support — each user's PDFs are separated.
- Clean deletion of PDFs and associated embeddings.

---

## Tech Stack

- **Backend:** `FastAPI`, `SQLAlchemy`, `PostgreSQL`
- **Vector Database:** `Chroma (default)`, future support for `pgvector` possible
- **Language Model:**` Ollama `
- **Frontend:** `Streamlit`
- **Python Version:** 3.13+

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/PDF_Rag.git
cd PDF_Rag
```

2. Create a virtual environment and activate:
```bash
python3 -m venv .venv      # Linux / macOS
source .venv/bin/activate  

python -m venv .venv       # Windows
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the app

### Backend (FastAPI)
```bash
uvicorn app.backend.main:app --reload
```

- The API will be available at http://localhost:8000.
- Swagger docs: http://localhost:8000/docs

### Frontend (Streamlit)
```bash
streamlit run app/frontend/Home.py
```
- Access the Streamlit frontend at http://localhost:8501

## File Structure

```bash
PDF_Rag/
├─ app/
│  ├─ backend/
|  |  ├─ routers/
|  |  |  ├─ auth.py 
|  |  |  ├─ document.py 
|  |  |  ├─ query.py 
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ oauth2.py
│  │  ├─ schemas.py
│  │  └─ utils.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ base_rag.py
│  │  └─ ollama_rag.py
|  ├─ db/                  # Persisted embeddings
│  ├─ frontend/
│  │  └─ pages/
│  │  |  ├─ 1_Sign-up.py
│  │  |  ├─ 2_Log-in.py
│  │  |  └─ 3_PlayGround.py
│  │  └─  Home.py
│  └─ __int__.py
├─ uploads/                # Uploaded PDFs
├─ requirements.txt
└─ README.md
```

## Notes

- Persist Directory: Currently, embeddings are stored on the server under db/{filename}.
- Storing on client devices is not supported, as the RAG pipeline requires server access to embeddings.

- Multi-user Support: Each uploaded PDF is tied to the uploading user's ID.

## License

MIT License © 2025

