// 상품 상세 페이지 컴포넌트
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ProductDetailPage.css';
import { useFavorites } from '../contexts/FavoritesContext';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { dummyProducts } from '../data/dummyProducts';

/**
 * ProductDetailPage 컴포넌트 - 상품 상세 정보를 표시하는 페이지
 * 
 * @param {string} productId - URL 파라미터에서 가져온 상품 ID
 */
function ProductDetailPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { isFavorite, toggleFavorite } = useFavorites();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);

  // 상품 데이터 로드
  useEffect(() => {
    // 더미 데이터에서 상품 찾기
    const foundProduct = dummyProducts.find(p => p.product_id === productId);
    
    if (foundProduct) {
      setProduct(foundProduct);
    } else {
      // TODO: API에서 상품 데이터 가져오기
      console.warn('상품을 찾을 수 없습니다:', productId);
    }
  }, [productId]);

  if (!product) {
    return (
      <div className="product-detail-page-wrapper">
        <div className="product-detail-not-found">
          <h2>상품을 찾을 수 없습니다</h2>
          <button onClick={() => navigate('/')}>홈으로 돌아가기</button>
        </div>
      </div>
    );
  }

  const favorite = isFavorite(product.product_id);

  /**
   * 상품 설명 생성 함수
   * description이 없거나 짧을 때 상품 정보를 기반으로 자동 생성
   */
  const generateProductDescription = (product) => {
    // description이 있고 충분히 길면 그대로 사용
    if (product.description && product.description.length > 30) {
      return product.description;
    }

    // 상품 정보를 기반으로 설명 생성
    const parts = [];
    
    // 기본 설명
    parts.push(`${product.name}입니다.`);
    
    // 카테고리별 설명
    const categoryDescriptions = {
      '상의': '편안한 착용감과 세련된 디자인으로 일상에서 활용하기 좋은 아이템입니다.',
      '하의': '완벽한 핏과 편안한 착용감을 제공하는 실용적인 아이템입니다.',
      '아우터': '트렌디한 디자인과 실용성을 겸비한 스타일리시한 아이템입니다.',
      '원피스': '우아하고 세련된 실루엣으로 다양한 스타일링이 가능한 아이템입니다.',
      '액세서리': '포인트가 되는 디테일로 스타일을 완성해주는 아이템입니다.'
    };
    
    if (categoryDescriptions[product.category]) {
      parts.push(categoryDescriptions[product.category]);
    }
    
    // 색상 설명
    if (product.color) {
      const colorDescriptions = {
        '블랙': '클래식한 블랙 컬러로 어떤 스타일과도 잘 어울립니다.',
        '화이트': '깔끔한 화이트 컬러로 시원하고 밝은 느낌을 줍니다.',
        '네이비': '차분한 네이비 컬러로 세련된 무드를 연출합니다.',
        '그레이': '모던한 그레이 컬러로 캐주얼부터 포멀까지 다양한 스타일에 활용 가능합니다.',
        '베이지': '부드러운 베이지 컬러로 따뜻하고 우아한 느낌을 줍니다.',
        '크림': '은은한 크림 컬러로 고급스러운 분위기를 연출합니다.',
        '인디고': '클래식한 인디고 컬러로 데일리룩에 완벽합니다.',
        '카키': '캐주얼한 카키 컬러로 편안하고 자연스러운 느낌을 줍니다.',
        '차콜': '시크한 차콜 컬러로 세련된 무드를 완성합니다.',
        '레드': '강렬한 레드 컬러로 포인트가 되는 스타일을 연출합니다.',
        '핑크': '로맨틱한 핑크 컬러로 부드럽고 여성스러운 느낌을 줍니다.',
        '브라운': '따뜻한 브라운 컬러로 자연스럽고 편안한 느낌을 줍니다.'
      };
      
      if (colorDescriptions[product.color]) {
        parts.push(colorDescriptions[product.color]);
      }
    }
    
    // 스타일 태그 설명
    if (product.style_tags && product.style_tags.length > 0) {
      const styleDescriptions = {
        '스트릿': '스트릿 감성의 트렌디한 디자인으로 개성 있는 스타일을 연출할 수 있습니다.',
        '캐주얼': '캐주얼한 디자인으로 일상에서 편하게 착용하기 좋습니다.',
        '미니멀': '미니멀한 디자인으로 깔끔하고 세련된 스타일을 완성합니다.',
        '오피스': '오피스룩에 적합한 세련된 디자인으로 비즈니스 캐주얼룩에 활용하기 좋습니다.',
        '오버핏': '넉넉한 오버핏으로 편안하고 트렌디한 느낌을 줍니다.',
        '슬림핏': '슬림핏으로 깔끔하고 정돈된 실루엣을 연출합니다.',
        '와이드': '와이드한 실루엣으로 편안하고 모던한 스타일을 완성합니다.',
        '크롭': '크롭 디자인으로 트렌디하고 세련된 스타일을 연출합니다.',
        '플리츠': '플리츠 디테일로 우아하고 여성스러운 느낌을 줍니다.',
        '페미닌': '페미닌한 디자인으로 부드럽고 우아한 스타일을 완성합니다.',
        '로맨틱': '로맨틱한 디자인으로 여성스럽고 우아한 느낌을 줍니다.'
      };
      
      const styleTag = product.style_tags[0];
      if (styleDescriptions[styleTag]) {
        parts.push(styleDescriptions[styleTag]);
      }
    }
    
    // 마무리 문구
    parts.push('다양한 코디와 함께 활용하여 나만의 스타일을 표현해보세요.');
    
    return parts.join(' ');
  };

  // 상품 설명 생성
  const productDescription = generateProductDescription(product);

  /**
   * 가격을 천 단위 콤마로 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  /**
   * 좋아요 버튼 클릭 핸들러
   */
  const handleFavoriteClick = () => {
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    toggleFavorite(product.product_id);
  };

  /**
   * 장바구니에 추가 핸들러
   */
  const handleAddToCart = () => {
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    const result = addToCart(product);
    if (result.success) {
      alert('장바구니에 추가되었습니다.');
    }
  };

  /**
   * 구매하기 핸들러
   */
  const handlePurchase = () => {
    if (!isAuthenticated) {
      alert('로그인이 필요합니다.');
      return;
    }
    // TODO: 구매 페이지로 이동
    alert('구매 기능은 준비 중입니다.');
  };

  return (
    <div className="product-detail-page-wrapper">
      <div className="product-detail-container">
        {/* 뒤로가기 버튼 */}
        <button
          className="product-detail-back-button"
          onClick={() => navigate(-1)}
          aria-label="뒤로가기"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M15 18L9 12L15 6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          뒤로가기
        </button>

        <div className="product-detail-content">
          {/* 상품 이미지 */}
          <div className="product-detail-image-container">
            <img
              src={product.image_url || 'https://via.placeholder.com/600x800?text=No+Image'}
              alt={product.name}
              className="product-detail-image"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/600x800?text=No+Image';
              }}
            />
          </div>

          {/* 상품 정보 */}
          <div className="product-detail-info">
            <div className="product-detail-header">
              <p className="product-detail-brand">{product.brand}</p>
              <h1 className="product-detail-name">{product.name}</h1>
            </div>

            <div className="product-detail-section">
              <h3 className="product-detail-section-title">상품 설명</h3>
              <p className="product-detail-description">{productDescription}</p>
            </div>

            <div className="product-detail-section">
              <h3 className="product-detail-section-title">상품 정보</h3>
              <dl className="product-detail-specs">
                <div className="product-detail-spec-item">
                  <dt>카테고리</dt>
                  <dd>{product.category}</dd>
                </div>
                <div className="product-detail-spec-item">
                  <dt>색상</dt>
                  <dd>{product.color}</dd>
                </div>
                {product.style_tags && product.style_tags.length > 0 && (
                  <div className="product-detail-spec-item">
                    <dt>스타일</dt>
                    <dd>
                      <div className="product-detail-tags">
                        {product.style_tags.map((tag, index) => (
                          <span key={index} className="product-detail-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            <div className="product-detail-footer">
              <div className="product-detail-price-container">
                <span className="product-detail-price-label">가격</span>
                <span className="product-detail-price">
                  {formatPrice(product.price)}원
                </span>
              </div>
              <div className="product-detail-action-buttons">
                <button
                  className={`product-detail-favorite-button ${favorite ? 'active' : ''}`}
                  onClick={handleFavoriteClick}
                  aria-label={favorite ? '좋아요 취소' : '좋아요'}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill={favorite ? 'currentColor' : 'none'}>
                    <path
                      d="M12 21L3.5 12.5C2.5 11.5 2 10.25 2 8.75C2 5.75 4.25 3.5 7.25 3.5C8.5 3.5 9.75 4 10.5 4.75C11.25 4 12.5 3.5 13.75 3.5C16.75 3.5 19 5.75 19 8.75C19 10.25 18.5 11.5 17.5 12.5L12 21Z"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
                <button
                  className="product-detail-cart-button"
                  onClick={handleAddToCart}
                >
                  장바구니 담기
                </button>
                <button 
                  className="product-detail-purchase-button" 
                  onClick={handlePurchase}
                >
                  구매하기
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetailPage;

