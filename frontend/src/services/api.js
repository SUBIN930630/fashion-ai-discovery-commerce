// src/services/api.js
import axios from 'axios';

// 나중에 백엔드 주소가 나오면 여기만 바꾸면 됩니다.
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 가짜 데이터 (백엔드 없이 화면 확인용)
const MOCK_PRODUCTS = [
  { product_id: 1, name: "베이직 오버핏 후드티", brand: "무신사 스탠다드", price: 39900, image_url: "", category: "상의" },
  { product_id: 2, name: "와이드 데님 팬츠", brand: "토피", price: 49000, image_url: "", category: "하의" },
  { product_id: 3, name: "캐시미어 머플러", brand: "247 SEOUL", price: 28000, image_url: "", category: "액세서리" },
  { product_id: 4, name: "독일군 스니커즈", brand: "아디다스", price: 129000, image_url: "", category: "신발" },
];

export const api = {
  // 4.1 상품 목록 조회
  getProducts: async () => {
    // 실제 서버 연결 시: return axios.get(`${API_BASE_URL}/products`);
    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: MOCK_PRODUCTS }), 500); // 0.5초 뒤 가짜 데이터 반환
    });
  },

  // 4.2 상품 상세 조회
  getProductDetail: async (id) => {
    // 실제 서버 연결 시: return axios.get(`${API_BASE_URL}/products/${id}`);
    const product = MOCK_PRODUCTS.find(p => p.product_id === parseInt(id));
    return new Promise((resolve) => resolve({ data: product }));
  },

  // 4.3 장바구니 추가
  addToCart: async (product) => {
    console.log("장바구니 추가됨:", product);
    return Promise.resolve({ success: true });
  }
};