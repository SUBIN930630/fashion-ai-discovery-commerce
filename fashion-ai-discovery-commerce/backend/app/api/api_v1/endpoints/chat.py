from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from app.services.chat_history_service import ChatHistoryService
from app.models.chat import ChatMessage, ChatSession
from app.database import get_db

router = APIRouter()
logger = get_logger(__name__)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    recommendations: Optional[List[dict]] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    created_at: datetime

# Dependency
def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db=db)

def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return SessionService(db=db)

def get_chat_history_service(db: Session = Depends(get_db)) -> ChatHistoryService:
    return ChatHistoryService(db)

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service)
):
    """사용자 메시지를 처리하고 AI 응답을 반환"""
    try:
        logger.info("Received chat message", 
                   user_id=request.user_id, 
                   message_length=len(request.message),
                   session_id=request.session_id)
        
        # 세션 관리
        session = await session_service.get_or_create_session(
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # 메시지 처리
        response_data = await chat_service.process_message(
            user_message=request.message,
            session=session
        )
        
        logger.info("Generated chat response",
                   session_id=session.session_id,
                   intent=response_data.get("intent"),
                   recommendations_count=len(response_data.get("recommendations", [])))
        
        # 데이터베이스 저장은 chat_service.process_message 내부에서 처리됨
        logger.debug("Message processed", session_id=session.session_id)
        
        return ChatResponse(
            response=response_data["response"],
            session_id=session.session_id,
            recommendations=response_data.get("recommendations"),
            intent=response_data.get("intent"),
            confidence=response_data.get("confidence")
        )
        
    except Exception as e:
        logger.error("Error processing chat message", error=str(e))
        raise HTTPException(status_code=500, detail="채팅 메시지 처리 중 오류가 발생했습니다.")

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    """특정 세션의 대화 히스토리를 반환"""
    try:
        history = await chat_history_service.get_session_chat_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

        session = await session_service.get_session(session_id)
        created_at = session.created_at if session else history[0].created_at

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

        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages,
            created_at=created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving chat history", 
                    session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="대화 히스토리 조회 중 오류가 발생했습니다.")

@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    session_service: SessionService = Depends(get_session_service)
):
    """사용자의 대화 세션 목록을 반환"""
    try:
        sessions = await session_service.get_user_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error("Error retrieving user sessions", 
                    user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="세션 목록 조회 중 오류가 발생했습니다.")

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """특정 세션을 삭제"""
    try:
        await session_service.delete_session(session_id)
        return {"message": "세션이 삭제되었습니다."}
        
    except Exception as e:
        logger.error("Error deleting session", 
                    session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="세션 삭제 중 오류가 발생했습니다.")

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service)
):
    """WebSocket을 통한 실시간 채팅"""
    await websocket.accept()
    logger.info("WebSocket connection established", user_id=user_id)
    
    # 새 세션 생성
    session = await session_service.create_session(user_id)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                await websocket.send_json({"error": "메시지가 비어있습니다."})
                continue
            
            logger.info("WebSocket message received", 
                       user_id=user_id, 
                       session_id=session.session_id,
                       message_length=len(message))
            
            # 메시지 처리
            response_data = await chat_service.process_message(
                user_message=message,
                session=session
            )
            
            # 응답 전송
            await websocket.send_json({
                "response": response_data["response"],
                "session_id": session.session_id,
                "recommendations": response_data.get("recommendations"),
                "intent": response_data.get("intent"),
                "confidence": response_data.get("confidence"),
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", 
                   user_id=user_id, 
                   session_id=session.session_id)
    except Exception as e:
        logger.error("WebSocket error", 
                    user_id=user_id, 
                    session_id=session.session_id,
                    error=str(e))
        await websocket.close(code=1000)
