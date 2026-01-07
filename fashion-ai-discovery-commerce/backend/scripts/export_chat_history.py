#!/usr/bin/env python3
"""
챗봇 대화 히스토리를 JSON 형식으로 내보내는 스크립트
AWS 배포 서버의 데이터베이스에서 채팅 데이터를 조회하여 정리
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
# backend/scripts/export_chat_history.py -> backend -> 프로젝트 루트
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.database import get_db, SessionLocal
from app.models.db_models import ChatHistory, ChatSession
from app.core.config import settings


def format_datetime(dt: datetime) -> str:
    """datetime을 ISO 형식 문자열로 변환"""
    if dt:
        return dt.isoformat()
    return None


def export_chat_history_to_json(
    db: Session,
    limit: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    output_file: str = "chat_history_export.json"
) -> Dict[str, Any]:
    """
    채팅 히스토리를 JSON 형식으로 내보내기
    
    Args:
        db: 데이터베이스 세션
        limit: 조회할 최대 개수 (None이면 전체)
        start_date: 시작 날짜
        end_date: 종료 날짜
        output_file: 출력 파일명
    
    Returns:
        내보낸 데이터 딕셔너리
    """
    
    # 쿼리 구성
    query = db.query(ChatHistory)
    
    # 날짜 필터 적용
    if start_date:
        query = query.filter(ChatHistory.created_at >= start_date)
    if end_date:
        query = query.filter(ChatHistory.created_at <= end_date)
    
    # 최신순 정렬
    query = query.order_by(desc(ChatHistory.created_at))
    
    # 개수 제한
    if limit:
        query = query.limit(limit)
    
    # 데이터 조회
    chat_history = query.all()
    
    # 세션별로 그룹화
    sessions_dict = {}
    conversations = []
    
    for msg in chat_history:
        session_id = msg.session_id
        
        if session_id not in sessions_dict:
            # 세션 정보 조회
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            sessions_dict[session_id] = {
                "session_id": session_id,
                "user_id": msg.user_id,
                "created_at": format_datetime(session.created_at) if session else format_datetime(msg.created_at),
                "messages": []
            }
        
        # 메시지 정보 추가
        message_data = {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": format_datetime(msg.created_at),
            "metadata": msg.meta_data if msg.meta_data else {}
        }
        
        sessions_dict[session_id]["messages"].append(message_data)
    
    # 세션별로 대화 쌍 구성 (user-assistant)
    for session_id, session_data in sessions_dict.items():
        messages = sorted(session_data["messages"], key=lambda x: x["created_at"])
        
        # user와 assistant 메시지를 쌍으로 구성
        i = 0
        while i < len(messages):
            if messages[i]["role"] == "user":
                user_msg = messages[i]
                
                # 다음 assistant 메시지 찾기
                assistant_msg = None
                if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
                    assistant_msg = messages[i + 1]
                    i += 2
                else:
                    i += 1
                
                # 대화 쌍 추가
                conversation = {
                    "session_id": session_id,
                    "user_id": session_data["user_id"],
                    "timestamp": user_msg["created_at"],
                    "user_message": user_msg["content"],
                    "assistant_message": assistant_msg["content"] if assistant_msg else None,
                    "intent": assistant_msg.get("metadata", {}).get("intent") if assistant_msg else None,
                    "confidence": assistant_msg.get("metadata", {}).get("confidence") if assistant_msg else None,
                    "exploration_intent": assistant_msg.get("metadata", {}).get("exploration_intent") if assistant_msg else None,
                    "recommendations": assistant_msg.get("metadata", {}).get("recommendations") if assistant_msg else None,
                    "recommendations_count": len(assistant_msg.get("metadata", {}).get("recommendations", [])) if assistant_msg and assistant_msg.get("metadata", {}).get("recommendations") else 0
                }
                
                conversations.append(conversation)
            else:
                i += 1
    
    # 통계 정보
    stats = {
        "total_sessions": len(sessions_dict),
        "total_conversations": len(conversations),
        "total_messages": len(chat_history),
        "user_messages": len([m for m in chat_history if m.role == "user"]),
        "assistant_messages": len([m for m in chat_history if m.role == "assistant"]),
        "export_date": datetime.utcnow().isoformat()
    }
    
    # 최종 데이터 구조
    export_data = {
        "export_info": {
            "export_date": stats["export_date"],
            "total_sessions": stats["total_sessions"],
            "total_conversations": stats["total_conversations"],
            "total_messages": stats["total_messages"],
            "date_range": {
                "start": format_datetime(start_date) if start_date else None,
                "end": format_datetime(end_date) if end_date else None
            }
        },
        "statistics": stats,
        "conversations": conversations,
        "sessions": list(sessions_dict.values())
    }
    
    # JSON 파일로 저장
    output_path = project_root / output_file
    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 채팅 히스토리 내보내기 완료!")
    print(f"📁 파일 위치: {output_path}")
    print(f"📊 통계:")
    print(f"   - 총 세션 수: {stats['total_sessions']}")
    print(f"   - 총 대화 수: {stats['total_conversations']}")
    print(f"   - 총 메시지 수: {stats['total_messages']}")
    print(f"   - 사용자 메시지: {stats['user_messages']}")
    print(f"   - 챗봇 응답: {stats['assistant_messages']}")
    
    return export_data


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='챗봇 대화 히스토리를 JSON으로 내보내기')
    parser.add_argument('--limit', type=int, help='조회할 최대 개수 (기본값: 전체)')
    parser.add_argument('--start-date', type=str, help='시작 날짜 (YYYY-MM-DD 형식)')
    parser.add_argument('--end-date', type=str, help='종료 날짜 (YYYY-MM-DD 형식)')
    parser.add_argument('--output', type=str, default='chat_history_export.json', help='출력 파일명')
    
    args = parser.parse_args()
    
    # 날짜 파싱
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    if args.end_date:
        end_date = datetime.fromisoformat(args.end_date)
    
    # 데이터베이스 연결
    db = SessionLocal()
    
    try:
        # 데이터 내보내기
        export_data = export_chat_history_to_json(
            db=db,
            limit=args.limit,
            start_date=start_date,
            end_date=end_date,
            output_file=args.output
        )
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

