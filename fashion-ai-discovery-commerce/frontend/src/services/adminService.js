// 관리자 서비스 - 관리자 전용 기능을 제공하는 서비스
import { dummyProducts } from '../data/dummyProducts';

// API 기본 URL (빈 문자열이면 상대 경로를 사용하여 nginx 프록시를 통해 요청)
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

/**
 * AdminService - 관리자 전용 기능을 제공하는 서비스 클래스
 * 로컬 스토리지와 백엔드 API를 사용합니다.
 */
class AdminService {
  /**
   * 모든 사용자 목록 가져오기
   * 
   * @returns {Array} 사용자 목록
   */
  getAllUsers() {
    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');
      // 비밀번호 제외하고 반환
      return users.map(user => ({
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role || 'user',
        createdAt: user.createdAt
      }));
    } catch (error) {
      console.error('사용자 목록 조회 오류:', error);
      return [];
    }
  }

  /**
   * 특정 사용자의 좋아요 목록 가져오기
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Array} 좋아요한 상품 ID 목록
   */
  getUserFavorites(userId) {
    try {
      const favorites = JSON.parse(localStorage.getItem(`favorites_${userId}`) || '[]');
      return favorites;
    } catch (error) {
      console.error('좋아요 목록 조회 오류:', error);
      return [];
    }
  }

  /**
   * 특정 사용자의 좋아요한 상품 상세 정보 가져오기
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Array} 좋아요한 상품 객체 배열
   */
  getUserFavoriteProducts(userId) {
    const favoriteIds = this.getUserFavorites(userId);
    return dummyProducts.filter(product => favoriteIds.includes(product.product_id));
  }

  /**
   * 모든 사용자의 좋아요 목록 가져오기
   * 
   * @returns {Array} 사용자별 좋아요 목록
   */
  getAllUsersFavorites() {
    const users = this.getAllUsers();
    return users.map(user => ({
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      },
      favorites: this.getUserFavorites(user.id),
      favoriteProducts: this.getUserFavoriteProducts(user.id)
    }));
  }

  /**
   * 특정 사용자의 장바구니 가져오기
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Array} 장바구니 아이템 배열
   */
  getUserCart(userId) {
    try {
      const cart = JSON.parse(localStorage.getItem(`cart_${userId}`) || '[]');
      return cart;
    } catch (error) {
      console.error('장바구니 조회 오류:', error);
      return [];
    }
  }

  /**
   * 모든 사용자의 장바구니 가져오기
   * 
   * @returns {Array} 사용자별 장바구니 목록
   */
  getAllUsersCarts() {
    const users = this.getAllUsers();
    return users.map(user => ({
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      },
      cartItems: this.getUserCart(user.id)
    }));
  }

  /**
   * 특정 사용자의 챗봇 대화 내역 가져오기
   * 
   * @param {string} userId - 사용자 ID
   * @returns {Array} 대화 내역 배열
   */
  getUserChatHistory(userId) {
    try {
      const history = JSON.parse(localStorage.getItem(`chat_history_${userId}`) || '[]');
      return history;
    } catch (error) {
      console.error('챗봇 대화 내역 조회 오류:', error);
      return [];
    }
  }

  /**
   * 모든 사용자의 챗봇 대화 내역 가져오기
   * 
   * @returns {Array} 사용자별 대화 내역 목록
   */
  getAllUsersChatHistory() {
    const users = this.getAllUsers();
    return users.map(user => ({
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      },
      chatHistory: this.getUserChatHistory(user.id)
    }));
  }

  /**
   * 새 사용자 추가
   * 
   * @param {string} email - 이메일 (ID를 포함한 형식)
   * @param {string} name - 이름
   * @param {string} password - 비밀번호
   * @param {string} role - 역할 (기본값: 'user')
   * @returns {Object} 생성된 사용자 정보
   */
  addUser(email, name, password, role = 'user') {
    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');
      
      // ID 중복 체크 (email에서 @ 앞부분이 ID)
      const userId = email.split('@')[0];
      if (users.find(u => {
        const existingUserId = u.email ? u.email.split('@')[0] : u.id;
        return existingUserId === userId;
      })) {
        throw new Error('이미 등록된 ID입니다.');
      }
      
      // 이메일 중복 체크 (전체 이메일)
      if (users.find(u => u.email === email)) {
        throw new Error('이미 등록된 이메일입니다.');
      }
      
      const newUser = {
        id: `user_${Date.now()}`,
        email,
        name,
        password, // 실제로는 해시화해야 하지만, 데모용으로 평문 저장
        role,
        createdAt: new Date().toISOString()
      };
      
      users.push(newUser);
      localStorage.setItem('users', JSON.stringify(users));
      
      return {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name,
        role: newUser.role,
        createdAt: newUser.createdAt
      };
    } catch (error) {
      console.error('사용자 추가 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자 정보 수정
   * 
   * @param {string} userId - 사용자 ID
   * @param {Object} updates - 수정할 정보 (name, role 등)
   * @returns {Object} 수정된 사용자 정보
   */
  updateUser(userId, updates) {
    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');
      const userIndex = users.findIndex(u => u.id === userId);
      
      if (userIndex === -1) {
        throw new Error('사용자를 찾을 수 없습니다.');
      }
      
      // 사용자 정보 업데이트
      users[userIndex] = {
        ...users[userIndex],
        ...updates
      };
      
      localStorage.setItem('users', JSON.stringify(users));
      
      return {
        id: users[userIndex].id,
        email: users[userIndex].email,
        name: users[userIndex].name,
        role: users[userIndex].role,
        createdAt: users[userIndex].createdAt
      };
    } catch (error) {
      console.error('사용자 수정 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자 삭제
   * 
   * @param {string} userId - 사용자 ID
   * @returns {boolean} 삭제 성공 여부
   */
  deleteUser(userId) {
    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');
      const filteredUsers = users.filter(u => u.id !== userId);
      
      if (filteredUsers.length === users.length) {
        throw new Error('사용자를 찾을 수 없습니다.');
      }
      
      localStorage.setItem('users', JSON.stringify(filteredUsers));
      
      // 사용자 관련 데이터도 삭제
      localStorage.removeItem(`favorites_${userId}`);
      localStorage.removeItem(`cart_${userId}`);
      localStorage.removeItem(`chat_history_${userId}`);
      
      return true;
    } catch (error) {
      console.error('사용자 삭제 오류:', error);
      throw error;
    }
  }

  /**
   * 사용자 통계 정보 가져오기
   * 
   * @param {string} userId - 사용자 ID (선택사항, 없으면 전체 통계)
   * @returns {Object} 통계 정보
   */
  getUserStats(userId = null) {
    if (userId) {
      // 특정 사용자 통계
      const favorites = this.getUserFavorites(userId);
      const cart = this.getUserCart(userId);
      const chatHistory = this.getUserChatHistory(userId);
      
      return {
        userId,
        favoritesCount: favorites.length,
        cartItemsCount: cart.reduce((sum, item) => sum + item.quantity, 0),
        cartTotalPrice: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
        chatMessagesCount: chatHistory.length
      };
    } else {
      // 전체 통계
      const users = this.getAllUsers();
      const allFavorites = this.getAllUsersFavorites();
      const allCarts = this.getAllUsersCarts();
      const allChatHistory = this.getAllUsersChatHistory();
      
      return {
        totalUsers: users.length,
        totalFavorites: allFavorites.reduce((sum, u) => sum + u.favorites.length, 0),
        totalCartItems: allCarts.reduce((sum, u) => sum + u.cartItems.reduce((s, item) => s + item.quantity, 0), 0),
        totalChatMessages: allChatHistory.reduce((sum, u) => sum + u.chatHistory.length, 0)
      };
    }
  }

  /**
   * 모든 주문 목록 가져오기
   * 
   * @returns {Promise<Array>} 주문 목록
   */
  async getAllOrders() {
    // localStorage에서 주문 데이터 가져오기 (기존 방식 유지)
    try {
      const orders = JSON.parse(localStorage.getItem('orders') || '[]');
      return orders;
    } catch (error) {
      console.error('주문 목록 조회 오류:', error);
      return [];
    }
  }

  /**
   * 주문 상태 업데이트
   * 
   * @param {string} orderId - 주문 ID
   * @param {string} status - 새로운 상태
   * @returns {Promise<boolean>} 성공 여부
   */
  async updateOrderStatus(orderId, status) {
    try {
      // 백엔드 API 호출 시도
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/orders/${orderId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        return true;
      }
    } catch (error) {
      console.warn('백엔드 API 호출 실패, localStorage에 저장합니다:', error);
    }
    
    // 백엔드 API가 실패하면 localStorage에 저장 (호환성 유지)
    try {
      const orders = JSON.parse(localStorage.getItem('orders') || '[]');
      const updatedOrders = orders.map(order =>
        order.order_id === orderId ? { ...order, status } : order
      );
      localStorage.setItem('orders', JSON.stringify(updatedOrders));
      return true;
    } catch (error) {
      console.error('주문 상태 업데이트 오류:', error);
      return false;
    }
  }
}

// 싱글톤 인스턴스 export
export const adminService = new AdminService();

