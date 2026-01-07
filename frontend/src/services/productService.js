// 상품 서비스 - 백엔드 상품 엔드포인트 호출
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const apiClient = {
  async get(url) {
    const response = await fetch(`${API_BASE_URL}${url}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
};

class ProductService {
  /**
   * 단일 상품 조회
   * @param {string} productId
   */
  async getProduct(productId) {
    try {
      return await apiClient.get(`/api/v1/products/${productId}`);
    } catch (error) {
      console.error('상품 조회 오류:', error);
      throw error;
    }
  }
}

export const productService = new ProductService();
