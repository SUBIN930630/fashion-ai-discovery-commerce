// 좋아요 컨텍스트 - 사용자의 좋아요한 상품 관리
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { favoriteService } from '../services/favoriteService';

const FavoritesContext = createContext(null);

/**
 * FavoritesProvider - 좋아요 컨텍스트 제공자
 * 사용자가 좋아요한 상품 목록을 관리합니다.
 */
export function FavoritesProvider({ children }) {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);

  // 사용자 변경 시 좋아요 목록 로드
  useEffect(() => {
    if (user) {
      const savedFavorites = localStorage.getItem(`favorites_${user.id}`);
      if (savedFavorites) {
        try {
          setFavorites(JSON.parse(savedFavorites));
        } catch (error) {
          console.error('좋아요 목록 로드 오류:', error);
        }
      }
    } else {
      setFavorites([]);
    }
  }, [user]);

  /**
   * 좋아요 목록 저장
   */
  useEffect(() => {
    if (user && favorites.length >= 0) {
      localStorage.setItem(`favorites_${user.id}`, JSON.stringify(favorites));
    }
  }, [favorites, user]);

  /**
   * 좋아요 토글
   * 
   * @param {string} productId - 상품 ID
   */
  const toggleFavorite = async (productId) => {
    if (!user) {
      return { success: false, message: '로그인이 필요합니다.' };
    }

    try {
      // 로컬 스토리지 업데이트
      const newFavorites = favorites.includes(productId)
        ? favorites.filter(id => id !== productId)
        : [...favorites, productId];
      
      setFavorites(newFavorites);

      // 백엔드 API 호출 (비동기, 에러가 나도 로컬 상태는 유지)
      favoriteService.toggleFavorite(user.id, productId)
        .catch(error => {
          console.error('좋아요 API 저장 오류:', error);
          // 에러 발생 시 롤백하지 않음 (로컬 스토리지 우선)
        });

      return { success: true };
    } catch (error) {
      console.error('좋아요 토글 오류:', error);
      return { success: false, message: '좋아요 처리 중 오류가 발생했습니다.' };
    }
  };

  /**
   * 상품이 좋아요 목록에 있는지 확인
   * 
   * @param {string} productId - 상품 ID
   * @returns {boolean} 좋아요 여부
   */
  const isFavorite = (productId) => {
    return favorites.includes(productId);
  };

  const value = {
    favorites,
    toggleFavorite,
    isFavorite,
    favoritesCount: favorites.length
  };

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
}

/**
 * useFavorites - 좋아요 컨텍스트를 사용하는 훅
 */
export function useFavorites() {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
}

