from typing import Dict, Any, Optional
from langchain.llms import Ollama
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from loguru import logger
import os

class LLMManager:
    def __init__(self, config):
        self.config = config
        self.llm = None
        self.prompt_template = None
        
        self._init_llm()
        self._init_prompt_template()
    
    def _init_llm(self):
        """Initialize LLM based on configuration"""
        try:
            if self.config.LLM_PROVIDER == "openai":
                if not self.config.OPENAI_API_KEY:
                    raise ValueError("OpenAI API key not configured")
                
                self.llm = ChatOpenAI(
                    model=self.config.LLM_MODEL,
                    temperature=0.1,
                    api_key=self.config.OPENAI_API_KEY
                )
                logger.info(f"Initialized OpenAI LLM: {self.config.LLM_MODEL}")
                
            elif self.config.LLM_PROVIDER == "ollama":
                self.llm = Ollama(
                    model=self.config.LLM_MODEL,
                    base_url=self.config.OLLAMA_BASE_URL,
                    temperature=0.1
                )
                logger.info(f"Initialized Ollama LLM: {self.config.LLM_MODEL}")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.LLM_PROVIDER}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _init_prompt_template(self):
        """Initialize the prompt template for RAG"""
        template = """You are TUK-ConvoSearch, an AI assistant for the Technical University of Kenya. Your purpose is to provide accurate, helpful information to students and staff based ONLY on the provided context.

Context Information:
{context}

User Question: {question}

Instructions:
1. Answer STRICTLY based on the context provided above
2. If the answer is not in the context, say "I cannot find specific information about this in the official TUK documents. Please contact the relevant department for assistance."
3. Keep answers concise and clear
4. If relevant, mention the source document
5. Format important dates, deadlines, or procedures clearly

Answer:"""

        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )
    
    def generate_response(self, question: str, context: str) -> Dict[str, Any]:
        """Generate response using LLM with RAG"""
        try:
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
            
            # Generate response
            response = chain.run(context=context, question=question)
            
            return {
                "answer": response.strip(),
                "sources_used": True if context else False,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                "sources_used": False,
                "error": str(e)
            }