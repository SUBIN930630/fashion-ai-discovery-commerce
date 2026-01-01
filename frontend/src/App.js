// 메인 App 컴포넌트
import React, { useState, useMemo } from 'react';
import './App.css';
import ProductList from './components/ProductList';
import FloatingChatButton from './components/FloatingChatButton';
import ChatModal from './components/ChatModal';
import ProductDetailModal from './components/ProductDetailModal';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import { AuthProvider } from './contexts/AuthContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import { CartProvider } from './contexts/CartContext';
import { dummyProducts } from './data/dummyProducts';

/**
 * App 컴포넌트 - 애플리케이션의 최상위 컴포넌트
 * 쇼핑몰 메인 페이지와 플로팅 챗봇을 관리합니다.
 */
function AppContent() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);

  /**
   * 챗봇 모달 열기/닫기 토글
   */
  const toggleChat = () => {
    setIsChatOpen(prev => !prev);
  };

  /**
   * 검색 실행 핸들러
   * 검색어에 따라 상품 목록을 필터링합니다.
   */
  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  /**
   * 상품 카드 클릭 핸들러
   * 선택된 상품을 설정하고 상세 모달을 엽니다.
   */
  const handleProductClick = (product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  /**
   * 상품 상세 모달 닫기 핸들러
   */
  const handleCloseProductModal = () => {
    setIsProductModalOpen(false);
    setSelectedProduct(null);
  };

  /**
   * 검색어에 따라 필터링된 상품 목록
   * 상품명, 브랜드, 카테고리, 스타일 태그에서 검색합니다.
   */
  const filteredProducts = useMemo(() => {
    if (!searchQuery.trim()) {
      return dummyProducts;
    }

    const query = searchQuery.toLowerCase().trim();
    
    return dummyProducts.filter(product => {
      // 상품명 검색
      const nameMatch = product.name.toLowerCase().includes(query);
      
      // 브랜드 검색
      const brandMatch = product.brand.toLowerCase().includes(query);
      
      // 카테고리 검색
      const categoryMatch = product.category.toLowerCase().includes(query);
      
      // 스타일 태그 검색
      const tagMatch = product.style_tags.some(tag => 
        tag.toLowerCase().includes(query)
      );
      
      // 색상 검색
      const colorMatch = product.color.toLowerCase().includes(query);
      
      // 설명 검색
      const descriptionMatch = product.description.toLowerCase().includes(query);
      
      return nameMatch || brandMatch || categoryMatch || tagMatch || colorMatch || descriptionMatch;
    });
  }, [searchQuery]);

  return (
    <div className="app">
      {/* 헤더 - 무신사 스타일 */}
      <Header onSearch={<SearchBar onSearch={handleSearch} />} />

      {/* 메인 컨텐츠 */}
      <main className="app-main">
        <div className="container">
          <div className="main-header">
            <h2>추천 상품</h2>
            <p>총 {filteredProducts.length}개</p>
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
      </main>

      {/* 플로팅 챗봇 버튼 */}
      <FloatingChatButton onClick={toggleChat} isOpen={isChatOpen} />

      {/* 챗봇 모달 */}
      <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      {/* 상품 상세 모달 */}
      <ProductDetailModal
        product={selectedProduct}
        isOpen={isProductModalOpen}
        onClose={handleCloseProductModal}
      />
    </div>
  );
}

/**
 * App 컴포넌트 - 컨텍스트 프로바이더로 감싸기
 */
function App() {
  return (
    <AuthProvider>
      <FavoritesProvider>
        <CartProvider>
          <AppContent />
        </CartProvider>
      </FavoritesProvider>
    </AuthProvider>
  );
}

export default App;
