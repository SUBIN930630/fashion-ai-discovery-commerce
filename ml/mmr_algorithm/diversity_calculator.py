import numpy as np
from typing import List, Dict, Set, Any
from collections import Counter

from app.core.logging import get_logger

logger = get_logger(__name__)


class DiversityCalculator:
    """다양성 점수 계산기"""
    
    def __init__(self):
        self.style_groups = {
            "미니멀": ["미니멀", "심플", "베이직", "클린"],
            "스트릿": ["스트릿", "힙합", "스케이터", "어반"],
            "캐주얼": ["캐주얼", "편안한", "데일리", "라이프스타일"],
            "포멀": ["포멀", "비즈니스", "드레시", "정장"],
            "아메카지": ["아메카지", "빈티지", "클래식", "레트로"],
            "모던": ["모던", "컨템포러리", "트렌디", "세련된"]
        }
        
        self.color_groups = {
            "무채색": ["블랙", "화이트", "그레이", "아이보리"],
            "어스톤": ["베이지", "브라운", "카키", "네이비"],
            "쿨톤": ["블루", "퍼플", "그린", "실버"],
            "웜톤": ["레드", "옐로우", "오렌지", "골드"],
            "파스텔": ["핑크", "라벤더", "민트", "크림"]
        }
        
        logger.info("Diversity calculator initialized")
    
    def calculate_overall_diversity(
        self, 
        products: List[Dict[str, Any]]
    ) -> float:
        """전체 다양성 점수 계산"""
        if not products:
            return 0.0
        
        try:
            # 각 차원별 다양성 계산
            style_diversity = self._calculate_style_diversity(products)
            category_diversity = self._calculate_category_diversity(products)
            color_diversity = self._calculate_color_diversity(products)
            price_diversity = self._calculate_price_diversity(products)
            brand_diversity = self._calculate_brand_diversity(products)
            
            # 가중 평균으로 전체 다양성 점수 계산
            overall_diversity = (
                0.25 * style_diversity +
                0.25 * category_diversity +
                0.2 * color_diversity +
                0.15 * price_diversity +
                0.15 * brand_diversity
            )
            
            logger.debug("Overall diversity calculated", 
                        products_count=len(products),
                        overall_score=overall_diversity,
                        style_score=style_diversity,
                        category_score=category_diversity,
                        color_score=color_diversity,
                        price_score=price_diversity,
                        brand_score=brand_diversity)
            
            return round(overall_diversity, 3)
            
        except Exception as e:
            logger.error("Error calculating overall diversity", 
                        products_count=len(products), 
                        error=str(e))
            return 0.0
    
    def calculate_style_diversity(
        self, 
        candidate_metadata: Dict,
        selected_metadata: List[Dict]
    ) -> float:
        """스타일 다양성 계산 (개별 상품 vs 선택된 상품들)"""
        if not selected_metadata:
            return 1.0
        
        candidate_styles = set(candidate_metadata.get("style_tags", []))
        
        # 선택된 상품들의 스타일 태그 수집
        selected_styles = set()
        for metadata in selected_metadata:
            selected_styles.update(metadata.get("style_tags", []))
        
        # 교집합이 적을수록 다양성이 높음
        if not candidate_styles or not selected_styles:
            return 1.0
        
        intersection = candidate_styles.intersection(selected_styles)
        union = candidate_styles.union(selected_styles)
        
        # Jaccard 거리로 다양성 계산 (1 - Jaccard 유사도)
        jaccard_similarity = len(intersection) / len(union) if union else 0
        diversity = 1 - jaccard_similarity
        
        return round(diversity, 3)
    
    def calculate_category_diversity(
        self,
        candidate_metadata: Dict,
        selected_metadata: List[Dict]
    ) -> float:
        """카테고리 다양성 계산"""
        if not selected_metadata:
            return 1.0
        
        candidate_category = candidate_metadata.get("category", "")
        selected_categories = [m.get("category", "") for m in selected_metadata]
        
        # 동일한 카테고리가 이미 있으면 다양성 낮음
        if candidate_category in selected_categories:
            category_count = selected_categories.count(candidate_category)
            # 동일 카테고리 개수에 따라 다양성 감소
            diversity = max(0, 1 - (category_count * 0.3))
        else:
            diversity = 1.0
        
        return round(diversity, 3)
    
    def calculate_color_diversity(
        self,
        candidate_metadata: Dict,
        selected_metadata: List[Dict]
    ) -> float:
        """컬러 다양성 계산"""
        if not selected_metadata:
            return 1.0
        
        candidate_color = candidate_metadata.get("color", "")
        selected_colors = [m.get("color", "") for m in selected_metadata]
        
        # 색상 그룹 기반 다양성 계산
        candidate_color_group = self._get_color_group(candidate_color)
        selected_color_groups = [self._get_color_group(color) for color in selected_colors]
        
        # 동일한 색상 그룹 개수 계산
        same_group_count = selected_color_groups.count(candidate_color_group)
        
        # 다양성 점수 계산
        if same_group_count == 0:
            diversity = 1.0
        else:
            diversity = max(0, 1 - (same_group_count * 0.25))
        
        return round(diversity, 3)
    
    def calculate_price_diversity(
        self,
        candidate_metadata: Dict,
        selected_metadata: List[Dict]
    ) -> float:
        """가격 다양성 계산"""
        if not selected_metadata:
            return 1.0
        
        candidate_price = candidate_metadata.get("price", 0)
        selected_prices = [m.get("price", 0) for m in selected_metadata if m.get("price", 0) > 0]
        
        if not selected_prices:
            return 1.0
        
        # 가격 범위별 그룹화
        candidate_price_group = self._get_price_group(candidate_price)
        selected_price_groups = [self._get_price_group(price) for price in selected_prices]
        
        # 동일한 가격 그룹 개수
        same_group_count = selected_price_groups.count(candidate_price_group)
        
        # 다양성 점수
        if same_group_count == 0:
            diversity = 1.0
        else:
            diversity = max(0, 1 - (same_group_count * 0.2))
        
        return round(diversity, 3)
    
    def _calculate_style_diversity(self, products: List[Dict]) -> float:
        """스타일 다양성 계산 (전체 상품 기준)"""
        all_style_tags = []
        for product in products:
            all_style_tags.extend(product.get("style_tags", []))
        
        if not all_style_tags:
            return 0.0
        
        # 스타일 그룹별 분산도 계산
        style_groups_count = Counter()
        for tag in all_style_tags:
            group = self._get_style_group(tag)
            style_groups_count[group] += 1
        
        # 엔트로피 기반 다양성 계산
        return self._calculate_entropy(list(style_groups_count.values()))
    
    def _calculate_category_diversity(self, products: List[Dict]) -> float:
        """카테고리 다양성 계산 (전체 상품 기준)"""
        categories = [p.get("category", "") for p in products if p.get("category")]
        
        if not categories:
            return 0.0
        
        category_counts = Counter(categories)
        return self._calculate_entropy(list(category_counts.values()))
    
    def _calculate_color_diversity(self, products: List[Dict]) -> float:
        """컬러 다양성 계산 (전체 상품 기준)"""
        colors = [p.get("color", "") for p in products if p.get("color")]
        
        if not colors:
            return 0.0
        
        # 색상 그룹별로 분류
        color_groups = Counter()
        for color in colors:
            group = self._get_color_group(color)
            color_groups[group] += 1
        
        return self._calculate_entropy(list(color_groups.values()))
    
    def _calculate_price_diversity(self, products: List[Dict]) -> float:
        """가격 다양성 계산 (전체 상품 기준)"""
        prices = [p.get("price", 0) for p in products if p.get("price", 0) > 0]
        
        if not prices:
            return 0.0
        
        # 가격 범위별 그룹화
        price_groups = Counter()
        for price in prices:
            group = self._get_price_group(price)
            price_groups[group] += 1
        
        return self._calculate_entropy(list(price_groups.values()))
    
    def _calculate_brand_diversity(self, products: List[Dict]) -> float:
        """브랜드 다양성 계산"""
        brands = [p.get("brand", "") for p in products if p.get("brand")]
        
        if not brands:
            return 0.0
        
        brand_counts = Counter(brands)
        return self._calculate_entropy(list(brand_counts.values()))
    
    def _get_style_group(self, style_tag: str) -> str:
        """스타일 태그를 그룹으로 분류"""
        style_tag_lower = style_tag.lower()
        
        for group, tags in self.style_groups.items():
            for tag in tags:
                if tag.lower() in style_tag_lower:
                    return group
        
        return "기타"
    
    def _get_color_group(self, color: str) -> str:
        """색상을 그룹으로 분류"""
        color_lower = color.lower()
        
        for group, colors in self.color_groups.items():
            for c in colors:
                if c.lower() in color_lower:
                    return group
        
        return "기타"
    
    def _get_price_group(self, price: int) -> str:
        """가격을 범위별로 그룹화"""
        if price < 30000:
            return "저가"
        elif price < 70000:
            return "중저가"
        elif price < 150000:
            return "중가"
        elif price < 300000:
            return "중고가"
        else:
            return "고가"
    
    def _calculate_entropy(self, counts: List[int]) -> float:
        """엔트로피 기반 다양성 계산"""
        if not counts:
            return 0.0
        
        total = sum(counts)
        if total == 0:
            return 0.0
        
        probabilities = [count / total for count in counts]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        
        # 최대 엔트로피로 정규화 (0~1 범위)
        max_entropy = np.log2(len(counts)) if len(counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return round(normalized_entropy, 3)