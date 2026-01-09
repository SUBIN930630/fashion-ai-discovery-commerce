// src/contexts/CartContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  // 1. 초기 데이터는 로컬스토리지(내 컴퓨터)에서 가져옴
  const [cartItems, setCartItems] = useState(() => {
    const localData = localStorage.getItem('cart');
    return localData ? JSON.parse(localData) : [];
  });

  // 2. 장바구니가 변할 때마다 로컬스토리지에 자동 저장
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cartItems));
  }, [cartItems]);

  // 3. 상품 추가 기능 (이미 있으면 수량 증가)
  const addToCart = (product) => {
    setCartItems(prev => {
      const existing = prev.find(item => item.product_id === product.product_id);
      if (existing) {
        return prev.map(item => 
          item.product_id === product.product_id 
            ? { ...item, quantity: item.quantity + 1 } 
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  // 3b. 수량 변경
  const updateQuantity = (productId, quantity) => {
    setCartItems(prev => prev.map(item => item.product_id === productId ? { ...item, quantity: Math.max(1, quantity) } : item));
  };

  // 4. 상품 삭제 기능
  const removeFromCart = (productId) => {
    setCartItems(prev => prev.filter(item => item.product_id !== productId));
  };

  // 5. 총 금액 계산
  const totalPrice = cartItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  const totalQuantity = cartItems.reduce((acc, item) => acc + (item.quantity || 0), 0);

  const clearCart = () => setCartItems([]);

  return (
    <CartContext.Provider value={{ cartItems, addToCart, removeFromCart, updateQuantity, clearCart, totalPrice, totalQuantity }}>
      {children}
    </CartContext.Provider>
  );
};

// 이걸로 다른 파일에서 쉽게 사용
export const useCart = () => useContext(CartContext);