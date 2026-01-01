// 상품 상세 모달 컴포넌트
import React, { useEffect, useRef } from 'react';
import './ProductDetailModal.css';
import { useFavorites } from '../contexts/FavoritesContext';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

/**
 * ProductDetailModal 컴포넌트 - 상품 상세 정보를 표시하는 모달
 * 
 * @param {Object} product - 상품 정보 객체
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 */
function ProductDetailModal({ product, isOpen, onClose }) {
  const modalRef = useRef(null);
  const overlayRef = useRef(null);
  const { isFavorite, toggleFavorite } = useFavorites();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  // 모달 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (overlayRef.current && overlayRef.current === event.target) {
        onClose();
      }
    };

    // ESC 키로 모달 닫기
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      // 모달이 열릴 때 body 스크롤 방지
      document.body.style.overflow = 'hidden';

      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = 'unset';
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen || !product) {
    return null;
  }

  const favorite = isFavorite(product.product_id);

  /**
   * 가격을 천 단위 콤마로 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  /**
   * 좋아요 버튼 클릭 핸들러
   */
  const handleFavoriteClick = () => {
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    toggleFavorite(product.product_id);
  };

  /**
   * 장바구니에 추가 핸들러
   */
  const handleAddToCart = () => {
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    const result = addToCart(product);
    if (result.success) {
      alert('장바구니에 추가되었습니다.');
    }
  };

  return (
    <div className="product-detail-overlay" ref={overlayRef}>
      <div className="product-detail-modal" ref={modalRef}>
        {/* 닫기 버튼 */}
        <button
          className="product-detail-close"
          onClick={onClose}
          aria-label="상품 상세 닫기"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M18 6L6 18M6 6L18 18"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <div className="product-detail-content">
          {/* 상품 이미지 */}
          <div className="product-detail-image-container">
            <img
              src={product.image_url}
              alt={product.name}
              className="product-detail-image"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/600x800?text=No+Image';
              }}
            />
          </div>

          {/* 상품 정보 */}
          <div className="product-detail-info">
            <div className="product-detail-header">
              <p className="product-detail-brand">{product.brand}</p>
              <h2 className="product-detail-name">{product.name}</h2>
            </div>

            <div className="product-detail-section">
              <h3 className="product-detail-section-title">상품 설명</h3>
              <p className="product-detail-description">{product.description}</p>
            </div>

            <div className="product-detail-section">
              <h3 className="product-detail-section-title">상품 정보</h3>
              <dl className="product-detail-specs">
                <div className="product-detail-spec-item">
                  <dt>카테고리</dt>
                  <dd>{product.category}</dd>
                </div>
                <div className="product-detail-spec-item">
                  <dt>색상</dt>
                  <dd>{product.color}</dd>
                </div>
                {product.style_tags && product.style_tags.length > 0 && (
                  <div className="product-detail-spec-item">
                    <dt>스타일</dt>
                    <dd>
                      <div className="product-detail-tags">
                        {product.style_tags.map((tag, index) => (
                          <span key={index} className="product-detail-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            <div className="product-detail-footer">
              <div className="product-detail-price-container">
                <span className="product-detail-price-label">가격</span>
                <span className="product-detail-price">
                  {formatPrice(product.price)}원
                </span>
              </div>
              <div className="product-detail-action-buttons">
                <button
                  className={`product-detail-favorite-button ${favorite ? 'active' : ''}`}
                  onClick={handleFavoriteClick}
                  aria-label={favorite ? '좋아요 취소' : '좋아요'}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill={favorite ? 'currentColor' : 'none'}>
                    <path
                      d="M12 21L3.5 12.5C2.5 11.5 2 10.25 2 8.75C2 5.75 4.25 3.5 7.25 3.5C8.5 3.5 9.75 4 10.5 4.75C11.25 4 12.5 3.5 13.75 3.5C16.75 3.5 19 5.75 19 8.75C19 10.25 18.5 11.5 17.5 12.5L12 21Z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
                <button
                  className="product-detail-cart-button"
                  onClick={handleAddToCart}
                >
                  장바구니 담기
                </button>
                <button className="product-detail-purchase-button" onClick={handleAddToCart}>
                  구매하기
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetailModal;
