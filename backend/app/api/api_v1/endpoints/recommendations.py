from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.recommendation_service import RecommendationService
from app.database import get_db

router = APIRouter()
logger = get_logger(__name__)


class RecommendationRequest(BaseModel):
    """추천 요청 모델"""
    query: str
    user_id: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10


class RecommendationResponse(BaseModel):
    """추천 응답 모델"""
    recommendations: List[Dict[str, Any]]
    total_count: int
    diversity_score: float
    strategy_used: Dict[str, float]


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    """추천 서비스 의존성"""
    return RecommendationService(db=db)


@router.post("/search", response_model=RecommendationResponse)
async def search_recommendations(
    request: RecommendationRequest,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """상품 추천 검색"""
    try:
        logger.info("Recommendation search request", 
                   user_id=request.user_id,
                   query=request.query[:50],
                   limit=request.limit)
        
        result = await rec_service.get_recommendations(
            query=request.query,
            user_id=request.user_id,
            filters=request.filters,
            limit=request.limit
        )
        
        return RecommendationResponse(
            recommendations=result["recommendations"],
            total_count=result["total_count"],
            diversity_score=result["diversity_score"],
            strategy_used=result["strategy_used"]
        )
        
    except Exception as e:
        logger.error("Error in recommendation search", 
                    user_id=request.user_id,
                    error=str(e))
        raise HTTPException(
            status_code=500, 
            detail="추천 검색 중 오류가 발생했습니다."
        )


@router.get("/history/{user_id}")
async def get_recommendation_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """사용자 추천 히스토리 조회"""
    try:
        history = await rec_service.get_user_recommendation_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "user_id": user_id,
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error("Error retrieving recommendation history",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="추천 히스토리 조회 중 오류가 발생했습니다."
        )


@router.post("/feedback")
async def submit_recommendation_feedback(
    user_id: str,
    product_id: str,
    feedback_type: str,  # "click", "like", "dislike", "purchase"
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """추천 피드백 제출"""
    try:
        result = await rec_service.record_feedback(
            user_id=user_id,
            product_id=product_id,
            feedback_type=feedback_type
        )
        
        return {"message": "피드백이 기록되었습니다.", "success": result}
        
    except Exception as e:
        logger.error("Error recording feedback",
                    user_id=user_id,
                    product_id=product_id,
                    feedback_type=feedback_type,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="피드백 기록 중 오류가 발생했습니다."
        )


@router.get("/analytics/{user_id}")
async def get_user_recommendation_analytics(
    user_id: str,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """사용자 추천 분석 데이터"""
    try:
        analytics = await rec_service.get_user_analytics(user_id)
        
        return {
            "user_id": user_id,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error("Error retrieving user analytics",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="분석 데이터 조회 중 오류가 발생했습니다."
        )


@router.get("/products/search")
async def search_products(
    q: str = Query(..., description="검색 쿼리"),
    user_id: Optional[str] = Query(None, description="사용자 ID (로그인된 경우)"),
    limit: int = Query(50, ge=1, le=100, description="검색 결과 수"),
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    사용자 취향을 반영한 상품 검색
    
    - 로그인된 사용자(user_id 제공): 좋아요/장바구니 기반 취향 분석 후 유사도 높은 순으로 정렬
    - 비로그인 사용자: 인기도 기반 정렬
    """
    try:
        logger.info("Product search request",
                   query=q[:50],
                   user_id=user_id,
                   limit=limit)
        
        results = await rec_service.search_products_with_user_preferences(
            query=q,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "query": q,
            "user_id": user_id,
            "results": results,
            "total_count": len(results),
            "personalized": user_id is not None
        }
        
    except Exception as e:
        logger.error("Error in product search",
                    query=q[:50],
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="상품 검색 중 오류가 발생했습니다."
        )
