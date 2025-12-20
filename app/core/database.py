from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
from loguru import logger

Base = declarative_base()

class Conversation(Base):
    """Model for storing conversation history"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)  # Unique ID for each chat session
    user_id = Column(String, index=True, default="anonymous")  # Could be student ID in production
    query = Column(Text)
    answer = Column(Text)
    confidence = Column(Integer)  # 0-100
    sources_used = Column(JSON)  # Store sources as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    helpful_feedback = Column(Boolean, nullable=True)  # User feedback
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "query": self.query,
            "answer": self.answer,
            "confidence": self.confidence,
            "sources_used": json.loads(self.sources_used) if self.sources_used else [],
            "created_at": self.created_at.isoformat(),
            "helpful_feedback": self.helpful_feedback
        }

class DatabaseManager:
    """Manages conversation history database operations"""
    
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        
        if config.ENABLE_HISTORY:
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            # Create data directory if it doesn't exist
            import os
            os.makedirs("data", exist_ok=True)
            
            # Create engine
            self.engine = create_engine(
                self.config.DATABASE_URL,
                connect_args={"check_same_thread": False}  # Needed for SQLite
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info("Conversation history database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_conversation(self, conversation_data: dict) -> dict:
        """Save a conversation to database"""
        if not self.SessionLocal:
            return {"success": False, "error": "Database not initialized"}
        
        try:
            db = self.SessionLocal()
            
            conversation = Conversation(
                conversation_id=conversation_data.get("conversation_id"),
                user_id=conversation_data.get("user_id", "anonymous"),
                query=conversation_data.get("query", ""),
                answer=conversation_data.get("answer", ""),
                confidence=conversation_data.get("confidence", 0),
                sources_used=json.dumps(conversation_data.get("sources_used", [])),
                helpful_feedback=conversation_data.get("helpful_feedback")
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Saved conversation: {conversation.id}")
            
            return {
                "success": True,
                "conversation_id": conversation.conversation_id,
                "id": conversation.id
            }
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if db:
                db.close()
    
    def get_conversation_history(self, conversation_id: str = None, user_id: str = None, limit: int = 20) -> list:
        """Get conversation history for a session or user"""
        if not self.SessionLocal:
            return []
        
        try:
            db = self.SessionLocal()
            
            query = db.query(Conversation)
            
            if conversation_id:
                query = query.filter(Conversation.conversation_id == conversation_id)
            elif user_id:
                query = query.filter(Conversation.user_id == user_id)
            
            # Get latest conversations
            conversations = query.order_by(Conversation.created_at.desc()).limit(limit).all()
            
            return [conv.to_dict() for conv in conversations]
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return []
        finally:
            if db:
                db.close()
    
    def update_feedback(self, conversation_id: str, helpful: bool) -> bool:
        """Update feedback for a conversation"""
        if not self.SessionLocal:
            return False
        
        try:
            db = self.SessionLocal()
            
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            
            if conversation:
                conversation.helpful_feedback = helpful
                db.commit()
                logger.info(f"Updated feedback for conversation {conversation_id}: {helpful}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            return False
        finally:
            if db:
                db.close()
    
    def cleanup_old_conversations(self):
        """Clean up conversations older than retention period"""
        if not self.SessionLocal:
            return
        
        try:
            db = self.SessionLocal()
            
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.HISTORY_RETENTION_DAYS)
            
            deleted_count = db.query(Conversation).filter(
                Conversation.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old conversations")
            
        except Exception as e:
            logger.error(f"Error cleaning up old conversations: {e}")
        finally:
            if db:
                db.close()
    
    def get_statistics(self) -> dict:
        """Get conversation statistics"""
        if not self.SessionLocal:
            return {}
        
        try:
            db = self.SessionLocal()
            
            total_conversations = db.query(Conversation).count()
            
            helpful_count = db.query(Conversation).filter(
                Conversation.helpful_feedback == True
            ).count()
            
            unhelpful_count = db.query(Conversation).filter(
                Conversation.helpful_feedback == False
            ).count()
            
            today = datetime.utcnow().date()
            today_conversations = db.query(Conversation).filter(
                Conversation.created_at >= datetime(today.year, today.month, today.day)
            ).count()
            
            return {
                "total_conversations": total_conversations,
                "helpful_feedback": helpful_count,
                "unhelpful_feedback": unhelpful_count,
                "today_conversations": today_conversations
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            if db:
                db.close()