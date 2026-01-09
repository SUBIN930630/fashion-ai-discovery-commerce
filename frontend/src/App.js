// 메인 App 컴포넌트
import React, { useState, useMemo, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import ProductList from './components/ProductList';
import FloatingChatButton from './components/FloatingChatButton';
import ChatModal from './components/ChatModal';
import ProductDetailPage from './components/ProductDetailPage';
import CheckoutPage from './components/CheckoutPage';
import OrderCompletePage from './components/OrderCompletePage';
import MyPage from './components/MyPage';
import AdminDashboard from './components/AdminDashboard';
import Header from './components/Header';
import CartModal from './components/CartModal';
import FavoritesModal from './components/FavoritesModal';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { FavoritesProvider, useFavorites } from './contexts/FavoritesContext';
import { CartProvider, useCart } from './contexts/CartContext';
import { dummyProducts } from './data/dummyProducts';

/**
 * App 컴포넌트 - 애플리케이션의 최상위 컴포넌트
 * 쇼핑몰 메인 페이지와 플로팅 챗봇을 관리합니다.
 */
function AppContent() {
  const navigate = useNavigate();
  const [selectedGender, setSelectedGender] = useState('전체');
  const [selectedCategory, setSelectedCategory] = useState('전체');

  // 필터링된 상품 목록 (메모이제이션으로 불필요한 재계산 방지)
  const filteredProducts = useMemo(() => {
    let filtered = dummyProducts;

    // 성별 필터링
    if (selectedGender !== '전체') {
      filtered = filtered.filter(p => p.gender === selectedGender || p.gender === '공용');
    }

    // 카테고리 필터링
    if (selectedCategory !== '전체') {
      filtered = filtered.filter(p => p.category === selectedCategory);
    }

    return filtered;
  }, [selectedGender, selectedCategory]);

  const handleProductClick = useCallback((product) => {
    navigate(`/product/${product.product_id}`);
  }, [navigate]);

  return (
    <div id="main-content" className="container" tabIndex="-1">
      <div className="main-header">
        <h2>추천 상품</h2>
        <p>총 {filteredProducts.length}개</p>

        {/* 성별 필터 */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '15px' }}>
          {['전체', '남성', '여성'].map(gender => (
            <button
              key={gender}
              onClick={() => setSelectedGender(gender)}
              style={{
                padding: '8px 16px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                background: selectedGender === gender ? '#333' : 'white',
                color: selectedGender === gender ? 'white' : '#333',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {gender}
            </button>
          ))}
        </div>

        {/* 카테고리 필터 */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '10px' }}>
          {['전체', '상의', '하의', '아우터', '원피스'].map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              style={{
                padding: '8px 16px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                background: selectedCategory === category ? '#667eea' : 'white',
                color: selectedCategory === category ? 'white' : '#333',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {category}
            </button>
          ))}
        </div>
      </div>
      
      {filteredProducts.length > 0 ? (
        <ProductList
          products={filteredProducts}
          onProductClick={handleProductClick}
        />
      ) : (
        <div className="no-results">
          <p>검색 결과가 없습니다.</p>
          <p className="no-results-hint">다른 검색어를 시도해보세요.</p>
        </div>
      )}
    </div>
  );
}

// AppContent를 memo로 감싸서 불필요한 리렌더링 방지
const MemoizedAppContent = React.memo(AppContent);

/**
 * Header 제어 컴포넌트 - 상태 관리와 콜백만 담당
 */
function HeaderController() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isFavOpen, setIsFavOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const navigate = useNavigate();
  const { totalQuantity } = useCart();
  const { favorites } = useFavorites();
  const { user, signOut } = useAuth();

  const handleLogin = useCallback(() => {
    setAuthMode('login');
    setIsAuthOpen(true);
  }, []);

  const handleSignUp = useCallback(() => {
    setAuthMode('signup');
    setIsAuthOpen(true);
  }, []);

  const handleLogout = useCallback(() => {
    signOut();
    navigate('/');
  }, [signOut, navigate]);

  const toggleChat = useCallback(() => {
    setIsChatOpen(prev => !prev);
  }, []);

  return (
    <>
      <Header
        onLogin={handleLogin}
        onSignUp={handleSignUp}
        onLogout={handleLogout}
        onCart={() => setIsCartOpen(true)}
        onFavorites={() => setIsFavOpen(true)}
        cartCount={totalQuantity}
        favCount={favorites.length}
        user={user}
      />
      <FloatingChatButton onClick={toggleChat} isOpen={isChatOpen} />
      <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
      <FavoritesModal isOpen={isFavOpen} onClose={() => setIsFavOpen(false)} />
      <AuthModal isOpen={isAuthOpen} initialMode={authMode} onClose={() => {
        setIsAuthOpen(false);
        setAuthMode('login');
      }} />
    </>
  );
}

/**
 * 공통 레이아웃 컴포넌트 - 헤더와 챗봇 버튼을 포함
 */
function Layout({ children }) {
  return (
    <div className="app">
      <a href="#main-content" className="skip-link">본문으로 건너뛰기</a>
      <HeaderController />
      <main className="app-main">
        {children}
      </main>
    </div>
  );
}

/**
 * App 컴포넌트 - 컨텍스트 프로바이더와 라우터로 감싸기
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <FavoritesProvider>
          <CartProvider>
            <Layout>
              <Routes>
                <Route path="/" element={<MemoizedAppContent />} />
                <Route path="/product/:productId" element={<ProductDetailPage />} />
                <Route path="/checkout" element={<CheckoutPage />} />
                <Route path="/order-complete/:orderId" element={<OrderCompletePage />} />
                <Route path="/mypage" element={<MyPage />} />
                <Route path="/admin" element={<AdminDashboard />} />
              </Routes>
            </Layout>
          </CartProvider>
        </FavoritesProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
