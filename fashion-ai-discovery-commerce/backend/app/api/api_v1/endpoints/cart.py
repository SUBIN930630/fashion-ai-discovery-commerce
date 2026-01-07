# 장바구니 API 엔드포인트
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.cart_service import CartService
from app.database import get_db

router = APIRouter()
logger = get_logger(__name__)


class CartItemRequest(BaseModel):
    """장바구니 아이템 요청 모델"""
    user_id: str
    product_id: str
    quantity: int = 1
    product_data: Optional[Dict[str, Any]] = None


class CartItemResponse(BaseModel):
    """장바구니 아이템 응답 모델"""
    id: int
    user_id: str
    product_id: str
    quantity: int
    product_data: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
    request: CartItemRequest,
    db: Session = Depends(get_db)
):
    """장바구니에 상품 추가"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.add_to_cart(
            user_id=request.user_id,
            product_id=request.product_id,
            quantity=request.quantity,
            product_data=request.product_data
        )
        
        return CartItemResponse(
            id=cart_item.id,
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            product_data=cart_item.product_data,
            created_at=cart_item.created_at.isoformat() if cart_item.created_at else None,
            updated_at=cart_item.updated_at.isoformat() if cart_item.updated_at else None
        )
        
    except Exception as e:
        logger.error("Error adding to cart", error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 추가 중 오류가 발생했습니다.")


@router.put("/update")
async def update_cart_quantity(
    user_id: str,
    product_id: str,
    quantity: int,
    db: Session = Depends(get_db)
):
    """장바구니 아이템 수량 변경"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.update_cart_quantity(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="장바구니 아이템을 찾을 수 없습니다.")
        
        return CartItemResponse(
            id=cart_item.id,
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            product_data=cart_item.product_data,
            created_at=cart_item.created_at.isoformat() if cart_item.created_at else None,
            updated_at=cart_item.updated_at.isoformat() if cart_item.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating cart quantity", error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 수량 변경 중 오류가 발생했습니다.")


@router.delete("/remove")
async def remove_from_cart(
    user_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """장바구니에서 상품 제거"""
    try:
        cart_service = CartService(db)
        success = await cart_service.remove_from_cart(
            user_id=user_id,
            product_id=product_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="장바구니 아이템을 찾을 수 없습니다.")
        
        return {"message": "장바구니에서 제거되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error removing from cart", error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 제거 중 오류가 발생했습니다.")


@router.delete("/clear/{user_id}")
async def clear_cart(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자의 장바구니 전체 비우기"""
    try:
        cart_service = CartService(db)
        count = await cart_service.clear_cart(user_id)
        
        return {
            "message": f"{count}개의 아이템이 장바구니에서 제거되었습니다.",
            "items_removed": count
        }
        
    except Exception as e:
        logger.error("Error clearing cart",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 비우기 중 오류가 발생했습니다.")


@router.get("/user/{user_id}")
async def get_user_cart(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자의 장바구니 조회"""
    try:
        cart_service = CartService(db)
        cart_items = await cart_service.get_user_cart(user_id)
        
        return {
            "user_id": user_id,
            "total": len(cart_items),
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "product_data": item.product_data,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                }
                for item in cart_items
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving user cart",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 조회 중 오류가 발생했습니다.")

