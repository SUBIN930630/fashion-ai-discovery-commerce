import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dummyProducts } from '../data/dummyProducts';
import { useFavorites } from '../contexts/FavoritesContext';
import { useCart } from '../contexts/CartContext';

function ProductDetailPage() {
  const { productId, id } = useParams();
  const pid = productId || id;
  const navigate = useNavigate();
  const { isFavorite, toggleFavorite } = useFavorites();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    const found = dummyProducts.find(p => String(p.product_id) === String(pid));
    if (found) setProduct(found);
  }, [pid]);

  if (!product) return <div style={{ padding: 20 }}>상품을 찾을 수 없습니다.</div>;

  const liked = isFavorite(product.product_id);

  return (
    <div style={{ padding: 20, maxWidth: 1000, margin: '0 auto' }}>
      <button onClick={() => navigate(-1)} style={{ marginBottom: 12 }}>← 뒤로</button>
      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ flex: 1 }}>
          {product.image_url ? (
              <img src={product.image_url} alt={product.name} style={{ width: '100%', borderRadius: 8 }} onError={(e)=>{e.target.onerror=null;e.target.src='https://via.placeholder.com/600x800?text=No+Image';}} />
            ) : (
              <img src={'https://via.placeholder.com/600x800?text=No+Image'} alt="placeholder" style={{ width: '100%', borderRadius: 8 }} />
            )}
        </div>

        <div style={{ flex: 1 }}>
          <p style={{ color: '#666' }}>{product.brand}</p>
          <h1 style={{ margin: '8px 0' }}>{product.name}</h1>
          <p style={{ fontWeight: '700', fontSize: 20 }}>{new Intl.NumberFormat('ko-KR').format(product.price)}원</p>
          <p style={{ marginTop: 12, color: '#333' }}>{product.description}</p>

          <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
            <button onClick={() => toggleFavorite(product)} style={{ padding: '12px 16px', borderRadius: 8, border: '1px solid #ddd', background: liked ? '#fff0f0' : 'white', cursor: 'pointer' }}>{liked ? '❤️ 찜 취소' : '🤍 좋아요'}</button>
            <button onClick={() => addToCart(product)} style={{ padding: '12px 20px', borderRadius: 8, background: '#111', color: 'white', border: 'none', cursor: 'pointer' }}>장바구니 담기</button>
            <button onClick={() => { addToCart(product); navigate('/checkout'); }} style={{ padding: '12px 20px', borderRadius: 8, background: '#2b6cb0', color: 'white', border: 'none', cursor: 'pointer' }}>구매하기</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetailPage;

