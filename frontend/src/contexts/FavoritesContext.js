// src/contexts/FavoritesContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';

const FavoritesContext = createContext();

export const FavoritesProvider = ({ children }) => {
  // 1. 저장된 좋아요 목록 불러오기 (없으면 빈 배열)
  const [favorites, setFavorites] = useState(() => {
    const localData = localStorage.getItem('favorites');
    return localData ? JSON.parse(localData) : [];
  });

  // 2. 목록이 바뀔 때마다 컴퓨터(LocalStorage)에 저장
  useEffect(() => {
    localStorage.setItem('favorites', JSON.stringify(favorites));
  }, [favorites]);

  // 3. 좋아요 토글 (이미 있으면 삭제, 없으면 추가)
  const toggleFavorite = (product) => {
    setFavorites(prev => {
      const exists = prev.find(item => item.product_id === product.product_id);
      if (exists) {
        return prev.filter(item => item.product_id !== product.product_id); // 삭제
      }
      return [...prev, product]; // 추가
    });
  };

  // 4. 이 상품을 내가 좋아요 했는지 확인
  const isFavorite = (productId) => {
    return favorites.some(item => item.product_id === productId);
  };

  return (
    <FavoritesContext.Provider value={{ favorites, toggleFavorite, isFavorite }}>
      {children}
    </FavoritesContext.Provider>
  );
};

export const useFavorites = () => useContext(FavoritesContext);