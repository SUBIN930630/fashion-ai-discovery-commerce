// 장바구니 서비스 - 백엔드 API와 통신
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * API 클라이언트 - 기본 HTTP 요청 함수
 */
const apiClient = {
  async get(url) {
    const response = await fetch(`${API_BASE_URL}${url}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
  
  async post(url, data) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
  
  async put(url) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'PUT',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
  
  async delete(url) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
};

/**
 * CartService - 장바구니 관련 API 호출 서비스
 */
class CartService {
  /**
   * 장바구니에 상품 추가
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @param {number} quantity - 수량
   * @param {Object} productData - 상품 정보 전체
   * @returns {Promise<Object>} 장바구니 아이템
   */
  async addToCart(userId, productId, quantity = 1, productData = null) {
    try {
      return await apiClient.post('/api/v1/cart/add', {
        user_id: userId,
        product_id: productId,
        quantity: quantity,
        product_data: productData,
      });
    } catch (error) {
      console.error('장바구니 추가 오류:', error);
      throw error;
    }
  }

  /**
   * 장바구니 아이템 수량 변경
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @param {number} quantity - 새 수량
   * @returns {Promise<Object>} 장바구니 아이템
   */
  async updateQuantity(userId, productId, quantity) {
    try {
      return await apiClient.put(
        `/api/v1/cart/update?user_id=${userId}&product_id=${productId}&quantity=${quantity}`
      );
    } catch (error) {
      console.error('장바구니 수량 변경 오류:', error);
      throw error;
    }
  }

  /**
   * 장바구니에서 상품 제거
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<Object>} 결과
   */
  async removeFromCart(userId, productId) {
    try {
      return await apiClient.delete(
        `/api/v1/cart/remove?user_id=${userId}&product_id=${productId}`
      );
    } catch (error) {
      console.error('장바구니 제거 오류:', error);
      throw error;
    }
  }

  /**
   * 장바구니 전체 비우기
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 결과
   */
  async clearCart(userId) {
    try {
      return await apiClient.delete(`/api/v1/cart/clear/${userId}`);
    } catch (error) {
      console.error('장바구니 비우기 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자의 장바구니 조회
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 장바구니 아이템 목록
   */
  async getUserCart(userId) {
    try {
      return await apiClient.get(`/api/v1/cart/user/${userId}`);
    } catch (error) {
      console.error('장바구니 조회 오류:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 export
export const cartService = new CartService();

