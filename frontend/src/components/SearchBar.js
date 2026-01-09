import React from 'react';

function SearchBar({ onSearch }) {
  return (
    <input
      type="text"
      placeholder="상품명, 브랜드로 검색..."
      onChange={(e) => onSearch && onSearch(e.target.value)}
      style={{
        padding: '0.5rem 1rem',
        border: '1px solid #ddd',
        borderRadius: '4px',
        width: '300px'
      }}
    />
  );
}

export default SearchBar;
