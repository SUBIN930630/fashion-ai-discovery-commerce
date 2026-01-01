// 장바구니 컨텍스트 - 사용자의 장바구니 관리
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

/**
 * CartProvider - 장바구니 컨텍스트 제공자
 * 사용자의 장바구니 상품 목록을 관리합니다.
 */
export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cartItems, setCartItems] = useState([]);

  // 사용자 변경 시 장바구니 로드
  useEffect(() => {
    if (user) {
      const savedCart = localStorage.getItem(`cart_${user.id}`);
      if (savedCart) {
        try {
          setCartItems(JSON.parse(savedCart));
        } catch (error) {
          console.error('장바구니 로드 오류:', error);
        }
      }
    } else {
      setCartItems([]);
    }
  }, [user]);

  // 장바구니 저장
  useEffect(() => {
    if (user && cartItems.length >= 0) {
      localStorage.setItem(`cart_${user.id}`, JSON.stringify(cartItems));
    }
  }, [cartItems, user]);

  /**
   * 장바구니에 상품 추가
   * 
   * @param {Object} product - 상품 객체
   * @param {number} quantity - 수량 (기본값: 1)
   */
  const addToCart = (product, quantity = 1) => {
    if (!user) {
      return { success: false, message: '로그인이 필요합니다.' };
    }

    setCartItems(prev => {
      const existingItem = prev.find(item => item.product_id === product.product_id);
      
      if (existingItem) {
        // 이미 장바구니에 있는 경우 수량 증가
        return prev.map(item =>
          item.product_id === product.product_id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        // 새로운 상품 추가
        return [...prev, { ...product, quantity }];
      }
    });

    return { success: true, message: '장바구니에 추가되었습니다.' };
  };

  /**
   * 장바구니에서 상품 제거
   * 
   * @param {string} productId - 상품 ID
   */
  const removeFromCart = (productId) => {
    setCartItems(prev => prev.filter(item => item.product_id !== productId));
  };

  /**
   * 장바구니 상품 수량 변경
   * 
   * @param {string} productId - 상품 ID
   * @param {number} quantity - 새 수량
   */
  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCartItems(prev =>
      prev.map(item =>
        item.product_id === productId ? { ...item, quantity } : item
      )
    );
  };

  /**
   * 장바구니 비우기
   */
  const clearCart = () => {
    setCartItems([]);
  };

  /**
   * 장바구니 총 금액 계산
   */
  const getTotalPrice = () => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  /**
   * 장바구니 총 수량 계산
   */
  const getTotalQuantity = () => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  };

  const value = {
    cartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getTotalPrice,
    getTotalQuantity,
    cartCount: getTotalQuantity()
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

/**
 * useCart - 장바구니 컨텍스트를 사용하는 훅
 */
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}

