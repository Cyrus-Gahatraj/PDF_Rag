import ollama
from langchain_ollama import OllamaEmbeddings, ChatOllama

from .base_rag import BaseRAG

class OllamaRAG(BaseRAG):
    """RAG implementation using Ollama models."""
    
    def __init__(self, model: str, 
                 embedding_model: str = "nomic-embed-text", 
                 upgradability: bool = False):
        self.upgradability = upgradability
        super().__init__(model, embedding_model)
        self._embeddings = None
        
    def _initialize_models(self):
        """Ensure Ollama models are available locally and initialize."""
        if ollama is None:
            raise ImportError("Ollama package not installed. Install with: pip install ollama")
            
        self._pull_models()
        self.llm = ChatOllama(model=self.model)
        
    def _pull_models(self):
        """Ensure Ollama models are available locally."""
        try:
            # Check if Ollama is running
            ollama.list()
        except Exception as e:
            raise RuntimeError(f"Ollama is not running or not accessible. Please start Ollama first. Error: {e}")
        
        print(f"Pulling embedding model: {self.embedding_model}")
        ollama.pull(self.embedding_model)
        if self.upgradability:
            print(f"Pulling LLM model: {self.model}")
            ollama.pull(self.model)
            
    def _get_default_embedding_model(self) -> str:
        return "nomic-embed-text"
        
    def _get_embeddings(self):
        """Get embeddings instance for Ollama."""
        if self._embeddings is None:
            print(f"Initializing embeddings with model: {self.embedding_model}")
            self._embeddings = OllamaEmbeddings(model=self.embedding_model)
        return self._embeddings