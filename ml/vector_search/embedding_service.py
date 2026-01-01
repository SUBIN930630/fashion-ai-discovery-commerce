import openai
import numpy as np
from typing import List, Dict, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """OpenAI Embedding API를 사용한 임베딩 서비스"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "text-embedding-3-large",
        dimensions: int = 1536,
        cache_embeddings: bool = True
    ):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
        self.cache_embeddings = cache_embeddings
        self._cache = {}  # 간단한 메모리 캐시
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def embed_text(self, text: str) -> np.ndarray:
        """단일 텍스트의 임베딩 생성"""
        
        # 캐시 확인
        cache_key = self._get_cache_key(text)
        if self.cache_embeddings and cache_key in self._cache:
            logger.debug("Cache hit for text embedding", text_length=len(text))
            return self._cache[cache_key]
        
        try:
            # 비동기로 OpenAI API 호출
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._create_embedding_sync,
                text
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            # 캐시에 저장
            if self.cache_embeddings:
                self._cache[cache_key] = embedding
            
            logger.debug("Generated text embedding", 
                        text_length=len(text), 
                        embedding_shape=embedding.shape)
            
            return embedding
            
        except Exception as e:
            logger.error("Failed to generate text embedding", 
                        error=str(e), text_length=len(text))
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """여러 텍스트의 임베딩 생성 (배치 처리)"""
        
        # 캐시된 임베딩과 새로 생성할 텍스트 분리
        cached_embeddings = {}
        texts_to_embed = []
        
        if self.cache_embeddings:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    cached_embeddings[i] = self._cache[cache_key]
                else:
                    texts_to_embed.append((i, text))
        else:
            texts_to_embed = [(i, text) for i, text in enumerate(texts)]
        
        # 새 임베딩 생성
        new_embeddings = {}
        if texts_to_embed:
            try:
                # 배치로 임베딩 생성
                batch_texts = [text for _, text in texts_to_embed]
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    self.executor,
                    self._create_embeddings_batch_sync,
                    batch_texts
                )
                
                # 결과 매핑
                for (original_idx, text), embedding_data in zip(texts_to_embed, response.data):
                    embedding = np.array(embedding_data.embedding, dtype=np.float32)
                    new_embeddings[original_idx] = embedding
                    
                    # 캐시에 저장
                    if self.cache_embeddings:
                        cache_key = self._get_cache_key(text)
                        self._cache[cache_key] = embedding
                
                logger.info("Generated batch embeddings", 
                           count=len(batch_texts),
                           cached_count=len(cached_embeddings))
                
            except Exception as e:
                logger.error("Failed to generate batch embeddings", 
                            error=str(e), count=len(texts_to_embed))
                raise
        
        # 결과 정렬
        result = []
        for i in range(len(texts)):
            if i in cached_embeddings:
                result.append(cached_embeddings[i])
            elif i in new_embeddings:
                result.append(new_embeddings[i])
            else:
                # 빈 임베딩 (에러 케이스)
                result.append(np.zeros(self.dimensions, dtype=np.float32))
        
        return result
    
    async def embed_product(self, product: Dict) -> np.ndarray:
        """상품 정보를 임베딩으로 변환"""
        
        # 상품 정보를 텍스트로 구성
        text_parts = []
        
        # 기본 정보
        if product.get("name"):
            text_parts.append(f"상품명: {product['name']}")
        
        if product.get("brand"):
            text_parts.append(f"브랜드: {product['brand']}")
        
        if product.get("category"):
            text_parts.append(f"카테고리: {product['category']}")
        
        # 스타일 태그
        if product.get("style_tags"):
            tags = ", ".join(product["style_tags"])
            text_parts.append(f"스타일: {tags}")
        
        # 색상
        if product.get("color"):
            text_parts.append(f"색상: {product['color']}")
        
        # 소재
        if product.get("material"):
            text_parts.append(f"소재: {product['material']}")
        
        # 설명
        if product.get("description"):
            text_parts.append(f"설명: {product['description']}")
        
        # 가격 범위 (가격대별 구분)
        if product.get("price"):
            price = product["price"]
            if price < 50000:
                text_parts.append("가격대: 저가")
            elif price < 100000:
                text_parts.append("가격대: 중가")
            else:
                text_parts.append("가격대: 고가")
        
        product_text = " | ".join(text_parts)
        return await self.embed_text(product_text)
    
    async def embed_user_query(self, query: str, context: Optional[Dict] = None) -> np.ndarray:
        """사용자 쿼리를 컨텍스트와 함께 임베딩"""
        
        text_parts = [f"사용자 요청: {query}"]
        
        if context:
            # 사용자 취향 정보 추가
            if context.get("preferred_styles"):
                styles = ", ".join(context["preferred_styles"])
                text_parts.append(f"선호 스타일: {styles}")
            
            if context.get("preferred_categories"):
                categories = ", ".join(context["preferred_categories"])
                text_parts.append(f"선호 카테고리: {categories}")
            
            if context.get("price_range"):
                price_range = context["price_range"]
                text_parts.append(f"가격 범위: {price_range['min']}원 ~ {price_range['max']}원")
            
            # 최근 대화 맥락
            if context.get("recent_intent"):
                text_parts.append(f"최근 관심사: {context['recent_intent']}")
        
        query_text = " | ".join(text_parts)
        return await self.embed_text(query_text)
    
    def _create_embedding_sync(self, text: str):
        """동기적 임베딩 생성 (executor에서 사용)"""
        return self.client.embeddings.create(
            input=text,
            model=self.model,
            dimensions=self.dimensions
        )
    
    def _create_embeddings_batch_sync(self, texts: List[str]):
        """동기적 배치 임베딩 생성 (executor에서 사용)"""
        return self.client.embeddings.create(
            input=texts,
            model=self.model,
            dimensions=self.dimensions
        )
    
    def _get_cache_key(self, text: str) -> str:
        """캐시 키 생성"""
        cache_data = {
            "text": text,
            "model": self.model,
            "dimensions": self.dimensions
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def clear_cache(self):
        """임베딩 캐시 클리어"""
        self._cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return {
            "cache_size": len(self._cache),
            "total_cached_embeddings": len(self._cache)
        }