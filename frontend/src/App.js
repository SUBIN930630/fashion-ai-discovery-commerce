// 메인 App 컴포넌트
import React, { useState, useMemo, useEffect } from 'react';
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
import SearchBar from './components/SearchBar';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import { CartProvider } from './contexts/CartContext';
import { dummyProducts } from './data/dummyProducts';
import { searchService } from './services/searchService';

/**
 * App 컴포넌트 - 애플리케이션의 최상위 컴포넌트
 * 쇼핑몰 메인 페이지와 플로팅 챗봇을 관리합니다.
 */
function AppContent() {
  const navigate = useNavigate();
  const { user } = useAuth(); // 사용자 정보 가져오기
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGender, setSelectedGender] = useState('전체'); // 성별 필터
  const [selectedCategory, setSelectedCategory] = useState('전체'); // 카테고리 필터
  const [products, setProducts] = useState(dummyProducts); // 상품 목록 상태
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태

  // URL에서 검색어 가져오기
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
      setSearchQuery(query);
    }
  }, []);

  // 검색 이벤트 리스너 (Layout에서 검색 시)
  useEffect(() => {
    const handleSearchEvent = (event) => {
      setSearchQuery(event.detail);
    };
    
    window.addEventListener('search', handleSearchEvent);
    return () => {
      window.removeEventListener('search', handleSearchEvent);
    };
  }, []);

  // 검색어가 변경되면 백엔드 API 호출 (로그인된 사용자인 경우)
  useEffect(() => {
    const performSearch = async () => {
      // 검색어가 없으면 더미 데이터 사용
      if (!searchQuery.trim()) {
        setProducts(dummyProducts);
        return;
      }

      // 로그인된 사용자인 경우 백엔드 API 호출
      if (user && user.id) {
        setIsLoading(true);
        try {
          const result = await searchService.searchProducts(
            searchQuery,
            user.id,
            100 // 충분한 수의 결과 가져오기
          );
          
          // 백엔드에서 받은 결과를 상품 목록으로 변환
          const backendProducts = result.results.map(product => ({
            product_id: product.product_id,
            name: product.name,
            brand: product.brand,
            category: product.category,
            gender: product.gender,
            style_tags: product.style_tags || [],
            color: product.color,
            price: product.price,
            image_url: product.image_url,
            description: product.description,
            similarity_score: product.similarity_score // 유사도 점수 포함
          }));
          
          setProducts(backendProducts);
        } catch (error) {
          console.error('검색 오류:', error);
          // 오류 발생 시 더미 데이터 사용
          setProducts(dummyProducts);
        } finally {
          setIsLoading(false);
        }
      } else {
        // 비로그인 사용자는 더미 데이터 사용
        setProducts(dummyProducts);
      }
    };

    performSearch();
  }, [searchQuery, user]);

  /**
   * 상품 카드 클릭 핸들러
   * 상품 상세 페이지로 이동합니다.
   */
  const handleProductClick = (product) => {
    navigate(`/product/${product.product_id}`);
  };

  /**
   * 검색어, 성별, 카테고리에 따라 필터링된 상품 목록
   * 로그인된 사용자는 백엔드 검색 결과를 사용하고,
   * 비로그인 사용자는 더미 데이터를 필터링합니다.
   */
  const filteredProducts = useMemo(() => {
    let filtered = products;
    
    // 성별 필터링
    if (selectedGender !== '전체') {
      filtered = filtered.filter(product => 
        product.gender === selectedGender || product.gender === '공용'
      );
    }
    
    // 카테고리 필터링
    if (selectedCategory !== '전체') {
      filtered = filtered.filter(product => 
        product.category === selectedCategory
      );
    }
    
    // 검색어 필터링
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      
      filtered = filtered.filter(product => {
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
    }
    
    return filtered;
  }, [products, searchQuery, selectedGender, selectedCategory]);

  return (
    <div id="main-content" className="container" tabIndex="-1">
      <div className="main-header">
        <h2>추천 상품</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
          {isLoading ? (
            <p>검색 중...</p>
          ) : (
            <>
              <p>총 {filteredProducts.length}개</p>
              {user && searchQuery.trim() && (
                <p style={{ fontSize: '12px', color: '#667eea' }}>
                  맞춤 검색 결과 (유사도 높은 순)
                </p>
              )}
            </>
          )}
          {/* 성별 필터 */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
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
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
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

/**
 * 공통 레이아웃 컴포넌트 - 헤더와 챗봇 버튼을 포함
 */
function Layout({ children }) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const navigate = useNavigate();

  /**
   * 챗봇 모달 열기/닫기 토글
   */
  const toggleChat = () => {
    setIsChatOpen(prev => !prev);
  };

  /**
   * 검색 실행 핸들러
   * 홈 페이지로 이동하면서 검색어를 URL 파라미터로 전달
   */
  const handleSearch = (query) => {
    // 홈 페이지로 이동하면서 검색어 전달
    if (window.location.pathname !== '/') {
      navigate(`/?q=${encodeURIComponent(query)}`);
    } else {
      // 이미 홈 페이지에 있으면 이벤트를 발생시켜 AppContent에서 처리
      window.dispatchEvent(new CustomEvent('search', { detail: query }));
    }
  };

  return (
    <div className="app">
      <a href="#main-content" className="skip-link">본문으로 건너뛰기</a>
      {/* 헤더 - 무신사 스타일 */}
      <Header onSearch={<SearchBar onSearch={handleSearch} />} />

      {/* 메인 컨텐츠 */}
      <main className="app-main">
        {children}
      </main>

      {/* 플로팅 챗봇 버튼 */}
      <FloatingChatButton onClick={toggleChat} isOpen={isChatOpen} />

      {/* 챗봇 모달 */}
      <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
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
                <Route path="/" element={<AppContent />} />
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
