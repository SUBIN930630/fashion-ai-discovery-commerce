import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

function OrderCompletePage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const ordersRaw = localStorage.getItem('orders');
    const orders = ordersRaw ? JSON.parse(ordersRaw) : [];
    const found = orders.find(o => o.id === orderId);
    setOrder(found || null);
    setLoading(false);
  }, [orderId]);

  if (loading) return <div style={{ padding: 20, textAlign: 'center' }}>로딩 중...</div>;
  if (!order) return <div style={{ padding: 20, textAlign: 'center', color: 'red' }}>주문 정보를 찾을 수 없습니다.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 10, color: '#667eea' }}>
          🎉 주문이 완료되었습니다!
        </h1>
        <p style={{ fontSize: 16, color: '#666' }}>주문해주셔서 감사합니다.</p>
      </div>

      <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 30, marginBottom: 30 }}>
        {/* 주문 번호 및 기본 정보 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 30, paddingBottom: 30, borderBottom: '1px solid #eee' }}>
          <div>
            <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 번호</p>
            <p style={{ fontSize: 18, fontWeight: 600, fontFamily: 'monospace' }}>{order.id}</p>
          </div>
          <div>
            <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 일시</p>
            <p style={{ fontSize: 14 }}>{new Date(order.created_at).toLocaleString('ko-KR')}</p>
          </div>
        </div>

        {/* 배송 정보 */}
        <div style={{ marginBottom: 30 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>배송 정보</h2>
          <div style={{ background: '#f9f9f9', padding: 16, borderRadius: 6 }}>
            <p style={{ marginBottom: 8 }}>
              <span style={{ color: '#666', marginRight: 16 }}>수취인</span>
              <strong>{order.customer.name}</strong>
            </p>
            <p style={{ marginBottom: 8 }}>
              <span style={{ color: '#666', marginRight: 16 }}>휴대폰</span>
              <span>{order.customer.phone}</span>
            </p>
            <p style={{ marginBottom: 8 }}>
              <span style={{ color: '#666', marginRight: 16 }}>주소</span>
              <span>
                {order.customer.address} {order.customer.detailAddress && ` ${order.customer.detailAddress}`}
              </span>
            </p>
            {order.customer.zipcode && (
              <p>
                <span style={{ color: '#666', marginRight: 16 }}>우편번호</span>
                <span>{order.customer.zipcode}</span>
              </p>
            )}
          </div>
        </div>

        {/* 주문 상품 */}
        <div style={{ marginBottom: 30 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>주문 상품</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {order.items.map(item => (
              <div key={item.product_id} style={{ display: 'flex', justifyContent: 'space-between', padding: 12, background: '#f9f9f9', borderRadius: 4 }}>
                <span>{item.name}</span>
                <span>{item.quantity}개</span>
                <span style={{ fontWeight: 600 }}>{new Intl.NumberFormat('ko-KR').format(item.price * item.quantity)}원</span>
              </div>
            ))}
          </div>
        </div>

        {/* 결제 정보 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, paddingTop: 30, borderTop: '1px solid #eee' }}>
          <div>
            <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>결제 방법</p>
            <p style={{ fontSize: 14, fontWeight: 600 }}>
              {order.payment === 'card' && '💳 신용카드'}
              {order.payment === 'bank' && '🏦 무통장입금'}
              {order.payment === 'kakao' && '☕ 카카오페이'}
            </p>
          </div>
          <div>
            <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 상태</p>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#667eea' }}>✓ {order.status || '주문 완료'}</p>
          </div>
        </div>

        <div style={{ marginTop: 30, paddingTop: 30, borderTop: '1px solid #eee', textAlign: 'right' }}>
          <p style={{ fontSize: 14, color: '#999', marginBottom: 8 }}>총 결제 금액</p>
          <p style={{ fontSize: 28, fontWeight: 700, color: '#333' }}>
            {new Intl.NumberFormat('ko-KR').format(order.total)}원
          </p>
        </div>
      </div>

      {/* 액션 버튼 */}
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
        <Link to="/" style={{
          display: 'inline-block',
          padding: '12px 24px',
          background: '#333',
          color: 'white',
          textDecoration: 'none',
          borderRadius: 6,
          fontSize: 14,
          fontWeight: 600
        }}>
          계속 쇼핑하기
        </Link>
        <Link to="/mypage" style={{
          display: 'inline-block',
          padding: '12px 24px',
          background: '#667eea',
          color: 'white',
          textDecoration: 'none',
          borderRadius: 6,
          fontSize: 14,
          fontWeight: 600
        }}>
          주문 내역 보기
        </Link>
      </div>
    </div>
  );
}

export default OrderCompletePage;

