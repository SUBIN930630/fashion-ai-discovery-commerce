// src/components/Layout.js
import React, { useState } from 'react';
import ChatModal from './ChatModal';
import CartModal from './CartModal';
import FavoritesModal from './FavoritesModal'; // 추가됨
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext'; // 추가됨
import './Layout.css';

const Layout = ({ children }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isFavOpen, setIsFavOpen] = useState(false); // 좋아요 창 상태

  const { cartItems } = useCart();
  const { favorites } = useFavorites(); // 좋아요 개수 확인용

  return (
    <div className="layout-container">
      <div className="mobile-view">
        {/* 헤더 */}
        <header className="header">
          <h1 className="logo">FASHION AI</h1>
          <div className="header-icons">
            <button>🔍</button>
            
            {/* 좋아요 버튼 추가 */}
            <button onClick={() => setIsFavOpen(true)} style={{position: 'relative', marginRight: '5px'}}>
              ❤️
              {favorites.length > 0 && (
                <span style={{
                  position: 'absolute', top: '-5px', right: '-5px', 
                  background: 'red', color: 'white', borderRadius: '50%', 
                  width: '16px', height: '16px', fontSize: '10px', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {favorites.length}
                </span>
              )}
            </button>

            {/* 장바구니 버튼 */}
            <button onClick={() => setIsCartOpen(true)} style={{position: 'relative'}}>
              🛒
              {cartItems.length > 0 && (
                <span style={{
                  position: 'absolute', top: '-5px', right: '-5px', 
                  background: 'red', color: 'white', borderRadius: '50%', 
                  width: '16px', height: '16px', fontSize: '10px', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {cartItems.length}
                </span>
              )}
            </button>
          </div>
        </header>

        <main className="content">{children}</main>

        <button className="chatbot-btn" onClick={() => setIsChatOpen(!isChatOpen)}>
          {isChatOpen ? '✖' : '💬'} 
        </button>

        {/* 모든 모달 연결 */}
        <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
        <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
        <FavoritesModal isOpen={isFavOpen} onClose={() => setIsFavOpen(false)} />
      </div>
    </div>
  );
};

export default Layout;