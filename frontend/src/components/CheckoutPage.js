// 주문/결제 페이지 컴포넌트
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CheckoutPage.css';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

/**
 * CheckoutPage 컴포넌트 - 주문/결제 페이지
 * 장바구니 상품을 주문하고 결제하는 페이지입니다.
 */
function CheckoutPage() {
  const navigate = useNavigate();
  const { cartItems, getTotalPrice, clearCart } = useCart();
  const { user } = useAuth();
  const [orderInfo, setOrderInfo] = useState({
    recipient_name: user?.name || '',
    recipient_phone: '',
    shipping_address: '',
    shipping_address_detail: '',
    payment_method: 'card',
    delivery_request: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);

  /**
   * 컴포넌트 마운트 시 더미 배송 정보 자동 입력
   */
  useEffect(() => {
    // 더미 배송 정보 설정
    const dummyShippingInfo = {
      recipient_name: user?.name || '테스트 사용자 01',
      recipient_phone: '010-1234-5678',
      shipping_address: '서울시 강남구 테헤란로 123',
      shipping_address_detail: '101동 101호',
      payment_method: 'card',
      delivery_request: ''
    };

    setOrderInfo(prev => ({
      ...prev,
      ...dummyShippingInfo
    }));
  }, [user]);

  /**
   * 주문 정보 입력 핸들러
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setOrderInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * 주문 완료 핸들러
   */
  const handleOrder = async () => {
    // 필수 정보 검증
    if (!orderInfo.recipient_name || !orderInfo.recipient_phone || !orderInfo.shipping_address) {
      alert('배송 정보를 모두 입력해주세요.');
      return;
    }

    setIsProcessing(true);

    try {
      // 주문 정보 저장 (로컬 스토리지)
      const order = {
        order_id: `order_${Date.now()}`,
        user_id: user?.id,
        items: cartItems,
        total_price: getTotalPrice(),
        order_info: orderInfo,
        order_date: new Date().toISOString(),
        status: '주문완료'
      };

      // 주문 내역 저장
      const orders = JSON.parse(localStorage.getItem('orders') || '[]');
      orders.push(order);
      localStorage.setItem('orders', JSON.stringify(orders));

      // 장바구니 비우기
      await clearCart();

      // 주문 완료 페이지로 이동
      navigate(`/order-complete/${order.order_id}`);
    } catch (error) {
      console.error('주문 처리 오류:', error);
      alert('주문 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * 가격 포맷팅
   */
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price);
  };

  if (cartItems.length === 0) {
    return (
      <div className="checkout-page">
        <div className="checkout-empty">
          <h2>장바구니가 비어있습니다</h2>
          <button onClick={() => navigate('/')} className="checkout-back-button">
            쇼핑하러 가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <h1>주문/결제</h1>

        <div className="checkout-content">
          {/* 주문 상품 목록 */}
          <div className="checkout-section">
            <h2>주문 상품</h2>
            <div className="checkout-items">
              {cartItems.map((item) => (
                <div key={item.product_id} className="checkout-item">
                  <img src={item.image_url} alt={item.name} className="checkout-item-image" />
                  <div className="checkout-item-info">
                    <h3>{item.name}</h3>
                    <p>{item.brand}</p>
                    <p>수량: {item.quantity}개</p>
                    <p className="checkout-item-price">{formatPrice(item.price * item.quantity)}원</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 배송 정보 */}
          <div className="checkout-section">
            <h2>배송 정보</h2>
            <div className="checkout-form">
              <div className="checkout-form-group">
                <label>받는 분 이름 *</label>
                <input
                  type="text"
                  name="recipient_name"
                  value={orderInfo.recipient_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="checkout-form-group">
                <label>연락처 *</label>
                <input
                  type="tel"
                  name="recipient_phone"
                  value={orderInfo.recipient_phone}
                  onChange={handleInputChange}
                  placeholder="010-1234-5678"
                  required
                />
              </div>
              <div className="checkout-form-group">
                <label>배송 주소 *</label>
                <input
                  type="text"
                  name="shipping_address"
                  value={orderInfo.shipping_address}
                  onChange={handleInputChange}
                  placeholder="서울시 강남구 테헤란로 123"
                  required
                />
              </div>
              <div className="checkout-form-group">
                <label>상세 주소</label>
                <input
                  type="text"
                  name="shipping_address_detail"
                  value={orderInfo.shipping_address_detail}
                  onChange={handleInputChange}
                  placeholder="101동 101호"
                />
              </div>
              <div className="checkout-form-group">
                <label>배송 요청사항</label>
                <textarea
                  name="delivery_request"
                  value={orderInfo.delivery_request}
                  onChange={handleInputChange}
                  placeholder="배송 시 요청사항을 입력해주세요."
                  rows="3"
                />
              </div>
            </div>
          </div>

          {/* 결제 정보 */}
          <div className="checkout-section">
            <h2>결제 정보</h2>
            <div className="checkout-form">
              <div className="checkout-form-group">
                <label>결제 수단</label>
                <select
                  name="payment_method"
                  value={orderInfo.payment_method}
                  onChange={handleInputChange}
                >
                  <option value="card">신용카드</option>
                  <option value="bank">무통장 입금</option>
                  <option value="kakao">카카오페이</option>
                  <option value="naver">네이버페이</option>
                </select>
              </div>
            </div>
          </div>

          {/* 주문 요약 */}
          <div className="checkout-summary">
            <h2>주문 요약</h2>
            <div className="checkout-summary-row">
              <span>상품 금액</span>
              <span>{formatPrice(getTotalPrice())}원</span>
            </div>
            <div className="checkout-summary-row">
              <span>배송비</span>
              <span>무료</span>
            </div>
            <div className="checkout-summary-row checkout-total">
              <span>총 결제금액</span>
              <span>{formatPrice(getTotalPrice())}원</span>
            </div>
            <button
              className="checkout-order-button"
              onClick={handleOrder}
              disabled={isProcessing}
            >
              {isProcessing ? '주문 처리 중...' : '주문하기'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CheckoutPage;

