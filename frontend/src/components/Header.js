import React from 'react';
import { useNavigate } from 'react-router-dom';

function Header({ onSearch, onLogin, onSignUp, onCart, onFavorites, onLogout, cartCount = 0, favCount = 0, user }) {
  const navigate = useNavigate();

  return (
    <header style={{
      backgroundColor: '#fff',
      borderBottom: '1px solid #eee',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: '700', cursor: 'pointer' }} onClick={() => navigate('/')}>
        Fashion AI
      </h1>
      {onSearch && <div>{onSearch}</div>}
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button onClick={onFavorites} style={{ position: 'relative', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>
          ❤️
          {favCount > 0 && <span style={{ marginLeft: 6 }}>{favCount}</span>}
        </button>

        <button onClick={onCart} style={{ position: 'relative', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>
          🛒
          {cartCount > 0 && <span style={{ marginLeft: 6 }}>{cartCount}</span>}
        </button>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {user ? (
            <>
              <span style={{ marginRight: 8, fontSize: 14 }}>{user.name || user.email}</span>
              <button onClick={() => navigate('/mypage')} style={{ padding: '0.5rem 1rem', cursor: 'pointer', background: '#667eea', color: 'white', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600 }}>마이페이지</button>
              <button onClick={onLogout} style={{ padding: '0.5rem 1rem', cursor: 'pointer', background: 'none', border: '1px solid #ddd', borderRadius: 4, fontSize: 14 }}>로그아웃</button>
            </>
          ) : (
            <>
              <button onClick={onSignUp} style={{ padding: '0.5rem 1rem', cursor: 'pointer', background: '#667eea', color: 'white', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600 }}>회원가입</button>
              <button onClick={onLogin} style={{ padding: '0.5rem 1rem', cursor: 'pointer', background: 'none', border: '1px solid #ddd', borderRadius: 4, fontSize: 14 }}>로그인</button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
