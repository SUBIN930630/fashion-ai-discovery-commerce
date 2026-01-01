import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings
from app.models.chat import ChatSession, ChatMessage, MessageRole
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ml.intent_analyzer import IntentClassifier
from ml.vector_search import SearchEngine
from ml.mmr_algorithm import MMRScorer
from ml.response_generator import ResponseGenerator

logger = get_logger(__name__)


class ChatService:
    """채팅 서비스 - 사용자 메시지 처리 및 AI 응답 생성"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        self.search_engine = SearchEngine()
        self.mmr_scorer = MMRScorer(lambda_param=settings.MMR_LAMBDA)
        self.response_generator = ResponseGenerator(
            api_key=settings.OPENAI_API_KEY
        )
        
        logger.info("Chat service initialized")
    
    async def process_message(
        self, 
        user_message: str, 
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        사용자 메시지를 처리하여 AI 응답 생성
        
        Args:
            user_message: 사용자 메시지
            session: 채팅 세션 정보
            
        Returns:
            Dict containing response, recommendations, intent, etc.
        """
        try:
            logger.info("Processing user message", 
                       session_id=session.session_id,
                       message_length=len(user_message))
            
            # 1. 대화 히스토리 조회
            chat_history = await self._get_chat_history(session.session_id)
            
            # 2. 사용자 프로필 조회 (추후 구현)
            user_profile = await self._get_user_profile(session.user_id)
            
            # 3. 의도 분석
            intent_result = await self.intent_classifier.classify_intent(
                user_message=user_message,
                chat_history=chat_history,
                user_profile=user_profile
            )
            
            logger.info("Intent analyzed", 
                       intent=intent_result.intent.value,
                       confidence=intent_result.confidence,
                       exploration_intent=intent_result.exploration_intent)
            
            # 4. 상품 검색 및 추천
            recommendations = await self._generate_recommendations(
                user_message=user_message,
                intent_result=intent_result,
                user_profile=user_profile,
                session=session
            )
            
            # 5. AI 응답 생성
            ai_response = await self.response_generator.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                recommendations=recommendations,
                user_profile=user_profile,
                chat_history=chat_history
            )
            
            # 6. 메시지 저장
            await self._save_messages(session, user_message, ai_response, intent_result)
            
            return {
                "response": ai_response,
                "recommendations": recommendations,
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "exploration_intent": intent_result.exploration_intent
            }
            
        except Exception as e:
            logger.error("Error processing message", 
                        session_id=session.session_id,
                        error=str(e))
            
            # 에러 시 기본 응답 반환
            return {
                "response": "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
                "recommendations": [],
                "intent": "system_error",
                "confidence": 0.0,
                "exploration_intent": False
            }
    
    async def _get_chat_history(self, session_id: str) -> List[Dict]:
        """채팅 히스토리 조회 (추후 데이터베이스 연동)"""
        # TODO: 실제 데이터베이스에서 히스토리 조회
        return []
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """사용자 프로필 조회 (추후 데이터베이스 연동)"""
        # TODO: 실제 데이터베이스에서 사용자 프로필 조회
        return {
            "user_id": user_id,
            "style_distribution": {"스트릿": 0.4, "캐주얼": 0.3, "미니멀": 0.3},
            "preferred_categories": ["상의", "아우터"],
            "preferred_colors": ["블랙", "그레이", "네이비"],
            "price_range": {"min": 30000, "max": 100000},
            "exploration_score": 0.3
        }
    
    async def _generate_recommendations(
        self,
        user_message: str,
        intent_result: Any,
        user_profile: Optional[Dict],
        session: ChatSession
    ) -> List[Dict]:
        """상품 추천 생성"""
        try:
            # 검색 쿼리 생성
            search_results = await self.search_engine.search_products(
                query=user_message,
                user_profile=user_profile,
                intent=intent_result.intent,
                limit=50  # 후보군 확대
            )
            
            if not search_results:
                logger.warning("No search results found", 
                              query=user_message[:50])
                return []
            
            # MMR 알고리즘으로 다양성 있는 추천 선택
            mmr_result = await self.mmr_scorer.select_recommendations(
                query_embedding=None,  # search_engine에서 임베딩 처리
                candidates=search_results,
                target_count=settings.MAX_RECOMMENDATIONS,
                strategy=intent_result.recommendation_strategy,
                excluded_ids=await self._get_excluded_products(session.user_id),
                user_history=await self._get_user_history(session.user_id)
            )
            
            # 응답 형식으로 변환
            recommendations = []
            for product in mmr_result.selected_products:
                recommendations.append({
                    "id": product.id,
                    "name": product.metadata.get("name", ""),
                    "brand": product.metadata.get("brand", ""),
                    "price": product.metadata.get("price", 0),
                    "image_url": product.metadata.get("image_url", ""),
                    "similarity_score": product.similarity_score,
                    "recommendation_type": product.recommendation_type.value,
                    "reasoning": f"유사도: {product.similarity_score:.2f}"
                })
            
            logger.info("Recommendations generated", 
                       count=len(recommendations),
                       diversity_score=mmr_result.total_diversity_score)
            
            return recommendations
            
        except Exception as e:
            logger.error("Error generating recommendations", error=str(e))
            return []
    
    async def _get_excluded_products(self, user_id: str) -> set:
        """최근 추천된 상품 ID 목록 (재추천 방지)"""
        # TODO: 실제 데이터베이스에서 조회
        return set()
    
    async def _get_user_history(self, user_id: str) -> List[Dict]:
        """사용자 구매/클릭 히스토리"""
        # TODO: 실제 데이터베이스에서 조회
        return []
    
    async def _save_messages(
        self, 
        session: ChatSession, 
        user_message: str, 
        ai_response: str,
        intent_result: Any
    ):
        """메시지를 데이터베이스에 저장"""
        try:
            # 사용자 메시지 저장
            user_msg = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session.session_id,
                role=MessageRole.USER,
                content=user_message,
                timestamp=datetime.now()
            )
            
            # AI 응답 저장
            ai_msg = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session.session_id,
                role=MessageRole.ASSISTANT,
                content=ai_response,
                timestamp=datetime.now(),
                metadata={
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence,
                    "exploration_intent": intent_result.exploration_intent
                }
            )
            
            # TODO: 실제 데이터베이스에 저장
            logger.debug("Messages saved to database", 
                        session_id=session.session_id)
            
        except Exception as e:
            logger.error("Error saving messages", 
                        session_id=session.session_id,
                        error=str(e))