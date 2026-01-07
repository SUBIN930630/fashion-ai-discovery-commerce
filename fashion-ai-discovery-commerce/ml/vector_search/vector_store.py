import numpy as np
from typing import List, Dict, Optional, Tuple, Union
import json
from abc import ABC, abstractmethod
import asyncio

# Vector DB 클라이언트들
try:
    import pinecone
except ImportError:
    pinecone = None

try:
    import weaviate
except ImportError:
    weaviate = None

from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStoreBase(ABC):
    """벡터 스토어 추상 클래스"""
    
    @abstractmethod
    async def upsert(self, vectors: List[Dict]) -> bool:
        """벡터 데이터 삽입/업데이트"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """유사도 검색"""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """벡터 데이터 삭제"""
        pass


class PineconeVectorStore(VectorStoreBase):
    """Pinecone 벡터 스토어"""
    
    def __init__(
        self, 
        api_key: str, 
        environment: str,
        index_name: str,
        dimension: int = 1536
    ):
        if pinecone is None:
            raise ImportError("pinecone-client package is required")
        
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        
        # Pinecone 초기화
        pinecone.init(api_key=api_key, environment=environment)
        
        # 인덱스 생성 또는 연결
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine"
            )
        
        self.index = pinecone.Index(index_name)
        logger.info("Pinecone vector store initialized", 
                   index_name=index_name, dimension=dimension)
    
    async def upsert(self, vectors: List[Dict]) -> bool:
        """벡터 데이터 업서트"""
        try:
            # Pinecone 형식으로 변환
            upsert_data = []
            for vector in vectors:
                upsert_data.append({
                    "id": vector["id"],
                    "values": vector["embedding"].tolist(),
                    "metadata": vector.get("metadata", {})
                })
            
            # 배치로 업서트
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.index.upsert, upsert_data)
            
            logger.info("Vectors upserted to Pinecone", count=len(vectors))
            return True
            
        except Exception as e:
            logger.error("Failed to upsert vectors to Pinecone", 
                        error=str(e), count=len(vectors))
            return False
    
    async def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """유사도 검색"""
        try:
            # Pinecone 필터 형식으로 변환
            pinecone_filter = self._convert_filters(filters) if filters else None
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.index.query(
                    vector=query_vector.tolist(),
                    top_k=top_k,
                    include_metadata=True,
                    filter=pinecone_filter
                )
            )
            
            # 결과 변환
            results = []
            for match in response["matches"]:
                results.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                })
            
            logger.debug("Vector search completed", 
                        query_shape=query_vector.shape,
                        top_k=top_k,
                        results_count=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to search vectors in Pinecone", 
                        error=str(e), top_k=top_k)
            return []
    
    async def delete(self, ids: List[str]) -> bool:
        """벡터 삭제"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.index.delete, ids)
            
            logger.info("Vectors deleted from Pinecone", count=len(ids))
            return True
            
        except Exception as e:
            logger.error("Failed to delete vectors from Pinecone", 
                        error=str(e), count=len(ids))
            return False
    
    def _convert_filters(self, filters: Dict) -> Dict:
        """필터를 Pinecone 형식으로 변환"""
        pinecone_filter = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                pinecone_filter[key] = {"$in": value}
            elif isinstance(value, dict) and "min" in value and "max" in value:
                pinecone_filter[key] = {"$gte": value["min"], "$lte": value["max"]}
            else:
                pinecone_filter[key] = value
        
        return pinecone_filter


