from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import or_, String

from app.core.logging import get_logger
from app.models.db_models import RecommendationFeedback, RecommendationHistory, Product, UserFavorite, UserCart

logger = get_logger(__name__)


class RecommendationService:
    """추천 서비스"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._recommendation_history = {} if db is None else None
        self._feedback_data = {} if db is None else None
        logger.info("Recommendation service initialized", has_db=db is not None)
    
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
            if self.db is None:
                history = self._recommendation_history.get(user_id, [])

                # 정렬 및 페이지네이션
                history.sort(key=lambda x: x["timestamp"], reverse=True)

                start = offset
                end = offset + limit

                logger.debug(
                    "Retrieved recommendation history",
                    user_id=user_id,
                    total=len(history),
                    returned=len(history[start:end]),
                )

                return history[start:end]

            rows = self.db.query(RecommendationHistory).filter(
                RecommendationHistory.user_id == user_id
            ).order_by(RecommendationHistory.created_at.desc()).offset(offset).limit(limit).all()

            history = [
                {
                    "query": row.query,
                    "timestamp": row.created_at.isoformat() if row.created_at else None,
                    "recommendations_count": row.total_count,
                    "diversity_score": row.diversity_score,
                    "strategy_used": row.strategy_used,
                }
                for row in rows
            ]

            logger.debug(
                "Retrieved recommendation history",
                user_id=user_id,
                total=len(history),
                returned=len(history),
            )

            return history

        except Exception as e:
            logger.error(
                "Error retrieving recommendation history",
                user_id=user_id,
                error=str(e),
            )
            return []
    
    async def record_feedback(
        self,
        user_id: str,
        product_id: str,
        feedback_type: str
    ) -> bool:
        """추천 피드백 기록"""
        try:
            if self.db is None:
                if user_id not in self._feedback_data:
                    self._feedback_data[user_id] = []

                feedback = {
                    "product_id": product_id,
                    "feedback_type": feedback_type,
                    "timestamp": datetime.now().isoformat(),
                }

                self._feedback_data[user_id].append(feedback)

                logger.info(
                    "Feedback recorded",
                    user_id=user_id,
                    product_id=product_id,
                    feedback_type=feedback_type,
                )

                return True

            feedback_row = RecommendationFeedback(
                user_id=user_id,
                product_id=product_id,
                feedback_type=feedback_type,
            )
            self.db.add(feedback_row)
            self.db.commit()
            logger.info(
                "Feedback recorded",
                user_id=user_id,
                product_id=product_id,
                feedback_type=feedback_type,
            )

            return True

        except Exception as e:
            if self.db:
                self.db.rollback()
            logger.error(
                "Error recording feedback",
                user_id=user_id,
                product_id=product_id,
                error=str(e),
            )
            return False
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """사용자 추천 분석"""
        try:
            if self.db is None:
                history = self._recommendation_history.get(user_id, [])
                feedback = self._feedback_data.get(user_id, [])
            else:
                history_rows = self.db.query(RecommendationHistory).filter(
                    RecommendationHistory.user_id == user_id
                ).all()
                feedback_rows = self.db.query(RecommendationFeedback).filter(
                    RecommendationFeedback.user_id == user_id
                ).all()

                history = [
                    {
                        "recommendations_count": row.total_count,
                        "diversity_score": row.diversity_score,
                        "timestamp": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in history_rows
                ]
                feedback = [
                    {
                        "product_id": row.product_id,
                        "feedback_type": row.feedback_type,
                        "timestamp": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in feedback_rows
                ]
            
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
        if self.db is None:
            if user_id not in self._recommendation_history:
                self._recommendation_history[user_id] = []

            history_entry = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "recommendations_count": result["total_count"],
                "diversity_score": result["diversity_score"],
                "strategy_used": result["strategy_used"],
            }

            self._recommendation_history[user_id].append(history_entry)

            # 최대 100개까지만 보관
            if len(self._recommendation_history[user_id]) > 100:
                self._recommendation_history[user_id] = self._recommendation_history[user_id][-100:]
            return

        history_row = RecommendationHistory(
            user_id=user_id,
            query=query,
            recommendations=result.get("recommendations", []),
            total_count=result["total_count"],
            diversity_score=result["diversity_score"],
            strategy_used=result["strategy_used"],
        )
        try:
            self.db.add(history_row)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to save recommendation history", error=str(e))
    
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
    
    async def analyze_user_preferences_from_db(self, user_id: str) -> Dict[str, Any]:
        """
        DB에서 사용자 취향 분석 (좋아요, 장바구니 기반)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 취향 정보 (style_distribution, preferred_categories, preferred_brands, price_range)
        """
        if not self.db:
            logger.warning("Database not available for user preference analysis")
            return {}
        
        try:
            # 좋아요한 상품 ID 목록
            favorite_product_ids = [
                f.product_id 
                for f in self.db.query(UserFavorite).filter(
                    UserFavorite.user_id == user_id
                ).all()
            ]
            
            # 장바구니에 담은 상품 ID 목록
            cart_product_ids = [
                c.product_id 
                for c in self.db.query(UserCart).filter(
                    UserCart.user_id == user_id
                ).all()
            ]
            
            # 모든 관심 상품 ID (중복 제거)
            all_interested_product_ids = list(set(favorite_product_ids + cart_product_ids))
            
            if not all_interested_product_ids:
                logger.debug("No user preferences found", user_id=user_id)
                return {}
            
            # 상품 정보 조회
            products = self.db.query(Product).filter(
                Product.product_id.in_(all_interested_product_ids)
            ).all()
            
            # 스타일 태그 분석
            style_counter = Counter()
            category_counter = Counter()
            brand_counter = Counter()
            prices = []
            
            for product in products:
                # 스타일 태그
                if product.style_tags:
                    if isinstance(product.style_tags, list):
                        for tag in product.style_tags:
                            style_counter[tag] += 1
                    elif isinstance(product.style_tags, str):
                        style_counter[product.style_tags] += 1
                
                # 카테고리
                if product.category:
                    category_counter[product.category] += 1
                
                # 브랜드
                if product.brand:
                    brand_counter[product.brand] += 1
                
                # 가격
                if product.price:
                    prices.append(product.price)
            
            # 스타일 분포 계산 (정규화)
            total_style_count = sum(style_counter.values())
            style_distribution = {
                style: round(count / total_style_count, 3) 
                for style, count in style_counter.most_common(10)
            } if total_style_count > 0 else {}
            
            # 선호 카테고리 (상위 5개)
            preferred_categories = [
                category for category, _ in category_counter.most_common(5)
            ]
            
            # 선호 브랜드 (상위 5개)
            preferred_brands = [
                brand for brand, _ in brand_counter.most_common(5)
            ]
            
            # 가격 범위
            price_range = {}
            if prices:
                price_range = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": round(sum(prices) / len(prices))
                }
            
            preferences = {
                "style_distribution": style_distribution,
                "preferred_categories": preferred_categories,
                "preferred_brands": preferred_brands,
                "price_range": price_range,
                "favorite_count": len(favorite_product_ids),
                "cart_count": len(cart_product_ids),
                "total_interested_products": len(all_interested_product_ids)
            }
            
            logger.info("User preferences analyzed from DB",
                       user_id=user_id,
                       styles_count=len(style_distribution),
                       categories_count=len(preferred_categories),
                       brands_count=len(preferred_brands))
            
            return preferences
            
        except Exception as e:
            logger.error("Error analyzing user preferences from DB",
                        user_id=user_id, error=str(e))
            return {}
    
    async def search_products_with_user_preferences(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        사용자 취향을 반영한 상품 검색
        
        Args:
            query: 검색 쿼리
            user_id: 사용자 ID (로그인된 경우)
            limit: 검색 결과 수
            
        Returns:
            검색 결과 리스트 (유사도 높은 순으로 정렬)
        """
        if not self.db:
            logger.warning("Database not available for product search")
            return []
        
        try:
            # 기본 검색: 상품명, 브랜드, 카테고리, 스타일 태그에서 검색
            search_terms = query.lower().split()
            
            # SQL 쿼리 구성
            query_obj = self.db.query(Product)
            
            # 검색 조건 (OR 조건)
            conditions = []
            for term in search_terms:
                conditions.append(Product.name.ilike(f"%{term}%"))
                conditions.append(Product.brand.ilike(f"%{term}%"))
                conditions.append(Product.category.ilike(f"%{term}%"))
                # JSON 필드 검색 (style_tags)
                # PostgreSQL의 경우 JSONB 연산자 사용
                conditions.append(Product.style_tags.cast(String).ilike(f"%{term}%"))
            
            if conditions:
                query_obj = query_obj.filter(or_(*conditions))
            
            # 검색 결과 조회
            products = query_obj.limit(limit * 2).all()  # 정렬 후 필터링을 위해 더 많이 가져옴
            
            if not products:
                logger.info("No products found", query=query)
                return []
            
            # 사용자 취향 분석 (로그인된 경우)
            user_preferences = {}
            if user_id:
                user_preferences = await self.analyze_user_preferences_from_db(user_id)
            
            # 검색 결과를 딕셔너리로 변환하고 유사도 점수 계산
            results = []
            for product in products:
                product_dict = {
                    "product_id": product.product_id,
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "gender": product.gender,
                    "style_tags": product.style_tags if product.style_tags else [],
                    "color": product.color,
                    "price": product.price,
                    "image_url": product.image_url,
                    "description": product.description,
                    "popularity_score": product.popularity_score or 0.0,
                    "similarity_score": 0.0  # 기본값
                }
                
                # 사용자 취향 기반 유사도 점수 계산
                if user_preferences:
                    similarity = self._calculate_preference_similarity(
                        product_dict, user_preferences
                    )
                    product_dict["similarity_score"] = similarity
                else:
                    # 비로그인 사용자는 인기도 기반 점수
                    product_dict["similarity_score"] = product.popularity_score or 0.0
                
                results.append(product_dict)
            
            # 유사도 점수 기준으로 정렬 (높은 순)
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # limit만큼만 반환
            results = results[:limit]
            
            logger.info("Product search completed",
                       query=query,
                       user_id=user_id,
                       results_count=len(results),
                       has_preferences=bool(user_preferences))
            
            return results
            
        except Exception as e:
            logger.error("Error searching products with user preferences",
                        query=query, user_id=user_id, error=str(e))
            return []
    
    def _calculate_preference_similarity(
        self,
        product: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> float:
        """
        상품과 사용자 취향 간의 유사도 점수 계산
        
        Args:
            product: 상품 정보
            user_preferences: 사용자 취향 정보
            
        Returns:
            유사도 점수 (0.0 ~ 1.0)
        """
        score = 0.0
        weight_sum = 0.0
        
        # 1. 스타일 태그 유사도 (가중치: 0.4)
        style_weight = 0.4
        style_distribution = user_preferences.get("style_distribution", {})
        if style_distribution and product.get("style_tags"):
            product_styles = product["style_tags"] if isinstance(product["style_tags"], list) else [product["style_tags"]]
            style_match_score = sum(
                style_distribution.get(style, 0) for style in product_styles
            )
            score += style_match_score * style_weight
            weight_sum += style_weight
        
        # 2. 카테고리 유사도 (가중치: 0.3)
        category_weight = 0.3
        preferred_categories = user_preferences.get("preferred_categories", [])
        if preferred_categories and product.get("category"):
            if product["category"] in preferred_categories:
                # 상위 카테고리일수록 높은 점수
                category_index = preferred_categories.index(product["category"])
                category_score = 1.0 - (category_index * 0.1)  # 1.0, 0.9, 0.8, ...
                score += category_score * category_weight
            weight_sum += category_weight
        
        # 3. 브랜드 유사도 (가중치: 0.2)
        brand_weight = 0.2
        preferred_brands = user_preferences.get("preferred_brands", [])
        if preferred_brands and product.get("brand"):
            if product["brand"] in preferred_brands:
                brand_index = preferred_brands.index(product["brand"])
                brand_score = 1.0 - (brand_index * 0.1)
                score += brand_score * brand_weight
            weight_sum += brand_weight
        
        # 4. 가격 범위 유사도 (가중치: 0.1)
        price_weight = 0.1
        price_range = user_preferences.get("price_range", {})
        if price_range and product.get("price"):
            price_min = price_range.get("min", 0)
            price_max = price_range.get("max", float('inf'))
            product_price = product["price"]
            
            if price_min <= product_price <= price_max:
                # 가격 범위 내에 있으면 높은 점수
                price_score = 1.0
            else:
                # 범위 밖이면 거리에 따라 점수 감소
                if product_price < price_min:
                    distance = price_min - product_price
                else:
                    distance = product_price - price_max
                
                # 거리가 가격 범위의 50% 이내면 점수 부여
                range_size = price_max - price_min if price_max != float('inf') else price_min
                if range_size > 0:
                    price_score = max(0.0, 1.0 - (distance / (range_size * 0.5)))
                else:
                    price_score = 0.5
                
            score += price_score * price_weight
            weight_sum += price_weight
        
        # 정규화 (가중치 합으로 나누기)
        if weight_sum > 0:
            normalized_score = score / weight_sum
        else:
            normalized_score = 0.0
        
        # 인기도 점수 추가 (최대 0.2까지)
        popularity_bonus = min(0.2, (product.get("popularity_score", 0.0) or 0.0) * 0.2)
        final_score = min(1.0, normalized_score + popularity_bonus)
        
        return round(final_score, 3)
