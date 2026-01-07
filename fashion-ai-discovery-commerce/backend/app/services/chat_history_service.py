# 챗봇 히스토리 저장 서비스
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.db_models import ChatHistory, ChatSession
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatHistoryService:
    """챗봇 히스토리 저장 및 조회 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _ensure_db_initialized(self):
        """데이터베이스 테이블이 존재하는지 확인하고 없으면 생성"""
        try:
            from app.database import Base, engine
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.warning("Database initialization check failed", error=str(e))
    
    async def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatHistory:
        """
        메시지를 데이터베이스에 저장
        
        Args:
            session_id: 세션 ID
            user_id: 사용자 ID
            role: 메시지 역할 ('user' or 'assistant')
            content: 메시지 내용
            metadata: 추가 메타데이터 (intent, confidence, recommendations 등)
        
        Returns:
            저장된 ChatHistory 객체
        """
        try:
            chat_history = ChatHistory(
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=content,
                meta_data=metadata or {}
            )
            
            self.db.add(chat_history)
            self.db.commit()
            self.db.refresh(chat_history)
            
            logger.info("Chat message saved",
                       session_id=session_id,
                       user_id=user_id,
                       role=role,
                       message_id=chat_history.id)
            
            return chat_history
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error saving chat message",
                        session_id=session_id,
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def save_conversation(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ChatHistory]:
        """
        사용자 메시지와 AI 응답을 함께 저장
        
        Args:
            session_id: 세션 ID
            user_id: 사용자 ID
            user_message: 사용자 메시지
            assistant_message: AI 응답
            metadata: 추가 메타데이터
        
        Returns:
            저장된 ChatHistory 객체 리스트
        """
        messages = []
        
        # 사용자 메시지 저장
        user_msg = await self.save_message(
            session_id=session_id,
            user_id=user_id,
            role='user',
            content=user_message
        )
        messages.append(user_msg)
        
        # AI 응답 저장
        assistant_msg = await self.save_message(
            session_id=session_id,
            user_id=user_id,
            role='assistant',
            content=assistant_message,
            metadata=metadata
        )
        messages.append(assistant_msg)
        
        return messages
    
    async def get_user_chat_history(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatHistory]:
        """
        특정 사용자의 챗봇 대화 내역 조회
        
        Args:
            user_id: 사용자 ID
            limit: 가져올 개수
            offset: 오프셋
        
        Returns:
            ChatHistory 객체 리스트
        """
        try:
            history = self.db.query(ChatHistory)\
                .filter(ChatHistory.user_id == user_id)\
                .order_by(ChatHistory.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            logger.debug("Retrieved chat history",
                        user_id=user_id,
                        count=len(history))
            
            return history
            
        except Exception as e:
            logger.error("Error retrieving chat history",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def get_session_chat_history(
        self,
        session_id: str
    ) -> List[ChatHistory]:
        """
        특정 세션의 챗봇 대화 내역 조회
        
        Args:
            session_id: 세션 ID
        
        Returns:
            ChatHistory 객체 리스트
        """
        try:
            history = self.db.query(ChatHistory)\
                .filter(ChatHistory.session_id == session_id)\
                .order_by(ChatHistory.created_at.asc())\
                .all()
            
            logger.debug("Retrieved session chat history",
                        session_id=session_id,
                        count=len(history))
            
            return history
            
        except Exception as e:
            logger.error("Error retrieving session chat history",
                        session_id=session_id,
                        error=str(e))
            raise
    
    async def get_all_chat_history(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatHistory]:
        """
        모든 사용자의 챗봇 대화 내역 조회 (관리자용)
        
        Args:
            limit: 가져올 개수
            offset: 오프셋
        
        Returns:
            ChatHistory 객체 리스트
        """
        try:
            history = self.db.query(ChatHistory)\
                .order_by(ChatHistory.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            logger.debug("Retrieved all chat history",
                        count=len(history))
            
            return history
            
        except Exception as e:
            logger.error("Error retrieving all chat history",
                        error=str(e))
            raise
