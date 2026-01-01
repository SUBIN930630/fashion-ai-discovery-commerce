import numpy as np
from typing import List, Dict, Optional, Any
from enum import Enum

from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from ..mmr_algorithm.mmr_scorer import ProductCandidate, RecommendationType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SearchEngine:
    """상품 검색 엔진"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL,
            dimensions=settings.EMBEDDING_DIMENSIONS
        )
        
        self.vector_store = VectorStore(
            store_type=settings.VECTOR_DB_TYPE,
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME,
            dimension=settings.EMBEDDING_DIMENSIONS
        )
        
        logger.info("Search engine initialized")
    
    async def search_products(
        self,
        query: str,
        user_profile: Optional[Dict] = None,
        intent: Any = None,
        limit: int = 50,
        filters: Optional[Dict] = None
    ) -> List[ProductCandidate]:
        """
        상품 검색
        
        Args:
            query: 검색 쿼리
            user_profile: 사용자 프로필
            intent: 분석된 의도
            limit: 검색 결과 수
            filters: 추가 필터
            
        Returns:
            List[ProductCandidate]: 검색된 상품 후보들
        """
        try:
            logger.info("Starting product search", 
                       query=query[:50], 
                       limit=limit)
            
            # 1. 쿼리 임베딩 생성
            query_context = self._build_query_context(query, user_profile, intent)
            query_embedding = await self.embedding_service.embed_user_query(
                query, query_context
            )
            
            # 2. 벡터 검색 실행
            search_results = await self.vector_store.search(
                query_vector=query_embedding,
                top_k=limit,
                filters=filters
            )
            
            if not search_results:
                logger.warning("No search results found", query=query[:50])
                return []
            
            # 3. ProductCandidate 객체로 변환
            candidates = []
            for result in search_results:
                candidate = await self._convert_to_candidate(
                    result, query_embedding, user_profile, intent
                )
                if candidate:
                    candidates.append(candidate)
            
            logger.info("Search completed", 
                       query=query[:50],
                       results_count=len(candidates))
            
            return candidates
            
        except Exception as e:
            logger.error("Error in product search", 
                        query=query[:50], 
                        error=str(e))
            return []
    
    async def search_by_similarity_ranges(
        self,
        query: str,
        user_profile: Optional[Dict] = None,
        exploitation_limit: int = 20,
        exploration_limit: int = 20,
        bridge_limit: int = 10
    ) -> Dict[str, List[ProductCandidate]]:
        """
        유사도 범위별로 상품 검색
        
        Returns:
            Dict with 'exploitation', 'exploration', 'bridge' keys
        """
        try:
            # 전체 검색 실행
            all_candidates = await self.search_products(
                query=query,
                user_profile=user_profile,
                limit=exploitation_limit + exploration_limit + bridge_limit
            )
            
            # 유사도 기준으로 분류
            exploitation_candidates = []
            bridge_candidates = []
            exploration_candidates = []
            
            for candidate in all_candidates:
                similarity = candidate.similarity_score
                
                if similarity >= settings.MAX_SIMILARITY_THRESHOLD:
                    exploitation_candidates.append(candidate)
                    candidate.recommendation_type = RecommendationType.EXPLOITATION
                elif similarity >= 0.5:
                    bridge_candidates.append(candidate)
                    candidate.recommendation_type = RecommendationType.BRIDGE
                else:
                    exploration_candidates.append(candidate)
                    candidate.recommendation_type = RecommendationType.EXPLORATION
            
            # 제한 수만큼 선택
            result = {
                "exploitation": exploitation_candidates[:exploitation_limit],
                "bridge": bridge_candidates[:bridge_limit],
                "exploration": exploration_candidates[:exploration_limit]
            }
            
            logger.info("Similarity-based search completed",
                       exploitation_count=len(result["exploitation"]),
                       bridge_count=len(result["bridge"]),
                       exploration_count=len(result["exploration"]))
            
            return result
            
        except Exception as e:
            logger.error("Error in similarity-based search", error=str(e))
            return {"exploitation": [], "bridge": [], "exploration": []}
    
    def _build_query_context(
        self, 
        query: str, 
        user_profile: Optional[Dict], 
        intent: Any
    ) -> Dict:
        """검색 쿼리 컨텍스트 구성"""
        context = {}
        
        if user_profile:
            context.update({
                "preferred_styles": list(user_profile.get("style_distribution", {}).keys()),
                "preferred_categories": user_profile.get("preferred_categories", []),
                "price_range": user_profile.get("price_range", {})
            })
        
        if intent:
            context["recent_intent"] = str(intent)
        
        return context
    
    async def _convert_to_candidate(
        self,
        search_result: Dict,
        query_embedding: np.ndarray,
        user_profile: Optional[Dict],
        intent: Any
    ) -> Optional[ProductCandidate]:
        """검색 결과를 ProductCandidate로 변환"""
        try:
            metadata = search_result.get("metadata", {})
            
            # 상품 임베딩 재구성 (실제로는 벡터 DB에서 가져와야 함)
            product_embedding = np.random.rand(settings.EMBEDDING_DIMENSIONS).astype(np.float32)
            
            # 추천 유형 결정
            similarity_score = search_result.get("score", 0.0)
            rec_type = self._determine_recommendation_type(
                similarity_score, user_profile, metadata
            )
            
            # 다양성 점수 계산 (간단한 버전)
            diversity_scores = {
                "style": 0.5,
                "category": 0.5,
                "color": 0.5,
                "price": 0.5
            }
            
            candidate = ProductCandidate(
                id=search_result["id"],
                embedding=product_embedding,
                metadata=metadata,
                similarity_score=similarity_score,
                recommendation_type=rec_type,
                diversity_scores=diversity_scores
            )
            
            return candidate
            
        except Exception as e:
            logger.error("Error converting to candidate", 
                        result_id=search_result.get("id", "unknown"),
                        error=str(e))
            return None
    
    def _determine_recommendation_type(
        self,
        similarity_score: float,
        user_profile: Optional[Dict],
        metadata: Dict
    ) -> RecommendationType:
        """유사도 점수를 기반으로 추천 유형 결정"""
        
        if similarity_score >= settings.MAX_SIMILARITY_THRESHOLD:
            return RecommendationType.EXPLOITATION
        elif similarity_score >= 0.5:
            return RecommendationType.BRIDGE
        else:
            return RecommendationType.EXPLORATION
    
    async def index_products(self, products: List[Dict]) -> bool:
        """상품들을 벡터 DB에 인덱싱"""
        try:
            logger.info("Starting product indexing", count=len(products))
            
            # 상품 임베딩 생성
            vectors = []
            for product in products:
                embedding = await self.embedding_service.embed_product(product)
                
                vectors.append({
                    "id": product["id"],
                    "embedding": embedding,
                    "metadata": product
                })
            
            # 벡터 DB에 저장
            success = await self.vector_store.upsert(vectors)
            
            if success:
                logger.info("Product indexing completed", count=len(products))
            else:
                logger.error("Product indexing failed")
            
            return success
            
        except Exception as e:
            logger.error("Error indexing products", 
                        count=len(products), 
                        error=str(e))
            return False