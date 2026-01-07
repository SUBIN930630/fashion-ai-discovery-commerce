import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .diversity_calculator import DiversityCalculator
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecommendationType(str, Enum):
    """추천 유형"""
    EXPLOITATION = "exploitation"  # 기존 취향
    EXPLORATION = "exploration"    # 새로운 발견
    BRIDGE = "bridge"             # 브릿지 스타일


@dataclass
class ProductCandidate:
    """상품 후보 정보"""
    id: str
    embedding: np.ndarray
    metadata: Dict
    similarity_score: float
    recommendation_type: RecommendationType
    diversity_scores: Dict[str, float]  # 다양성 점수들


@dataclass
class MMRResult:
    """MMR 알고리즘 결과"""
    selected_products: List[ProductCandidate]
    total_diversity_score: float
    type_distribution: Dict[str, int]
    selection_reasoning: List[str]


class MMRScorer:
    """
    MMR (Maximal Marginal Relevance) 알고리즘을 구현하는 클래스
    유사도와 다양성의 균형을 맞춰 상품을 추천
    """
    
    def __init__(
        self,
        lambda_param: float = 0.7,
        diversity_calculator: Optional[DiversityCalculator] = None
    ):
        self.lambda_param = lambda_param  # 유사도 vs 다양성 가중치
        self.diversity_calculator = diversity_calculator or DiversityCalculator()
        
        logger.info("MMR Scorer initialized", lambda_param=lambda_param)
    
    async def select_recommendations(
        self,
        query_embedding: np.ndarray,
        candidates: List[ProductCandidate],
        target_count: int = 10,
        strategy: Dict[str, float] = None,
        excluded_ids: Optional[Set[str]] = None,
        user_history: Optional[List[Dict]] = None
    ) -> MMRResult:
        """
        MMR 알고리즘을 사용하여 추천 상품을 선택
        
        Args:
            query_embedding: 사용자 쿼리 임베딩
            candidates: 후보 상품 리스트
            target_count: 목표 추천 개수
            strategy: 추천 전략 비율 {exploitation: 0.7, exploration: 0.3}
            excluded_ids: 제외할 상품 ID
            user_history: 사용자 이력
            
        Returns:
            MMRResult: 선택된 상품과 메타데이터
        """
        
        if not candidates:
            logger.warning("No candidates provided for MMR selection")
            return MMRResult([], 0.0, {}, ["후보 상품이 없습니다."])
        
        # 제외 상품 필터링
        if excluded_ids:
            candidates = [c for c in candidates if c.id not in excluded_ids]
        
        # 기본 전략 설정
        if strategy is None:
            strategy = {"exploitation": 0.7, "exploration": 0.3}
        
        logger.info("Starting MMR selection", 
                   candidates_count=len(candidates),
                   target_count=target_count,
                   strategy=strategy)
        
        selected = []
        selection_reasoning = []
        
        # 유형별 목표 개수 계산
        type_targets = self._calculate_type_targets(target_count, strategy)
        type_selected = {rtype.value: 0 for rtype in RecommendationType}
        
        # 후보를 유형별로 그룹화
        candidates_by_type = self._group_candidates_by_type(candidates)
        
        # MMR 선택 루프
        for step in range(target_count):
            if not any(candidates_by_type.values()):
                break
            
            # 현재 단계에서 선택할 유형 결정
            target_type = self._select_next_type(
                type_selected, type_targets, candidates_by_type
            )
            
            if not target_type or not candidates_by_type[target_type]:
                # 다른 유형에서 선택
                available_types = [t for t, cands in candidates_by_type.items() if cands]
                if not available_types:
                    break
                target_type = available_types[0]
            
            # MMR 점수 계산하여 최적 후보 선택
            best_candidate = self._select_best_candidate(
                query_embedding, candidates_by_type[target_type], selected
            )
            
            if best_candidate is None:
                break
            
            # 선택된 상품 추가
            selected.append(best_candidate)
            type_selected[target_type] += 1
            
            # 해당 후보를 후보 목록에서 제거
            candidates_by_type[target_type].remove(best_candidate)
            
            # 선택 이유 기록
            reasoning = self._generate_selection_reasoning(
                best_candidate, step + 1, len(selected), target_type
            )
            selection_reasoning.append(reasoning)
            
            logger.debug("Product selected", 
                        step=step + 1,
                        product_id=best_candidate.id,
                        type=target_type,
                        mmr_score=getattr(best_candidate, 'mmr_score', 0))
        
        # 전체 다양성 점수 계산
        total_diversity = self.diversity_calculator.calculate_overall_diversity(
            [p.metadata for p in selected]
        )
        
        logger.info("MMR selection completed",
                   selected_count=len(selected),
                   type_distribution=type_selected,
                   total_diversity=total_diversity)
        
        return MMRResult(
            selected_products=selected,
            total_diversity_score=total_diversity,
            type_distribution=type_selected,
            selection_reasoning=selection_reasoning
        )
    
    def _calculate_type_targets(
        self, 
        target_count: int, 
        strategy: Dict[str, float]
    ) -> Dict[str, int]:
        """유형별 목표 개수 계산"""
        
        targets = {}
        
        for rtype in RecommendationType:
            ratio = strategy.get(rtype.value, 0.0)
            targets[rtype.value] = max(1, int(target_count * ratio))
        
        # 합계가 목표 개수와 맞지 않으면 조정
        total = sum(targets.values())
        if total != target_count:
            diff = target_count - total
            # exploration 유형에서 조정
            if RecommendationType.EXPLORATION.value in targets:
                targets[RecommendationType.EXPLORATION.value] += diff
            else:
                # 가장 큰 비율의 유형에서 조정
                max_type = max(targets.keys(), key=lambda k: targets[k])
                targets[max_type] += diff
        
        return targets
    
    def _group_candidates_by_type(
        self, 
        candidates: List[ProductCandidate]
    ) -> Dict[str, List[ProductCandidate]]:
        """후보를 추천 유형별로 그룹화"""
        
        groups = {rtype.value: [] for rtype in RecommendationType}
        
        for candidate in candidates:
            groups[candidate.recommendation_type.value].append(candidate)
        
        return groups
    
    def _select_next_type(
        self,
        type_selected: Dict[str, int],
        type_targets: Dict[str, int],
        candidates_by_type: Dict[str, List[ProductCandidate]]
    ) -> Optional[str]:
        """다음에 선택할 추천 유형 결정"""
        
        # 목표에 도달하지 않은 유형 중에서 선택
        available_types = []
        for rtype in RecommendationType:
            type_name = rtype.value
            if (type_selected[type_name] < type_targets[type_name] and 
                candidates_by_type[type_name]):
                available_types.append(type_name)
        
        if not available_types:
            return None
        
        # 우선순위: exploitation -> bridge -> exploration
        priority_order = [
            RecommendationType.EXPLOITATION.value,
            RecommendationType.BRIDGE.value,
            RecommendationType.EXPLORATION.value
        ]
        
        for priority_type in priority_order:
            if priority_type in available_types:
                return priority_type
        
        return available_types[0]
    
    def _select_best_candidate(
        self,
        query_embedding: np.ndarray,
        candidates: List[ProductCandidate],
        selected: List[ProductCandidate]
    ) -> Optional[ProductCandidate]:
        """
        현재 후보들 중에서 MMR 점수가 가장 높은 상품 선택
        문서 규칙: 같은 브랜드는 최대 2개까지만 추천
        """
        
        if not candidates:
            return None
        
        best_candidate = None
        best_mmr_score = -1
        
        for candidate in candidates:
            # 브랜드 제한 체크 (문서 규칙: 동일 브랜드 최대 2개)
            if not self._check_brand_limit(candidate, selected, max_brands=2):
                logger.debug("Candidate excluded due to brand limit",
                           product_id=candidate.id,
                           brand=candidate.metadata.get("brand", "unknown"))
                continue
            
            mmr_score = self._calculate_mmr_score(
                query_embedding, candidate, selected
            )
            
            # MMR 점수를 후보 객체에 저장 (디버깅용)
            candidate.mmr_score = mmr_score
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate = candidate
        
        return best_candidate
    
    def _check_brand_limit(
        self,
        candidate: ProductCandidate,
        selected: List[ProductCandidate],
        max_brands: int = 2
    ) -> bool:
        """
        브랜드 제한 체크
        문서 규칙: 동일 브랜드 상품은 최대 2개까지만 추천
        
        Args:
            candidate: 검사할 후보 상품
            selected: 이미 선택된 상품 리스트
            max_brands: 브랜드당 최대 개수 (기본값: 2)
            
        Returns:
            bool: 브랜드 제한을 통과하면 True, 아니면 False
        """
        candidate_brand = candidate.metadata.get("brand", "")
        
        # 브랜드가 없으면 제한 없음
        if not candidate_brand:
            return True
        
        # 이미 선택된 상품 중 같은 브랜드 개수 계산
        brand_count = sum(
            1 for p in selected 
            if p.metadata.get("brand", "") == candidate_brand
        )
        
        # 최대 개수 미만이면 통과
        return brand_count < max_brands
    
    def _calculate_mmr_score(
        self,
        query_embedding: np.ndarray,
        candidate: ProductCandidate,
        selected: List[ProductCandidate]
    ) -> float:
        """
        MMR 점수 계산
        MMR = λ × Similarity(q, d) - (1-λ) × max Similarity(d, d')
        """
        
        # 쿼리와의 유사도 (이미 계산됨)
        query_similarity = candidate.similarity_score
        
        # 이미 선택된 상품들과의 최대 유사도
        max_selected_similarity = 0.0
        
        if selected:
            similarities = []
            for selected_product in selected:
                similarity = self._cosine_similarity(
                    candidate.embedding, 
                    selected_product.embedding
                )
                similarities.append(similarity)
            
            max_selected_similarity = max(similarities)
        
        # MMR 점수 계산
        mmr_score = (
            self.lambda_param * query_similarity - 
            (1 - self.lambda_param) * max_selected_similarity
        )
        
        # 다양성 보너스 추가
        diversity_bonus = self._calculate_diversity_bonus(candidate, selected)
        mmr_score += diversity_bonus
        
        return mmr_score
    
    def _calculate_diversity_bonus(
        self,
        candidate: ProductCandidate,
        selected: List[ProductCandidate]
    ) -> float:
        """다양성 보너스 점수 계산"""
        
        if not selected:
            return 0.0
        
        # 메타데이터 기반 다양성 점수들을 평균
        diversity_scores = candidate.diversity_scores
        
        # 선택된 상품들과의 다양성 계산
        selected_metadata = [p.metadata for p in selected]
        
        # 스타일 다양성
        style_diversity = self.diversity_calculator.calculate_style_diversity(
            candidate.metadata, selected_metadata
        )
        
        # 카테고리 다양성  
        category_diversity = self.diversity_calculator.calculate_category_diversity(
            candidate.metadata, selected_metadata
        )
        
        # 컬러 다양성
        color_diversity = self.diversity_calculator.calculate_color_diversity(
            candidate.metadata, selected_metadata
        )
        
        # 가격 다양성
        price_diversity = self.diversity_calculator.calculate_price_diversity(
            candidate.metadata, selected_metadata
        )
        
        # 가중 평균으로 다양성 보너스 계산
        diversity_bonus = (
            0.3 * style_diversity +
            0.25 * category_diversity +
            0.25 * color_diversity +
            0.2 * price_diversity
        ) * 0.1  # 전체 MMR 점수에 10% 정도 영향
        
        return diversity_bonus
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _generate_selection_reasoning(
        self,
        candidate: ProductCandidate,
        step: int,
        total_selected: int,
        target_type: str
    ) -> str:
        """선택 이유 생성"""
        
        product_name = candidate.metadata.get("name", f"Product {candidate.id}")
        similarity = candidate.similarity_score
        mmr_score = getattr(candidate, 'mmr_score', 0)
        
        reasoning = (
            f"{step}번째 선택: {product_name} "
            f"(유형: {target_type}, 유사도: {similarity:.3f}, MMR: {mmr_score:.3f})"
        )
        
        return reasoning
    
    def update_lambda(self, new_lambda: float):
        """Lambda 파라미터 업데이트"""
        if 0 <= new_lambda <= 1:
            self.lambda_param = new_lambda
            logger.info("Lambda parameter updated", new_lambda=new_lambda)
        else:
            raise ValueError("Lambda must be between 0 and 1")