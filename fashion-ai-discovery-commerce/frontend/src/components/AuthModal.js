// 인증 모달 컴포넌트 - 로그인/회원가입
import React, { useState } from 'react';
import './AuthModal.css';
import { useAuth } from '../contexts/AuthContext';

/**
 * AuthModal 컴포넌트 - 로그인 및 회원가입 모달
 * 
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 * @param {string} initialMode - 초기 모드 ('login' 또는 'signup')
 */
function AuthModal({ isOpen, onClose, initialMode = 'login' }) {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState(initialMode); // 'login' 또는 'signup'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 모달이 열릴 때 초기화
  React.useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setFormData({ email: '', password: '', name: '' });
      setError('');
    }
  }, [isOpen, initialMode]);

  /**
   * 입력 필드 변경 핸들러
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // 에러 메시지 초기화
  };

  /**
   * 모드 전환 (로그인 ↔ 회원가입)
   */
  const toggleMode = () => {
    setMode(prev => prev === 'login' ? 'signup' : 'login');
    setFormData({ email: '', password: '', name: '' });
    setError('');
  };

  /**
   * 폼 제출 핸들러
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      let result;
      if (mode === 'login') {
        result = signIn(formData.email, formData.password);
      } else {
        result = signUp(formData.email, formData.password, formData.name);
      }

      if (result.success) {
        onClose(); // 모달 닫기
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('처리 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={onClose} aria-label="닫기">
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

        <div className="auth-modal-content">
          <h2 className="auth-modal-title">
            {mode === 'login' ? '로그인' : '회원가입'}
          </h2>

          <form onSubmit={handleSubmit} className="auth-form">
            {mode === 'signup' && (
              <div className="auth-form-group">
                <label htmlFor="name">이름</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="이름을 입력하세요"
                  required
                />
              </div>
            )}

            <div className="auth-form-group">
              <label htmlFor="email">{mode === 'login' ? '아이디' : '이메일'}</label>
              <input
                type="text"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder={mode === 'login' ? '아이디를 입력하세요' : '이메일을 입력하세요'}
                required
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="password">비밀번호</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder={mode === 'login' ? '비밀번호를 입력하세요' : '6자 이상 입력하세요'}
                required
                minLength={mode === 'signup' ? 6 : undefined}
              />
            </div>

            {error && <div className="auth-error">{error}</div>}

            <button
              type="submit"
              className="auth-submit-button"
              disabled={isLoading}
            >
              {isLoading ? '처리 중...' : mode === 'login' ? '로그인' : '회원가입'}
            </button>
          </form>

          <div className="auth-modal-footer">
            <span>
              {mode === 'login' ? '계정이 없으신가요? ' : '이미 계정이 있으신가요? '}
            </span>
            <button
              type="button"
              className="auth-toggle-button"
              onClick={toggleMode}
            >
              {mode === 'login' ? '회원가입' : '로그인'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthModal;

