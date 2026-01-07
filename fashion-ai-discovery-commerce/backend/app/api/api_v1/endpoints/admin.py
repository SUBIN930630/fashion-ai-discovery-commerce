# 관리자 API 엔드포인트
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import sys
import os

from app.core.logging import get_logger
from app.services.chat_history_service import ChatHistoryService
from app.services.favorite_service import FavoriteService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.database import get_db
from app.models.db_models import ChatHistory, Product, Order

router = APIRouter()
logger = get_logger(__name__)


class ChatHistoryResponse(BaseModel):
    """챗봇 히스토리 응답 모델"""
    id: int
    session_id: str
    user_id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("/chat-history/all")
async def get_all_chat_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """모든 사용자의 챗봇 대화 내역 조회 (관리자용)"""
    try:
        chat_history_service = ChatHistoryService(db)
        history = await chat_history_service.get_all_chat_history(
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(history),
            "history": [
                {
                    "id": h.id,
                    "session_id": h.session_id,
                    "user_id": h.user_id,
                    "role": h.role,
                    "content": h.content,
                    "metadata": h.meta_data,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving all chat history", error=str(e))
        raise HTTPException(status_code=500, detail="챗봇 대화 내역 조회 중 오류가 발생했습니다.")


@router.get("/chat-history/user/{user_id}")
async def get_user_chat_history(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """특정 사용자의 챗봇 대화 내역 조회"""
    try:
        chat_history_service = ChatHistoryService(db)
        history = await chat_history_service.get_user_chat_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "user_id": user_id,
            "total": len(history),
            "history": [
                {
                    "id": h.id,
                    "session_id": h.session_id,
                    "role": h.role,
                    "content": h.content,
                    "metadata": h.meta_data,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving user chat history",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="사용자 챗봇 대화 내역 조회 중 오류가 발생했습니다.")


@router.get("/chat-history/session/{session_id}")
async def get_session_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """특정 세션의 챗봇 대화 내역 조회"""
    try:
        chat_history_service = ChatHistoryService(db)
        history = await chat_history_service.get_session_chat_history(
            session_id=session_id
        )
        
        return {
            "session_id": session_id,
            "total": len(history),
            "history": [
                {
                    "id": h.id,
                    "user_id": h.user_id,
                    "role": h.role,
                    "content": h.content,
                    "metadata": h.meta_data,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving session chat history",
                    session_id=session_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="세션 챗봇 대화 내역 조회 중 오류가 발생했습니다.")


@router.get("/favorites/all")
async def get_all_favorites(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """모든 사용자의 좋아요 목록 조회 (관리자용)"""
    try:
        favorite_service = FavoriteService(db)
        favorites = await favorite_service.get_all_favorites(
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(favorites),
            "favorites": [
                {
                    "id": f.id,
                    "user_id": f.user_id,
                    "product_id": f.product_id,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in favorites
            ]
        }
        
    except Exception as e:
        logger.error("Error retrieving all favorites", error=str(e))
        raise HTTPException(status_code=500, detail="좋아요 목록 조회 중 오류가 발생했습니다.")


@router.get("/cart/all")
async def get_all_carts(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """모든 사용자의 장바구니 조회 (관리자용)"""
    try:
        cart_service = CartService(db)
        cart_items = await cart_service.get_all_carts(
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(cart_items),
            "items": [
                {
                    "id": item.id,
                    "user_id": item.user_id,
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
        logger.error("Error retrieving all carts", error=str(e))
        raise HTTPException(status_code=500, detail="장바구니 조회 중 오류가 발생했습니다.")


@router.get("/orders")
async def get_all_orders(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """모든 주문 조회 (관리자용)"""
    try:
        order_service = OrderService(db)
        orders = await order_service.get_all_orders(
            limit=limit,
            offset=offset,
            status=status
        )
        
        # 주문 데이터를 JSON 형식으로 변환
        orders_data = []
        for order in orders:
            # 주문 상품 정보 수집
            items = []
            for item in order.items:
                item_data = {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                # product_data가 있으면 추가
                if item.product_data:
                    item_data.update(item.product_data)
                items.append(item_data)
            
            order_data = {
                "order_id": order.order_id,
                "user_id": order.user_id,
                "total_price": order.total_price,
                "status": order.status,
                "order_date": order.created_at.isoformat() if order.created_at else None,
                "order_info": order.order_info,
                "items": items
            }
            orders_data.append(order_data)
        
        return {
            "total": len(orders_data),
            "orders": orders_data
        }
        
    except Exception as e:
        logger.error("Error retrieving all orders", error=str(e))
        raise HTTPException(status_code=500, detail="주문 목록 조회 중 오류가 발생했습니다.")


class OrderStatusUpdateRequest(BaseModel):
    """주문 상태 업데이트 요청 모델"""
    status: str


@router.put("/orders/{order_id}")
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """주문 상태 업데이트"""
    try:
        order_service = OrderService(db)
        order = await order_service.update_order_status(
            order_id=order_id,
            status=request.status
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
        
        return {
            "message": "주문 상태가 업데이트되었습니다.",
            "order_id": order.order_id,
            "status": order.status,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating order status",
                    order_id=order_id,
                    status=request.status,
                    error=str(e))
        raise HTTPException(status_code=500, detail="주문 상태 업데이트 중 오류가 발생했습니다.")


@router.post("/products/init")
async def init_products(
    db: Session = Depends(get_db)
):
    """상품 데이터 초기화 (더미 데이터 저장 및 임베딩 생성)"""
    try:
        from ml.vector_search import SearchEngine
        
        # 더미 상품 데이터 가져오기
        script_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'backend', 'scripts')
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        from init_products import DUMMY_PRODUCTS
        
        # SearchEngine 초기화
        search_engine = SearchEngine(db=db)
        
        logger.info(f"Starting product initialization... Total products: {len(DUMMY_PRODUCTS)}")
        
        # 상품 인덱싱 (임베딩 생성 및 SQL 저장)
        success = await search_engine.index_products(DUMMY_PRODUCTS)
        
        if success:
            product_count = db.query(Product).count()
            logger.info(f"Product initialization completed. Total products: {product_count}")
            return {
                "message": "상품 데이터 초기화 완료",
                "total_products": product_count,
                "indexed_products": len(DUMMY_PRODUCTS),
                "success": True
            }
        else:
            logger.error("Product indexing failed")
            raise HTTPException(status_code=500, detail="상품 데이터 초기화 실패")
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=f"모듈 import 오류: {str(e)}")
    except Exception as e:
        logger.error("Error initializing products", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"상품 데이터 초기화 중 오류가 발생했습니다: {str(e)}")


class ProductUpdateRequest(BaseModel):
    """상품 수정 요청 모델"""
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    style_tags: Optional[List[str]] = None
    color: Optional[str] = None
    price: Optional[int] = None
    popularity_score: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    season: Optional[str] = None
    situation: Optional[str] = None


@router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product_data: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    """상품 정보 수정"""
    try:
        # 상품 조회
        product = db.query(Product).filter(Product.product_id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
        
        # 상품 정보 업데이트
        update_data = product_data.dict(exclude_unset=True)
        
        # season과 situation은 meta_data에 저장
        meta_data = product.meta_data or {}
        if 'season' in update_data:
            meta_data['season'] = update_data.pop('season')
        if 'situation' in update_data:
            meta_data['situation'] = update_data.pop('situation')
        if meta_data:
            product.meta_data = meta_data
        
        # 나머지 필드 업데이트
        for key, value in update_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        # 임베딩이 변경될 수 있는 필드가 업데이트된 경우 재생성
        embedding_fields = ['name', 'brand', 'category', 'description', 'style_tags']
        if any(field in update_data for field in embedding_fields):
            try:
                from ml.vector_search import SearchEngine
                search_engine = SearchEngine(db=db)
                
                # 상품 데이터를 딕셔너리로 변환
                product_dict = {
                    'product_id': product.product_id,
                    'name': product.name,
                    'brand': product.brand,
                    'category': product.category,
                    'gender': product.gender,
                    'style_tags': product.style_tags,
                    'color': product.color,
                    'price': product.price,
                    'image_url': product.image_url,
                    'description': product.description,
                    'season': product.meta_data.get('season') if product.meta_data else None,
                    'situation': product.meta_data.get('situation') if product.meta_data else None,
                }
                
                # 임베딩 재생성
                await search_engine.index_products([product_dict])
                logger.info(f"Product embedding regenerated for {product_id}")
            except Exception as e:
                logger.warning(f"Failed to regenerate embedding for {product_id}: {e}")
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated: {product_id}")
        
        return {
            "message": "상품 정보가 수정되었습니다.",
            "product_id": product.product_id,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"상품 수정 중 오류가 발생했습니다: {str(e)}")

