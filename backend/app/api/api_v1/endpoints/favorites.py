# 좋아요 API 엔드포인트
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.favorite_service import FavoriteService
from app.database import get_db

router = APIRouter()
logger = get_logger(__name__)


class FavoriteRequest(BaseModel):
    """좋아요 요청 모델"""
    user_id: str
    product_id: str


class FavoriteResponse(BaseModel):
    """좋아요 응답 모델"""
    id: int
    user_id: str
    product_id: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/add", response_model=FavoriteResponse)
async def add_favorite(
    request: FavoriteRequest,
    db: Session = Depends(get_db)
):
    """좋아요 추가"""
    try:
        favorite_service = FavoriteService(db)
        favorite = await favorite_service.add_favorite(
            user_id=request.user_id,
            product_id=request.product_id
        )
        
        return FavoriteResponse(
            id=favorite.id,
            user_id=favorite.user_id,
            product_id=favorite.product_id,
            created_at=favorite.created_at.isoformat() if favorite.created_at else None
        )
        
    except Exception as e:
        logger.error("Error adding favorite", error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 추가 중 오류가 발생했습니다.")


@router.delete("/remove")
async def remove_favorite(
    user_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """좋아요 제거"""
    try:
        favorite_service = FavoriteService(db)
        success = await favorite_service.remove_favorite(
            user_id=user_id,
            product_id=product_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="좋아요를 찾을 수 없습니다.")
        
        return {"message": "좋아요가 제거되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error removing favorite", error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 제거 중 오류가 발생했습니다.")


@router.post("/toggle")
async def toggle_favorite(
    request: FavoriteRequest,
    db: Session = Depends(get_db)
):
    """좋아요 토글 (추가/제거)"""
    try:
        favorite_service = FavoriteService(db)
        favorite, is_added = await favorite_service.toggle_favorite(
            user_id=request.user_id,
            product_id=request.product_id
        )
        
        return {
            "message": "좋아요가 추가되었습니다." if is_added else "좋아요가 제거되었습니다.",
            "is_favorite": is_added,
            "favorite": {
                "id": favorite.id,
                "user_id": favorite.user_id,
                "product_id": favorite.product_id,
                "created_at": favorite.created_at.isoformat() if favorite.created_at else None
            } if favorite else None
        }
        
    except Exception as e:
        logger.error("Error toggling favorite", error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 토글 중 오류가 발생했습니다.")


@router.get("/user/{user_id}")
async def get_user_favorites(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자의 좋아요 목록 조회"""
    try:
        favorite_service = FavoriteService(db)
        favorites = await favorite_service.get_user_favorites(user_id)
        
        return {
            "user_id": user_id,
            "total": len(favorites),
            "favorites": [
                {
                    "id": f.id,
                    "product_id": f.product_id,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in favorites
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving user favorites",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 목록 조회 중 오류가 발생했습니다.")


@router.get("/user/{user_id}/product-ids")
async def get_user_favorite_product_ids(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자의 좋아요한 상품 ID 리스트 조회"""
    try:
        favorite_service = FavoriteService(db)
        product_ids = await favorite_service.get_user_favorite_product_ids(user_id)
        
        return {
            "user_id": user_id,
            "product_ids": product_ids
        }
        
    except Exception as e:
        logger.error("Error retrieving favorite product IDs",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 상품 ID 조회 중 오류가 발생했습니다.")


@router.get("/check/{user_id}/{product_id}")
async def check_favorite(
    user_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """특정 상품이 좋아요 목록에 있는지 확인"""
    try:
        favorite_service = FavoriteService(db)
        is_favorite = await favorite_service.is_favorite(user_id, product_id)
        
        return {
            "user_id": user_id,
            "product_id": product_id,
            "is_favorite": is_favorite
        }
        
    except Exception as e:
        logger.error("Error checking favorite",
                    user_id=user_id,
                    product_id=product_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 확인 중 오류가 발생했습니다.")

