// src/pages/MainPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // 이동 기능
import Layout from '../components/Layout';
import { api } from '../services/api'; // API 가져오기
import './MainPage.css';

const MainPage = () => {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate(); // 페이지 이동 훅

  // 화면이 켜지면 상품 데이터를 가져옴
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.getProducts();
        setProducts(response.data);
      } catch (error) {
        console.error("상품 로딩 실패", error);
      }
    };
    fetchProducts();
  }, []);

  return (
    <Layout>
      <div className="main-page">
        <h2 className="section-title">지금 뜨는 상품 🔥</h2>
        
        <div className="product-grid">
          {products.map((product) => (
            <div 
              key={product.product_id} 
              className="product-item"
              onClick={() => navigate(`/product/${product.product_id}`)} // 클릭 시 상세 페이지로 이동
            >
              <div className="img-placeholder">
                {product.image_url ? <img src={product.image_url} alt="" /> : "No Image"}
              </div>
              <div className="product-info">
                <span className="brand">{product.brand}</span>
                <span className="name">{product.name}</span>
                <span className="price">{product.price.toLocaleString()}원</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default MainPage;