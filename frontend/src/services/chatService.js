// 채팅 서비스 - 백엔드 API와의 통신을 담당하는 서비스 클래스
import axios from 'axios';

// API 기본 URL (환경 변수에서 가져오거나 기본값 사용)
// 빈 문자열이면 상대 경로를 사용하여 nginx 프록시를 통해 요청
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

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
 * 채팅 서비스 클래스
 * 백엔드 채팅 API와의 통신을 담당합니다.
 */
class ChatService {
  /**
   * 사용자 메시지를 서버로 전송하고 AI 응답을 받아옵니다.
   * 
   * @param {Object} request - 요청 데이터
   * @param {string} request.message - 사용자 메시지
   * @param {string} request.session_id - 세션 ID (선택사항)
   * @param {string} request.user_id - 사용자 ID
   * @returns {Promise<Object>} AI 응답 데이터
   */
  async sendMessage(request) {
    try {
      const response = await apiClient.post('/api/v1/chat/message', request);
      return response.data;
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      
      // 에러 응답 처리
      if (error.response) {
        throw new Error(error.response.data.detail || '서버 오류가 발생했습니다.');
      } else if (error.request) {
        throw new Error('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
      } else {
        throw new Error('요청 처리 중 오류가 발생했습니다.');
      }
    }
  }

  /**
   * 특정 세션의 대화 히스토리를 가져옵니다.
   * 
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<Object>} 대화 히스토리 데이터
   */
  async getChatHistory(sessionId) {
    try {
      const response = await apiClient.get(`/api/v1/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('대화 히스토리 조회 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자의 세션 목록을 가져옵니다.
   * 
   * @param {string} userId - 사용자 ID
   * @param {number} limit - 가져올 세션 수 (기본값: 10)
   * @param {number} offset - 오프셋 (기본값: 0)
   * @returns {Promise<Object>} 세션 목록 데이터
   */
  async getUserSessions(userId, limit = 10, offset = 0) {
    try {
      const response = await apiClient.get(`/api/v1/chat/sessions/${userId}`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('세션 목록 조회 오류:', error);
      throw error;
    }
  }

  /**
   * 특정 세션을 삭제합니다.
   * 
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<Object>} 삭제 결과
   */
  async deleteSession(sessionId) {
    try {
      const response = await apiClient.delete(`/api/v1/chat/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('세션 삭제 오류:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 export
export const chatService = new ChatService();