class WeaviateVectorStore(VectorStoreBase):
    """Weaviate 벡터 스토어"""
    
    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        class_name: str = "Product"
    ):
        if weaviate is None:
            raise ImportError("weaviate-client package is required")
        
        self.url = url
        self.api_key = api_key
        self.class_name = class_name
        
        # Weaviate 클라이언트 초기화
        if api_key:
            auth = weaviate.AuthApiKey(api_key=api_key)
            self.client = weaviate.Client(url=url, auth_client_secret=auth)
        else:
            self.client = weaviate.Client(url=url)
        
        # 클래스 스키마 생성
        self._create_schema()
        logger.info("Weaviate vector store initialized", 
                   url=url, class_name=class_name)
    
    def _create_schema(self):
        """Weaviate 스키마 생성"""
        schema = {
            "class": self.class_name,
            "properties": [
                {
                    "name": "product_id",
                    "dataType": ["string"]
                },
                {
                    "name": "name",
                    "dataType": ["string"]
                },
                {
                    "name": "brand",
                    "dataType": ["string"]
                },
                {
                    "name": "category",
                    "dataType": ["string"]
                },
                {
                    "name": "style_tags",
                    "dataType": ["string[]"]
                },
                {
                    "name": "color",
                    "dataType": ["string"]
                },
                {
                    "name": "price",
                    "dataType": ["number"]
                },
                {
                    "name": "popularity_score",
                    "dataType": ["number"]
                }
            ]
        }
        
        try:
            # 클래스가 이미 존재하는지 확인
            if not self.client.schema.exists(self.class_name):
                self.client.schema.create_class(schema)
                logger.info("Weaviate schema created", class_name=self.class_name)
        except Exception as e:
            logger.warning("Failed to create Weaviate schema", error=str(e))
    
    async def upsert(self, vectors: List[Dict]) -> bool:
        """벡터 데이터 업서트"""
        try:
            # 배치로 데이터 삽입
            with self.client.batch as batch:
                for vector in vectors:
                    metadata = vector.get("metadata", {})
                    
                    # Weaviate 객체 생성
                    data_object = {
                        "product_id": vector["id"],
                        "name": metadata.get("name", ""),
                        "brand": metadata.get("brand", ""),
                        "category": metadata.get("category", ""),
                        "style_tags": metadata.get("style_tags", []),
                        "color": metadata.get("color", ""),
                        "price": metadata.get("price", 0),
                        "popularity_score": metadata.get("popularity_score", 0.0)
                    }
                    
                    batch.add_data_object(
                        data_object=data_object,
                        class_name=self.class_name,
                        uuid=vector["id"],
                        vector=vector["embedding"].tolist()
                    )
            
            logger.info("Vectors upserted to Weaviate", count=len(vectors))
            return True
            
        except Exception as e:
            logger.error("Failed to upsert vectors to Weaviate", 
                        error=str(e), count=len(vectors))
            return False
    
    async def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """유사도 검색"""
        try:
            query = (
                self.client.query
                .get(self.class_name, ["product_id", "name", "brand", "category", 
                                     "style_tags", "color", "price", "popularity_score"])
                .with_near_vector({"vector": query_vector.tolist()})
                .with_limit(top_k)
                .with_additional(["certainty", "distance"])
            )
            
            # 필터 적용
            if filters:
                where_filter = self._convert_filters(filters)
                query = query.with_where(where_filter)
            
            response = query.do()
            
            # 결과 변환
            results = []
            if "data" in response and "Get" in response["data"]:
                for item in response["data"]["Get"][self.class_name]:
                    results.append({
                        "id": item["product_id"],
                        "score": item["_additional"]["certainty"],
                        "metadata": {
                            "name": item.get("name", ""),
                            "brand": item.get("brand", ""),
                            "category": item.get("category", ""),
                            "style_tags": item.get("style_tags", []),
                            "color": item.get("color", ""),
                            "price": item.get("price", 0),
                            "popularity_score": item.get("popularity_score", 0.0)
                        }
                    })
            
            logger.debug("Vector search completed", 
                        query_shape=query_vector.shape,
                        top_k=top_k,
                        results_count=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to search vectors in Weaviate", 
                        error=str(e), top_k=top_k)
            return []
    
    async def delete(self, ids: List[str]) -> bool:
        """벡터 삭제"""
        try:
            for vector_id in ids:
                self.client.data_object.delete(
                    uuid=vector_id,
                    class_name=self.class_name
                )
            
            logger.info("Vectors deleted from Weaviate", count=len(ids))
            return True
            
        except Exception as e:
            logger.error("Failed to delete vectors from Weaviate", 
                        error=str(e), count=len(ids))
            return False
    
    def _convert_filters(self, filters: Dict) -> Dict:
        """필터를 Weaviate 형식으로 변환"""
        where_conditions = []
        
        for key, value in filters.items():
            if isinstance(value, list):
                # 배열 값 중 하나와 일치
                or_conditions = []
                for v in value:
                    or_conditions.append({
                        "path": [key],
                        "operator": "Equal",
                        "valueString": str(v)
                    })
                
                if len(or_conditions) > 1:
                    where_conditions.append({
                        "operator": "Or",
                        "operands": or_conditions
                    })
                elif len(or_conditions) == 1:
                    where_conditions.append(or_conditions[0])
            
            elif isinstance(value, dict) and "min" in value and "max" in value:
                # 범위 필터
                where_conditions.extend([
                    {
                        "path": [key],
                        "operator": "GreaterThanEqual",
                        "valueNumber": value["min"]
                    },
                    {
                        "path": [key],
                        "operator": "LessThanEqual", 
                        "valueNumber": value["max"]
                    }
                ])
            else:
                # 단일 값 필터
                where_conditions.append({
                    "path": [key],
                    "operator": "Equal",
                    "valueString": str(value)
                })
        
        if len(where_conditions) == 1:
            return where_conditions[0]
        elif len(where_conditions) > 1:
            return {
                "operator": "And",
                "operands": where_conditions
            }
        else:
            return {}


class VectorStore:
    """벡터 스토어 팩토리 클래스"""
    
    def __init__(self, store_type: str = "pinecone", **kwargs):
        self.store_type = store_type
        
        if store_type == "pinecone":
            self.store = PineconeVectorStore(**kwargs)
        elif store_type == "weaviate":
            self.store = WeaviateVectorStore(**kwargs)
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")
    
    async def upsert(self, vectors: List[Dict]) -> bool:
        """벡터 데이터 업서트"""
        return await self.store.upsert(vectors)
    
    async def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """유사도 검색"""
        return await self.store.search(query_vector, top_k, filters)
    
    async def delete(self, ids: List[str]) -> bool:
        """벡터 데이터 삭제"""
        return await self.store.delete(ids)