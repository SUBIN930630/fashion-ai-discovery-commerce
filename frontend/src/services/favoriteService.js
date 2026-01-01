// 좋아요 서비스 - 백엔드 API와 통신
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
 * FavoriteService - 좋아요 관련 API 호출 서비스
 */
class FavoriteService {
  /**
   * 좋아요 추가
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<Object>} 좋아요 정보
   */
  async addFavorite(userId, productId) {
    try {
      return await apiClient.post('/api/v1/favorites/add', {
        user_id: userId,
        product_id: productId,
      });
    } catch (error) {
      console.error('좋아요 추가 오류:', error);
      throw error;
    }
  }

  /**
   * 좋아요 제거
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<Object>} 결과
   */
  async removeFavorite(userId, productId) {
    try {
      return await apiClient.delete(
        `/api/v1/favorites/remove?user_id=${userId}&product_id=${productId}`
      );
    } catch (error) {
      console.error('좋아요 제거 오류:', error);
      throw error;
    }
  }

  /**
   * 좋아요 토글 (추가/제거)
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<Object>} 결과
   */
  async toggleFavorite(userId, productId) {
    try {
      return await apiClient.post('/api/v1/favorites/toggle', {
        user_id: userId,
        product_id: productId,
      });
    } catch (error) {
      console.error('좋아요 토글 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자의 좋아요 목록 조회
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 좋아요 목록
   */
  async getUserFavorites(userId) {
    try {
      return await apiClient.get(`/api/v1/favorites/user/${userId}`);
    } catch (error) {
      console.error('좋아요 목록 조회 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자의 좋아요한 상품 ID 리스트 조회
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Promise<Object>} 상품 ID 리스트
   */
  async getUserFavoriteProductIds(userId) {
    try {
      const response = await apiClient.get(`/api/v1/favorites/user/${userId}/product-ids`);
      return response.product_ids || [];
    } catch (error) {
      console.error('좋아요 상품 ID 조회 오류:', error);
      return [];
    }
  }

  /**
   * 특정 상품이 좋아요 목록에 있는지 확인
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<boolean>} 좋아요 여부
   */
  async checkFavorite(userId, productId) {
    try {
      const response = await apiClient.get(`/api/v1/favorites/check/${userId}/${productId}`);
      return response.is_favorite || false;
    } catch (error) {
      console.error('좋아요 확인 오류:', error);
      return false;
    }
  }
}

// 싱글톤 인스턴스 export
export const favoriteService = new FavoriteService();

