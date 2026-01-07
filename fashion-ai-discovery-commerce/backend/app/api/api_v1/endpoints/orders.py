# 주문 API 엔드포인트
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.order_service import OrderService
from app.database import get_db
from app.models.db_models import Order

router = APIRouter()
logger = get_logger(__name__)


class OrderItemRequest(BaseModel):
    """주문 상품 요청 모델"""
    product_id: str
    quantity: int
    price: int
    product_data: Optional[dict] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None


class OrderCreateRequest(BaseModel):
    """주문 생성 요청 모델"""
    user_id: str
    items: List[OrderItemRequest]
    total_price: int
    order_info: dict
    status: Optional[str] = "주문완료"


class OrderResponse(BaseModel):
    """주문 응답 모델"""
    order_id: str
    user_id: str
    total_price: int
    status: str
    order_date: str
    order_info: dict
    items: List[dict]

    class Config:
        from_attributes = True


@router.post("", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db)
):
    """주문 생성"""
    try:
        order_service = OrderService(db)
        
        # 주문 상품 데이터 변환
        items_data = []
        for item in request.items:
            item_dict = {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            # product_data가 있으면 추가, 없으면 개별 필드 사용
            if item.product_data:
                item_dict["product_data"] = item.product_data
            else:
                item_dict["product_data"] = {
                    "name": item.name,
                    "brand": item.brand,
                    "image_url": item.image_url
                }
            items_data.append(item_dict)
        
        # 주문 생성
        order = await order_service.create_order(
            user_id=request.user_id,
            items=items_data,
            total_price=request.total_price,
            order_info=request.order_info,
            status=request.status
        )
        
        # 응답 데이터 구성
        items_response = []
        for item in order.items:
            item_data = {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            if item.product_data:
                item_data.update(item.product_data)
            items_response.append(item_data)
        
        return OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            total_price=order.total_price,
            status=order.status,
            order_date=order.created_at.isoformat() if order.created_at else "",
            order_info=order.order_info or {},
            items=items_response
        )
        
    except Exception as e:
        logger.error("Error creating order", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"주문 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """주문 조회"""
    try:
        order_service = OrderService(db)
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
        
        # 응답 데이터 구성
        items_response = []
        for item in order.items:
            item_data = {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            if item.product_data:
                item_data.update(item.product_data)
            items_response.append(item_data)
        
        return OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            total_price=order.total_price,
            status=order.status,
            order_date=order.created_at.isoformat() if order.created_at else "",
            order_info=order.order_info or {},
            items=items_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving order", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="주문 조회 중 오류가 발생했습니다.")

