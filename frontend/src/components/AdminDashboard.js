// 관리자 대시보드 컴포넌트
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminDashboard.css';
import { adminService } from '../services/adminService';
import { dummyProducts } from '../data/dummyProducts';
import { useAuth } from '../contexts/AuthContext';

/**
 * AdminDashboard 컴포넌트 - 관리자 전용 대시보드 페이지
 * 사용자별 및 전체 사용자의 좋아요, 장바구니, 챗봇 대화 내역을 조회할 수 있습니다.
 */
function AdminDashboard() {
  const navigate = useNavigate();
  const { isAuthenticated, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'users', 'orders', 'products', 'favorites', 'cart', 'chat', 'analytics'
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [users, setUsers] = useState([]);
  const [overviewStats, setOverviewStats] = useState(null);
  const [userFavorites, setUserFavorites] = useState([]);
  const [userCarts, setUserCarts] = useState([]);
  const [userChatHistory, setUserChatHistory] = useState([]);
  const [orders, setOrders] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [isEditUserModalOpen, setIsEditUserModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userRoleFilter, setUserRoleFilter] = useState('all'); // 'all', 'admin', 'user'
  const [newUser, setNewUser] = useState({
    id: '',
    name: '',
    password: '',
    role: 'user'
  });
  const [editUserName, setEditUserName] = useState('');
  const [orderStatusFilter, setOrderStatusFilter] = useState('all'); // 'all', '주문완료', '결제완료', '배송준비중', '배송중', '배송완료'
  const [productCategoryFilter, setProductCategoryFilter] = useState('all'); // 상품 관리 필터
  const [productGenderFilter, setProductGenderFilter] = useState('all'); // 상품 관리 필터
  const [favoritesUserFilter, setFavoritesUserFilter] = useState('all'); // 좋아요 목록 사용자 필터
  const [cartUserFilter, setCartUserFilter] = useState('all'); // 장바구니 사용자 필터
  const [isEditProductModalOpen, setIsEditProductModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [products, setProducts] = useState(dummyProducts); // 상품 목록 상태
  const [editProductData, setEditProductData] = useState({
    name: '',
    brand: '',
    category: '상의',
    gender: '남성',
    style_tags: [],
    color: '',
    price: 0,
    popularity_score: 0.0,
    image_url: '',
    description: '',
    season: '',
    situation: ''
  });

  // 관리자 권한 체크
  useEffect(() => {
    if (!isAuthenticated || !isAdmin) {
      navigate('/');
    }
  }, [isAuthenticated, isAdmin, navigate]);

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    loadData();
  }, []);

  // 탭 변경 시 데이터 로드
  useEffect(() => {
    loadTabData();
  }, [activeTab, selectedUserId]);

  /**
   * 초기 데이터 로드
   */
  const loadData = () => {
    const allUsers = adminService.getAllUsers();
    setUsers(allUsers);
    setOverviewStats(adminService.getUserStats());
  };

  /**
   * 탭별 데이터 로드
   */
  const loadTabData = () => {
    if (activeTab === 'orders') {
      // 주문 내역 로드
      const allOrders = JSON.parse(localStorage.getItem('orders') || '[]');
      setOrders(allOrders.sort((a, b) => new Date(b.order_date) - new Date(a.order_date)));
    } else if (activeTab === 'analytics') {
      // 챗봇 분석 데이터 로드
      const allChatHistory = adminService.getAllUsersChatHistory();
      const intentCounts = {};
      let totalMessages = 0;
      let totalRecommendations = 0;
      let totalClicks = 0;

      allChatHistory.forEach(userData => {
        userData.chatHistory.forEach(chat => {
          totalMessages++;
          if (chat.assistant_message?.intent) {
            const intent = chat.assistant_message.intent;
            intentCounts[intent] = (intentCounts[intent] || 0) + 1;
          }
          if (chat.assistant_message?.recommendations) {
            totalRecommendations += chat.assistant_message.recommendations.length;
          }
        });
      });

      setAnalytics({
        intentCounts,
        totalMessages,
        totalRecommendations,
        totalClicks,
        ctr: totalMessages > 0 ? ((totalClicks / totalRecommendations) * 100).toFixed(2) : '0.00'
      });
    } else if (activeTab === 'favorites') {
      if (selectedUserId) {
        const favorites = adminService.getUserFavoriteProducts(selectedUserId);
        setUserFavorites([{
          user: users.find(u => u.id === selectedUserId),
          favoriteProducts: favorites
        }]);
      } else {
        // 관리자 계정 제외
        const allFavorites = adminService.getAllUsersFavorites();
        const filteredFavorites = allFavorites.filter(userData => userData.user.role !== 'admin');
        setUserFavorites(filteredFavorites);
      }
    } else if (activeTab === 'cart') {
      if (selectedUserId) {
        const cart = adminService.getUserCart(selectedUserId);
        setUserCarts([{
          user: users.find(u => u.id === selectedUserId),
          cartItems: cart
        }]);
      } else {
        // 관리자 계정 제외
        const allCarts = adminService.getAllUsersCarts();
        const filteredCarts = allCarts.filter(userData => userData.user.role !== 'admin');
        setUserCarts(filteredCarts);
      }
    } else if (activeTab === 'chat') {
      if (selectedUserId) {
        const history = adminService.getUserChatHistory(selectedUserId);
        setUserChatHistory([{
          user: users.find(u => u.id === selectedUserId),
          chatHistory: history
        }]);
      } else {
        // 관리자 계정 제외
        const allChatHistory = adminService.getAllUsersChatHistory();
        const filteredChatHistory = allChatHistory.filter(userData => userData.user.role !== 'admin');
        setUserChatHistory(filteredChatHistory);
      }
    }
  };

  /**
   * 가격 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  /**
   * 날짜 포맷팅
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="admin-dashboard-page">
      <div className="admin-dashboard">
        <div className="admin-dashboard-header">
          <h2>관리자 대시보드</h2>
        </div>

        <div className="admin-dashboard-content">
          {/* 탭 메뉴 */}
          <div className="admin-tabs">
            <button
              className={`admin-tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              전체 통계
            </button>
            <button
              className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              사용자 관리
            </button>
            <button
              className={`admin-tab ${activeTab === 'orders' ? 'active' : ''}`}
              onClick={() => setActiveTab('orders')}
            >
              주문 관리
            </button>
            <button
              className={`admin-tab ${activeTab === 'products' ? 'active' : ''}`}
              onClick={() => setActiveTab('products')}
            >
              상품 관리
            </button>
            <button
              className={`admin-tab ${activeTab === 'favorites' ? 'active' : ''}`}
              onClick={() => setActiveTab('favorites')}
            >
              좋아요 목록
            </button>
            <button
              className={`admin-tab ${activeTab === 'cart' ? 'active' : ''}`}
              onClick={() => setActiveTab('cart')}
            >
              장바구니
            </button>
            <button
              className={`admin-tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              챗봇 대화 내역
            </button>
            <button
              className={`admin-tab ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              챗봇 분석
            </button>
          </div>

          {/* 사용자 선택 필터 */}
          {(activeTab === 'favorites' || activeTab === 'cart' || activeTab === 'chat') && (
            <div className="admin-user-filter">
              <label>사용자 필터:</label>
              <select
                value={selectedUserId || ''}
                onChange={(e) => setSelectedUserId(e.target.value || null)}
                className="admin-user-select"
              >
                <option value="">전체 사용자</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.email ? user.email.split('@')[0] : user.id || '-'}) {user.role === 'admin' ? '[관리자]' : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* 탭 컨텐츠 */}
          <div className="admin-tab-content">
            {activeTab === 'overview' && (
              <div className="admin-overview">
                <h3>전체 통계</h3>
                {overviewStats && (
                  <div className="admin-stats-grid">
                    <div className="admin-stat-card">
                      <h4>전체 사용자</h4>
                      <p className="admin-stat-value">{overviewStats.totalUsers}명</p>
                    </div>
                    <div className="admin-stat-card">
                      <h4>전체 좋아요</h4>
                      <p className="admin-stat-value">{overviewStats.totalFavorites}개</p>
                    </div>
                    <div className="admin-stat-card">
                      <h4>전체 장바구니 아이템</h4>
                      <p className="admin-stat-value">{overviewStats.totalCartItems}개</p>
                    </div>
                    <div className="admin-stat-card">
                      <h4>전체 챗봇 메시지</h4>
                      <p className="admin-stat-value">{overviewStats.totalChatMessages}개</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'users' && (
              <div className="admin-users">
                <div className="admin-users-header">
                  <div>
                    <h3>사용자 관리</h3>
                    <p className="admin-users-count">
                      총 {users.length}명
                      {userRoleFilter === 'admin' && ` (관리자: ${users.filter(u => u.role === 'admin').length}명)`}
                      {userRoleFilter === 'user' && ` (일반 사용자: ${users.filter(u => u.role === 'user').length}명)`}
                    </p>
                  </div>
                  <button
                    className="admin-add-user-button"
                    onClick={() => setIsAddUserModalOpen(true)}
                  >
                    + 계정 추가
                  </button>
                </div>
                
                {/* 역할 필터 */}
                <div className="admin-users-filter">
                  <button
                    className={`admin-filter-button ${userRoleFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setUserRoleFilter('all')}
                  >
                    전체
                  </button>
                  <button
                    className={`admin-filter-button ${userRoleFilter === 'admin' ? 'active' : ''}`}
                    onClick={() => setUserRoleFilter('admin')}
                  >
                    관리자만
                  </button>
                  <button
                    className={`admin-filter-button ${userRoleFilter === 'user' ? 'active' : ''}`}
                    onClick={() => setUserRoleFilter('user')}
                  >
                    일반 사용자만
                  </button>
                </div>

                {users.length === 0 ? (
                  <div className="admin-empty">사용자가 없습니다.</div>
                ) : (
                  <div className="admin-users-grid">
                    {users
                      .filter(user => {
                        if (userRoleFilter === 'all') return true;
                        if (userRoleFilter === 'admin') return user.role === 'admin';
                        if (userRoleFilter === 'user') return user.role === 'user';
                        return true;
                      })
                      .map(user => (
                      <div key={user.id} className="admin-user-card">
                        <div className="admin-user-card-header">
                          <div className="admin-user-avatar">
                            {user.name.charAt(0)}
                          </div>
                          <div className="admin-user-info">
                            <h4 className="admin-user-name">{user.name}</h4>
                            <p className="admin-user-email">{user.email ? user.email.split('@')[0] : user.id || '-'}</p>
                          </div>
                        </div>
                        <div className="admin-user-details">
                          <div className="admin-user-detail-item">
                            <span className="admin-user-detail-label">역할</span>
                            <span className={`admin-role-badge ${user.role === 'admin' ? 'admin' : 'user'}`}>
                              {user.role === 'admin' ? '관리자' : '일반 사용자'}
                            </span>
                          </div>
                          <div className="admin-user-detail-item">
                            <span className="admin-user-detail-label">가입일</span>
                            <span className="admin-user-detail-value">
                              {user.createdAt ? formatDate(user.createdAt) : '-'}
                            </span>
                          </div>
                        </div>
                        <div className="admin-user-actions">
                          <button
                            className="admin-edit-button"
                            onClick={() => {
                              setEditingUser(user);
                              setEditUserName(user.name);
                              setIsEditUserModalOpen(true);
                            }}
                          >
                            편집
                          </button>
                          <button
                            className="admin-delete-button"
                            onClick={() => {
                              if (window.confirm(`${user.name}님의 계정을 삭제하시겠습니까?`)) {
                                try {
                                  adminService.deleteUser(user.id);
                                  loadData(); // 목록 새로고침
                                  alert('계정이 삭제되었습니다.');
                                } catch (error) {
                                  alert('계정 삭제 중 오류가 발생했습니다: ' + error.message);
                                }
                              }
                            }}
                          >
                            삭제
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'orders' && (
              <div className="admin-orders">
                <div className="admin-orders-header">
                  <div>
                    <h3>주문 관리</h3>
                    <p className="admin-orders-count">
                      총 {orders.length}건
                      {orderStatusFilter !== 'all' && ` (${orderStatusFilter}: ${orders.filter(o => o.status === orderStatusFilter).length}건)`}
                    </p>
                  </div>
                </div>

                {/* 상태 필터 */}
                <div className="admin-orders-filter">
                  <button
                    className={`admin-filter-button ${orderStatusFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('all')}
                  >
                    전체
                  </button>
                  <button
                    className={`admin-filter-button ${orderStatusFilter === '주문완료' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('주문완료')}
                  >
                    주문완료
                  </button>
                  <button
                    className={`admin-filter-button ${orderStatusFilter === '결제완료' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('결제완료')}
                  >
                    결제완료
                  </button>
                  <button
                    className={`admin-filter-button ${orderStatusFilter === '배송준비중' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('배송준비중')}
                  >
                    배송준비중
                  </button>
                  <button
                    className={`admin-filter-button ${orderStatusFilter === '배송중' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('배송중')}
                  >
                    배송중
                  </button>
                  <button
                    className={`admin-filter-button ${orderStatusFilter === '배송완료' ? 'active' : ''}`}
                    onClick={() => setOrderStatusFilter('배송완료')}
                  >
                    배송완료
                  </button>
                </div>

                {orders.length === 0 ? (
                  <div className="admin-empty">주문 내역이 없습니다.</div>
                ) : (
                  <div className="admin-orders-grid">
                    {orders
                      .filter(order => {
                        if (orderStatusFilter === 'all') return true;
                        return order.status === orderStatusFilter;
                      })
                      .map(order => {
                        const orderUser = users.find(u => u.id === order.user_id);
                        return (
                          <div key={order.order_id} className="admin-order-card">
                            <div className="admin-order-card-header">
                              <div className="admin-order-info">
                                <h4 className="admin-order-id">주문번호: {order.order_id}</h4>
                                <p className="admin-order-date">{formatDate(order.order_date)}</p>
                                <p className="admin-order-user">
                                  {orderUser ? orderUser.name : order.user_id}
                                  {orderUser?.email && ` (${orderUser.email.split('@')[0]})`}
                                </p>
                              </div>
                              <div className="admin-order-status-wrapper">
                                <select
                                  className="admin-order-status-select"
                                  value={order.status || '주문완료'}
                                  onChange={(e) => {
                                    const updatedOrders = orders.map(o =>
                                      o.order_id === order.order_id ? { ...o, status: e.target.value } : o
                                    );
                                    setOrders(updatedOrders);
                                    const allOrders = JSON.parse(localStorage.getItem('orders') || '[]');
                                    const updatedAllOrders = allOrders.map(o =>
                                      o.order_id === order.order_id ? { ...o, status: e.target.value } : o
                                    );
                                    localStorage.setItem('orders', JSON.stringify(updatedAllOrders));
                                  }}
                                >
                                  <option value="주문완료">주문완료</option>
                                  <option value="결제완료">결제완료</option>
                                  <option value="배송준비중">배송준비중</option>
                                  <option value="배송중">배송중</option>
                                  <option value="배송완료">배송완료</option>
                                </select>
                              </div>
                            </div>
                            
                            <div className="admin-order-items-section">
                              <p className="admin-order-items-label">주문 상품 ({order.items.length}개)</p>
                              <div className="admin-order-items-list">
                                {order.items.slice(0, 3).map((item, idx) => (
                                  <div key={idx} className="admin-order-item-compact">
                                    <img 
                                      src={item.image_url || 'https://via.placeholder.com/60x60?text=No+Image'} 
                                      alt={item.name} 
                                      className="admin-order-item-image-compact"
                                      onError={(e) => {
                                        e.target.src = 'https://via.placeholder.com/60x60?text=No+Image';
                                      }}
                                    />
                                    <div className="admin-order-item-info-compact">
                                      <p className="admin-order-item-name">{item.name}</p>
                                      <p className="admin-order-item-details">
                                        {item.brand} · 수량: {item.quantity}개
                                      </p>
                                    </div>
                                    <p className="admin-order-item-price-compact">
                                      {formatPrice(item.price * item.quantity)}원
                                    </p>
                                  </div>
                                ))}
                                {order.items.length > 3 && (
                                  <p className="admin-order-more-items">
                                    외 {order.items.length - 3}개 상품
                                  </p>
                                )}
                              </div>
                            </div>

                            <div className="admin-order-card-footer">
                              <div className="admin-order-total">
                                <span className="admin-order-total-label">총 결제금액</span>
                                <span className="admin-order-total-value">{formatPrice(order.total_price)}원</span>
                              </div>
                              {order.order_info && (
                                <div className="admin-order-shipping">
                                  <p className="admin-order-shipping-label">배송지</p>
                                  <p className="admin-order-shipping-address">
                                    {order.order_info.shipping_address} {order.order_info.shipping_address_detail || ''}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'products' && (
              <div className="admin-products">
                <div className="admin-products-header">
                  <div>
                    <h3>상품 관리</h3>
                    <p className="admin-products-count">
                      총 {products.length}개
                      {productCategoryFilter !== 'all' && ` (${productCategoryFilter}: ${products.filter(p => p.category === productCategoryFilter).length}개)`}
                      {productGenderFilter !== 'all' && ` (${productGenderFilter}: ${products.filter(p => p.gender === productGenderFilter || p.gender === '공용').length}개)`}
                    </p>
                  </div>
                  <button
                    className="admin-add-user-button"
                    onClick={() => {
                      alert('상품 등록 기능은 별도 페이지에서 구현됩니다.');
                    }}
                  >
                    + 상품 등록
                  </button>
                </div>

                {/* 카테고리 필터 */}
                <div className="admin-products-filter">
                  <div className="admin-filter-group">
                    <label className="admin-filter-label">카테고리</label>
                    <div className="admin-filter-buttons">
                      <button
                        className={`admin-filter-button ${productCategoryFilter === 'all' ? 'active' : ''}`}
                        onClick={() => setProductCategoryFilter('all')}
                      >
                        전체
                      </button>
                      {['상의', '하의', '아우터', '신발', '액세서리', '기타'].map(category => (
                        <button
                          key={category}
                          className={`admin-filter-button ${productCategoryFilter === category ? 'active' : ''}`}
                          onClick={() => setProductCategoryFilter(category)}
                        >
                          {category}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="admin-filter-group">
                    <label className="admin-filter-label">성별</label>
                    <div className="admin-filter-buttons">
                      <button
                        className={`admin-filter-button ${productGenderFilter === 'all' ? 'active' : ''}`}
                        onClick={() => setProductGenderFilter('all')}
                      >
                        전체
                      </button>
                      {['남성', '여성', '공용'].map(gender => (
                        <button
                          key={gender}
                          className={`admin-filter-button ${productGenderFilter === gender ? 'active' : ''}`}
                          onClick={() => setProductGenderFilter(gender)}
                        >
                          {gender}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="admin-products-grid">
                  {products
                    .filter(product => {
                      if (productCategoryFilter !== 'all' && product.category !== productCategoryFilter) return false;
                      if (productGenderFilter !== 'all' && product.gender !== productGenderFilter && product.gender !== '공용') return false;
                      if (productGenderFilter === '공용' && product.gender !== '공용') return false;
                      return true;
                    })
                    .map(product => (
                      <div key={product.product_id} className="admin-product-card">
                        <div className="admin-product-card-image-wrapper">
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="admin-product-card-image"
                            onError={(e) => {
                              e.target.src = 'https://via.placeholder.com/200x200?text=No+Image';
                            }}
                          />
                        </div>
                        <div className="admin-product-card-info">
                          <p className="admin-product-card-brand">{product.brand}</p>
                          <h4 className="admin-product-card-name">{product.name}</h4>
                          <div className="admin-product-card-meta">
                            <span className="admin-product-card-category">{product.category}</span>
                            <span className="admin-product-card-gender">{product.gender}</span>
                          </div>
                          <p className="admin-product-card-price">{formatPrice(product.price)}원</p>
                          <div className="admin-product-card-actions">
                            <button
                              className="admin-edit-button"
                              onClick={() => {
                                setEditingProduct(product);
                                setEditProductData({
                                  name: product.name || '',
                                  brand: product.brand || '',
                                  category: product.category || '상의',
                                  gender: product.gender || '남성',
                                  style_tags: Array.isArray(product.style_tags) ? product.style_tags.join(', ') : (product.style_tags || ''),
                                  color: product.color || '',
                                  price: product.price || 0,
                                  popularity_score: product.popularity_score || 0.0,
                                  image_url: product.image_url || '',
                                  description: product.description || '',
                                  season: product.season || '',
                                  situation: product.situation || ''
                                });
                                setIsEditProductModalOpen(true);
                              }}
                            >
                              수정
                            </button>
                            <button
                              className="admin-delete-button"
                              onClick={() => {
                                if (window.confirm('정말 삭제하시겠습니까?')) {
                                  alert('상품 삭제 기능은 백엔드 API 연동이 필요합니다.');
                                }
                              }}
                            >
                              삭제
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="admin-analytics">
                <div className="admin-analytics-header">
                  <div>
                    <h3>챗봇 분석</h3>
                    <p className="admin-analytics-count">
                      {analytics ? `총 ${analytics.totalMessages}개 메시지 분석` : '데이터 로딩 중...'}
                    </p>
                  </div>
                </div>
                {analytics ? (
                  <div className="admin-analytics-content">
                    <div className="admin-analytics-stats-grid">
                      <div className="admin-stat-card">
                        <div className="admin-stat-icon">💬</div>
                        <div className="admin-stat-info">
                          <h4>전체 메시지 수</h4>
                          <p className="admin-stat-value">{analytics.totalMessages}개</p>
                        </div>
                      </div>
                      <div className="admin-stat-card">
                        <div className="admin-stat-icon">🎯</div>
                        <div className="admin-stat-info">
                          <h4>전체 추천 수</h4>
                          <p className="admin-stat-value">{analytics.totalRecommendations}개</p>
                        </div>
                      </div>
                      <div className="admin-stat-card">
                        <div className="admin-stat-icon">👆</div>
                        <div className="admin-stat-info">
                          <h4>클릭 수</h4>
                          <p className="admin-stat-value">{analytics.totalClicks}개</p>
                        </div>
                      </div>
                      <div className="admin-stat-card">
                        <div className="admin-stat-icon">📊</div>
                        <div className="admin-stat-info">
                          <h4>CTR (클릭률)</h4>
                          <p className="admin-stat-value">{analytics.ctr}%</p>
                        </div>
                      </div>
                    </div>
                    <div className="admin-analytics-section-card">
                      <h4 className="admin-analytics-section-title">Intent 분포</h4>
                      <div className="admin-intent-grid">
                        {Object.entries(analytics.intentCounts)
                          .sort(([, a], [, b]) => b - a)
                          .map(([intent, count]) => {
                            const percentage = analytics.totalMessages > 0 
                              ? ((count / analytics.totalMessages) * 100).toFixed(1) 
                              : 0;
                            return (
                              <div key={intent} className="admin-intent-card">
                                <div className="admin-intent-card-header">
                                  <span className="admin-intent-name">{intent}</span>
                                  <span className="admin-intent-count">{count}회</span>
                                </div>
                                <div className="admin-intent-bar">
                                  <div
                                    className="admin-intent-bar-fill"
                                    style={{
                                      width: `${percentage}%`
                                    }}
                                  />
                                </div>
                                <p className="admin-intent-percentage">{percentage}%</p>
                              </div>
                            );
                          })}
                      </div>
                    </div>
                    <div className="admin-analytics-section-card">
                      <h4 className="admin-analytics-section-title">재추천 케이스</h4>
                      <p className="admin-note">
                        재추천 케이스는 챗봇 대화 내역에서 확인할 수 있습니다.
                        동일한 사용자가 같은 상품을 여러 번 추천받은 경우를 의미합니다.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="admin-empty">분석 데이터를 불러오는 중...</div>
                )}
              </div>
            )}

            {activeTab === 'favorites' && (
              <div className="admin-favorites">
                <div className="admin-favorites-header">
                  <div>
                    <h3>좋아요 목록</h3>
                    <p className="admin-favorites-count">
                      총 {userFavorites.reduce((sum, u) => sum + u.favoriteProducts.length, 0)}개
                    </p>
                  </div>
                </div>


                {userFavorites.length === 0 ? (
                  <div className="admin-empty">데이터가 없습니다.</div>
                ) : (
                  <div className="admin-favorites-grid">
                    {userFavorites
                      .map((userData, index) => (
                        userData.favoriteProducts.length > 0 && (
                          <div key={index} className="admin-favorite-user-card">
                            <div className="admin-favorite-user-header">
                              <div className="admin-favorite-user-avatar">
                                {userData.user.name.charAt(0)}
                              </div>
                              <div className="admin-favorite-user-info">
                                <h4 className="admin-favorite-user-name">{userData.user.name}</h4>
                                <p className="admin-favorite-user-id">
                                  {userData.user.email ? userData.user.email.split('@')[0] : userData.user.id || '-'}
                                </p>
                              </div>
                              <span className="admin-favorite-count-badge">
                                {userData.favoriteProducts.length}개
                              </span>
                            </div>
                            <div className="admin-favorite-products-grid">
                              {userData.favoriteProducts.map(product => (
                                <div key={product.product_id} className="admin-favorite-product-card">
                                  <img
                                    src={product.image_url}
                                    alt={product.name}
                                    className="admin-favorite-product-image"
                                    onError={(e) => {
                                      e.target.src = 'https://via.placeholder.com/150x150?text=No+Image';
                                    }}
                                  />
                                  <div className="admin-favorite-product-info">
                                    <p className="admin-favorite-product-brand">{product.brand}</p>
                                    <p className="admin-favorite-product-name">{product.name}</p>
                                    <p className="admin-favorite-product-price">{formatPrice(product.price)}원</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )
                      ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'cart' && (
              <div className="admin-cart">
                <div className="admin-cart-header">
                  <div>
                    <h3>장바구니</h3>
                    <p className="admin-cart-count">
                      총 {userCarts.reduce((sum, u) => sum + u.cartItems.length, 0)}개 상품
                    </p>
                  </div>
                </div>


                {userCarts.length === 0 ? (
                  <div className="admin-empty">데이터가 없습니다.</div>
                ) : (
                  <div className="admin-cart-grid">
                    {userCarts
                      .map((userData, index) => {
                        const totalItems = userData.cartItems.reduce((sum, item) => sum + item.quantity, 0);
                        const totalPrice = userData.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                        return (
                          userData.cartItems.length > 0 && (
                            <div key={index} className="admin-cart-user-card">
                              <div className="admin-cart-user-header">
                                <div className="admin-cart-user-avatar">
                                  {userData.user.name.charAt(0)}
                                </div>
                                <div className="admin-cart-user-info">
                                  <h4 className="admin-cart-user-name">{userData.user.name}</h4>
                                  <p className="admin-cart-user-id">
                                    {userData.user.email ? userData.user.email.split('@')[0] : userData.user.id || '-'}
                                  </p>
                                </div>
                                <div className="admin-cart-user-summary">
                                  <span className="admin-cart-summary-label">총 {totalItems}개</span>
                                  <span className="admin-cart-summary-price">{formatPrice(totalPrice)}원</span>
                                </div>
                              </div>
                              <div className="admin-cart-items-grid">
                                {userData.cartItems.map((item, itemIndex) => (
                                  <div key={itemIndex} className="admin-cart-item-card">
                                    <img
                                      src={item.image_url}
                                      alt={item.name}
                                      className="admin-cart-item-card-image"
                                      onError={(e) => {
                                        e.target.src = 'https://via.placeholder.com/100x100?text=No+Image';
                                      }}
                                    />
                                    <div className="admin-cart-item-card-info">
                                      <p className="admin-cart-item-card-brand">{item.brand}</p>
                                      <p className="admin-cart-item-card-name">{item.name}</p>
                                      <div className="admin-cart-item-card-details">
                                        <span className="admin-cart-item-card-quantity">수량: {item.quantity}개</span>
                                        <span className="admin-cart-item-card-price">
                                          {formatPrice(item.price * item.quantity)}원
                                        </span>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )
                        );
                      })}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'chat' && (
              <div className="admin-chat">
                <div className="admin-chat-header">
                  <div>
                    <h3>챗봇 대화 내역</h3>
                    <p className="admin-chat-count">
                      총 {userChatHistory.reduce((sum, u) => sum + u.chatHistory.length, 0)}개 대화
                    </p>
                  </div>
                </div>
                {userChatHistory.length === 0 ? (
                  <div className="admin-empty">데이터가 없습니다.</div>
                ) : (
                  <div className="admin-chat-grid">
                    {userChatHistory
                      .filter(userData => userData.chatHistory.length > 0)
                      .map((userData, index) => (
                        <div key={index} className="admin-chat-user-card">
                          <div className="admin-chat-user-header">
                            <div className="admin-chat-user-avatar">
                              {userData.user.name.charAt(0)}
                            </div>
                            <div className="admin-chat-user-info">
                              <h4 className="admin-chat-user-name">{userData.user.name}</h4>
                              <p className="admin-chat-user-id">
                                {userData.user.email ? userData.user.email.split('@')[0] : userData.user.id || '-'}
                              </p>
                            </div>
                            <span className="admin-chat-count-badge">
                              {userData.chatHistory.length}개
                            </span>
                          </div>
                          <div className="admin-chat-messages-list">
                            {userData.chatHistory.slice(0, 5).map((chat, chatIndex) => (
                              <div key={chatIndex} className="admin-chat-message-card">
                                <div className="admin-chat-message-header-compact">
                                  <span className="admin-chat-timestamp-compact">
                                    {formatDate(chat.timestamp)}
                                  </span>
                                  {chat.session_id && (
                                    <span className="admin-chat-session-badge">
                                      {chat.session_id.substring(0, 8)}...
                                    </span>
                                  )}
                                </div>
                                <div className="admin-chat-message-bubble user">
                                  <span className="admin-chat-message-label">사용자</span>
                                  <p className="admin-chat-message-text">
                                    {chat.user_message?.content || 'N/A'}
                                  </p>
                                </div>
                                <div className="admin-chat-message-bubble assistant">
                                  <span className="admin-chat-message-label">챗봇</span>
                                  <p className="admin-chat-message-text">
                                    {chat.assistant_message?.content || 'N/A'}
                                  </p>
                                </div>
                              </div>
                            ))}
                            {userData.chatHistory.length > 5 && (
                              <p className="admin-chat-more">
                                외 {userData.chatHistory.length - 5}개 대화 더 보기
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 상품 수정 모달 */}
      {isEditProductModalOpen && editingProduct && (
        <div className="admin-modal-overlay" onClick={() => setIsEditProductModalOpen(false)}>
          <div className="admin-modal admin-modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h3>상품 수정</h3>
              <button
                className="admin-modal-close"
                onClick={() => setIsEditProductModalOpen(false)}
                aria-label="닫기"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M18 6L6 18M6 6L18 18"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
            <div className="admin-modal-content">
              <div className="admin-form-group">
                <label htmlFor="edit-product-id">상품 ID</label>
                <input
                  id="edit-product-id"
                  type="text"
                  value={editingProduct.product_id}
                  disabled
                  style={{ backgroundColor: '#f9fafb', color: '#6b7280' }}
                />
                <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: '0.25rem 0 0 0' }}>
                  상품 ID는 변경할 수 없습니다.
                </p>
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-name">상품명 *</label>
                <input
                  id="edit-product-name"
                  type="text"
                  value={editProductData.name}
                  onChange={(e) => setEditProductData({ ...editProductData, name: e.target.value })}
                  placeholder="오버핏 후드티"
                  required
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-brand">브랜드 *</label>
                <input
                  id="edit-product-brand"
                  type="text"
                  value={editProductData.brand}
                  onChange={(e) => setEditProductData({ ...editProductData, brand: e.target.value })}
                  placeholder="무신사 Style"
                  required
                />
              </div>
              <div className="admin-form-row">
                <div className="admin-form-group">
                  <label htmlFor="edit-product-category">카테고리 *</label>
                  <select
                    id="edit-product-category"
                    value={editProductData.category}
                    onChange={(e) => setEditProductData({ ...editProductData, category: e.target.value })}
                    required
                  >
                    <option value="상의">상의</option>
                    <option value="하의">하의</option>
                    <option value="아우터">아우터</option>
                    <option value="신발">신발</option>
                    <option value="액세서리">액세서리</option>
                    <option value="기타">기타</option>
                  </select>
                </div>
                <div className="admin-form-group">
                  <label htmlFor="edit-product-gender">성별 *</label>
                  <select
                    id="edit-product-gender"
                    value={editProductData.gender}
                    onChange={(e) => setEditProductData({ ...editProductData, gender: e.target.value })}
                    required
                  >
                    <option value="남성">남성</option>
                    <option value="여성">여성</option>
                    <option value="공용">공용</option>
                  </select>
                </div>
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-price">가격 *</label>
                <input
                  id="edit-product-price"
                  type="number"
                  value={editProductData.price}
                  onChange={(e) => setEditProductData({ ...editProductData, price: parseInt(e.target.value) || 0 })}
                  placeholder="89000"
                  min="0"
                  required
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-image-url">이미지 URL *</label>
                <input
                  id="edit-product-image-url"
                  type="url"
                  value={editProductData.image_url}
                  onChange={(e) => setEditProductData({ ...editProductData, image_url: e.target.value })}
                  placeholder="https://images.unsplash.com/photo-..."
                  required
                />
                {editProductData.image_url && (
                  <img
                    src={editProductData.image_url}
                    alt="미리보기"
                    style={{
                      width: '100%',
                      maxHeight: '200px',
                      objectFit: 'contain',
                      marginTop: '0.5rem',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-description">상품 설명</label>
                <textarea
                  id="edit-product-description"
                  value={editProductData.description}
                  onChange={(e) => setEditProductData({ ...editProductData, description: e.target.value })}
                  placeholder="상품에 대한 상세 설명을 입력하세요."
                  rows="4"
                  style={{ resize: 'vertical' }}
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-product-style-tags">스타일 태그 (쉼표로 구분)</label>
                <input
                  id="edit-product-style-tags"
                  type="text"
                  value={editProductData.style_tags}
                  onChange={(e) => setEditProductData({ ...editProductData, style_tags: e.target.value })}
                  placeholder="무신사 감성, 스트릿, 오버핏"
                />
                <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: '0.25rem 0 0 0' }}>
                  여러 태그는 쉼표로 구분하여 입력하세요.
                </p>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-group">
                  <label htmlFor="edit-product-color">색상</label>
                  <input
                    id="edit-product-color"
                    type="text"
                    value={editProductData.color}
                    onChange={(e) => setEditProductData({ ...editProductData, color: e.target.value })}
                    placeholder="블랙"
                  />
                </div>
                <div className="admin-form-group">
                  <label htmlFor="edit-product-popularity">인기도 점수</label>
                  <input
                    id="edit-product-popularity"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={editProductData.popularity_score}
                    onChange={(e) => setEditProductData({ ...editProductData, popularity_score: parseFloat(e.target.value) || 0 })}
                    placeholder="0.92"
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-group">
                  <label htmlFor="edit-product-season">계절</label>
                  <select
                    id="edit-product-season"
                    value={editProductData.season}
                    onChange={(e) => setEditProductData({ ...editProductData, season: e.target.value })}
                  >
                    <option value="">선택 안함</option>
                    <option value="봄">봄</option>
                    <option value="여름">여름</option>
                    <option value="가을">가을</option>
                    <option value="겨울">겨울</option>
                    <option value="봄/여름">봄/여름</option>
                    <option value="가을/겨울">가을/겨울</option>
                    <option value="봄/가을">봄/가을</option>
                    <option value="사계절">사계절</option>
                  </select>
                </div>
                <div className="admin-form-group">
                  <label htmlFor="edit-product-situation">상황</label>
                  <input
                    id="edit-product-situation"
                    type="text"
                    value={editProductData.situation}
                    onChange={(e) => setEditProductData({ ...editProductData, situation: e.target.value })}
                    placeholder="데일리, 데이트, 출근 등"
                  />
                </div>
              </div>
            </div>
            <div className="admin-modal-footer">
              <button
                className="admin-modal-cancel"
                onClick={() => {
                  setIsEditProductModalOpen(false);
                  setEditingProduct(null);
                  setEditProductData({
                    name: '',
                    brand: '',
                    category: '상의',
                    gender: '남성',
                    style_tags: [],
                    color: '',
                    price: 0,
                    popularity_score: 0.0,
                    image_url: '',
                    description: '',
                    season: '',
                    situation: ''
                  });
                }}
              >
                취소
              </button>
              <button
                className="admin-modal-submit"
                onClick={async () => {
                  if (!editProductData.name || !editProductData.brand || !editProductData.category || !editProductData.gender || !editProductData.price || !editProductData.image_url) {
                    alert('필수 항목을 모두 입력해주세요.');
                    return;
                  }

                  try {
                    // 스타일 태그 처리 (쉼표로 구분된 문자열을 배열로 변환)
                    const styleTagsArray = editProductData.style_tags
                      ? editProductData.style_tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
                      : [];

                    // 백엔드 API 호출
                    // 빈 문자열이면 상대 경로를 사용하여 nginx 프록시를 통해 요청
                    const API_BASE_URL = process.env.REACT_APP_API_URL || '';
                    const response = await fetch(`${API_BASE_URL}/api/v1/admin/products/${editingProduct.product_id}`, {
                      method: 'PUT',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        name: editProductData.name.trim(),
                        brand: editProductData.brand.trim(),
                        category: editProductData.category,
                        gender: editProductData.gender,
                        style_tags: styleTagsArray,
                        color: editProductData.color.trim() || null,
                        price: parseInt(editProductData.price),
                        popularity_score: parseFloat(editProductData.popularity_score) || 0.0,
                        image_url: editProductData.image_url.trim(),
                        description: editProductData.description.trim() || null,
                        season: editProductData.season || null,
                        situation: editProductData.situation.trim() || null
                      })
                    });

                    if (!response.ok) {
                      const errorData = await response.json();
                      throw new Error(errorData.detail || '상품 수정에 실패했습니다.');
                    }

                    // 프론트엔드 products 상태 업데이트
                    const updatedProduct = {
                      ...editingProduct,
                      name: editProductData.name.trim(),
                      brand: editProductData.brand.trim(),
                      category: editProductData.category,
                      gender: editProductData.gender,
                      style_tags: styleTagsArray,
                      color: editProductData.color.trim() || '',
                      price: parseInt(editProductData.price),
                      popularity_score: parseFloat(editProductData.popularity_score) || 0.0,
                      image_url: editProductData.image_url.trim(),
                      description: editProductData.description.trim() || '',
                      season: editProductData.season || '',
                      situation: editProductData.situation.trim() || ''
                    };

                    // products 상태 업데이트
                    setProducts(prevProducts => 
                      prevProducts.map(p => 
                        p.product_id === editingProduct.product_id ? updatedProduct : p
                      )
                    );

                    // 모달 닫기 및 상태 초기화
                    setIsEditProductModalOpen(false);
                    setEditingProduct(null);
                    setEditProductData({
                      name: '',
                      brand: '',
                      category: '상의',
                      gender: '남성',
                      style_tags: [],
                      color: '',
                      price: 0,
                      popularity_score: 0.0,
                      image_url: '',
                      description: '',
                      season: '',
                      situation: ''
                    });
                    alert('상품 정보가 수정되었습니다.');
                  } catch (error) {
                    console.error('상품 수정 오류:', error);
                    alert('상품 수정 중 오류가 발생했습니다: ' + error.message);
                  }
                }}
              >
                저장
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 계정 추가 모달 */}
      {isAddUserModalOpen && (
        <div className="admin-modal-overlay" onClick={() => setIsAddUserModalOpen(false)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h3>새 계정 추가</h3>
              <button
                className="admin-modal-close"
                onClick={() => setIsAddUserModalOpen(false)}
                aria-label="닫기"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M18 6L6 18M6 6L18 18"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
            <div className="admin-modal-content">
              <div className="admin-form-group">
                <label htmlFor="new-user-id">ID *</label>
                <input
                  id="new-user-id"
                  type="text"
                  value={newUser.id}
                  onChange={(e) => setNewUser({ ...newUser, id: e.target.value })}
                  placeholder="user001"
                  required
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="new-user-name">이름 *</label>
                <input
                  id="new-user-name"
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  placeholder="홍길동"
                  required
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="new-user-password">비밀번호 *</label>
                <input
                  id="new-user-password"
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  placeholder="6자 이상"
                  required
                  minLength={6}
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="new-user-role">역할 *</label>
                <select
                  id="new-user-role"
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                >
                  <option value="user">일반 사용자</option>
                  <option value="admin">관리자</option>
                </select>
              </div>
            </div>
            <div className="admin-modal-footer">
              <button
                className="admin-modal-cancel"
                onClick={() => {
                  setIsAddUserModalOpen(false);
                  setNewUser({ id: '', name: '', password: '', role: 'user' });
                }}
              >
                취소
              </button>
              <button
                className="admin-modal-submit"
                onClick={() => {
                  if (!newUser.id || !newUser.name || !newUser.password) {
                    alert('모든 필드를 입력해주세요.');
                    return;
                  }
                  
                  if (newUser.password.length < 6) {
                    alert('비밀번호는 6자 이상이어야 합니다.');
                    return;
                  }

                  try {
                    // ID를 이메일 형식으로 변환 (adminService는 email을 받지만 실제로는 ID로 사용)
                    const email = `${newUser.id}@example.com`;
                    adminService.addUser(
                      email,
                      newUser.name,
                      newUser.password,
                      newUser.role
                    );
                    loadData(); // 목록 새로고침
                    setIsAddUserModalOpen(false);
                    setNewUser({ id: '', name: '', password: '', role: 'user' });
                    alert('계정이 추가되었습니다.');
                  } catch (error) {
                    alert('계정 추가 중 오류가 발생했습니다: ' + error.message);
                  }
                }}
              >
                추가
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 계정 편집 모달 */}
      {isEditUserModalOpen && editingUser && (
        <div className="admin-modal-overlay" onClick={() => setIsEditUserModalOpen(false)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h3>계정 편집</h3>
              <button
                className="admin-modal-close"
                onClick={() => {
                  setIsEditUserModalOpen(false);
                  setEditingUser(null);
                  setEditUserName('');
                }}
                aria-label="닫기"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M18 6L6 18M6 6L18 18"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
            <div className="admin-modal-content">
              <div className="admin-form-group">
                <label htmlFor="edit-user-id">ID</label>
                <input
                  id="edit-user-id"
                  type="text"
                  value={editingUser.email ? editingUser.email.split('@')[0] : editingUser.id || ''}
                  disabled
                  style={{ backgroundColor: '#f9fafb', color: '#6b7280' }}
                />
                <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: '0.25rem 0 0 0' }}>
                  ID는 변경할 수 없습니다.
                </p>
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-user-name">이름 *</label>
                <input
                  id="edit-user-name"
                  type="text"
                  value={editUserName}
                  onChange={(e) => setEditUserName(e.target.value)}
                  placeholder="홍길동"
                  required
                />
              </div>
              <div className="admin-form-group">
                <label htmlFor="edit-user-role">역할</label>
                <select
                  id="edit-user-role"
                  value={editingUser.role}
                  onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value })}
                >
                  <option value="user">일반 사용자</option>
                  <option value="admin">관리자</option>
                </select>
              </div>
            </div>
            <div className="admin-modal-footer">
              <button
                className="admin-modal-cancel"
                onClick={() => {
                  setIsEditUserModalOpen(false);
                  setEditingUser(null);
                  setEditUserName('');
                }}
              >
                취소
              </button>
              <button
                className="admin-modal-submit"
                onClick={() => {
                  if (!editUserName.trim()) {
                    alert('이름을 입력해주세요.');
                    return;
                  }

                  try {
                    adminService.updateUser(editingUser.id, {
                      name: editUserName.trim(),
                      role: editingUser.role
                    });
                    loadData(); // 목록 새로고침
                    setIsEditUserModalOpen(false);
                    setEditingUser(null);
                    setEditUserName('');
                    alert('계정 정보가 수정되었습니다.');
                  } catch (error) {
                    alert('계정 수정 중 오류가 발생했습니다: ' + error.message);
                  }
                }}
              >
                저장
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;

