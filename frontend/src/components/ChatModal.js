// 채팅 모달 컴포넌트
import React, { useState, useEffect, useRef } from 'react';
import './ChatModal.css';
import { chatService } from '../services/chatService';

/**
 * ChatModal 컴포넌트 - 모달 형태의 채팅 인터페이스
 * 플로팅 버튼을 클릭하면 열리는 작은 채팅 창
 * 
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 */
function ChatModal({ isOpen, onClose }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userId] = useState(`user_${Date.now()}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const modalRef = useRef(null);

  // 모달이 열릴 때 포커스 설정
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  // 메시지 목록이 변경될 때 스크롤을 맨 아래로 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 컴포넌트 마운트 시 환영 메시지 표시
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage = {
        role: 'assistant',
        content: '안녕하세요! 원하시는 패션 스타일이나 상품을 알려주세요. 추천해드리겠습니다. 😊',
        timestamp: new Date().toISOString()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen]);

  // 모달 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        // 플로팅 버튼 클릭은 제외
        if (!event.target.closest('.floating-chat-button')) {
          onClose();
        }
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen, onClose]);

  /**
   * 메시지 전송 핸들러
   */
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) {
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: inputMessage,
        session_id: sessionId,
        user_id: userId
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        recommendations: response.recommendations,
        intent: response.intent,
        confidence: response.confidence,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: '죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  /**
   * Enter 키 핸들러
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="chat-modal-overlay">
      <div className="chat-modal" ref={modalRef}>
        <div className="chat-modal-header">
          <div className="chat-modal-header-content">
            <h3>패션 추천 챗봇</h3>
            <p>원하시는 스타일을 알려주세요</p>
          </div>
          <button
            className="chat-modal-close"
            onClick={onClose}
            aria-label="채팅 닫기"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M15 5L5 15M5 5L15 15"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <div className="chat-modal-messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message ${message.role} ${message.isError ? 'error' : ''}`}
            >
              <div className="chat-message-content">
                <p>{message.content}</p>
                {message.recommendations && message.recommendations.length > 0 && (
                  <div className="chat-recommendations">
                    <p className="chat-recommendations-title">추천 상품:</p>
                    <ul>
                      {message.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec.name || rec.product_id}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant loading">
              <div className="chat-message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-modal-input-container">
          <textarea
            ref={inputRef}
            className="chat-modal-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="chat-modal-send-button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatModal;

