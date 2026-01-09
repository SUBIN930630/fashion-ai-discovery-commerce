import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { dummyProducts } from '../data/dummyProducts';

function MyPage() {
  const navigate = useNavigate();
  const { user, updateProfile, signOut } = useAuth();
  const [orders, setOrders] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: user?.name || '', email: user?.email || '' });
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }

    // 주문 내역 로드
    const ordersRaw = localStorage.getItem('orders');
    setOrders(ordersRaw ? JSON.parse(ordersRaw) : []);

    // 좋아요 목록 로드
    const favRaw = localStorage.getItem('favorites');
    const favIds = favRaw ? JSON.parse(favRaw) : [];
    const favProducts = favIds.map(id => dummyProducts.find(p => p.product_id === id)).filter(Boolean);
    setFavorites(favProducts);
  }, [user, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (form.name.trim()) {
      updateProfile({ name: form.name });
      setEditing(false);
    }
  };

  const handleLogout = () => {
    signOut();
    navigate('/');
  };

  if (!user) {
    return (
      <div style={{ padding: 20, textAlign: 'center' }}>
        <p>로그인이 필요합니다.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ marginBottom: 30 }}>마이페이지</h1>

      {/* 탭 네비게이션 */}
      <div style={{ display: 'flex', gap: 20, marginBottom: 30, borderBottom: '2px solid #eee' }}>
        {[
          { id: 'profile', label: '프로필' },
          { id: 'orders', label: '주문 내역' },
          { id: 'favorites', label: '좋아요 목록' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 20px',
              background: 'none',
              border: 'none',
              fontSize: 16,
              fontWeight: 600,
              cursor: 'pointer',
              color: activeTab === tab.id ? '#667eea' : '#999',
              borderBottom: activeTab === tab.id ? '2px solid #667eea' : 'none',
              marginBottom: -2
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 프로필 탭 */}
      {activeTab === 'profile' && (
        <section style={{ maxWidth: 600 }}>
          <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 30 }}>
            {editing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', marginBottom: 8, fontSize: 14, fontWeight: 600 }}>이름</label>
                  <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
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

                <div>
                  <label style={{ display: 'block', marginBottom: 8, fontSize: 14, fontWeight: 600 }}>이메일</label>
                  <input
                    type="email"
                    value={form.email}
                    disabled
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: 4,
                      fontSize: 14,
                      boxSizing: 'border-box',
                      background: '#f9f9f9',
                      cursor: 'not-allowed'
                    }}
                  />
                  <p style={{ fontSize: 12, color: '#999', marginTop: 6 }}>이메일은 변경할 수 없습니다.</p>
                </div>

                <div style={{ display: 'flex', gap: 10 }}>
                  <button
                    onClick={handleSave}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    저장
                  </button>
                  <button
                    onClick={() => {
                      setEditing(false);
                      setForm({ name: user.name || '', email: user.email || '' });
                    }}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#eee',
                      color: '#333',
                      border: 'none',
                      borderRadius: 4,
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    취소
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>이름</p>
                  <p style={{ fontSize: 16, fontWeight: 600 }}>{user.name || '-'}</p>
                </div>

                <div>
                  <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>이메일</p>
                  <p style={{ fontSize: 14 }}>{user.email}</p>
                </div>

                <div style={{ display: 'flex', gap: 10, paddingTop: 16, borderTop: '1px solid #eee' }}>
                  <button
                    onClick={() => setEditing(true)}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    프로필 수정
                  </button>
                  <button
                    onClick={handleLogout}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#ff6b6b',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    로그아웃
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 주문 내역 탭 */}
      {activeTab === 'orders' && (
        <section>
          {orders.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, background: '#f9f9f9', borderRadius: 8 }}>
              <p style={{ fontSize: 16, color: '#999', marginBottom: 16 }}>주문 내역이 없습니다.</p>
              <button
                onClick={() => navigate('/')}
                style={{
                  padding: '10px 20px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: 4,
                  cursor: 'pointer'
                }}
              >
                상품 둘러보기
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {orders.map((order, idx) => (
                <div key={order.id} style={{ border: '1px solid #eee', borderRadius: 8, padding: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <div>
                      <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 번호</p>
                      <p style={{ fontSize: 14, fontWeight: 600, fontFamily: 'monospace' }}>{order.id}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 날짜</p>
                      <p style={{ fontSize: 14 }}>{new Date(order.created_at).toLocaleDateString('ko-KR')}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>주문 상태</p>
                      <p style={{ fontSize: 14, fontWeight: 600, color: '#667eea' }}>✓ {order.status || '완료'}</p>
                    </div>
                  </div>

                  <div style={{ background: '#f9f9f9', padding: 12, borderRadius: 4, marginBottom: 16 }}>
                    {order.items.map((item, itemIdx) => (
                      <div key={itemIdx} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
                        <span>{item.name} x{item.quantity}</span>
                        <span>{new Intl.NumberFormat('ko-KR').format(item.price * item.quantity)}원</span>
                      </div>
                    ))}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 16, borderTop: '1px solid #eee' }}>
                    <div>
                      <p style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>총 결제액</p>
                      <p style={{ fontSize: 18, fontWeight: 700 }}>{new Intl.NumberFormat('ko-KR').format(order.total)}원</p>
                    </div>
                    <button
                      onClick={() => navigate(`/order-complete/${order.id}`)}
                      style={{
                        padding: '8px 16px',
                        background: '#333',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        cursor: 'pointer',
                        fontSize: 14
                      }}
                    >
                      상세보기
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* 좋아요 목록 탭 */}
      {activeTab === 'favorites' && (
        <section>
          {favorites.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, background: '#f9f9f9', borderRadius: 8 }}>
              <p style={{ fontSize: 16, color: '#999', marginBottom: 16 }}>찜한 상품이 없습니다.</p>
              <button
                onClick={() => navigate('/')}
                style={{
                  padding: '10px 20px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: 4,
                  cursor: 'pointer'
                }}
              >
                상품 둘러보기
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 20 }}>
              {favorites.map(product => (
                <div
                  key={product.product_id}
                  onClick={() => navigate(`/product/${product.product_id}`)}
                  style={{
                    border: '1px solid #eee',
                    borderRadius: 8,
                    overflow: 'hidden',
                    cursor: 'pointer',
                    transition: 'box-shadow 0.2s',
                    boxShadow: '0 0 0 1px #eee'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 0 0 1px #eee'}
                >
                  <div style={{ height: 200, background: '#f0f0f0', overflow: 'hidden' }}>
                    <img
                      src={product.image_url}
                      alt={product.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                      }}
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/200x200?text=No+Image';
                      }}
                    />
                  </div>
                  <div style={{ padding: 12 }}>
                    <p style={{ fontSize: 12, color: '#999' }}>{product.brand}</p>
                    <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>{product.name}</p>
                    <p style={{ fontSize: 16, fontWeight: 700, color: '#333' }}>
                      {new Intl.NumberFormat('ko-KR').format(product.price)}원
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default MyPage;
