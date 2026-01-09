import React from 'react';

function FloatingChatButton({ onClick, isOpen }) {
  return (
    <button
      onClick={onClick}
      className="floating-chat-button"
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        backgroundColor: '#667eea',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
        fontSize: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        zIndex: 100,
        transition: 'transform 0.2s'
      }}
      title="채팅"
    >
      💬
    </button>
  );
}

export default FloatingChatButton;
