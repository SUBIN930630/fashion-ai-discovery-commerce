import React from 'react';

export const AuthContext = React.createContext();

export function AuthProvider({ children }) {
  // 로컬스토리지 기반 세션 관리
  const [user, setUser] = React.useState(() => {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  });

  // 로컬스토리지 동기화 (마운트 시에만 실행)
  React.useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  const signIn = ({ email, password }) => {
    // 데모용 간단한 인증: users 리스트를 localStorage에 저장해서 사용
    const usersRaw = localStorage.getItem('local_users');
    const users = usersRaw ? JSON.parse(usersRaw) : [];
    const found = users.find(u => u.email === email && u.password === password);
    if (found) {
      const session = { id: found.id, email: found.email, name: found.name || found.email };
      setUser(session);
      return { success: true };
    }
    return { success: false, message: '이메일 또는 비밀번호가 일치하지 않습니다.' };
  };

  const signUp = ({ name, email, password }) => {
    const usersRaw = localStorage.getItem('local_users');
    const users = usersRaw ? JSON.parse(usersRaw) : [];
    if (users.find(u => u.email === email)) {
      return { success: false, message: '이미 등록된 이메일입니다.' };
    }
    const id = `user_${Date.now()}`;
    const newUser = { id, name, email, password };
    users.push(newUser);
    localStorage.setItem('local_users', JSON.stringify(users));
    setUser({ id, name, email });
    return { success: true };
  };

  const signOut = () => {
    setUser(null);
  };

  const updateProfile = (updates) => {
    setUser(prev => ({ ...prev, ...updates }));
    // update stored user in local users list
    const usersRaw = localStorage.getItem('local_users');
    const users = usersRaw ? JSON.parse(usersRaw) : [];
    const idx = users.findIndex(u => u.id === user?.id);
    if (idx !== -1) {
      users[idx] = { ...users[idx], ...updates };
      localStorage.setItem('local_users', JSON.stringify(users));
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthenticated: !!user, signIn, signUp, signOut, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
