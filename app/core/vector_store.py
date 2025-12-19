import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
from loguru import logger
import pickle
import os

class VectorStoreManager:
    def __init__(self, config):
        self.config = config
        self.embedding_model = None
        self.client = None
        self.collection = None
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Initialize ChromaDB
        self._init_vector_store()
    
    def _init_embedding_model(self):
        """Initialize sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _init_vector_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persistent directory if it doesn't exist
            os.makedirs(self.config.VECTOR_DB_PATH, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.config.VECTOR_DB_PATH,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="tuk_documents",
                metadata={"description": "TUK official documents"}
            )
            
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for list of texts"""
        return self.embedding_model.encode(texts, show_progress_bar=True)
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector store"""
        try:
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Generate embeddings
            embeddings = self.create_embeddings(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    
    def search(self, query: str, n_results: int = None) -> List[Dict]:
        """Search for similar documents"""
        if n_results is None:
            n_results = self.config.TOP_K_RESULTS
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "embedding_model": self.config.EMBEDDING_MODEL,
                "vector_db_path": self.config.VECTOR_DB_PATH
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}