import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

function CheckoutPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { cartItems, totalPrice, clearCart } = useCart();
  const location = useLocation();
  const [form, setForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    address: '',
    detailAddress: '',
    zipcode: '',
    payment: 'card'
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (cartItems.length === 0) {
      navigate('/');
    }
  }, [cartItems.length, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = '이름을 입력해주세요';
    if (!form.phone.trim()) newErrors.phone = '휴대폰 번호를 입력해주세요';
    if (!form.address.trim()) newErrors.address = '주소를 입력해주세요';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const ordersRaw = localStorage.getItem('orders');
      const orders = ordersRaw ? JSON.parse(ordersRaw) : [];
      const orderId = `order_${Date.now()}`;
      const order = {
        id: orderId,
        items: cartItems,
        total: totalPrice,
        customer: {
          name: form.name,
          email: form.email,
          phone: form.phone,
          address: form.address,
          detailAddress: form.detailAddress,
          zipcode: form.zipcode
        },
        payment: form.payment,
        status: '주문 완료',
        created_at: new Date().toISOString()
      };
      orders.push(order);
      localStorage.setItem('orders', JSON.stringify(orders));
      clearCart();
      navigate(`/order-complete/${orderId}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ marginBottom: 30 }}>주문/결제</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 30 }}>
        {/* 주문 정보 입력 폼 */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* 배송 정보 */}
          <section style={{ border: '1px solid #eee', padding: 20, borderRadius: 8 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>배송 정보</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: 14 }}>
                  이름 <span style={{ color: 'red' }}>*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="수취인 이름"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: errors.name ? '1px solid red' : '1px solid #ddd',
                    borderRadius: 4,
                    fontSize: 14,
                    boxSizing: 'border-box'
                  }}
                />
                {errors.name && <span style={{ color: 'red', fontSize: 12, marginTop: 4 }}>{errors.name}</span>}
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: 14 }}>
                  휴대폰 번호 <span style={{ color: 'red' }}>*</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  placeholder="010-1234-5678"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: errors.phone ? '1px solid red' : '1px solid #ddd',
                    borderRadius: 4,
                    fontSize: 14,
                    boxSizing: 'border-box'
                  }}
                />
                {errors.phone && <span style={{ color: 'red', fontSize: 12, marginTop: 4 }}>{errors.phone}</span>}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ display: 'block', marginBottom: 8, fontSize: 14 }}>
                    주소 <span style={{ color: 'red' }}>*</span>
                  </label>
                  <input
                    type="text"
                    name="address"
                    value={form.address}
                    onChange={handleChange}
                    placeholder="시/도 구/군 동/읍"
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: errors.address ? '1px solid red' : '1px solid #ddd',
                      borderRadius: 4,
                      fontSize: 14,
                      boxSizing: 'border-box'
                    }}
                  />
                  {errors.address && <span style={{ color: 'red', fontSize: 12, marginTop: 4 }}>{errors.address}</span>}
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: 8, fontSize: 14 }}>우편번호</label>
                  <input
                    type="text"
                    name="zipcode"
                    value={form.zipcode}
                    onChange={handleChange}
                    placeholder="12345"
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: 4,
                      fontSize: 14,
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: 14 }}>상세주소</label>
                <input
                  type="text"
                  name="detailAddress"
                  value={form.detailAddress}
                  onChange={handleChange}
                  placeholder="아파트/호수 등"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: 4,
                    fontSize: 14,
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>
          </section>

          {/* 결제 정보 */}
          <section style={{ border: '1px solid #eee', padding: 20, borderRadius: 8 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>결제 방법</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { value: 'card', label: '💳 신용카드' },
                { value: 'bank', label: '🏦 무통장입금' },
                { value: 'kakao', label: '☕ 카카오페이' }
              ].map(method => (
                <label key={method.value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="payment"
                    value={method.value}
                    checked={form.payment === method.value}
                    onChange={handleChange}
                    style={{ marginRight: 10 }}
                  />
                  <span>{method.label}</span>
                </label>
              ))}
            </div>
          </section>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              padding: '16px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              fontSize: 16,
              fontWeight: 600,
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.6 : 1
            }}
          >
            {isSubmitting ? '처리 중...' : `${new Intl.NumberFormat('ko-KR').format(totalPrice)}원 결제하기`}
          </button>
        </form>

        {/* 주문 요약 */}
        <div style={{ position: 'sticky', top: 20, height: 'fit-content' }}>
          <section style={{ border: '1px solid #eee', padding: 20, borderRadius: 8 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>주문 요약</h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 20 }}>
              {cartItems.map(item => (
                <div key={item.product_id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}>
                  <span>{item.name} x{item.quantity}</span>
                  <span>{new Intl.NumberFormat('ko-KR').format(item.price * item.quantity)}원</span>
                </div>
              ))}
            </div>

            <div style={{ borderTop: '1px solid #eee', borderBottom: '1px solid #eee', padding: '12px 0', marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, marginBottom: 8 }}>
                <span>소계</span>
                <span>{new Intl.NumberFormat('ko-KR').format(totalPrice)}원</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, marginBottom: 8 }}>
                <span>배송료</span>
                <span>무료</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18, fontWeight: 600 }}>
              <span>총 결제액</span>
              <span>{new Intl.NumberFormat('ko-KR').format(totalPrice)}원</span>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default CheckoutPage;

