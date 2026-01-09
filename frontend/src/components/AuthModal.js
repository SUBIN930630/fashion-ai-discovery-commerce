import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

function AuthModal({ isOpen, onClose, initialMode = 'login' }) {
  const { signIn, signUp, user, signOut } = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState(null);

  // initialMode가 변경되면 모드 업데이트
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setError(null);
      setForm({ name: '', email: '', password: '' });
    }
  }, [initialMode, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleLogin = async (e) => {
    e.preventDefault();
    const res = await signIn({ email: form.email, password: form.password });
    if (!res.success) setError(res.message);
    else onClose();
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    const res = await signUp({ name: form.name, email: form.email, password: form.password });
    if (!res.success) setError(res.message);
    else onClose();
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1200 }}>
      <div style={{ width: 360, background: 'white', padding: 20, borderRadius: 8 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <button onClick={() => setMode('login')} style={{ flex: 1, padding: 8, background: mode === 'login' ? '#333' : '#f3f3f3', color: mode === 'login' ? 'white' : 'black' }}>로그인</button>
          <button onClick={() => setMode('signup')} style={{ flex: 1, padding: 8, background: mode === 'signup' ? '#333' : '#f3f3f3', color: mode === 'signup' ? 'white' : 'black' }}>회원가입</button>
        </div>

        {user ? (
          <div>
            <p>로그인됨: {user.name || user.email}</p>
            <button onClick={() => { signOut(); onClose(); }} style={{ padding: 8, background: '#e53e3e', color: 'white', border: 'none', borderRadius: 4 }}>로그아웃</button>
          </div>
        ) : (
          <form onSubmit={mode === 'login' ? handleLogin : handleSignup}>
            {mode === 'signup' && (
              <div style={{ marginBottom: 8 }}>
                <input name="name" value={form.name} onChange={handleChange} placeholder="이름" style={{ width: '100%', padding: 8 }} />
              </div>
            )}
            <div style={{ marginBottom: 8 }}>
              <input name="email" value={form.email} onChange={handleChange} placeholder="이메일" style={{ width: '100%', padding: 8 }} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <input name="password" value={form.password} onChange={handleChange} placeholder="비밀번호" type="password" style={{ width: '100%', padding: 8 }} />
            </div>
            {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit" style={{ flex: 1, padding: 8, background: '#2d3748', color: 'white', border: 'none', borderRadius: 4 }}>{mode === 'login' ? '로그인' : '회원가입'}</button>
              <button type="button" onClick={onClose} style={{ padding: 8 }}>닫기</button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default AuthModal;
