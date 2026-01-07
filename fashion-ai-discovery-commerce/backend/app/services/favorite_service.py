# 사용자 좋아요 서비스
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.db_models import UserFavorite
from app.core.logging import get_logger

logger = get_logger(__name__)


class FavoriteService:
    """사용자 좋아요 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def add_favorite(
        self,
        user_id: str,
        product_id: str
    ) -> UserFavorite:
        """
        좋아요 추가
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
        
        Returns:
            UserFavorite 객체
        """
        try:
            # 이미 좋아요가 있는지 확인
            existing = self.db.query(UserFavorite).filter(
                and_(
                    UserFavorite.user_id == user_id,
                    UserFavorite.product_id == product_id
                )
            ).first()
            
            if existing:
                logger.debug("Favorite already exists",
                           user_id=user_id,
                           product_id=product_id)
                return existing
            
            # 새 좋아요 추가
            favorite = UserFavorite(
                user_id=user_id,
                product_id=product_id
            )
            
            self.db.add(favorite)
            self.db.commit()
            self.db.refresh(favorite)
            
            logger.info("Favorite added",
                       user_id=user_id,
                       product_id=product_id,
                       favorite_id=favorite.id)
            
            return favorite
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error adding favorite",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            raise
    
    async def remove_favorite(
        self,
        user_id: str,
        product_id: str
    ) -> bool:
        """
        좋아요 제거
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
        
        Returns:
            성공 여부
        """
        try:
            favorite = self.db.query(UserFavorite).filter(
                and_(
                    UserFavorite.user_id == user_id,
                    UserFavorite.product_id == product_id
                )
            ).first()
            
            if not favorite:
                logger.warning("Favorite not found",
                              user_id=user_id,
                              product_id=product_id)
                return False
            
            self.db.delete(favorite)
            self.db.commit()
            
            logger.info("Favorite removed",
                       user_id=user_id,
                       product_id=product_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error("Error removing favorite",
                        user_id=user_id,
                        product_id=product_id,
                        error=str(e))
            raise
    
    async def toggle_favorite(
        self,
        user_id: str,
        product_id: str
    ) -> tuple[UserFavorite, bool]:  # (favorite, is_added)
        """
        좋아요 토글 (추가/제거)
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
        
        Returns:
            (UserFavorite 객체, 추가 여부) 튜플
        """
        favorite = self.db.query(UserFavorite).filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.product_id == product_id
            )
        ).first()
        
        if favorite:
            await self.remove_favorite(user_id, product_id)
            return (favorite, False)
        else:
            favorite = await self.add_favorite(user_id, product_id)
            return (favorite, True)
    
    async def get_user_favorites(
        self,
        user_id: str
    ) -> List[UserFavorite]:
        """
        사용자의 좋아요 목록 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            UserFavorite 객체 리스트
        """
        try:
            favorites = self.db.query(UserFavorite)\
                .filter(UserFavorite.user_id == user_id)\
                .order_by(UserFavorite.created_at.desc())\
                .all()
            
            logger.debug("Retrieved user favorites",
                        user_id=user_id,
                        count=len(favorites))
            
            return favorites
            
        except Exception as e:
            logger.error("Error retrieving user favorites",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def get_user_favorite_product_ids(
        self,
        user_id: str
    ) -> List[str]:
        """
        사용자의 좋아요한 상품 ID 리스트 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            상품 ID 리스트
        """
        favorites = await self.get_user_favorites(user_id)
        return [f.product_id for f in favorites]
    
    async def is_favorite(
        self,
        user_id: str,
        product_id: str
    ) -> bool:
        """
        특정 상품이 좋아요 목록에 있는지 확인
        
        Args:
            user_id: 사용자 ID
            product_id: 상품 ID
        
        Returns:
            좋아요 여부
        """
        favorite = self.db.query(UserFavorite).filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.product_id == product_id
            )
        ).first()
        
        return favorite is not None
    
    async def get_all_favorites(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserFavorite]:
        """
        모든 사용자의 좋아요 목록 조회 (관리자용)
        
        Args:
            limit: 가져올 개수
            offset: 오프셋
        
        Returns:
            UserFavorite 객체 리스트
        """
        try:
            favorites = self.db.query(UserFavorite)\
                .order_by(UserFavorite.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            logger.debug("Retrieved all favorites",
                        count=len(favorites))
            
            return favorites
            
        except Exception as e:
            logger.error("Error retrieving all favorites",
                        error=str(e))
            raise

