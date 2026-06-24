import React from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatScreen.css';

const ChatScreen = ({
  isSidebarOpen,
  setIsSidebarOpen,
  handleNewChat,
  sessions,
  activeSessionId,
  setActiveSessionId,
  setCurrentView,
  isLoggedIn,
  handleLogout,
  activeSession,
  userInfo,
  messagesEndRef,
  inputValue,
  setInputValue,
  handleSendMessage
}) => {
  return (
    <div className="gpt-chat-screen">
      {/* Sidebar */}
      <div className={`gpt-sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={handleNewChat}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
              <path d="M12 4V20M4 12H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Trò chuyện mới
          </button>
          <button className="icon-btn hide-sidebar-btn" onClick={() => setIsSidebarOpen(false)} title="Ẩn menu">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        <div className="sidebar-history">
          <div className="history-label">Gần đây</div>
          {sessions.map(session => (
            <button
              key={session.id}
              className={`history-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => setActiveSessionId(session.id)}
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="history-title">{session.title}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <button className="back-home-btn" onClick={() => { window.scrollTo(0, 0); setCurrentView('home'); }} style={{ marginBottom: '0.5rem' }}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M9 22V12h6v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Về trang chủ
          </button>
          {isLoggedIn && (
            <button className="back-home-btn" onClick={handleLogout} style={{ color: '#e11d48' }}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Đăng xuất
            </button>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="gpt-main-area">
        {!isSidebarOpen && (
          <button className="show-sidebar-btn" onClick={() => setIsSidebarOpen(true)}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
              <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        )}

        <div className="gpt-messages-container">
          {activeSession.messages.map((msg, index) => (
            <div key={msg.id} className={`gpt-message-row ${msg.sender}`}>
              <div className="gpt-message-content">
                <div className="gpt-avatar">
                  {msg.sender === 'bot' ? '✨' : ''}
                </div>
                <div className="gpt-message-text">
                  <div className="gpt-sender-name">
                    {msg.sender === 'bot' ? 'ViMind' : (userInfo.fullName || userInfo.username || 'Bạn')}
                  </div>
                  {msg.isLoading ? (
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  ) : (
                    <div className="markdown-content">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} className="messages-bottom-spacer" />
        </div>

        <div className={`gpt-input-area-wrapper ${activeSession.messages.length === 0 ? 'centered' : ''}`}>
          {activeSession.messages.length === 0 && (
            <>
              <div className="gemini-greeting">
                Xin chào, <span className="greeting-gradient">tôi có thể giúp gì?</span>
              </div>
              <div className="suggestions-grid">
                <div className="suggestion-card" onClick={() => { setInputValue('Tôi đang cảm thấy áp lực và mệt mỏi trong công việc.'); }}>
                  <div className="suggestion-card-title">Giảm căng thẳng 🌬️</div>
                  Giúp tôi tìm cách thư giãn sau một ngày làm việc dài.
                </div>
                <div className="suggestion-card" onClick={() => { setInputValue('Làm sao để giao tiếp tốt hơn với người thân?'); }}>
                  <div className="suggestion-card-title">Cải thiện mối quan hệ 🤝</div>
                  Tôi muốn biết cách giao tiếp và thấu hiểu người khác.
                </div>
                <div className="suggestion-card" onClick={() => { setInputValue('Tôi thường bị mất ngủ và suy nghĩ nhiều vào ban đêm.'); }}>
                  <div className="suggestion-card-title">Khó ngủ ban đêm 🌙</div>
                  Làm sao để ngừng suy nghĩ và có giấc ngủ ngon?
                </div>
                <div className="suggestion-card" onClick={() => { setInputValue('Hãy hướng dẫn tôi một bài tập hít thở.'); }}>
                  <div className="suggestion-card-title">Bài tập hít thở 🧘</div>
                  Hướng dẫn bài tập hít thở sâu 4-7-8 để lấy lại bình tĩnh.
                </div>
              </div>
            </>
          )}
          <form className="gpt-input-box" onSubmit={(e) => { e.preventDefault(); handleSendMessage(e); }}>
            <button type="button" className="gpt-attach-btn" title="Đính kèm">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
            </button>
            <textarea
              placeholder="Nhắn tin cho ViMind..."
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (inputValue.trim()) {
                    handleSendMessage(e);
                    e.target.style.height = 'auto';
                  }
                }
              }}
              rows={1}
            />
            <button type="submit" className="gpt-send-btn" disabled={!inputValue.trim()}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
                <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor" />
              </svg>
            </button>
          </form>
          <div className="gpt-footer-note">
            ViMind có thể mắc lỗi. Vui lòng kiểm tra lại các thông tin quan trọng.
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
