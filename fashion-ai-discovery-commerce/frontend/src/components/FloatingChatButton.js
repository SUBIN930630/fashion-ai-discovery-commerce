// 플로팅 챗봇 버튼 컴포넌트
import React from 'react';
import './FloatingChatButton.css';

/**
 * FloatingChatButton 컴포넌트 - 우측 하단에 고정된 플로팅 챗봇 버튼
 * 
 * @param {Function} onClick - 버튼 클릭 핸들러
 * @param {boolean} isOpen - 챗봇 창이 열려있는지 여부
 */
function FloatingChatButton({ onClick, isOpen }) {
  return (
    <button
      className={`floating-chat-button ${isOpen ? 'active' : ''}`}
      onClick={onClick}
      aria-label="챗봇 열기"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="chat-icon"
      >
        {isOpen ? (
          // 닫기 아이콘 (X)
          <path
            d="M18 6L6 18M6 6L18 18"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ) : (
          // 채팅 아이콘
          <path
            d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
      </svg>
      {!isOpen && <span className="notification-badge"></span>}
    </button>
  );
}

export default FloatingChatButton;

