// 주문 서비스 - 백엔드 API와 통신
// API 기본 URL (빈 문자열이면 상대 경로를 사용하여 nginx 프록시를 통해 요청)
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

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
};

/**
 * OrderService - 주문 관련 API 호출 서비스
 */
class OrderService {
  /**
   * 주문 생성
   * 
   * @param {string} userId - 사용자 ID
   * @param {Array} items - 주문 상품 목록
   * @param {number} totalPrice - 총 주문 금액
   * @param {Object} orderInfo - 주문 정보 (배송 정보, 결제 정보 등)
   * @returns {Promise<Object>} 생성된 주문 정보
   */
  async createOrder(userId, items, totalPrice, orderInfo) {
    try {
      // 주문 상품 데이터 변환
      const orderItems = items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price || item.product_data?.price || 0,
        name: item.name || item.product_data?.name,
        brand: item.brand || item.product_data?.brand,
        image_url: item.image_url || item.product_data?.image_url,
        product_data: item.product_data || {
          name: item.name,
          brand: item.brand,
          image_url: item.image_url,
          price: item.price
        }
      }));

      const response = await apiClient.post('/api/v1/orders', {
        user_id: userId,
        items: orderItems,
        total_price: totalPrice,
        order_info: orderInfo,
        status: '주문완료'
      });

      return response;
    } catch (error) {
      console.error('주문 생성 오류:', error);
      throw error;
    }
  }

  /**
   * 주문 조회
   * 
   * @param {string} orderId - 주문 ID
   * @returns {Promise<Object>} 주문 정보
   */
  async getOrder(orderId) {
    try {
      const response = await apiClient.get(`/api/v1/orders/${orderId}`);
      return response;
    } catch (error) {
      console.error('주문 조회 오류:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 export
export const orderService = new OrderService();

