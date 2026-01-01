// 검색 서비스 - 백엔드 API와의 통신을 담당하는 서비스 클래스
import axios from 'axios';

// API 기본 URL (환경 변수에서 가져오거나 기본값 사용)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * axios 인스턴스 생성 - 기본 설정 포함
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30초 타임아웃
});

/**
 * SearchService 클래스
 * 백엔드 검색 API와의 통신을 담당합니다.
 */
class SearchService {
  /**
   * 사용자 취향을 반영한 상품 검색
   * 
   * @param {string} query - 검색 쿼리
   * @param {string|null} userId - 사용자 ID (로그인된 경우)
   * @param {number} limit - 검색 결과 수 (기본값: 50)
   * @returns {Promise<Object>} 검색 결과
   */
  async searchProducts(query, userId = null, limit = 50) {
    try {
      const params = {
        q: query,
        limit: limit,
      };
      
      // 로그인된 사용자인 경우 user_id 추가
      if (userId) {
        params.user_id = userId;
      }
      
      const response = await apiClient.get('/api/v1/recommendations/products/search', {
        params: params,
      });
      
      return response.data;
    } catch (error) {
      console.error('상품 검색 오류:', error);
      
      // 에러 응답 처리
      if (error.response) {
        throw new Error(error.response.data.detail || '검색 중 오류가 발생했습니다.');
      } else if (error.request) {
        throw new Error('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
      } else {
        throw new Error('요청 처리 중 오류가 발생했습니다.');
      }
    }
  }
}

// 싱글톤 인스턴스 export
export const searchService = new SearchService();

