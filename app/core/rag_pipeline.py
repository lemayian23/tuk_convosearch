from typing import Dict, Any, List
from loguru import logger
import json

# Add to RAGPipeline class __init__
class RAGPipeline:
    def __init__(self, config, vector_store, llm_manager, db_manager=None):
        self.config = config
        self.vector_store = vector_store
        self.llm_manager = llm_manager
        self.db_manager = db_manager  # Add database manager
    
    # Update process_query method
    def process_query(self, query: str, conversation_id: str = None, user_id: str = "anonymous") -> Dict[str, Any]:
        """Process a query through the full RAG pipeline with history tracking"""
        try:
            logger.info(f"Processing query: {query}")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.vector_store.search(query)
            
            if not retrieved_docs:
                response = {
                    "answer": "I couldn't find relevant information in the TUK documents for your query. Please try rephrasing or contact the relevant department.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": None
                }
                self._save_to_history(response, query, conversation_id, user_id)
                return response
            
            # Filter by similarity threshold
            filtered_docs = [
                doc for doc in retrieved_docs 
                if doc["similarity_score"] >= self.config.SIMILARITY_THRESHOLD
            ]
            
            if not filtered_docs:
                response = {
                    "answer": "The information I found doesn't meet the confidence threshold for accuracy. Please consult official sources directly.",
                    "sources": retrieved_docs,
                    "confidence": max([doc["similarity_score"] for doc in retrieved_docs]),
                    "error": None
                }
                self._save_to_history(response, query, conversation_id, user_id)
                return response
            
            # Step 2: Prepare context
            context = self._prepare_context(filtered_docs)
            
            # Step 3: Generate response
            llm_response = self.llm_manager.generate_response(query, context)
            
            # Step 4: Prepare final result
            result = {
                "answer": llm_response["answer"],
                "sources": filtered_docs,
                "confidence": sum([doc["similarity_score"] for doc in filtered_docs]) / len(filtered_docs),
                "sources_used": llm_response["sources_used"],
                "error": llm_response["error"],
                "conversation_id": conversation_id
            }
            
            logger.info(f"Query processed successfully. Confidence: {result['confidence']:.2f}")
            
            # Save to history
            self._save_to_history(result, query, conversation_id, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                "answer": "An error occurred while processing your query. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _save_to_history(self, response: dict, query: str, conversation_id: str, user_id: str):
        """Save conversation to history database"""
        if self.db_manager and self.config.ENABLE_HISTORY:
            conversation_data = {
                "conversation_id": conversation_id or f"conv_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "query": query,
                "answer": response.get("answer", ""),
                "confidence": int(response.get("confidence", 0) * 100),
                "sources_used": [
                    {
                        "source": doc.get("metadata", {}).get("source", "Unknown"),
                        "similarity": doc.get("similarity_score", 0)
                    }
                    for doc in response.get("sources", [])
                ]
            }
            
            self.db_manager.save_conversation(conversation_data)
    
    # Add new method to get conversation history
    def get_conversation_history(self, conversation_id: str = None, user_id: str = None, limit: int = 10) -> list:
        """Get conversation history"""
        if self.db_manager and self.config.ENABLE_HISTORY:
            return self.db_manager.get_conversation_history(conversation_id, user_id, limit)
        return []
    
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