// 추천 서비스 - 추천 피드백(클릭 로그) 전송을 담당하는 서비스
import axios from 'axios';

// API 기본 URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * axios 인스턴스 생성
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10초 타임아웃
});

/**
 * RecommendationService 클래스
 * 추천 피드백(클릭 로그) 전송을 담당합니다.
 */
class RecommendationService {
  /**
   * 추천 상품 클릭 로그 전송
   * 문서 규칙: 이전에 추천했으나 클릭하지 않은 상품 우선 제외를 위한 클릭 로그 수집
   * 
   * @param {string} userId - 사용자 ID
   * @param {string} productId - 상품 ID
   * @returns {Promise<boolean>} 성공 여부
   */
  async recordClick(userId, productId) {
    try {
      // 비동기로 전송 (에러가 나도 사용자 경험에 영향 없음)
      apiClient.post('/api/v1/recommendations/feedback', null, {
        params: {
          user_id: userId,
          product_id: productId,
          feedback_type: 'click'
        }
      }).catch(error => {
        // 에러 로그만 남기고 사용자에게는 영향 없음
        console.warn('클릭 로그 전송 실패:', error);
      });
      
      return true;
    } catch (error) {
      console.warn('클릭 로그 전송 오류:', error);
      return false;
    }
  }
}

// 싱글톤 인스턴스 export
export const recommendationService = new RecommendationService();

