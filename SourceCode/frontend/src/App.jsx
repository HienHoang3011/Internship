import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home' | 'chat' | 'login' | 'register'

  // Chat State
  const [sessions, setSessions] = useState([
    {
      id: 1,
      title: 'Cuộc trò chuyện đầu tiên',
      messages: [
        { id: 1, text: "Chào bạn, mình là MindCareAI. Bạn đang cảm thấy thế nào? Hãy chia sẻ cùng mình nhé, mình luôn ở đây để lắng nghe.", sender: 'bot' }
      ]
    }
  ]);
  const [activeSessionId, setActiveSessionId] = useState(1);
  const [inputValue, setInputValue] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // for mobile toggle
  const messagesEndRef = useRef(null);

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newUserMsg = { id: Date.now(), text: inputValue, sender: 'user' };

    // Update active session messages
    setSessions(prevSessions => prevSessions.map(session => {
      if (session.id === activeSessionId) {
        return { ...session, messages: [...session.messages, newUserMsg] };
      }
      return session;
    }));

    setInputValue('');

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        text: "Mình hiểu những gì bạn đang trải qua. Bạn có thể kể thêm chi tiết hơn để mình hiểu trọn vẹn cảm xúc của bạn lúc này không?",
        sender: 'bot'
      };

      setSessions(prevSessions => prevSessions.map(session => {
        if (session.id === activeSessionId) {
          // If title is default, update it based on user's first query
          let newTitle = session.title;
          if (session.messages.length === 1 && newTitle.includes("Cuộc trò chuyện mới")) {
            newTitle = inputValue.length > 20 ? inputValue.substring(0, 20) + '...' : inputValue;
          }
          return { ...session, title: newTitle, messages: [...session.messages, botResponse] };
        }
        return session;
      }));
    }, 1200);
  };

  const handleNewChat = () => {
    const newSession = {
      id: Date.now(),
      title: 'Cuộc trò chuyện mới',
      messages: [
        { id: Date.now() + 1, text: "MindCareAI luôn bên bạn. Hôm nay bạn muốn tâm sự điều gì?", sender: 'bot' }
      ]
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newSession.id);
  };

  useEffect(() => {
    if (messagesEndRef.current && currentView === 'chat') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [sessions, activeSessionId, currentView]);

  return (
    <div className="app-container">
      {currentView === 'home' ? (
        // --- HOME SCREEN ---
        <div className="home-screen">
          {/* Background Elements */}
          <div className="ambient-light light-1"></div>
          <div className="ambient-light light-2"></div>

          <header className="navbar">
            <div className="logo" onClick={() => setCurrentView('home')} style={{ cursor: 'pointer' }}>MindCare<span>AI</span></div>
            <nav>
              <a href="#faq">Về chúng tôi</a>
              <a href="#faq">Câu hỏi thường gặp</a>
              <div className="auth-buttons">
                <button className="btn-text" onClick={() => setCurrentView('chat')}>💬 Trò chuyện</button>
                <button className="nav-btn" onClick={() => setCurrentView('register')}>Đăng ký</button>
              </div>
            </nav>
          </header>

          <main className="hero-section">
            <div className="hero-content">
              <h1 className="hero-title">Khoảng Lặng Bình Yên <br /><span className="gradient-text">Cho Tâm Trí Bạn</span></h1>
              <p className="hero-subtitle">
                MindCareAI là chuyên gia tâm lý ảo luôn sẵn sàng lắng nghe, thấu hiểu khía cạnh cảm xúc của bạn một cách an toàn và riêng tư. Bất cứ khi nào bạn cần, chúng tôi luôn ở đây.
              </p>
              <div className="hero-actions">
                <button className="btn-primary" onClick={() => setCurrentView('chat')}>Bắt đầu tâm sự</button>
                <a href="#faq" className="btn-secondary">Tìm hiểu thêm</a>
              </div>
            </div>
          </main>

          <section id="faq" className="faq-section">
            <div className="faq-container">
              <h2 className="faq-heading">Câu Hỏi Thường Gặp</h2>
              <div className="faq-list">
                <div className="faq-item">
                  <h3>Trò chuyện với MindCareAI có được bảo mật không?</h3>
                  <p>Hoàn toàn bảo mật. Mọi cuộc trò chuyện của bạn với AI đều được mã hóa và không chia sẻ cho bất kỳ bên thứ ba nào. Không gian này là của riêng bạn.</p>
                </div>
                <div className="faq-item">
                  <h3>MindCareAI có thể thay thế bác sĩ tâm lý không?</h3>
                  <p>Không. MindCareAI là một công cụ hỗ trợ cảm xúc sơ cấp, giúp bạn giải tỏa căng thẳng và thấu hiểu bản thân. Nếu bạn gặp các vấn đề nghiêm trọng, chúng tôi khuyến khích bạn tìm đến các chuyên gia tâm lý hoặc bác sĩ chuyên khoa.</p>
                </div>
                <div className="faq-item">
                  <h3>MindCareAI hoạt động như thế nào?</h3>
                  <p>Hệ thống sử dụng trí tuệ nhân tạo để phân tích ngôn ngữ tự nhiên, từ đó đưa ra các phản hồi mang tính đồng cảm và gợi mở, giúp bạn giải phóng những cảm xúc tiêu cực một cách tự nhiên nhất.</p>
                </div>
              </div>
            </div>
          </section>

          <footer className="footer">
            <p>&copy; 2026 MindCareAI. Đồng hành cùng sức khỏe tinh thần của bạn.</p>
          </footer>
        </div>
      ) : currentView === 'login' || currentView === 'register' ? (
        // --- AUTH SCREENS ---
        <div className="auth-screen">
          <div className="ambient-light light-1"></div>
          <div className="ambient-light light-2"></div>

          <div className="auth-card">
            <div className="auth-logo" onClick={() => setCurrentView('home')}>MindCare<span>AI</span></div>
            <h2>{currentView === 'login' ? 'Đăng nhập vào tài khoản' : 'Tạo tài khoản mới'}</h2>
            <p className="auth-subtitle">
              {currentView === 'login' ? 'Chào mừng bạn quay trở lại với MindCareAI' : 'Bắt đầu hành trình chăm sóc sức khỏe tinh thần cùng chúng tôi'}
            </p>

            <form className="auth-form" onSubmit={(e) => { e.preventDefault(); setCurrentView('chat'); }}>
              {currentView === 'register' && (
                <div className="form-group">
                  <label>Họ và tên</label>
                  <input type="text" placeholder="Nguyễn Văn A" required />
                </div>
              )}
              <div className="form-group">
                <label>Email</label>
                <input type="email" placeholder="email@example.com" required />
              </div>
              <div className="form-group">
                <label>Mật khẩu</label>
                <input type="password" placeholder="••••••••" required />
              </div>
              {currentView === 'register' && (
                <div className="form-group">
                  <label>Xác nhận mật khẩu</label>
                  <input type="password" placeholder="••••••••" required />
                </div>
              )}

              <button type="submit" className="auth-submit-btn">
                {currentView === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}
              </button>
            </form>

            <div className="auth-switch">
              {currentView === 'login' ? (
                <p>Chưa có tài khoản? <button onClick={() => setCurrentView('register')} className="auth-link">Đăng ký ngay</button></p>
              ) : (
                <p>Đã có tài khoản? <button onClick={() => setCurrentView('login')} className="auth-link">Đăng nhập</button></p>
              )}
            </div>

            <button className="auth-back-btn" onClick={() => setCurrentView('home')}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
                <path d="M20 11H7.83L13.42 5.41L12 4L4 12L12 20L13.41 18.59L7.83 13H20V11Z" fill="currentColor" />
              </svg>
              Quay lại trang chủ
            </button>
          </div>
        </div>
      ) : (
        // --- CHAT SCREEN (ChatGPT Style) ---
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
              <div className="history-label">Hôm nay</div>
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
              <button className="back-home-btn" onClick={() => setCurrentView('home')}>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M9 22V12h6v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Về trang chủ
              </button>
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
                      {msg.sender === 'bot' ? '☘️' : 'U'}
                    </div>
                    <div className="gpt-message-text">
                      <div className="gpt-sender-name">
                        {msg.sender === 'bot' ? 'MindCareAI' : 'Bạn'}
                      </div>
                      <p>{msg.text}</p>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} className="messages-bottom-spacer" />
            </div>

            <div className="gpt-input-area-wrapper">
              <form className="gpt-input-box" onSubmit={handleSendMessage}>
                <button type="button" className="gpt-attach-btn" title="Đính kèm">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
                </button>
                <input
                  type="text"
                  placeholder="Nhắn tin cho MindCareAI..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                />
                <button type="submit" className="gpt-send-btn" disabled={!inputValue.trim()}>
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
                    <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor" />
                  </svg>
                </button>
              </form>
              <div className="gpt-footer-note">
                MindCareAI có thể mắc lỗi. Vui lòng kiểm tra lại các thông tin quan trọng.
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}

export default App;
