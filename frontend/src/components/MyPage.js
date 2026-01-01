// 마이페이지 컴포넌트
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MyPage.css';
import { useAuth } from '../contexts/AuthContext';
import { useFavorites } from '../contexts/FavoritesContext';
import { dummyProducts } from '../data/dummyProducts';

/**
 * MyPage 컴포넌트 - 마이페이지
 * 주문 내역, 좋아요 목록 등을 확인할 수 있는 페이지입니다.
 */
function MyPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { favorites, toggleFavorite } = useFavorites();
  const [orders, setOrders] = useState([]);
  const [activeTab, setActiveTab] = useState('orders'); // 'orders', 'favorites'

  // 좋아요한 상품들을 가져오기
  const favoriteProducts = dummyProducts.filter(product =>
    favorites.includes(product.product_id)
  );

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }

    // 주문 내역 로드
    const allOrders = JSON.parse(localStorage.getItem('orders') || '[]');
    const userOrders = allOrders.filter(order => order.user_id === user?.id);
    setOrders(userOrders.sort((a, b) => new Date(b.order_date) - new Date(a.order_date)));
  }, [user, isAuthenticated, navigate]);

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
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="mypage">
      <div className="mypage-container">
        <h1>마이페이지</h1>
        <div className="mypage-user-info">
          <h2>{user?.name}님 안녕하세요!</h2>
        </div>

        <div className="mypage-tabs">
          <button
            className={`mypage-tab ${activeTab === 'orders' ? 'active' : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            주문 내역
          </button>
          <button
            className={`mypage-tab ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorites')}
          >
            좋아요 ({favorites?.length || 0})
          </button>
        </div>

        <div className="mypage-content">
          {activeTab === 'orders' && (
            <div className="mypage-orders">
              {orders.length === 0 ? (
                <div className="mypage-empty">
                  <p>주문 내역이 없습니다.</p>
                  <button onClick={() => navigate('/')} className="mypage-button">
                    쇼핑하러 가기
                  </button>
                </div>
              ) : (
                <div className="mypage-orders-list">
                  {orders.map((order) => (
                    <div key={order.order_id} className="mypage-order-card">
                      <div className="mypage-order-header">
                        <div>
                          <h3>주문번호: {order.order_id}</h3>
                          <p className="mypage-order-date">{formatDate(order.order_date)}</p>
                        </div>
                        <span className={`mypage-order-status ${order.status === '주문완료' ? 'completed' : ''}`}>
                          {order.status}
                        </span>
                      </div>
                      <div className="mypage-order-items">
                        {order.items.map((item) => (
                          <div key={item.product_id} className="mypage-order-item">
                            <img src={item.image_url} alt={item.name} className="mypage-order-item-image" />
                            <div className="mypage-order-item-info">
                              <h4>{item.name}</h4>
                              <p>{item.brand}</p>
                              <p>수량: {item.quantity}개</p>
                            </div>
                            <p className="mypage-order-item-price">
                              {formatPrice(item.price * item.quantity)}원
                            </p>
                          </div>
                        ))}
                      </div>
                      <div className="mypage-order-footer">
                        <div className="mypage-order-total">
                          <span>총 결제금액</span>
                          <span>{formatPrice(order.total_price)}원</span>
                        </div>
                        <button
                          className="mypage-order-detail-button"
                          onClick={() => navigate(`/order-complete/${order.order_id}`)}
                        >
                          상세보기
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'favorites' && (
            <div className="mypage-favorites">
              {favoriteProducts.length === 0 ? (
                <div className="mypage-empty">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" className="mypage-empty-icon">
                    <path
                      d="M12 21L3.5 12.5C2.5 11.5 2 10.25 2 8.75C2 5.75 4.25 3.5 7.25 3.5C8.5 3.5 9.75 4 10.5 4.75C11.25 4 12.5 3.5 13.75 3.5C16.75 3.5 19 5.75 19 8.75C19 10.25 18.5 11.5 17.5 12.5L12 21Z"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p>좋아요한 상품이 없습니다.</p>
                  <p className="mypage-empty-hint">상품에 하트를 눌러 좋아요를 추가해보세요.</p>
                  <button onClick={() => navigate('/')} className="mypage-button">
                    쇼핑하러 가기
                  </button>
                </div>
              ) : (
                <>
                  <div className="mypage-favorites-grid">
                    {favoriteProducts.map((product) => (
                      <div key={product.product_id} className="mypage-favorites-item">
                        <div className="mypage-favorites-item-image-container">
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="mypage-favorites-item-image"
                            onClick={() => navigate(`/product/${product.product_id}`)}
                            onError={(e) => {
                              e.target.src = 'https://via.placeholder.com/300x400?text=No+Image';
                            }}
                          />
                          <button
                            className="mypage-favorites-item-remove-button"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFavorite(product.product_id);
                            }}
                            aria-label="좋아요 취소"
                          >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                              <path
                                d="M10 17.5L3.33333 10.8333C2.41667 9.91667 1.83333 8.66667 1.83333 7.33333C1.83333 4.58333 4.08333 2.33333 6.83333 2.33333C8.08333 2.33333 9.25 2.83333 10 3.66667C10.75 2.83333 11.9167 2.33333 13.1667 2.33333C15.9167 2.33333 18.1667 4.58333 18.1667 7.33333C18.1667 8.66667 17.5833 9.91667 16.6667 10.8333L10 17.5Z"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                            </svg>
                          </button>
                        </div>
                        <div className="mypage-favorites-item-info">
                          <p className="mypage-favorites-item-brand">{product.brand}</p>
                          <p className="mypage-favorites-item-name">{product.name}</p>
                          <p className="mypage-favorites-item-price">{formatPrice(product.price)}원</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mypage-favorites-footer">
                    <p>총 {favoriteProducts.length}개의 상품</p>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MyPage;

