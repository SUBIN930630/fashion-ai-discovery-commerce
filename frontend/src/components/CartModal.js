// src/components/CartModal.js
import React from 'react';
import { useCart } from '../contexts/CartContext';
import './CartModal.css';

const CartModal = ({ isOpen, onClose }) => {
  const { cartItems, removeFromCart, totalPrice } = useCart();

  if (!isOpen) return null;

  return (
    <div className="cart-modal-overlay">
      <div className="cart-window">
        <div className="cart-header">
          <h2>🛒 장바구니</h2>
          <button onClick={onClose} className="close-btn">✖</button>
        </div>

        <div className="cart-items">
          {cartItems.length === 0 ? (
            <p className="empty-msg">장바구니가 비었습니다.</p>
          ) : (
            cartItems.map(item => (
              <div key={item.product_id} className="cart-item">
                <div className="item-info">
                  <span className="item-name">{item.name}</span>
                  <span className="item-price">{item.price.toLocaleString()}원</span>
                  <span className="item-qty">x {item.quantity}</span>
                </div>
                <button onClick={() => removeFromCart(item.product_id)} className="delete-btn">삭제</button>
              </div>
            ))
          )}
        </div>

        <div className="cart-footer">
          <div className="total-area">
            <span>총 결제금액</span>
            <span className="total-price">{totalPrice.toLocaleString()}원</span>
          </div>
          <button className="checkout-btn" onClick={() => alert('결제 페이지로 이동합니다 (미구현)')}>
            구매하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartModal;