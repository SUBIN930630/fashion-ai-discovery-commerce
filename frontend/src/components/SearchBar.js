// 상품 검색 바 컴포넌트
import React, { useState } from 'react';
import './SearchBar.css';

/**
 * SearchBar 컴포넌트 - 상품 검색 기능을 제공하는 검색 바
 * 
 * @param {Function} onSearch - 검색 실행 핸들러 (검색어를 인자로 받음)
 * @param {string} placeholder - 검색 바 플레이스홀더 텍스트
 */
function SearchBar({ onSearch, placeholder = '상품명, 브랜드, 스타일로 검색...' }) {
  const [searchQuery, setSearchQuery] = useState('');

  /**
   * 검색어 변경 핸들러
   */
  const handleChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    // 실시간 검색 (입력할 때마다 검색 실행)
    if (onSearch) {
      onSearch(value);
    }
  };

  /**
   * 검색 실행 핸들러 (Enter 키 또는 검색 버튼 클릭)
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    }
  };

  /**
   * 검색어 초기화 핸들러
   */
  const handleClear = () => {
    setSearchQuery('');
    if (onSearch) {
      onSearch('');
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-bar-container">
        <svg
          className="search-icon"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M9 17C13.4183 17 17 13.4183 17 9C17 4.58172 13.4183 1 9 1C4.58172 1 1 4.58172 1 9C1 13.4183 4.58172 17 9 17Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M19 19L14.65 14.65"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <input
          type="text"
          className="search-input"
          value={searchQuery}
          onChange={handleChange}
          placeholder={placeholder}
          aria-label="상품 검색"
        />
        {searchQuery && (
          <button
            type="button"
            className="search-clear-button"
            onClick={handleClear}
            aria-label="검색어 지우기"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M12 4L4 12M4 4L12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        )}
        <button
          type="submit"
          className="search-submit-button"
          aria-label="검색"
        >
          검색
        </button>
      </div>
    </form>
  );
}

export default SearchBar;

