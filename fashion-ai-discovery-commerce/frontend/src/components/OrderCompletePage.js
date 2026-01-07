// 주문 완료 페이지 컴포넌트
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './OrderCompletePage.css';

/**
 * OrderCompletePage 컴포넌트 - 주문 완료 페이지
 * 주문이 완료된 후 표시되는 확인 페이지입니다.
 */
function OrderCompletePage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const headerRef = useRef(null);

  useEffect(() => {
    // 주문 정보 로드
    const orders = JSON.parse(localStorage.getItem('orders') || '[]');
    const foundOrder = orders.find(o => o.order_id === orderId);
    
    if (foundOrder) {
      setOrder(foundOrder);
    }
  }, [orderId]);

  // 주문 데이터 로드 후 제목에 포커스 (접근성)
  useEffect(() => {
    if (order && headerRef.current) {
      headerRef.current.focus();
    }
  }, [order]);

  if (!order) {
    return (
      <div className="order-complete-page">
        <div className="order-complete-container">
          <h2>주문 정보를 찾을 수 없습니다</h2>
          <button onClick={() => navigate('/')} className="order-complete-button">
            홈으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

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

  return (
    <div className="order-complete-page">
      <div className="order-complete-container">
        <div className="order-complete-icon">✓</div>
        <h1 tabIndex="-1" ref={headerRef}>주문이 완료되었습니다!</h1>
        <p className="order-complete-message">
          주문해주셔서 감사합니다. 주문 내역은 마이페이지에서 확인하실 수 있습니다.
        </p>

        <div className="order-complete-info">
          <div className="order-info-section">
            <h2>주문 정보</h2>
            <div className="order-info-row">
              <span>주문번호</span>
              <span>{order.order_id}</span>
            </div>
            <div className="order-info-row">
              <span>주문일시</span>
              <span>{formatDate(order.order_date)}</span>
            </div>
            <div className="order-info-row">
              <span>주문 상태</span>
              <span className="order-status">{order.status}</span>
            </div>
          </div>

          <div className="order-info-section">
            <h2>주문 상품</h2>
            <div className="order-items">
              {order.items.map((item) => (
                <div key={item.product_id} className="order-item">
                  <img src={item.image_url} alt={item.name} className="order-item-image" />
                  <div className="order-item-info">
                    <h3>{item.name}</h3>
                    <p>{item.brand}</p>
                    <p>수량: {item.quantity}개</p>
                    <p className="order-item-price">{formatPrice(item.price * item.quantity)}원</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="order-info-section">
            <h2>배송 정보</h2>
            <div className="order-info-row">
              <span>받는 분</span>
              <span>{order.order_info.recipient_name}</span>
            </div>
            <div className="order-info-row">
              <span>연락처</span>
              <span>{order.order_info.recipient_phone}</span>
            </div>
            <div className="order-info-row">
              <span>배송 주소</span>
              <span>
                {order.order_info.shipping_address} {order.order_info.shipping_address_detail}
              </span>
            </div>
          </div>

          <div className="order-info-section">
            <h2>결제 정보</h2>
            <div className="order-info-row">
              <span>결제 수단</span>
              <span>
                {order.order_info.payment_method === 'card' && '신용카드'}
                {order.order_info.payment_method === 'bank' && '무통장 입금'}
                {order.order_info.payment_method === 'kakao' && '카카오페이'}
                {order.order_info.payment_method === 'naver' && '네이버페이'}
              </span>
            </div>
            <div className="order-info-row order-total">
              <span>총 결제금액</span>
              <span>{formatPrice(order.total_price)}원</span>
            </div>
          </div>
        </div>

        <div className="order-complete-actions">
          <button
            className="order-complete-button primary"
            onClick={() => navigate('/mypage')}
          >
            마이페이지로 이동
          </button>
          <button
            className="order-complete-button secondary"
            onClick={() => navigate('/')}
          >
            쇼핑 계속하기
          </button>
        </div>
      </div>
    </div>
  );
}

export default OrderCompletePage;

