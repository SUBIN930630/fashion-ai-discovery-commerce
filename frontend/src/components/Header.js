// 헤더 컴포넌트
import React, { useState } from 'react';
import './Header.css';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext';
import AuthModal from './AuthModal';
import CartModal from './CartModal';
import FavoritesModal from './FavoritesModal';

/**
 * Header 컴포넌트 - 사이트 헤더
 * 로그인/회원가입, 장바구니 기능을 포함합니다.
 */
function Header({ onSearch }) {
  const { user, signOut, isAuthenticated } = useAuth();
  const { cartCount } = useCart();
  const { favoritesCount } = useFavorites();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [isCartModalOpen, setIsCartModalOpen] = useState(false);
  const [isFavoritesModalOpen, setIsFavoritesModalOpen] = useState(false);

  /**
   * 로그인 모달 열기
   */
  const handleLoginClick = () => {
    setAuthMode('login');
    setIsAuthModalOpen(true);
  };

  /**
   * 회원가입 모달 열기
   */
  const handleSignUpClick = () => {
    setAuthMode('signup');
    setIsAuthModalOpen(true);
  };

  /**
   * 로그아웃 핸들러
   */
  const handleLogout = () => {
    signOut();
  };

  return (
    <>
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1 className="header-logo">Fashion AI Discovery</h1>
            <p className="header-subtitle">당신만의 스타일을 찾아보세요</p>
          </div>
          
          <div className="header-right">
            {onSearch && (
              <div style={{ width: '100%', maxWidth: '500px' }}>
                {onSearch}
              </div>
            )}
            
            <div className="header-actions">
              {isAuthenticated ? (
                <>
                  <span className="header-user-name">{user.name}님</span>
                  <button
                    className="header-button favorites-button"
                    onClick={() => setIsFavoritesModalOpen(true)}
                    aria-label="좋아요"
                  >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M10 17.5L3.33333 10.8333C2.41667 9.91667 1.83333 8.66667 1.83333 7.33333C1.83333 4.58333 4.08333 2.33333 6.83333 2.33333C8.08333 2.33333 9.25 2.83333 10 3.66667C10.75 2.83333 11.9167 2.33333 13.1667 2.33333C15.9167 2.33333 18.1667 4.58333 18.1667 7.33333C18.1667 8.66667 17.5833 9.91667 16.6667 10.8333L10 17.5Z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    {favoritesCount > 0 && (
                      <span className="favorites-badge">{favoritesCount}</span>
                    )}
                  </button>
                  <button
                    className="header-button cart-button"
                    onClick={() => setIsCartModalOpen(true)}
                    aria-label="장바구니"
                  >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M5 5H17L15 11H7L5 5ZM5 5L3 2H1M7 14C6.44772 14 6 14.4477 6 15C6 15.5523 6.44772 16 7 16C7.55228 16 8 15.5523 8 15C8 14.4477 7.55228 14 7 14ZM15 14C14.4477 14 14 14.4477 14 15C14 15.5523 14.4477 16 15 16C15.5523 16 16 15.5523 16 15C16 14.4477 15.5523 14 15 14Z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    {cartCount > 0 && (
                      <span className="cart-badge">{cartCount}</span>
                    )}
                  </button>
                  <button
                    className="header-button logout-button"
                    onClick={handleLogout}
                  >
                    로그아웃
                  </button>
                </>
              ) : (
                <>
                  <button
                    className="header-button login-button"
                    onClick={handleLoginClick}
                  >
                    로그인
                  </button>
                  <button
                    className="header-button signup-button"
                    onClick={handleSignUpClick}
                  >
                    회원가입
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode={authMode}
      />

      <CartModal
        isOpen={isCartModalOpen}
        onClose={() => setIsCartModalOpen(false)}
      />

      <FavoritesModal
        isOpen={isFavoritesModalOpen}
        onClose={() => setIsFavoritesModalOpen(false)}
      />
    </>
  );
}

export default Header;

