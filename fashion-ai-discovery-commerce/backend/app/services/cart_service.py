# 사용자 장바구니 서비스
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.db_models import UserCart
from app.core.logging import get_logger

logger = get_logger(__name__)


class CartService:
    """사용자 장바구니 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def add_to_cart(
        self,
        user_id: str,
        product_id: str,
        quantity: int = 1,
        product_data: Optional[Dict[str, Any]] = None
    ) -> UserCart:
        """
        장바구니에 상품 추가 (또는 수량 증가)
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
            quantity: 수량
            product_data: 상품 정보 전체 (스냅샷)
        
        Returns:
            UserCart 객체
        """
        try:
            # 기존 장바구니 아이템 확인
            existing = self.db.query(UserCart).filter(
                and_(
                    UserCart.user_id == user_id,
                    UserCart.product_id == product_id
                )
            ).first()
            
            if existing:
                # 수량 증가
                existing.quantity += quantity
                if product_data:
                    existing.product_data = product_data
                self.db.commit()
                self.db.refresh(existing)
                
                logger.info("Cart item quantity updated",
                           user_id=user_id,
                           product_id=product_id,
                           quantity=existing.quantity)
                
                return existing
            else:
                # 새 아이템 추가
                cart_item = UserCart(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    product_data=product_data
                )
                
                self.db.add(cart_item)
                self.db.commit()
                self.db.refresh(cart_item)
                
                logger.info("Item added to cart",
                           user_id=user_id,
                           product_id=product_id,
                           quantity=quantity,
                           cart_id=cart_item.id)
                
                return cart_item
                
        except Exception as e:
            self.db.rollback()
            logger.error("Error adding to cart",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            raise
    
    async def update_cart_quantity(
        self,
        user_id: str,
        product_id: str,
        quantity: int
    ) -> Optional[UserCart]:
        """
        장바구니 아이템 수량 변경
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
            quantity: 새 수량 (0이면 삭제)
        
        Returns:
            UserCart 객체 (삭제된 경우 None)
        """
        try:
            if quantity <= 0:
                return await self.remove_from_cart(user_id, product_id)
            
            cart_item = self.db.query(UserCart).filter(
                and_(
                    UserCart.user_id == user_id,
                    UserCart.product_id == product_id
                )
            ).first()
            
            if not cart_item:
                logger.warning("Cart item not found",
                              user_id=user_id,
                              product_id=product_id)
                return None
            
            cart_item.quantity = quantity
            self.db.commit()
            self.db.refresh(cart_item)
            
            logger.info("Cart item quantity updated",
                       user_id=user_id,
                       product_id=product_id,
                       quantity=quantity)
            
            return cart_item
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error updating cart quantity",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            raise
    
    async def remove_from_cart(
        self,
        user_id: str,
        product_id: str
    ) -> bool:
        """
        장바구니에서 상품 제거
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
        
        Returns:
            성공 여부
        """
        try:
            cart_item = self.db.query(UserCart).filter(
                and_(
                    UserCart.user_id == user_id,
                    UserCart.product_id == product_id
                )
            ).first()
            
            if not cart_item:
                logger.warning("Cart item not found",
                              user_id=user_id,
                              product_id=product_id)
                return False
            
            self.db.delete(cart_item)
            self.db.commit()
            
            logger.info("Item removed from cart",
                       user_id=user_id,
                       product_id=product_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error removing from cart",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            raise
    
    async def clear_cart(
        self,
        user_id: str
    ) -> int:
        """
        사용자의 장바구니 전체 비우기
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            삭제된 아이템 수
        """
        try:
            cart_items = self.db.query(UserCart)\
                .filter(UserCart.user_id == user_id)\
                .all()
            
            count = len(cart_items)
            
            for item in cart_items:
                self.db.delete(item)
            
            self.db.commit()
            
            logger.info("Cart cleared",
                       user_id=user_id,
                       items_removed=count)
            
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error clearing cart",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def get_user_cart(
        self,
        user_id: str
    ) -> List[UserCart]:
        """
        사용자의 장바구니 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            UserCart 객체 리스트
        """
        try:
            cart_items = self.db.query(UserCart)\
                .filter(UserCart.user_id == user_id)\
                .order_by(UserCart.created_at.desc())\
                .all()
            
            logger.debug("Retrieved user cart",
                        user_id=user_id,
                        count=len(cart_items))
            
            return cart_items
            
        except Exception as e:
            logger.error("Error retrieving user cart",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def get_all_carts(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserCart]:
        """
        모든 사용자의 장바구니 조회 (관리자용)
        
        Args:
            limit: 가져올 개수
            offset: 오프셋
        
        Returns:
            UserCart 객체 리스트
        """
        try:
            cart_items = self.db.query(UserCart)\
                .order_by(UserCart.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            logger.debug("Retrieved all carts",
                        count=len(cart_items))
            
            return cart_items
            
        except Exception as e:
            logger.error("Error retrieving all carts",
                        error=str(e))
            raise

