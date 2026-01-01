// 장바구니 모달 컴포넌트
import React from 'react';
import './CartModal.css';
import { useCart } from '../contexts/CartContext';

/**
 * CartModal 컴포넌트 - 장바구니 모달
 * 
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 */
function CartModal({ isOpen, onClose }) {
  const { cartItems, removeFromCart, updateQuantity, getTotalPrice, clearCart } = useCart();

  if (!isOpen) {
    return null;
  }

  /**
   * 가격 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  return (
    <div className="cart-modal-overlay" onClick={onClose}>
      <div className="cart-modal" onClick={(e) => e.stopPropagation()}>
        <div className="cart-modal-header">
          <h2>장바구니</h2>
          <button className="cart-modal-close" onClick={onClose} aria-label="닫기">
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

        <div className="cart-modal-content">
          {cartItems.length === 0 ? (
            <div className="cart-empty">
              <p>장바구니가 비어있습니다.</p>
            </div>
          ) : (
            <>
              <div className="cart-items">
                {cartItems.map((item) => (
                  <div key={item.product_id} className="cart-item">
                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="cart-item-image"
                    />
                    <div className="cart-item-info">
                      <p className="cart-item-brand">{item.brand}</p>
                      <p className="cart-item-name">{item.name}</p>
                      <p className="cart-item-price">{formatPrice(item.price)}원</p>
                    </div>
                    <div className="cart-item-actions">
                      <div className="cart-item-quantity">
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                          className="quantity-button"
                        >
                          -
                        </button>
                        <span>{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                          className="quantity-button"
                        >
                          +
                        </button>
                      </div>
                      <button
                        onClick={() => removeFromCart(item.product_id)}
                        className="cart-item-remove"
                        aria-label="상품 제거"
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="cart-footer">
                <div className="cart-total">
                  <span>총 결제금액</span>
                  <span className="cart-total-price">{formatPrice(getTotalPrice())}원</span>
                </div>
                <div className="cart-footer-buttons">
                  <button className="cart-clear-button" onClick={clearCart}>
                    전체 삭제
                  </button>
                  <button className="cart-checkout-button">
                    주문하기
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default CartModal;

