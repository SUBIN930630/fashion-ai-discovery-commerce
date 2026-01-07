// src/components/ChatModal.js
import React, { useState } from 'react';
import './ChatModal.css';

const ChatModal = ({ isOpen, onClose }) => {
  const [message, setMessage] = useState('');

  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay">
      <div className="chat-window">
        <div className="chat-header">
          <span className="chat-title">🤖 AI 스타일리스트</span>
          <button className="close-btn" onClick={onClose}>✖</button>
        </div>
        <div className="chat-messages">
          <div className="message ai-message">
            안녕하세요! 오늘 어떤 스타일을 찾으시나요? 👋
          </div>
        </div>
        <div className="chat-input-area">
          <input 
            type="text" 
            placeholder="예: 요즘 유행하는 후드티 추천해줘"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button className="send-btn">전송</button>
        </div>
      </div>
    </div>
  );
};

export default ChatModal;