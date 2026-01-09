import React from 'react';

function ProductList({ products, onProductClick }) {
  const placeholder = 'https://via.placeholder.com/400x500?text=No+Image';
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1.5rem' }}>
      {products.map(product => (
        <div
          key={product.product_id}
          onClick={() => onProductClick(product)}
          style={{
            cursor: 'pointer',
            border: '1px solid #eee',
            borderRadius: '8px',
            overflow: 'hidden',
            transition: 'transform 0.2s'
          }}
        >
          <img src={product.image_url || placeholder} alt={product.name} style={{ width: '100%', height: '250px', objectFit: 'cover' }} onError={(e) => { e.target.onerror = null; e.target.src = placeholder; }} />
          <div style={{ padding: '1rem' }}>
            <p style={{ fontSize: '0.875rem', color: '#666', margin: '0 0 0.5rem 0' }}>{product.brand}</p>
            <p style={{ fontSize: '1rem', fontWeight: '600', margin: '0 0 0.5rem 0' }}>{product.name}</p>
            <p style={{ fontSize: '1.125rem', fontWeight: '700', color: '#000' }}>
              {new Intl.NumberFormat('ko-KR').format(product.price)}원
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProductList;
