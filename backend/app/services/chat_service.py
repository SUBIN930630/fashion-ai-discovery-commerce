import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.config import settings
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.favorite_service import FavoriteService
from app.services.cart_service import CartService
from app.services.chat_history_service import ChatHistoryService
from app.services.recommendation_service import RecommendationService
from app.models.db_models import RecommendationFeedback
import sys
import os
# 프로젝트 루트를 sys.path에 추가
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.append(project_root)
# ml 디렉토리도 직접 추가 (Docker 컨테이너 내부에서 /ml로 마운트됨)
if os.path.exists('/ml'):
    sys.path.insert(0, '/ml')

from ml.intent_analyzer import IntentClassifier
from ml.vector_search import SearchEngine
from ml.mmr_algorithm import MMRScorer
from ml.response_generator import ResponseGenerator

logger = get_logger(__name__)


class ChatService:
    """채팅 서비스 - 사용자 메시지 처리 및 AI 응답 생성"""
    
    def __init__(self, db: Optional[Session] = None):
        self.intent_classifier = IntentClassifier(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        # SQL 기반 벡터 검색 엔진 사용 (db 세션 전달)
        self.search_engine = SearchEngine(db=db)
        self.mmr_scorer = MMRScorer(lambda_param=settings.MMR_LAMBDA)
        self.response_generator = ResponseGenerator(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        self.db = db
        # 데이터베이스가 있을 때만 서비스 초기화, 없어도 챗봇은 작동하도록 처리
        try:
            self.favorite_service = FavoriteService(db) if db else None
            self.cart_service = CartService(db) if db else None
            self.chat_history_service = ChatHistoryService(db) if db else None
            self.recommendation_service = RecommendationService(db) if db else None
        except Exception as e:
            logger.warning(f"Failed to initialize services: {e}", exc_info=True)
            self.favorite_service = None
            self.cart_service = None
            self.chat_history_service = None
            self.recommendation_service = None
        
        logger.info("Chat service initialized", has_db=db is not None)
    
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
            # 질문 단계(정보 수집 단계)에서는 추천 상품을 보여주지 않음
            # - confidence가 낮을 때 (의도 파악이 불명확)
            # - 사용자 메시지가 매우 짧을 때 (구체적인 요구사항 없음)
            should_show_recommendations = self._should_show_recommendations(
                user_message=user_message,
                intent_result=intent_result,
                chat_history=chat_history
            )
            
            recommendations = []
            if should_show_recommendations:
                recommendations = await self._generate_recommendations(
                    user_message=user_message,
                    intent_result=intent_result,
                    user_profile=user_profile,
                    session=session
                )
            else:
                logger.info("Skipping recommendations - information gathering phase",
                           confidence=intent_result.confidence,
                           message_length=len(user_message))
            
            # 5. AI 응답 생성
            ai_response = await self.response_generator.generate_response(
                user_message=user_message,
                intent_result=intent_result,
                recommendations=recommendations,
                user_profile=user_profile,
                chat_history=chat_history
            )
            
            # 6. GPT 응답에서 상품명 추출 및 DB 매칭 (새로운 단계)
            # recommendations가 비어있고, GPT 응답이 상품 추천 내용을 포함하는 경우
            if (not recommendations or len(recommendations) == 0) and \
               self._is_product_recommendation_response(ai_response):
                logger.info("Extracting products from GPT response",
                           response_length=len(ai_response),
                           session_id=session.session_id)
                extracted_recommendations = await self._match_products_from_response(
                    ai_response=ai_response,
                    user_message=user_message,
                    intent_result=intent_result,
                    user_profile=user_profile,
                    session=session
                )
                if extracted_recommendations:
                    recommendations = extracted_recommendations
                    logger.info("Products extracted from GPT response",
                               count=len(recommendations),
                               session_id=session.session_id)
            
            # 7. 메시지 저장
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
                        error=str(e),
                        exc_info=True)
            
            # 에러 시 기본 응답 반환
            return {
                "response": "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
                "recommendations": [],
                "intent": "system_error",
                "confidence": 0.0,
                "exploration_intent": False
            }
    
    async def _get_chat_history(self, session_id: str) -> List[Dict]:
        """채팅 히스토리 조회"""
        if not self.chat_history_service:
            return []
            
        try:
            history_objs = await self.chat_history_service.get_session_chat_history(session_id)
            return [
                {"role": h.role, "content": h.content} 
                for h in history_objs
            ]
        except Exception as e:
            logger.warning(f"Failed to get chat history: {e}")
            return []
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        사용자 프로필 조회 - 좋아요, 장바구니 정보 포함
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            사용자 프로필 정보 (좋아요, 장바구니, 통계 포함)
        """
        try:
            profile = {
                "user_id": user_id,
                "favorites": [],
                "cart_items": [],
                "favorite_product_ids": [],
                "cart_product_ids": [],
                "stats": {
                    "favorites_count": 0,
                    "cart_items_count": 0,
                    "cart_total_price": 0
                }
            }
            
            # 좋아요 정보 조회
            if self.favorite_service:
                try:
                    favorites = await self.favorite_service.get_user_favorites(user_id)
                    profile["favorites"] = [
                        {
                            "product_id": f.product_id,
                            "created_at": f.created_at.isoformat() if f.created_at else None
                        }
                        for f in favorites
                    ]
                    profile["favorite_product_ids"] = [f.product_id for f in favorites]
                    profile["stats"]["favorites_count"] = len(favorites)
                except Exception as e:
                    logger.warning(f"Failed to get user favorites: {e}")
            
            # 장바구니 정보 조회
            if self.cart_service:
                try:
                    cart_items = await self.cart_service.get_user_cart(user_id)
                    profile["cart_items"] = [
                        {
                            "product_id": item.product_id,
                            "quantity": item.quantity,
                            "product_data": item.product_data,
                            "created_at": item.created_at.isoformat() if item.created_at else None
                        }
                        for item in cart_items
                    ]
                    profile["cart_product_ids"] = [item.product_id for item in cart_items]
                    profile["stats"]["cart_items_count"] = sum(item.quantity for item in cart_items)
                    profile["stats"]["cart_total_price"] = sum(
                        (item.product_data.get("price", 0) * item.quantity) 
                        if item.product_data else 0
                        for item in cart_items
                    )
                except Exception as e:
                    logger.warning(f"Failed to get user cart: {e}")
            
            # 전체 사용자 통계 (추천 다양성 계산에 활용)
            if self.favorite_service and self.cart_service:
                try:
                    all_favorites = await self.favorite_service.get_all_favorites(limit=1000)
                    all_carts = await self.cart_service.get_all_carts(limit=1000)
                    
                    # 인기 상품 추출 (다른 사용자들이 좋아요한 상품)
                    product_favorite_count = {}
                    for fav in all_favorites:
                        product_id = fav.product_id
                        product_favorite_count[product_id] = product_favorite_count.get(product_id, 0) + 1
                    
                    # 인기 상품 TOP 10
                    popular_products = sorted(
                        product_favorite_count.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                    
                    profile["popular_products"] = [pid for pid, _ in popular_products]
                    profile["global_stats"] = {
                        "total_favorites": len(all_favorites),
                        "total_cart_items": len(all_carts),
                        "popular_products_count": len(popular_products)
                    }
                except Exception as e:
                    logger.warning(f"Failed to get global stats: {e}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            # 기본 프로필 반환
            return {
                "user_id": user_id,
                "favorites": [],
                "cart_items": [],
                "favorite_product_ids": [],
                "cart_product_ids": [],
                "stats": {
                    "favorites_count": 0,
                    "cart_items_count": 0,
                    "cart_total_price": 0
                }
            }
    
    def _should_show_recommendations(
        self,
        user_message: str,
        intent_result: Any,
        chat_history: List[Dict]
    ) -> bool:
        """
        추천 상품을 보여줄지 여부를 결정
        
        질문 단계(정보 수집 단계)에서는 추천 상품을 보여주지 않음
        
        Args:
            user_message: 사용자 메시지
            intent_result: 의도 분석 결과
            chat_history: 대화 히스토리
            
        Returns:
            bool: 추천 상품을 보여줄지 여부
        """
        # 1. confidence가 낮으면 (0.6 미만) 추천하지 않음
        if intent_result.confidence < 0.6:
            return False
        
        # 2. 사용자 메시지가 매우 짧으면 (5자 이하) 추천하지 않음
        message_length = len(user_message.strip())
        if message_length <= 5:
            return False
        
        # 3. 대화 히스토리가 없거나 매우 짧으면 (첫 대화) 항상 추천
        if not chat_history or len(chat_history) <= 2:
            return True
        
        # 4. 최근 대화에서 사용자가 질문만 하고 구체적인 요구사항이 없는 경우 체크
        # (예: "네", "좋아", "어떻게" 등)
        question_only_keywords = ['네', '좋아', '어떻게', '뭐', '무엇', '어떤', '어디', '언제', '누구']
        user_message_lower = user_message.strip().lower()
        if any(keyword in user_message_lower for keyword in question_only_keywords):
            if message_length <= 10:  # 질문 키워드만 있고 짧은 경우
                return False
        
        return True
    
    def _extract_product_keywords_from_response(self, response: str) -> List[str]:
        """
        GPT 응답에서 상품 관련 키워드 추출
        
        Args:
            response: GPT 응답 텍스트
            
        Returns:
            List[str]: 추출된 상품 키워드 리스트
        """
        # 패션 상품 키워드 사전 (카테고리별)
        product_keywords = [
            # 상의
            "티셔츠", "셔츠", "후드티", "맨투맨", "니트", "가디건", "블라우스", "탱크톱",
            "화이트 셔츠", "블랙 셔츠", "긴팔 셔츠", "반팔 셔츠",
            # 하의
            "바지", "팬츠", "슬랙스", "청바지", "조거팬츠", "치노", "와이드팬츠", "스키니",
            "와이드 팬츠", "스키니 팬츠", "슬림 팬츠",
            # 아우터
            "자켓", "코트", "패딩", "바람막이", "블레이저", "트러커", "MA-1", "무스탕",
            "오버사이즈 블레이저", "클래식 블레이저", "체크 블레이저",
            # 원피스/스커트
            "원피스", "스커트", "치마", "롱 원피스", "미니 원피스", "A라인 스커트",
            # 신발
            "운동화", "구두", "부츠", "슬리퍼", "샌들", "로퍼", "스니커즈", "하이탑",
            # 기타
            "액세서리", "가방", "시계", "모자", "벨트"
        ]
        
        found_keywords = []
        response_lower = response.lower()
        
        for keyword in product_keywords:
            # 키워드가 응답에 포함되어 있는지 확인 (공백 차이 무시)
            keyword_normalized = keyword.replace(" ", "")
            if keyword in response or keyword_normalized in response_lower.replace(" ", ""):
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _is_product_recommendation_response(self, response: str) -> bool:
        """
        GPT 응답이 상품 추천 완료 신호를 포함하는지 확인
        
        Args:
            response: GPT 응답 텍스트
            
        Returns:
            bool: 상품 추천 완료 신호가 있으면 True
        """
        # 완료 신호 키워드
        completion_signals = [
            "혹시 더 궁금한 점",
            "다른 스타일에 대한 요청",
            "다른 스타일에 대한",
            "추천해드릴게요",
            "추천드릴게요",
            "추천해드려요",
            "추천드려요",
            "제안",
            "어떤 스타일",
            "다른 스타일",
            "추천드립니다",
            "추천합니다",
        ]
        
        # 상품 키워드 개수 확인
        product_keywords = self._extract_product_keywords_from_response(response)
        
        # 신호가 있거나 상품 키워드가 2개 이상이면 추천 완료로 간주
        has_completion_signal = any(
            signal in response for signal in completion_signals
        )
        has_multiple_products = len(product_keywords) >= 2
        
        return has_completion_signal or has_multiple_products
    
    async def _match_products_from_response(
        self,
        response: str,
        user_message: str,
        intent_result: Any,
        user_profile: Optional[Dict],
        session: ChatSession
    ) -> List[Dict]:
        """
        GPT 응답에서 상품명을 추출하여 DB에서 매칭
        
        Args:
            response: GPT 응답 텍스트
            user_message: 사용자 메시지
            intent_result: 의도 분석 결과
            user_profile: 사용자 프로필
            session: 채팅 세션
        
        Returns:
            List[Dict]: 매칭된 상품 리스트
        """
        try:
            # 1. 상품 키워드 추출
            product_keywords = self._extract_product_keywords_from_response(response)
            
            # 2. 검색 쿼리 생성 (키워드 또는 사용자 메시지 사용)
            search_query = user_message
            if product_keywords:
                # 키워드를 조합하여 검색 쿼리 생성 (상위 3개 키워드)
                search_query = " ".join(product_keywords[:3])
                logger.info("Extracted product keywords from response",
                           keywords=product_keywords[:3],
                           query=search_query)
            
            # 3. DB 검색
            search_results = await self.search_engine.search_products(
                query=search_query,
                user_profile=user_profile,
                intent=intent_result.intent,
                limit=50
            )
            
            if not search_results:
                logger.warning("No products found for extracted keywords",
                             query=search_query)
                return []
            
            # 4. MMR 알고리즘으로 다양성 있는 추천 선택
            mmr_result = await self.mmr_scorer.select_recommendations(
                query_embedding=None,  # search_engine에서 임베딩 처리
                candidates=search_results,
                target_count=settings.MAX_RECOMMENDATIONS,
                strategy=intent_result.recommendation_strategy,
                excluded_ids=await self._get_excluded_products(session.user_id),
                user_history=await self._get_user_history(session.user_id)
            )
            
            # 5. 응답 형식으로 변환
            recommendations = []
            for product in mmr_result.selected_products:
                product_id = product.id
                product_url = f"/product/{product_id}"
                
                recommendations.append({
                    "id": product_id,
                    "name": product.metadata.get("name", ""),
                    "brand": product.metadata.get("brand", ""),
                    "price": product.metadata.get("price", 0),
                    "image_url": product.metadata.get("image_url", ""),
                    "product_url": product_url,
                    "similarity_score": product.similarity_score,
                    "recommendation_type": product.recommendation_type.value,
                    "reasoning": f"유사도: {product.similarity_score:.2f}"
                })
            
            logger.info("Products matched from GPT response",
                       count=len(recommendations),
                       keywords=product_keywords[:3])
            
            return recommendations
            
        except Exception as e:
            logger.error("Error matching products from response",
                        error=str(e),
                        exc_info=True)
            return []
    
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
            
            # 문서 규칙: 스타일 다양성 강제 (3개 이상의 다른 스타일 포함)
            mmr_result = await self._enforce_style_diversity(
                mmr_result=mmr_result,
                all_candidates=search_results,
                excluded_ids=await self._get_excluded_products(session.user_id)
            )
            
            # 응답 형식으로 변환
            recommendations = []
            for product in mmr_result.selected_products:
                product_id = product.id
                # 상품 상세 페이지 URL 생성
                product_url = f"/product/{product_id}"
                
                recommendations.append({
                    "id": product_id,
                    "name": product.metadata.get("name", ""),
                    "brand": product.metadata.get("brand", ""),
                    "price": product.metadata.get("price", 0),
                    "image_url": product.metadata.get("image_url", ""),
                    "product_url": product_url,  # 상품 상세 페이지 링크
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
        """
        최근 추천된 상품 ID 목록 (재추천 방지)
        문서 규칙:
        1. 최근 5회 대화에서 추천한 상품은 제외
        2. 이전에 추천했으나 클릭하지 않은 상품 우선 제외
        """
        excluded = set()
        
        if not self.chat_history_service:
            return excluded
            
        try:
            # 1. 최근 5개 대화에서 추천된 상품 ID 수집 (문서 규칙 준수)
            history = await self.chat_history_service.get_user_chat_history(user_id, limit=5)
            recommended_products = set()
            
            for h in history:
                if h.role == 'assistant' and h.meta_data:
                    # 메타데이터 구조에 따라 다를 수 있음 (recommendations가 ID 리스트인지 객체 리스트인지 확인 필요)
                    # 여기서는 안전하게 처리
                    recs = h.meta_data.get("recommendations", [])
                    for rec in recs:
                        if isinstance(rec, dict) and "id" in rec:
                            recommended_products.add(rec["id"])
                        elif isinstance(rec, str):
                            recommended_products.add(rec)
            
            excluded.update(recommended_products)
            
            # 2. 클릭 안 한 상품 제외 (문서 규칙: 이전에 추천했으나 클릭하지 않은 상품 우선 제외)
            if self.db and recommended_products:
                try:
                    # 클릭한 상품 목록 조회
                    clicked_products = set()
                    feedback_rows = self.db.query(RecommendationFeedback).filter(
                        RecommendationFeedback.user_id == user_id,
                        RecommendationFeedback.feedback_type == 'click',
                        RecommendationFeedback.product_id.in_(list(recommended_products))
                    ).all()
                    
                    clicked_products = {row.product_id for row in feedback_rows}
                    
                    # 추천했지만 클릭 안 한 상품 = 추천한 상품 - 클릭한 상품
                    not_clicked_products = recommended_products - clicked_products
                    
                    # 클릭 안 한 상품을 우선적으로 제외 목록에 추가
                    # (이미 excluded에 recommended_products가 포함되어 있으므로 별도 처리 불필요)
                    # 하지만 클릭 안 한 상품에 더 높은 우선순위를 주기 위해 별도로 관리
                    logger.debug("Click analysis", 
                                user_id=user_id,
                                recommended_count=len(recommended_products),
                                clicked_count=len(clicked_products),
                                not_clicked_count=len(not_clicked_products))
                    
                    # 클릭 안 한 상품은 더 강하게 제외 (추가 마킹)
                    # excluded에 이미 포함되어 있으므로 추가 작업 불필요
                    # 다만 로그로 기록
                    if not_clicked_products:
                        logger.info("Products recommended but not clicked will be excluded",
                                  user_id=user_id,
                                  not_clicked_products=list(not_clicked_products)[:5])  # 최대 5개만 로그
                    
                except Exception as e:
                    logger.warning(f"Failed to get click feedback: {e}")
            
            logger.debug("Excluded products collected", 
                        user_id=user_id,
                        excluded_count=len(excluded),
                        history_count=len(history))
            return excluded
        except Exception as e:
            logger.warning(f"Failed to get excluded products: {e}")
            return excluded
    
    async def _get_user_history(self, user_id: str) -> List[Dict]:
        """
        사용자 히스토리 조회
        클릭 로그가 없으므로 장바구니/좋아요 내역을 히스토리로 대체를서 활용
        """
        history = []
        
        # 1. 장바구니 내역 추가
        if self.cart_service:
            try:
                cart_items = await self.cart_service.get_user_cart(user_id)
                for item in cart_items:
                    history.append({
                        "product_id": item.product_id,
                        "action": "cart_add",
                        "timestamp": item.created_at.isoformat() if item.created_at else None,
                        "metadata": item.product_data or {}
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch cart history: {e}")

        # 2. 좋아요 내역 추가
        if self.favorite_service:
            try:
                favorites = await self.favorite_service.get_user_favorites(user_id)
                for fav in favorites:
                    history.append({
                        "product_id": fav.product_id,
                        "action": "like",
                        "timestamp": fav.created_at.isoformat() if fav.created_at else None,
                        "metadata": {}
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch favorite history: {e}")
        
        # 최신순 정렬
        history.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        return history
    
    async def _enforce_style_diversity(
        self,
        mmr_result: Any,
        all_candidates: List[Any],
        excluded_ids: set
    ) -> Any:
        """
        스타일 다양성 강제 검증
        문서 규칙: 한 번에 3개 이상의 다른 스타일 포함
        
        Args:
            mmr_result: MMR 알고리즘 결과
            all_candidates: 전체 후보 상품 리스트
            excluded_ids: 제외할 상품 ID 집합
            
        Returns:
            수정된 MMRResult (최소 3개 이상의 다른 스타일 보장)
        """
        from ml.mmr_algorithm.mmr_scorer import MMRResult, ProductCandidate
        
        selected_products = mmr_result.selected_products
        
        if not selected_products:
            return mmr_result
        
        # 선택된 상품들의 스타일 태그 수집
        style_tags_set = set()
        for product in selected_products:
            style_tags = product.metadata.get("style_tags", [])
            if isinstance(style_tags, list):
                style_tags_set.update(style_tags)
            elif isinstance(style_tags, str):
                # 문자열인 경우 쉼표로 분리
                style_tags_set.update([s.strip() for s in style_tags.split(",")])
        
        unique_style_count = len(style_tags_set)
        
        logger.debug("Style diversity check",
                    unique_styles=unique_style_count,
                    style_tags=list(style_tags_set)[:10])  # 최대 10개만 로그
        
        # 문서 규칙: 최소 3개 이상의 다른 스타일 필요
        if unique_style_count >= 3:
            logger.info("Style diversity requirement met",
                       unique_styles=unique_style_count)
            return mmr_result
        
        # 3개 미만이면 추가 상품 선택 시도
        logger.warning("Style diversity requirement not met, attempting to add diverse products",
                     current_styles=unique_style_count,
                     required=3)
        
        # 이미 선택된 상품 ID 집합
        selected_ids = {p.id for p in selected_products}
        
        # 추가 선택 가능한 후보 (제외 목록과 이미 선택된 상품 제외)
        available_candidates = [
            c for c in all_candidates
            if c.id not in excluded_ids
            and c.id not in selected_ids
        ]
        
        # 스타일 태그가 다른 상품 찾기
        additional_products = []
        target_additional = max(1, 3 - unique_style_count)  # 최소 1개, 최대 필요한 만큼
        
        for candidate in available_candidates:
            if len(additional_products) >= target_additional:
                break
            
            candidate_styles = candidate.metadata.get("style_tags", [])
            if isinstance(candidate_styles, str):
                candidate_styles = [s.strip() for s in candidate_styles.split(",")]
            
            candidate_style_set = set(candidate_styles) if isinstance(candidate_styles, list) else set()
            
            # 기존 스타일과 겹치지 않는 상품 우선 선택
            if not candidate_style_set.intersection(style_tags_set):
                additional_products.append(candidate)
                style_tags_set.update(candidate_style_set)
            # 겹치지만 새로운 스타일 태그가 있는 경우도 고려
            elif len(candidate_style_set - style_tags_set) > 0:
                additional_products.append(candidate)
                style_tags_set.update(candidate_style_set)
        
        # 추가 상품이 있으면 결과에 추가
        if additional_products:
            selected_products.extend(additional_products)
            logger.info("Added products to meet style diversity requirement",
                       added_count=len(additional_products),
                       total_styles=len(style_tags_set))
        else:
            logger.warning("Could not find additional products to meet style diversity requirement",
                         current_styles=unique_style_count)
        
        # MMRResult 재생성 (다양성 점수 재계산)
        from ml.mmr_algorithm.diversity_calculator import DiversityCalculator
        diversity_calculator = DiversityCalculator()
        total_diversity = diversity_calculator.calculate_overall_diversity(
            [p.metadata for p in selected_products]
        )
        
        # 타입 분포 재계산
        type_distribution = {}
        for product in selected_products:
            rec_type = product.recommendation_type.value if hasattr(product.recommendation_type, 'value') else str(product.recommendation_type)
            type_distribution[rec_type] = type_distribution.get(rec_type, 0) + 1
        
        # 선택 이유 업데이트
        selection_reasoning = mmr_result.selection_reasoning.copy()
        if additional_products:
            selection_reasoning.append(
                f"스타일 다양성 강제: {len(additional_products)}개 상품 추가 (총 {len(style_tags_set)}개 스타일)"
            )
        
        return MMRResult(
            selected_products=selected_products,
            total_diversity_score=total_diversity,
            type_distribution=type_distribution,
            selection_reasoning=selection_reasoning
        )
    
    async def _save_messages(
        self, 
        session: ChatSession, 
        user_message: str, 
        ai_response: str,
        intent_result: Any
    ):
        """메시지를 데이터베이스에 저장"""
        if not self.chat_history_service:
            logger.warning("Chat history service not initialized, skipping save")
            return

        try:
            metadata = {
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "exploration_intent": intent_result.exploration_intent,
                "category_shift": intent_result.category_shift
            }
            
            await self.chat_history_service.save_conversation(
                session_id=session.session_id,
                user_id=session.user_id,
                user_message=user_message,
                assistant_message=ai_response,
                metadata=metadata
            )
            
            logger.debug("Messages saved to database", 
                        session_id=session.session_id)
            
        except Exception as e:
            logger.error("Error saving messages", 
                        session_id=session.session_id,
                        error=str(e))