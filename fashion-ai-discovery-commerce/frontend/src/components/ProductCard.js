// 상품 카드 컴포넌트 - 무신사 스타일
import React from 'react';
import './ProductCard.css';
import { useFavorites } from '../contexts/FavoritesContext';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

/**
 * ProductCard 컴포넌트 - 개별 상품을 카드 형태로 표시
 * 무신사 스타일: 미니멀하고 깔끔한 디자인
 * 좋아요 및 장바구니 기능 포함
 * 
 * @param {Object} product - 상품 정보 객체
 * @param {Function} onClick - 카드 클릭 핸들러
 */
function ProductCard({ product, onClick }) {
  const { isFavorite, toggleFavorite } = useFavorites();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  const favorite = isFavorite(product.product_id);

  /**
   * 가격을 천 단위 콤마로 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  /**
   * 카드 클릭 핸들러
   */
  const handleClick = () => {
    if (onClick) {
      onClick(product);
    }
  };

  /**
   * 좋아요 버튼 클릭 핸들러
   */
  const handleFavoriteClick = (e) => {
    e.stopPropagation(); // 카드 클릭 이벤트 전파 방지
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    toggleFavorite(product.product_id);
  };

  /**
   * 장바구니 버튼 클릭 핸들러
   */
  const handleAddToCart = (e) => {
    e.stopPropagation(); // 카드 클릭 이벤트 전파 방지
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    const result = addToCart(product);
    if (result.success) {
      // 성공 메시지는 필요시 토스트로 표시 가능
    }
  };

  return (
    <div className="product-card" onClick={handleClick}>
      <div className="product-image-container">
        <img 
          src={product.image_url || 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&h=800&fit=crop'} 
          alt={product.name}
          className="product-image"
          loading="lazy"
          onError={(e) => {
            // 이미지 로드 실패 시 기본 의류 이미지로 대체
            e.target.src = 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&h=800&fit=crop';
            e.target.onerror = null; // 무한 루프 방지
          }}
        />
        {/* 좋아요 버튼 */}
        <button
          className={`product-favorite-button ${favorite ? 'active' : ''}`}
          onClick={handleFavoriteClick}
          aria-label={favorite ? '좋아요 취소' : '좋아요'}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill={favorite ? 'currentColor' : 'none'}>
            <path
              d="M10 17.5L3.33333 10.8333C2.41667 9.91667 1.83333 8.66667 1.83333 7.33333C1.83333 4.58333 4.08333 2.33333 6.83333 2.33333C8.08333 2.33333 9.25 2.83333 10 3.66667C10.75 2.83333 11.9167 2.33333 13.1667 2.33333C15.9167 2.33333 18.1667 4.58333 18.1667 7.33333C18.1667 8.66667 17.5833 9.91667 16.6667 10.8333L10 17.5Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        {/* 장바구니 버튼 */}
        <button
          className="product-cart-button"
          onClick={handleAddToCart}
          aria-label="장바구니에 추가"
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path
              d="M4 4H14L12.6 9.9H5.4L4 4ZM4 4L2.7 1.8H1M6 12.6C5.44772 12.6 5 13.0477 5 13.6C5 14.1523 5.44772 14.6 6 14.6C6.55228 14.6 7 14.1523 7 13.6C7 13.0477 6.55228 12.6 6 12.6ZM13.5 12.6C12.9477 12.6 12.5 13.0477 12.5 13.6C12.5 14.1523 12.9477 14.6 13.5 14.6C14.0523 14.6 14.5 14.1523 14.5 13.6C14.5 13.0477 14.0523 12.6 13.5 12.6Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div className="product-info">
        <p className="product-brand">{product.brand}</p>
        <h3 className="product-name">{product.name}</h3>
        <div className="product-footer">
          <span className="product-price">{formatPrice(product.price)}원</span>
        </div>
      </div>
    </div>
  );
}

export default ProductCard;
