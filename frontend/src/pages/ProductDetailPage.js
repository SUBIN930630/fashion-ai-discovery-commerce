// src/pages/ProductDetailPage.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { api } from '../services/api';
import { useCart } from '../contexts/CartContext';
import { useFavorites } from '../contexts/FavoritesContext'; // 추가됨

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  
  const { addToCart } = useCart(); // 장바구니 기능
  const { toggleFavorite, isFavorite } = useFavorites(); // 좋아요 기능 추가

  useEffect(() => {
    api.getProductDetail(id).then(res => setProduct(res.data));
  }, [id]);

  const handleAddToCart = () => {
    addToCart(product);
    if(window.confirm('장바구니에 담겼습니다! 확인하시겠습니까?')) {
      // 확인 누르면 장바구니 로직 (지금은 그냥 둠)
    }
  };

  if (!product) return <div>로딩중...</div>;

  // 현재 상품이 좋아요 상태인지 확인 (true/false)
  const isLiked = isFavorite(product.product_id);

  return (
    <Layout>
      <div style={{ padding: '20px' }}>
        <button onClick={() => navigate(-1)} style={{ marginBottom: '10px', border:'none', background:'none', cursor:'pointer' }}>
          ← 뒤로가기
        </button>
        
        <div style={{ height: '300px', backgroundColor: '#f0f0f0', borderRadius: '8px', marginBottom: '20px', display:'flex', alignItems:'center', justifyContent:'center' }}>
          {product.image_url ? <img src={product.image_url} alt="" style={{width:'100%', height:'100%', objectFit:'cover'}} /> : "이미지 없음"}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <p style={{ fontSize: '14px', fontWeight: 'bold', color: '#555' }}>{product.brand}</p>
          <h1 style={{ fontSize: '20px', margin: '5px 0' }}>{product.name}</h1>
          <p style={{ fontSize: '18px', fontWeight: 'bold' }}>{product.price.toLocaleString()}원</p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {/* 좋아요 버튼 기능 연결 */}
          <button 
            onClick={() => toggleFavorite(product)}
            style={{ 
              flex: 1, padding: '15px', borderRadius: '8px', 
              border: '1px solid #ddd', 
              backgroundColor: isLiked ? '#ffebee' : 'white', // 찜하면 연분홍색
              color: isLiked ? 'red' : 'black', // 찜하면 빨간 글씨
              fontWeight: 'bold', cursor: 'pointer' 
            }}
          >
            {isLiked ? '❤️ 찜 취소' : '🤍 좋아요'}
          </button>

          <button 
            style={{ flex: 2, padding: '15px', borderRadius: '8px', border: 'none', backgroundColor: 'black', color: 'white', fontWeight: 'bold', cursor: 'pointer' }}
            onClick={handleAddToCart}
          >
            장바구니 담기
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default ProductDetailPage;