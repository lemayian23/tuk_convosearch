from typing import Dict, Any, List
from loguru import logger
import json

class RAGPipeline:
    def __init__(self, config, vector_store, llm_manager):
        self.config = config
        self.vector_store = vector_store
        self.llm_manager = llm_manager
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the full RAG pipeline"""
        try:
            logger.info(f"Processing query: {query}")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.vector_store.search(query)
            
            if not retrieved_docs:
                return {
                    "answer": "I couldn't find relevant information in the TUK documents for your query. Please try rephrasing or contact the relevant department.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": None
                }
            
            # Filter by similarity threshold
            filtered_docs = [
                doc for doc in retrieved_docs 
                if doc["similarity_score"] >= self.config.SIMILARITY_THRESHOLD
            ]
            
            if not filtered_docs:
                return {
                    "answer": "The information I found doesn't meet the confidence threshold for accuracy. Please consult official sources directly.",
                    "sources": retrieved_docs,
                    "confidence": max([doc["similarity_score"] for doc in retrieved_docs]),
                    "error": None
                }
            
            # Step 2: Prepare context
            context = self._prepare_context(filtered_docs)
            
            # Step 3: Generate response
            response = self.llm_manager.generate_response(query, context)
            
            # Step 4: Prepare final result
            result = {
                "answer": response["answer"],
                "sources": filtered_docs,
                "confidence": sum([doc["similarity_score"] for doc in filtered_docs]) / len(filtered_docs),
                "sources_used": response["sources_used"],
                "error": response["error"]
            }
            
            logger.info(f"Query processed successfully. Confidence: {result['confidence']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                "answer": "An error occurred while processing your query. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(documents):
            source_info = f"[Source: {doc['metadata'].get('source', 'Unknown')}]"
            content = doc['content']
            context_parts.append(f"Document {i+1} {source_info}:\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and statistics"""
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            "system_name": self.config.PROJECT_NAME,
            "version": self.config.VERSION,
            "vector_store": vector_stats,
            "llm_provider": self.config.LLM_PROVIDER,
            "llm_model": self.config.LLM_MODEL,
            "embedding_model": self.config.EMBEDDING_MODEL,
            "chunk_size": self.config.CHUNK_SIZE
        }