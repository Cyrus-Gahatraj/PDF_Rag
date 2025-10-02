from abc import ABC, abstractmethod
from typing import  Generator
import os

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

class BaseRAG(ABC):
    """
    Abstract base class for RAG pipeline supporting multiple AI providers.
    """
    
    def __init__(self, model: str, embedding_model: str = None):
        self.model = model
        self.embedding_model = embedding_model or self._get_default_embedding_model()
        self.vector_store_name = "pdf-rag"
        self.persist_dir = ''
        self.llm = None
        self.vector_db = None
        self.chain = None
        
    @abstractmethod
    def _initialize_models(self):
        """Initialize the LLM and embedding models for the specific provider."""
        pass
    
    @abstractmethod
    def _get_default_embedding_model(self) -> str:
        """Get default embedding model for the provider."""
        pass
    
    def _create_db(self, documents):
        """Create or update a Chroma vector database from documents."""
        try:
            embeddings = self._get_embeddings()

            # Ensure the persist directory exists
            os.makedirs(self.persist_dir, exist_ok=True)
            print(f"Creating new database at: {self.persist_dir}")
            
            # Create new DB - Chroma automatically persists with persist_directory
            self.vector_db = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=self.vector_store_name,
                persist_directory=self.persist_dir,
            )
            print("Database created successfully")
            
        except Exception as e:
            print(f"Error in _create_db: {e}")
            raise RuntimeError(f"Failed to create vector database: {e}")
    
    @abstractmethod
    def _get_embeddings(self):
        """Get embeddings instance for the provider."""
        pass

    def _split_doc(self, documents, chunk_size: int = 1000, overlap_ratio: float = 0.2):
        """Split documents into chunks and create a DB."""
        chunk_overlap = int(chunk_size * overlap_ratio)
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_documents(documents)
        print(f"Chunks created: {len(chunks)}")
        self._create_db(chunks)

    def load_pdf(self, path: str, name: str, lang: str = "en", chunk_size: int = 1000):
        """Load a PDF file, split it, and store it in Chroma DB."""
        try:
            extension = ".pdf"
            name = name.removesuffix(extension)
            pdf_path = os.path.join(path, f"{name + extension}")

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF not found at path: {pdf_path}")

            base_dir = os.path.abspath(os.path.dirname(__file__)) 
            db_root = os.path.join(base_dir, "..", "db")            
            os.makedirs(db_root, exist_ok=True)

            persist_path = os.path.join(db_root, name)
            self.persist_dir = persist_path

            print(f"Looking for PDF at: {os.path.abspath(pdf_path)}")
            loader = UnstructuredPDFLoader(file_path=pdf_path, language=lang)
            documents = loader.load()
            print(f"Documents loaded: {len(documents)}")
            self._split_doc(documents, chunk_size=chunk_size)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            raise RuntimeError(f"Failed to load PDF: {e}")

    def create_chain(self, persist_dir: str = None, prompt_template: str = None):
        """Build retriever + RAG chain for answering questions."""

        if persist_dir:
            if not os.path.exists(persist_dir):
                raise ValueError(f"Persistence directory not found: {persist_dir}")

            embeddings = self._get_embeddings()
            self.vector_db = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name=self.vector_store_name,
            )

        if not self.llm:
            self._initialize_models()

        if not prompt_template:
            prompt_template = (
                "You are an AI assistant. Generate five different versions of the user question "
                "to retrieve relevant documents from a vector database. "
                "Provide these alternative questions separated by newlines.\n"
                "Original question: {question}"
            )

        query_prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vector_db.as_retriever(),
            llm=self.llm,
            prompt=query_prompt,
        )

        rag_template = (
            "Answer the question based ONLY on the following context:\n"
            "{context}\n\n"
            "Question: {question}"
        )

        prompt = ChatPromptTemplate.from_template(template=rag_template)

        self.chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print('Your PDF is ready to chat with')

    def query(self, question: str) -> Generator[str, None, None]:
        """Ask a question to the RAG pipeline."""

        if not self.chain:
            raise RuntimeError("Chain not initialized. Call `create_chain()` first.")
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        for chunk in self.chain.stream(question): 
            yield chunk
