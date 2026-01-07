// 상품 목록 컴포넌트
import React from 'react';
import ProductCard from './ProductCard';
import './ProductList.css';

/**
 * ProductList 컴포넌트 - 상품 목록을 그리드 형태로 표시
 * 
 * @param {Array} products - 상품 배열
 * @param {Function} onProductClick - 상품 카드 클릭 핸들러
 */
function ProductList({ products, onProductClick }) {
  if (!products || products.length === 0) {
    return (
      <div className="product-list-empty">
        <p>상품이 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="product-list">
      {products.map((product) => (
        <ProductCard
          key={product.product_id}
          product={product}
          onClick={onProductClick}
        />
      ))}
    </div>
  );
}

export default ProductList;
