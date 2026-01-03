# 주문 서비스
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.db_models import Order, OrderItem
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrderService:
    """주문 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_orders(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Order]:
        """
        모든 주문 조회 (관리자용)
        
        Args:
            limit: 조회할 최대 개수
            offset: 오프셋
            status: 주문 상태 필터 (선택사항)
        
        Returns:
            Order 객체 리스트
        """
        try:
            query = self.db.query(Order)
            
            # 상태 필터 적용
            if status:
                query = query.filter(Order.status == status)
            
            # 최신순 정렬
            query = query.order_by(desc(Order.created_at))
            
            # 오프셋 적용
            if offset > 0:
                query = query.offset(offset)
            
            # 개수 제한
            if limit:
                query = query.limit(limit)
            
            orders = query.all()
            
            logger.info("All orders retrieved",
                       total=len(orders),
                       status=status,
                       limit=limit,
                       offset=offset)
            
            return orders
            
        except Exception as e:
            logger.error("Error retrieving all orders",
                        error=str(e))
            raise
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        주문 ID로 주문 조회
        
        Args:
            order_id: 주문 ID
        
        Returns:
            Order 객체 또는 None
        """
        try:
            order = self.db.query(Order).filter(
                Order.order_id == order_id
            ).first()
            
            return order
            
        except Exception as e:
            logger.error("Error retrieving order",
                        order_id=order_id,
                        error=str(e))
            raise
    
    async def update_order_status(
        self,
        order_id: str,
        status: str
    ) -> Optional[Order]:
        """
        주문 상태 업데이트
        
        Args:
            order_id: 주문 ID
            status: 새로운 상태
        
        Returns:
            업데이트된 Order 객체
        """
        try:
            order = self.db.query(Order).filter(
                Order.order_id == order_id
            ).first()
            
            if not order:
                return None
            
            order.status = status
            self.db.commit()
            self.db.refresh(order)
            
            logger.info("Order status updated",
                       order_id=order_id,
                       status=status)
            
            return order
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error updating order status",
                        order_id=order_id,
                        status=status,
                        error=str(e))
            raise
    
    async def create_order(
        self,
        user_id: str,
        items: List[Dict[str, Any]],
        total_price: int,
        order_info: Dict[str, Any],
        status: str = "주문완료"
    ) -> Order:
        """
        주문 생성
        
        Args:
            user_id: 사용자 ID
            items: 주문 상품 목록 (각 항목은 product_id, quantity, price, product_data 포함)
            total_price: 총 주문 금액
            order_info: 주문 정보 (배송 정보, 결제 정보 등)
            status: 주문 상태 (기본값: "주문완료")
        
        Returns:
            생성된 Order 객체
        """
        try:
            import uuid
            from datetime import datetime
            
            # 주문 ID 생성
            order_id = f"order_{int(datetime.utcnow().timestamp() * 1000)}"
            
            # 주문 생성
            order = Order(
                order_id=order_id,
                user_id=user_id,
                total_price=total_price,
                status=status,
                order_info=order_info
            )
            
            self.db.add(order)
            self.db.flush()  # order.id를 얻기 위해 flush
            
            # 주문 상품 생성
            for item in items:
                order_item = OrderItem(
                    order_id=order_id,
                    product_id=item.get("product_id"),
                    quantity=item.get("quantity", 1),
                    price=item.get("price", 0),
                    product_data=item.get("product_data") or {
                        "name": item.get("name"),
                        "brand": item.get("brand"),
                        "image_url": item.get("image_url")
                    }
                )
                self.db.add(order_item)
            
            self.db.commit()
            self.db.refresh(order)
            
            logger.info("Order created",
                       order_id=order_id,
                       user_id=user_id,
                       total_price=total_price,
                       items_count=len(items))
            
            return order
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error creating order",
                        user_id=user_id,
                        error=str(e))
            raise

