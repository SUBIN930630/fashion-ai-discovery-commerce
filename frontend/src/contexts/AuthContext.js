// 인증 컨텍스트 - 사용자 인증 상태 관리
import React, { createContext, useState, useContext, useEffect } from 'react';

/**
 * AuthContext - 사용자 인증 정보를 관리하는 컨텍스트
 */
const AuthContext = createContext(null);

// 데모 모드 플래그 (기본값: true)
const isDemoMode = process.env.REACT_APP_DEMO_MODE !== 'false';

/**
 * 테스트 계정 초기화 함수
 * 로컬 스토리지에 테스트 계정들을 생성합니다.
 */
const initializeTestAccounts = () => {
  const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
  
  // 이미 초기화되었는지 확인
  const isInitialized = localStorage.getItem('test_accounts_initialized');
  
  if (isInitialized) {
    return; // 이미 초기화됨
  }

  // 테스트 계정 10개 생성 (demo01 ~ demo10)
  const testAccounts = [];
  for (let i = 1; i <= 10; i++) {
    const num = String(i).padStart(2, '0'); // 01, 02, ..., 10
    const email = `demo${num}`;
    const name = `테스트 사용자 ${num}`;
    
    // 이미 존재하는 계정이 아닌 경우만 추가
    if (!existingUsers.find(u => u.email === email)) {
      testAccounts.push({
        id: `user_demo_${num}`,
        email: email,
        password: email, // 비밀번호도 demo01, demo02 등
        name: name,
        role: 'user', // 일반 사용자 역할
        createdAt: new Date().toISOString()
      });
    }
  }

  // 기존 사용자 목록에 테스트 계정 추가
  if (testAccounts.length > 0) {
    const updatedUsers = [...existingUsers, ...testAccounts];
    localStorage.setItem('users', JSON.stringify(updatedUsers));
  }

  // 초기화 완료 표시
  localStorage.setItem('test_accounts_initialized', 'true');
};

/**
 * 관리자 계정 초기화 함수
 * 로컬 스토리지에 관리자 계정들을 생성합니다.
 */
const initializeAdminAccounts = () => {
  const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
  
  // 이미 초기화되었는지 확인
  const isAdminInitialized = localStorage.getItem('admin_accounts_initialized');
  
  if (isAdminInitialized) {
    return; // 이미 초기화됨
  }

  // 관리자 계정 10개 생성 (admin01 ~ admin10)
  const adminAccounts = [];
  for (let i = 1; i <= 10; i++) {
    const num = String(i).padStart(2, '0'); // 01, 02, ..., 10
    const email = `admin${num}`;
    const name = `관리자 ${num}`;
    
    // 이미 존재하는 계정이 아닌 경우만 추가
    if (!existingUsers.find(u => u.email === email)) {
      adminAccounts.push({
        id: `admin_${num}`,
        email: email,
        password: email, // 비밀번호도 admin01, admin02 등
        name: name,
        role: 'admin', // 관리자 역할
        createdAt: new Date().toISOString()
      });
    }
  }

  // 기존 사용자 목록에 관리자 계정 추가
  if (adminAccounts.length > 0) {
    const updatedUsers = [...existingUsers, ...adminAccounts];
    localStorage.setItem('users', JSON.stringify(updatedUsers));
  }

  // 초기화 완료 표시
  localStorage.setItem('admin_accounts_initialized', 'true');
};

/**
 * AuthProvider - 인증 컨텍스트 제공자 컴포넌트
 * 로그인, 로그아웃, 회원가입 기능을 제공합니다.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // 컴포넌트 마운트 시 테스트 계정 및 관리자 계정 초기화 및 사용자 정보 로드
  useEffect(() => {
    if (isDemoMode) {
      // 테스트 계정 초기화
      initializeTestAccounts();
      
      // 관리자 계정 초기화
      initializeAdminAccounts();
    }

    // 로컬 스토리지에서 사용자 정보 로드
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('사용자 정보 로드 오류:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  /**
   * 회원가입 함수
   * 
   * @param {string} email - 이메일
   * @param {string} password - 비밀번호
   * @param {string} name - 이름
   * @returns {Object} 성공 여부 및 메시지
   */
  const signUp = (email, password, name) => {
    try {
      // 간단한 유효성 검사
      if (!email || !password || !name) {
        return { success: false, message: '모든 필드를 입력해주세요.' };
      }

      if (password.length < 6) {
        return { success: false, message: '비밀번호는 6자 이상이어야 합니다.' };
      }

      // 기존 사용자 확인 (로컬 스토리지에서)
      const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
      if (existingUsers.find(u => u.email === email)) {
        return { success: false, message: '이미 등록된 이메일입니다.' };
      }

      // 새 사용자 생성
      const newUser = {
        id: `user_${Date.now()}`,
        email,
        name,
        role: 'user', // 기본 역할은 일반 사용자
        createdAt: new Date().toISOString()
      };

      // 사용자 목록에 추가
      existingUsers.push({
        ...newUser,
        password // 실제로는 해시화해야 하지만, 데모용으로 평문 저장
      });
      localStorage.setItem('users', JSON.stringify(existingUsers));

      // 로그인 상태로 설정
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));

      return { success: true, message: '회원가입이 완료되었습니다.' };
    } catch (error) {
      console.error('회원가입 오류:', error);
      return { success: false, message: '회원가입 중 오류가 발생했습니다.' };
    }
  };

  /**
   * 로그인 함수
   * 
   * @param {string} email - 이메일
   * @param {string} password - 비밀번호
   * @returns {Object} 성공 여부 및 메시지
   */
  const signIn = (email, password) => {
    try {
      if (!email || !password) {
        return { success: false, message: '이메일과 비밀번호를 입력해주세요.' };
      }

      // 사용자 목록에서 찾기
      const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
      const foundUser = existingUsers.find(
        u => u.email === email && u.password === password
      );

      if (!foundUser) {
        return { success: false, message: '이메일 또는 비밀번호가 일치하지 않습니다.' };
      }

      // 로그인 성공
      const userData = {
        id: foundUser.id,
        email: foundUser.email,
        name: foundUser.name,
        role: foundUser.role || 'user', // 역할 정보 포함 (없으면 기본값 'user')
        createdAt: foundUser.createdAt
      };

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));

      return { success: true, message: '로그인되었습니다.' };
    } catch (error) {
      console.error('로그인 오류:', error);
      return { success: false, message: '로그인 중 오류가 발생했습니다.' };
    }
  };

  /**
   * 로그아웃 함수
   */
  const signOut = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    isLoading,
    signUp,
    signIn,
    signOut,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin' // 관리자 여부 확인
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * useAuth - 인증 컨텍스트를 사용하는 훅
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
