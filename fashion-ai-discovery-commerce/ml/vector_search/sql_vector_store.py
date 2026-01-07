import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from app.core.logging import get_logger
from app.models.db_models import Product

logger = get_logger(__name__)


class SQLVectorStore:
    """SQL 기반 벡터 스토어 - PostgreSQL/SQLite에서 벡터 검색"""
    
    def __init__(self, db: Optional[Session] = None):
        """
        SQL 벡터 스토어 초기화
        
        Args:
            db: SQLAlchemy 세션 (선택사항)
        """
        self.db = db
        logger.info("SQL vector store initialized")
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        코사인 유사도 계산
        
        Args:
            vec1: 첫 번째 벡터
            vec2: 두 번째 벡터
            
        Returns:
            코사인 유사도 (0~1)
        """
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            # 코사인 유사도를 0~1 범위로 정규화
            return max(0.0, min(1.0, (similarity + 1) / 2))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _json_to_array(self, embedding_json: Optional[List]) -> Optional[np.ndarray]:
        """
        JSON 배열을 numpy 배열로 변환
        
        Args:
            embedding_json: JSON 배열 형태의 임베딩
            
        Returns:
            numpy 배열 또는 None
        """
        if embedding_json is None:
            return None
        
        try:
            if isinstance(embedding_json, list):
                return np.array(embedding_json, dtype=np.float32)
            elif isinstance(embedding_json, str):
                # JSON 문자열인 경우 파싱
                return np.array(json.loads(embedding_json), dtype=np.float32)
            else:
                return None
        except Exception as e:
            logger.error(f"Error converting JSON to array: {e}")
            return None
    
    async def upsert(self, vectors: List[Dict]) -> bool:
        """
        벡터 데이터 삽입/업데이트
        
        Args:
            vectors: 벡터 데이터 리스트
                각 항목은 {
                    "id": "product_id",
                    "embedding": np.ndarray,
                    "metadata": {...}
                } 형태
        
        Returns:
            성공 여부
        """
        if not self.db:
            logger.warning("Database session not available for upsert")
            return False
        
        try:
            for vector_data in vectors:
                product_id = vector_data["id"]
                embedding = vector_data["embedding"]
                metadata = vector_data.get("metadata", {})
                
                # numpy 배열을 JSON 배열로 변환
                embedding_json = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                
                # 기존 상품 조회
                product = self.db.query(Product).filter(Product.product_id == product_id).first()
                
                if product:
                    # 업데이트
                    product.embedding = embedding_json
                    product.name = metadata.get("name", product.name)
                    product.brand = metadata.get("brand", product.brand)
                    product.category = metadata.get("category", product.category)
                    product.gender = metadata.get("gender", product.gender)
                    product.style_tags = metadata.get("style_tags", product.style_tags)
                    product.color = metadata.get("color", product.color)
                    product.price = metadata.get("price", product.price)
                    product.popularity_score = metadata.get("popularity_score", product.popularity_score)
                    product.image_url = metadata.get("image_url", product.image_url)
                    product.description = metadata.get("description", product.description)
                    product.meta_data = metadata
                else:
                    # 새로 생성
                    product = Product(
                        product_id=product_id,
                        name=metadata.get("name", ""),
                        brand=metadata.get("brand"),
                        category=metadata.get("category"),
                        gender=metadata.get("gender"),
                        style_tags=metadata.get("style_tags"),
                        color=metadata.get("color"),
                        price=metadata.get("price"),
                        popularity_score=metadata.get("popularity_score", 0.0),
                        image_url=metadata.get("image_url"),
                        description=metadata.get("description"),
                        embedding=embedding_json,
                        meta_data=metadata
                    )
                    self.db.add(product)
            
            self.db.commit()
            logger.info("Vectors upserted to SQL database", count=len(vectors))
            return True
            
        except Exception as e:
            logger.error("Failed to upsert vectors to SQL", 
                        error=str(e), count=len(vectors))
            if self.db:
                self.db.rollback()
            return False
    
    async def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        유사도 검색
        
        Args:
            query_vector: 검색 쿼리 벡터
            top_k: 반환할 결과 수
            filters: 필터 조건 (category, brand, price_range 등)
            
        Returns:
            검색 결과 리스트
                각 항목은 {
                    "id": "product_id",
                    "score": similarity_score,
                    "metadata": {...}
                } 형태
        """
        if not self.db:
            logger.warning("Database session not available for search")
            return []
        
        try:
            # 모든 상품 조회 (임베딩이 있는 것만)
            query = self.db.query(Product).filter(Product.embedding.isnot(None))
            
            # 필터 적용
            if filters:
                if filters.get("category"):
                    query = query.filter(Product.category == filters["category"])
                if filters.get("gender"):
                    query = query.filter(Product.gender == filters["gender"])
                if filters.get("brand"):
                    query = query.filter(Product.brand == filters["brand"])
                if filters.get("price_min"):
                    query = query.filter(Product.price >= filters["price_min"])
                if filters.get("price_max"):
                    query = query.filter(Product.price <= filters["price_max"])
            
            products = query.all()
            
            if not products:
                logger.warning("No products found in database")
                return []
            
            # 각 상품과의 유사도 계산
            results = []
            for product in products:
                product_embedding = self._json_to_array(product.embedding)
                
                if product_embedding is None:
                    continue
                
                # 코사인 유사도 계산
                similarity = self._cosine_similarity(query_vector, product_embedding)
                
                # 메타데이터 구성
                metadata = {
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "gender": product.gender,
                    "style_tags": product.style_tags if product.style_tags else [],
                    "color": product.color,
                    "price": product.price,
                    "popularity_score": product.popularity_score or 0.0,
                    "image_url": product.image_url,
                    "description": product.description
                }
                
                # 추가 메타데이터 병합
                if product.meta_data:
                    metadata.update(product.meta_data)
                
                results.append({
                    "id": product.product_id,
                    "score": similarity,
                    "metadata": metadata,
                    "embedding": product_embedding
                })
            
            # 유사도 순으로 정렬
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # top_k만큼 반환
            top_results = results[:top_k]
            
            logger.debug("Vector search completed", 
                        query_shape=query_vector.shape,
                        top_k=top_k,
                        results_count=len(top_results))
            
            return top_results
            
        except Exception as e:
            logger.error("Error in vector search", error=str(e))
            return []
    
    async def delete(self, ids: List[str]) -> bool:
        """
        벡터 데이터 삭제
        
        Args:
            ids: 삭제할 상품 ID 리스트
            
        Returns:
            성공 여부
        """
        if not self.db:
            logger.warning("Database session not available for delete")
            return False
        
        try:
            deleted_count = self.db.query(Product).filter(
                Product.product_id.in_(ids)
            ).delete(synchronize_session=False)
            
            self.db.commit()
            logger.info("Vectors deleted from SQL", count=deleted_count)
            return True
            
        except Exception as e:
            logger.error("Failed to delete vectors from SQL", 
                        error=str(e), ids=ids)
            if self.db:
                self.db.rollback()
            return False
