// 채팅 모달 컴포넌트
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './ChatModal.css';
import { chatService } from '../services/chatService';
import { recommendationService } from '../services/recommendationService';
import { useAuth } from '../contexts/AuthContext';

/**
 * ChatModal 컴포넌트 - 모달 형태의 채팅 인터페이스
 * 플로팅 버튼을 클릭하면 열리는 작은 채팅 창
 * 
 * @param {boolean} isOpen - 모달이 열려있는지 여부
 * @param {Function} onClose - 모달 닫기 핸들러
 */
function ChatModal({ isOpen, onClose }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false); // 확대/축소 상태
  const [guestUserId] = useState(() => {
    const storageKey = 'guest_user_id';
    try {
      const savedId = localStorage.getItem(storageKey);
      if (savedId) {
        return savedId;
      }
      const newId = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      localStorage.setItem(storageKey, newId);
      return newId;
    } catch (error) {
      return `guest_${Date.now()}`;
    }
  });
  const userId = user?.id || guestUserId;
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const modalRef = useRef(null);

  // 모달이 열릴 때 포커스 설정 및 확대 상태 초기화
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    } else {
      // 모달이 닫힐 때 확대 상태 초기화
      setIsExpanded(false);
    }
  }, [isOpen]);

  // 메시지 목록이 변경될 때 스크롤을 맨 아래로 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 입력창 높이 자동 조절
  useEffect(() => {
    if (inputRef.current) {
      // 높이를 초기화하여 정확한 scrollHeight 계산
      inputRef.current.style.height = 'auto';
      // scrollHeight에 맞춰 높이 조절 (최소 1줄, 최대 6줄)
      const maxHeight = 150; // 약 6줄 (25px * 6)
      const minHeight = 25; // 약 1줄
      const newHeight = Math.min(Math.max(inputRef.current.scrollHeight, minHeight), maxHeight);
      inputRef.current.style.height = `${newHeight}px`;
    }
  }, [inputMessage]);

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

      // 대화 내역을 로컬 스토리지에 저장
      if (user?.id) {
        const chatHistory = JSON.parse(localStorage.getItem(`chat_history_${user.id}`) || '[]');
        chatHistory.push({
          session_id: response.session_id || sessionId || `session_${Date.now()}`,
          user_message: userMessage,
          assistant_message: assistantMessage,
          timestamp: new Date().toISOString()
        });
        localStorage.setItem(`chat_history_${user.id}`, JSON.stringify(chatHistory));
      }
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

  /**
   * 확대/축소 토글 핸들러
   */
  const toggleExpand = (e) => {
    e.stopPropagation(); // 이벤트 전파 방지
    e.preventDefault(); // 기본 동작 방지
    setIsExpanded(prev => !prev);
  };

  return (
    <div className="chat-modal-overlay">
      <div className={`chat-modal ${isExpanded ? 'expanded' : ''}`} ref={modalRef}>
        <div className="chat-modal-header">
          <div className="chat-modal-header-content">
            <h3>AI 스타일리스트 💬</h3>
          </div>
          <div className="chat-modal-header-actions">
            {/* 확대/축소 버튼 */}
            <button
              className="chat-modal-expand"
              onClick={toggleExpand}
              aria-label={isExpanded ? '축소' : '확대'}
              title={isExpanded ? '축소' : '확대'}
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect
                  x="4"
                  y="4"
                  width="12"
                  height="12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            {/* 닫기 버튼 */}
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
                    <ul className="chat-recommendations-list">
                      {message.recommendations.map((rec, idx) => (
                        <li key={idx} className="chat-recommendation-item">
                          <button
                            className="chat-recommendation-link"
                            onClick={() => {
                              if (rec.product_url) {
                                // 클릭 로그 전송 (문서 규칙: 클릭 안 한 상품 제외를 위한 로그 수집)
                                const userId = user?.id || guestUserId;
                                if (rec.id || rec.product_id) {
                                  recommendationService.recordClick(
                                    userId,
                                    rec.id || rec.product_id
                                  );
                                }
                                
                                navigate(rec.product_url);
                                onClose(); // 챗봇 모달 닫기
                              }
                            }}
                          >
                            <span className="chat-recommendation-name">
                              {rec.name || rec.product_id}
                            </span>
                            {rec.brand && (
                              <span className="chat-recommendation-brand">
                                {rec.brand}
                              </span>
                            )}
                            {rec.price && (
                              <span className="chat-recommendation-price">
                                {new Intl.NumberFormat('ko-KR').format(rec.price)}원
                              </span>
                            )}
                          </button>
                        </li>
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
            style={{
              resize: 'none',
              overflow: 'hidden',
              minHeight: '25px',
              maxHeight: '150px'
            }}
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
