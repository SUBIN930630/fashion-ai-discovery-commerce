import uuid
from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.chat import ChatSession
from app.models.db_models import ChatHistory

logger = get_logger(__name__)


class SessionService:
    """세션 관리 서비스"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._sessions = {} if db is None else None
        logger.info("Session service initialized", has_db=db is not None)
    
    async def get_or_create_session(
        self, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> ChatSession:
        """기존 세션을 가져오거나 새 세션을 생성"""
        
        if self.db is None:
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                logger.debug("Retrieved existing session",
                            session_id=session_id, user_id=user_id)
                return session
        else:
            if session_id:
                session = self.db.query(ChatSession).filter(
                    ChatSession.session_id == session_id
                ).first()
                if session:
                    if session.user_id != user_id:
                        logger.warning(
                            "Session user mismatch; creating new session",
                            session_id=session_id,
                            user_id=user_id,
                            session_user_id=session.user_id,
                        )
                    else:
                        session.updated_at = datetime.now()
                        self.db.commit()
                        self.db.refresh(session)
                        logger.debug(
                            "Retrieved existing session",
                            session_id=session_id,
                            user_id=user_id,
                        )
                        return session
        
        # 새 세션 생성
        new_session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        if self.db is None:
            self._sessions[new_session.session_id] = new_session
        else:
            try:
                self.db.add(new_session)
                self.db.commit()
                self.db.refresh(new_session)
            except Exception as e:
                self.db.rollback()
                logger.error("Failed to create session", error=str(e))
                raise

        logger.info(
            "Created new session",
            session_id=new_session.session_id,
            user_id=user_id,
        )

        return new_session
    
    async def create_session(self, user_id: str) -> ChatSession:
        """새 세션 생성"""
        return await self.get_or_create_session(user_id)
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 조회"""
        if self.db is None:
            session = self._sessions.get(session_id)
        else:
            session = self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()

        if session:
            logger.debug("Session found", session_id=session_id)
        else:
            logger.warning("Session not found", session_id=session_id)

        return session
    
    async def update_session(self, session: ChatSession) -> bool:
        """세션 업데이트"""
        try:
            session.updated_at = datetime.now()
            if self.db is None:
                self._sessions[session.session_id] = session
            else:
                self.db.add(session)
                self.db.commit()
                self.db.refresh(session)

            logger.debug("Session updated", session_id=session.session_id)
            return True

        except Exception as e:
            if self.db:
                self.db.rollback()
            logger.error(
                "Error updating session",
                session_id=session.session_id,
                error=str(e),
            )
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        try:
            if self.db is None:
                if session_id in self._sessions:
                    del self._sessions[session_id]
                    logger.info("Session deleted", session_id=session_id)
                    return True
                logger.warning("Session not found for deletion", session_id=session_id)
                return False

            session = self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            if not session:
                logger.warning("Session not found for deletion", session_id=session_id)
                return False

            self.db.delete(session)
            self.db.commit()
            logger.info("Session deleted", session_id=session_id)
            return True

        except Exception as e:
            if self.db:
                self.db.rollback()
            logger.error(
                "Error deleting session",
                session_id=session_id,
                error=str(e),
            )
            return False
    
    async def get_chat_history(self, session_id: str) -> Optional[Dict]:
        """대화 히스토리 조회"""
        session = await self.get_session(session_id)
        
        if not session:
            return None
        
        if self.db is None:
            # TODO: 실제 데이터베이스에서 메시지 히스토리 조회
            return {
                "session_id": session_id,
                "messages": [],
                "created_at": session.created_at,
            }

        history = self.db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.created_at.asc()).all()

        messages = [
            {
                "id": h.id,
                "role": h.role,
                "content": h.content,
                "metadata": h.meta_data,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ]

        return {
            "session_id": session_id,
            "messages": messages,
            "created_at": session.created_at,
        }
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict]:
        """사용자의 세션 목록 조회"""
        try:
            user_sessions = []
            
            if self.db is not None:
                # 데이터베이스에서 세션 조회
                sessions = self.db.query(ChatSession)\
                    .filter(ChatSession.user_id == user_id)\
                    .order_by(ChatSession.updated_at.desc())\
                    .limit(limit)\
                    .offset(offset)\
                    .all()
                
                for session in sessions:
                    user_sessions.append({
                        "session_id": session.session_id,
                        "created_at": session.created_at,
                        "updated_at": session.updated_at,
                        "is_active": session.is_active
                    })
            else:
                # 인메모리에서 세션 조회
                for session in self._sessions.values():
                    if session.user_id == user_id:
                        user_sessions.append({
                            "session_id": session.session_id,
                            "created_at": session.created_at,
                            "updated_at": session.updated_at,
                            "is_active": session.is_active
                        })
                
                # 정렬 및 페이지네이션
                user_sessions.sort(key=lambda x: x["updated_at"], reverse=True)
                
                start = offset
                end = offset + limit
                user_sessions = user_sessions[start:end]
            
            logger.debug("Retrieved user sessions", 
                        user_id=user_id, 
                        total=len(user_sessions))
            
            return user_sessions
            
        except Exception as e:
            logger.error("Error retrieving user sessions", 
                        user_id=user_id, 
                        error=str(e))
            return []
