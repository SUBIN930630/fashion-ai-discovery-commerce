// src/components/FavoritesModal.js
import React from 'react';
import { useFavorites } from '../contexts/FavoritesContext';
import './FavoritesModal.css';

const FavoritesModal = ({ isOpen, onClose }) => {
  const { favorites, toggleFavorite } = useFavorites();

  if (!isOpen) return null;

  return (
    <div className="favorites-modal-overlay">
      <div className="favorites-window">
        <div className="favorites-header">
          <h2>❤️ 찜한 상품</h2>
          <button onClick={onClose} className="close-btn">✖</button>
        </div>

        <div className="favorites-items">
          {favorites.length === 0 ? (
            <p className="empty-msg">찜한 상품이 없습니다.</p>
          ) : (
            favorites.map(product => (
              <div key={product.product_id} className="favorite-item">
                <div className="item-img">
                   {/* 이미지가 있으면 보여주고 없으면 회색 박스 */}
                   {product.image_url ? <img src={product.image_url} alt="" /> : <div className="no-img">No Image</div>}
                </div>
                <div className="item-info">
                  <span className="item-brand">{product.brand}</span>
                  <span className="item-name">{product.name}</span>
                  <span className="item-price">{product.price.toLocaleString()}원</span>
                </div>
                <button onClick={() => toggleFavorite(product)} className="delete-btn">삭제</button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default FavoritesModal;