from typing import List, Dict, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RecommendationService:
    """추천 서비스"""
    
    def __init__(self):
        # TODO: 실제 데이터베이스 연결
        self._recommendation_history = {}  # 임시 메모리 저장
        self._feedback_data = {}
        logger.info("Recommendation service initialized")
    
    async def get_recommendations(
        self,
        query: str,
        user_id: str,
        filters: Optional[Dict] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """상품 추천 조회"""
        try:
            logger.info("Getting recommendations",
                       user_id=user_id, 
                       query=query[:50], 
                       limit=limit)
            
            # TODO: 실제 추천 로직 구현 (ChatService와 연동)
            # 현재는 더미 데이터 반환
            dummy_recommendations = self._generate_dummy_recommendations(limit)
            
            result = {
                "recommendations": dummy_recommendations,
                "total_count": len(dummy_recommendations),
                "diversity_score": 0.75,
                "strategy_used": {
                    "exploitation": 0.7,
                    "exploration": 0.3
                }
            }
            
            # 추천 히스토리 저장
            await self._save_recommendation_history(user_id, query, result)
            
            return result
            
        except Exception as e:
            logger.error("Error getting recommendations",
                        user_id=user_id, error=str(e))
            raise
    
    async def get_user_recommendation_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """사용자 추천 히스토리 조회"""
        try:
            history = self._recommendation_history.get(user_id, [])
            
            # 정렬 및 페이지네이션
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            start = offset
            end = offset + limit
            
            logger.debug("Retrieved recommendation history",
                        user_id=user_id,
                        total=len(history),
                        returned=len(history[start:end]))
            
            return history[start:end]
            
        except Exception as e:
            logger.error("Error retrieving recommendation history",
                        user_id=user_id, error=str(e))
            return []
    
    async def record_feedback(
        self,
        user_id: str,
        product_id: str,
        feedback_type: str
    ) -> bool:
        """추천 피드백 기록"""
        try:
            if user_id not in self._feedback_data:
                self._feedback_data[user_id] = []
            
            feedback = {
                "product_id": product_id,
                "feedback_type": feedback_type,
                "timestamp": datetime.now().isoformat()
            }
            
            self._feedback_data[user_id].append(feedback)
            
            logger.info("Feedback recorded",
                       user_id=user_id,
                       product_id=product_id,
                       feedback_type=feedback_type)
            
            return True
            
        except Exception as e:
            logger.error("Error recording feedback",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            return False
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """사용자 추천 분석"""
        try:
            history = self._recommendation_history.get(user_id, [])
            feedback = self._feedback_data.get(user_id, [])
            
            analytics = {
                "total_recommendations": len(history),
                "total_feedback": len(feedback),
                "feedback_breakdown": self._analyze_feedback(feedback),
                "recommendation_patterns": self._analyze_recommendation_patterns(history),
                "exploration_rate": self._calculate_exploration_rate(feedback)
            }
            
            logger.debug("User analytics generated", user_id=user_id)
            
            return analytics
            
        except Exception as e:
            logger.error("Error generating user analytics",
                        user_id=user_id, error=str(e))
            return {}
    
    def _generate_dummy_recommendations(self, limit: int) -> List[Dict]:
        """더미 추천 데이터 생성"""
        recommendations = []
        
        dummy_products = [
            {"name": "미니멀 코튼 셔츠", "brand": "브랜드A", "price": 59000, "type": "exploitation"},
            {"name": "오버핏 후드티", "brand": "브랜드B", "price": 45000, "type": "exploitation"},
            {"name": "워크 재킷", "brand": "브랜드C", "price": 89000, "type": "exploration"},
            {"name": "린넨 블레이저", "brand": "브랜드D", "price": 120000, "type": "exploration"},
            {"name": "세미 와이드 슬랙스", "brand": "브랜드E", "price": 69000, "type": "bridge"},
        ]
        
        for i in range(min(limit, len(dummy_products))):
            product = dummy_products[i % len(dummy_products)]
            recommendations.append({
                "id": f"prod_{i+1:03d}",
                "name": f"{product['name']} {i+1}",
                "brand": product["brand"],
                "price": product["price"],
                "image_url": f"https://example.com/image_{i+1}.jpg",
                "similarity_score": 0.85 - (i * 0.05),
                "recommendation_type": product["type"],
                "reasoning": f"추천 이유 {i+1}"
            })
        
        return recommendations
    
    async def _save_recommendation_history(
        self,
        user_id: str,
        query: str,
        result: Dict
    ):
        """추천 히스토리 저장"""
        if user_id not in self._recommendation_history:
            self._recommendation_history[user_id] = []
        
        history_entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "recommendations_count": result["total_count"],
            "diversity_score": result["diversity_score"],
            "strategy_used": result["strategy_used"]
        }
        
        self._recommendation_history[user_id].append(history_entry)
        
        # 최대 100개까지만 보관
        if len(self._recommendation_history[user_id]) > 100:
            self._recommendation_history[user_id] = self._recommendation_history[user_id][-100:]
    
    def _analyze_feedback(self, feedback: List[Dict]) -> Dict[str, int]:
        """피드백 분석"""
        breakdown = {"click": 0, "like": 0, "dislike": 0, "purchase": 0}
        
        for fb in feedback:
            feedback_type = fb.get("feedback_type", "")
            if feedback_type in breakdown:
                breakdown[feedback_type] += 1
        
        return breakdown
    
    def _analyze_recommendation_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """추천 패턴 분석"""
        if not history:
            return {}
        
        total_recommendations = sum(h.get("recommendations_count", 0) for h in history)
        avg_diversity = sum(h.get("diversity_score", 0) for h in history) / len(history)
        
        return {
            "total_sessions": len(history),
            "total_recommendations": total_recommendations,
            "avg_recommendations_per_session": total_recommendations / len(history) if history else 0,
            "avg_diversity_score": round(avg_diversity, 3)
        }
    
    def _calculate_exploration_rate(self, feedback: List[Dict]) -> float:
        """탐색률 계산"""
        if not feedback:
            return 0.0
        
        exploration_actions = ["like", "purchase"]
        exploration_count = sum(1 for fb in feedback if fb.get("feedback_type") in exploration_actions)
        
        return round(exploration_count / len(feedback), 3)