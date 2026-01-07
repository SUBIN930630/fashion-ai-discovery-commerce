from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ChatSession(Base):
    """채팅 세션 테이블 모델"""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    chat_history = relationship(
        "ChatHistory",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ChatHistory(Base):
    """채팅 메시지 히스토리 테이블 모델"""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="chat_history")


class Product(Base):
    """상품 테이블 모델"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100))
    category = Column(String(50), index=True)
    gender = Column(String(20), index=True)
    style_tags = Column(JSON)
    color = Column(String(50))
    price = Column(Integer)
    popularity_score = Column(Float, default=0.0)
    image_url = Column(Text)
    description = Column(Text)
    embedding = Column(JSON)
    meta_data = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserFavorite(Base):
    """사용자 좋아요 테이블 모델"""

    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_favorites_user_product"),
    )


class UserCart(Base):
    """사용자 장바구니 테이블 모델"""

    __tablename__ = "user_cart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    product_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_cart_user_product"),
    )


class RecommendationHistory(Base):
    """추천 히스토리 테이블 모델"""

    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    query = Column(Text, nullable=False)
    recommendations = Column(JSON)
    total_count = Column(Integer, nullable=False)
    diversity_score = Column(Float, nullable=False)
    strategy_used = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RecommendationFeedback(Base):
    """추천 피드백 테이블 모델"""

    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Order(Base):
    """주문 테이블 모델"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    total_price = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="주문완료", index=True)
    order_info = Column(JSON)  # 배송 정보, 결제 정보 등
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(Base):
    """주문 상품 테이블 모델"""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(255), ForeignKey("orders.order_id"), nullable=False, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Integer, nullable=False)  # 주문 시점의 가격
    product_data = Column(JSON)  # 상품 정보 스냅샷 (이름, 브랜드, 이미지 등)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")
