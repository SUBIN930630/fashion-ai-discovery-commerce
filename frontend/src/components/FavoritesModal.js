// 좋아요 모달 컴포넌트
import React from 'react';
import './FavoritesModal.css';
import { useFavorites } from '../contexts/FavoritesContext';
import { dummyProducts } from '../data/dummyProducts';

/**
 * FavoritesModal 컴포넌트 - 좋아요한 상품 목록을 표시하는 모달
 * 
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 */
function FavoritesModal({ isOpen, onClose }) {
  const { favorites, toggleFavorite } = useFavorites();

  if (!isOpen) {
    return null;
  }

  // 좋아요한 상품들을 가져오기
  const favoriteProducts = dummyProducts.filter(product =>
    favorites.includes(product.product_id)
  );

  /**
   * 가격 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  /**
   * 좋아요 취소 핸들러
   */
  const handleRemoveFavorite = (productId) => {
    toggleFavorite(productId);
  };

  return (
    <div className="favorites-modal-overlay" onClick={onClose}>
      <div className="favorites-modal" onClick={(e) => e.stopPropagation()}>
        <div className="favorites-modal-header">
          <h2>좋아요한 상품</h2>
          <button className="favorites-modal-close" onClick={onClose} aria-label="닫기">
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
        </div>

        <div className="favorites-modal-content">
          {favoriteProducts.length === 0 ? (
            <div className="favorites-empty">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" className="favorites-empty-icon">
                <path
                  d="M12 21L3.5 12.5C2.5 11.5 2 10.25 2 8.75C2 5.75 4.25 3.5 7.25 3.5C8.5 3.5 9.75 4 10.5 4.75C11.25 4 12.5 3.5 13.75 3.5C16.75 3.5 19 5.75 19 8.75C19 10.25 18.5 11.5 17.5 12.5L12 21Z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <p>좋아요한 상품이 없습니다.</p>
              <p className="favorites-empty-hint">상품에 하트를 눌러 좋아요를 추가해보세요.</p>
            </div>
          ) : (
            <div className="favorites-grid">
              {favoriteProducts.map((product) => (
                <div key={product.product_id} className="favorites-item">
                  <div className="favorites-item-image-container">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="favorites-item-image"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x400?text=No+Image';
                      }}
                    />
                    <button
                      className="favorites-item-remove-button"
                      onClick={() => handleRemoveFavorite(product.product_id)}
                      aria-label="좋아요 취소"
                    >
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path
                          d="M10 17.5L3.33333 10.8333C2.41667 9.91667 1.83333 8.66667 1.83333 7.33333C1.83333 4.58333 4.08333 2.33333 6.83333 2.33333C8.08333 2.33333 9.25 2.83333 10 3.66667C10.75 2.83333 11.9167 2.33333 13.1667 2.33333C15.9167 2.33333 18.1667 4.58333 18.1667 7.33333C18.1667 8.66667 17.5833 9.91667 16.6667 10.8333L10 17.5Z"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                  </div>
                  <div className="favorites-item-info">
                    <p className="favorites-item-brand">{product.brand}</p>
                    <p className="favorites-item-name">{product.name}</p>
                    <p className="favorites-item-price">{formatPrice(product.price)}원</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {favoriteProducts.length > 0 && (
          <div className="favorites-modal-footer">
            <p>총 {favoriteProducts.length}개의 상품</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default FavoritesModal;

