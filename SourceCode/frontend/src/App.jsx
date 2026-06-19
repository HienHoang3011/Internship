import { useState, useEffect, useRef } from 'react';
import './App.css';
import { apiFetch } from './utils/api';
import AdminDashboard from './components/AdminDashboard';
import TestViewer from './components/TestViewer';
import DiaryViewer from './components/DiaryViewer';
import LessonViewer from './components/LessonViewer';
import AuthScreen from './components/AuthScreen';
import HomeScreen from './components/HomeScreen';
import ChatScreen from './components/ChatScreen';
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [currentId, setCurrentId] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isUtilitiesOpen, setIsUtilitiesOpen] = useState(false);

  // Auth State
  const [authUsername, setAuthUsername] = useState('');
  const [authFullName, setAuthFullName] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authConfirmPassword, setAuthConfirmPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState({ username: '', email: '', fullName: '' });
  const [showPassword, setShowPassword] = useState(false);


  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      const role = localStorage.getItem("role");
      
      if (role === 'admin' && (!hash || hash === 'home' || hash === 'chat')) {
        window.location.hash = 'admin_dashboard';
        return;
      }
      
      if (hash) {
        const parts = hash.split('/');
        if (parts[0] === 'faq') {
          setCurrentView('home');
          setTimeout(() => {
            document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        } else {
          setCurrentView(parts[0]);
          setCurrentId(parts.length > 1 ? parts[1] : null);
        }
      } else {
        if (role === 'admin') {
          window.location.hash = 'admin_dashboard';
        } else {
          setCurrentView('home');
          setCurrentId(null);
        }
      }
    };
    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);

    const onLogout = () => {
      alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
      handleLogout();
    };
    window.addEventListener('auth:logout', onLogout);

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
      window.removeEventListener('auth:logout', onLogout);
    };
  }, []);

  useEffect(() => {
    if (localStorage.getItem("accessToken")) {
      setIsLoggedIn(true);
      const email = localStorage.getItem("email") || '';
      const role = localStorage.getItem("role") || 'user';
      setUserInfo({
        username: localStorage.getItem("username") || '',
        email: email,
        fullName: localStorage.getItem("fullName") || '',
        role: role
      });
      if (role === 'admin') {
        window.location.hash = 'admin_dashboard';
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    localStorage.removeItem("fullName");
    localStorage.removeItem("role");
    setIsLoggedIn(false);
    setUserInfo({ username: '', email: '', fullName: '', role: 'user' });
    setSessions([]);
    setActiveSessionId(null);
    setIsChatLoaded(false);
    window.location.hash = 'home';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Chat State
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isChatLoaded, setIsChatLoaded] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // for mobile toggle
  const messagesEndRef = useRef(null);

  const activeSession = sessions.find(s => s.id === activeSessionId) || { messages: [] };

  const fetchChats = async () => {
    if (!isLoggedIn) return;
    try {
      const res = await apiFetch("http://localhost:8000/api/chat/");
      if (res.status === 401) return; // handled by interceptor
      if (res.ok) {
        let data = await res.json();
        if (data.length === 0) {
          data = [{ id: 'temp', title: 'Cuộc trò chuyện mới', messages: [] }];
        }
        setSessions(prevSessions => {
          const hasTemp = prevSessions.some(s => s.id === 'temp') || currentId === 'temp';
          if (hasTemp && !data.some(s => s.id === 'temp')) {
            return [{ id: 'temp', title: 'Cuộc trò chuyện mới', messages: [] }, ...data];
          }
          return data;
        });
        setActiveSessionId(prevId => {
          if (currentId) return parseInt(currentId) || currentId;
          if (prevId === 'temp') return 'temp';
          return data[0].id;
        });
        setIsChatLoaded(true);
      }
    } catch (err) {
      console.error("Lỗi khi tải chat:", err);
    }
  };

  useEffect(() => {
    if (currentView === 'chat' && activeSessionId) {
      window.location.hash = `chat/${activeSessionId}`;
    }
  }, [activeSessionId, currentView]);

  useEffect(() => {
    if (currentView === 'chat' && currentId && isChatLoaded) {
      // Don't sync if they are already the same to avoid redundant updates
      const parsedId = parseInt(currentId) || currentId;
      if (activeSessionId !== parsedId) {
        setActiveSessionId(parsedId);
      }
    }
  }, [currentId, currentView, isChatLoaded]);

  useEffect(() => {
    if (currentView === 'chat' && !isChatLoaded) {
      fetchChats();
    }
  }, [currentView, isChatLoaded, isLoggedIn]);


  const [isSending, setIsSending] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isSending) return;

    setIsSending(true);
    const currentInput = inputValue;
    setInputValue(''); // Clear input immediately
    const newUserMsg = { id: Date.now(), text: currentInput, sender: 'user' };
    const botLoadingId = Date.now() + 1;

    let targetSessionId = activeSessionId;

    if (targetSessionId === 'temp') {
      try {
        const createRes = await apiFetch("http://localhost:8000/api/chat/", {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        if (createRes.ok) {
          const newSession = await createRes.json();
          targetSessionId = newSession.id;
          setActiveSessionId(targetSessionId);
        } else {
          setIsSending(false);
          return;
        }
      } catch (err) {
        console.error("Lỗi tạo chat mới:", err);
        setIsSending(false);
        return;
      }
    }

    // Lấy context hiện tại của cuộc hội thoại
    const currentSession = sessions.find(s => s.id === activeSessionId) || { title: 'Cuộc trò chuyện mới', messages: [] };
    let newTitle = currentSession.title;
    if (currentSession.messages.length === 0) {
      newTitle = currentInput.length > 20 ? currentInput.substring(0, 20) + '...' : currentInput;
    }

    // Update UI ngay lập tức với câu hỏi của User và một trạng thái Loading của Bot
    setSessions(prevSessions => {
      let updatedSessions = prevSessions;
      // Change 'temp' to new targetSessionId if needed
      if (activeSessionId === 'temp') {
        updatedSessions = updatedSessions.map(s => s.id === 'temp' ? { ...s, id: targetSessionId } : s);
      }
      return updatedSessions.map(session => {
        if (session.id === targetSessionId) {
          return {
            ...session,
            title: newTitle,
            messages: [...session.messages, newUserMsg, { id: botLoadingId, text: "Đang phân tích...", sender: 'bot', isLoading: true }]
          };
        }
        return session;
      });
    });

    setInputValue('');

    try {
      const response = await apiFetch(`http://localhost:8000/api/chat/${targetSessionId}/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: currentInput })
      });

      if (response.status === 401) {
        setIsSending(false);
        return;
      }

      if (response.ok) {
        const data = await response.json();
        const botText = data.bot_message.text;
        const newTitle = data.session_title;
        setSessions(prevSessions => prevSessions.map(session => {
          if (session.id === targetSessionId) {
            const updatedMessages = session.messages.map(m => {
              if (m.id === newUserMsg.id) return data.user_message;
              if (m.id === botLoadingId) return { ...m, id: data.bot_message.id, text: botText, isLoading: false };
              return m;
            });
            return { ...session, title: newTitle, messages: updatedMessages };
          }
          return session;
        }));
      } else {
        setSessions(prevSessions => prevSessions.map(session => {
          if (session.id === targetSessionId) {
            const updatedMessages = session.messages.map(m =>
              m.id === botLoadingId ? { ...m, text: "Mất kết nối với máy chủ. Vui lòng thử lại sau.", isLoading: false } : m
            );
            return { ...session, messages: updatedMessages };
          }
          return session;
        }));
      }
    } catch (error) {
      console.error("Lỗi gọi Chat API:", error);
      setSessions(prevSessions => prevSessions.map(session => {
        if (session.id === targetSessionId) {
          const updatedMessages = session.messages.map(m =>
            m.id === botLoadingId ? { ...m, text: "Mất kết nối với máy chủ. Vui lòng thử lại sau.", isLoading: false } : m
          );
          return { ...session, messages: updatedMessages };
        }
        return session;
      }));
    } finally {
      setIsSending(false);
    }
  };

  const handleNewChat = () => {
    const emptySession = sessions.find(s => s.id === 'temp' || (s.messages && s.messages.length === 0));
    if (emptySession) {
      setActiveSessionId(emptySession.id);
      window.location.hash = `chat/${emptySession.id}`;
      return;
    }
    const newSession = { id: 'temp', title: 'Cuộc trò chuyện mới', messages: [] };
    setSessions([newSession, ...sessions]);
    setActiveSessionId('temp');
    window.location.hash = `chat/temp`;
  };

  useEffect(() => {
    if (messagesEndRef.current && currentView === 'chat') {
      setTimeout(() => {
        const container = messagesEndRef.current.parentElement;
        if (container) {
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 150);
    }
  }, [sessions, activeSessionId, currentView]);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (currentView === 'register') {
      if (authPassword !== authConfirmPassword) {
        setAuthError('Mật khẩu xác nhận không khớp.');
        return;
      }
      try {
        const res = await fetch("http://localhost:8000/api/auth/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: authUsername,
            email: authEmail,
            password: authPassword,
            full_name: authFullName
          })
        });
        if (!res.ok) {
          const errData = await res.json();
          setAuthError(JSON.stringify(errData));
          return;
        }
        alert("Đăng ký thành công! Vui lòng đăng nhập.");
        setAuthPassword('');
        setAuthConfirmPassword('');
        setAuthUsername('');
        setAuthFullName('');
        setCurrentView('login');
      } catch (err) {
        setAuthError('Lỗi kết nối đến máy chủ.');
      }
    } else {
      // Login
      try {
        const res = await fetch("http://localhost:8000/api/auth/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, password: authPassword })
        });
        if (!res.ok) {
          setAuthError('Tài khoản hoặc mật khẩu không chính xác.');
          return;
        }
        const data = await res.json();
        localStorage.setItem("accessToken", data.access);
        localStorage.setItem("refreshToken", data.refresh);
        localStorage.setItem("username", data.username || '');
        localStorage.setItem("email", data.email || '');
        localStorage.setItem("fullName", data.full_name || '');
        localStorage.setItem("role", data.role || 'user');
        setIsLoggedIn(true);
        setUserInfo({
          username: data.username || '',
          email: data.email || '',
          fullName: data.full_name || '',
          role: data.role || 'user'
        });
        if (data.role === 'admin') {
          window.location.hash = 'admin_dashboard';
        } else {
          window.location.hash = 'home';
        }
      } catch (err) {
        setAuthError('Lỗi kết nối đến máy chủ.');
      }
    }
  };

  const switchAuthMode = (mode) => {
    setAuthError('');
    setAuthEmail('');
    setAuthPassword('');
    setAuthConfirmPassword('');
    setAuthUsername('');
    setAuthFullName('');
    window.location.hash = mode;
  };



  return (
    <div className="app-container">
      {currentView === 'home' ? (
        <HomeScreen 
          setCurrentView={(v) => window.location.hash = v}
          isLoggedIn={isLoggedIn}
          userInfo={userInfo}
          handleLogout={handleLogout}
          isDropdownOpen={isDropdownOpen}
          setIsDropdownOpen={setIsDropdownOpen}
          isUtilitiesOpen={isUtilitiesOpen}
          setIsUtilitiesOpen={setIsUtilitiesOpen}
          handleNewChat={handleNewChat}
        />
      ) : currentView === 'login' || currentView === 'register' ? (
        <AuthScreen 
          currentView={currentView}
          setCurrentView={(v) => window.location.hash = v}
          handleAuthSubmit={handleAuthSubmit}
          authError={authError}
          authUsername={authUsername} setAuthUsername={setAuthUsername}
          authFullName={authFullName} setAuthFullName={setAuthFullName}
          authEmail={authEmail} setAuthEmail={setAuthEmail}
          authPassword={authPassword} setAuthPassword={setAuthPassword}
          authConfirmPassword={authConfirmPassword} setAuthConfirmPassword={setAuthConfirmPassword}
          switchAuthMode={switchAuthMode}
        />
      ) : currentView === 'chat' ? (
        <ChatScreen 
          initialId={currentId}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          handleNewChat={handleNewChat}
          sessions={sessions}
          activeSessionId={activeSessionId}
          setActiveSessionId={setActiveSessionId}
          setCurrentView={(v) => window.location.hash = v}
          isLoggedIn={isLoggedIn}
          handleLogout={handleLogout}
          activeSession={activeSession}
          userInfo={userInfo}
          messagesEndRef={messagesEndRef}
          inputValue={inputValue}
          setInputValue={setInputValue}
          handleSendMessage={handleSendMessage}
          isSending={isSending}
        />
      ) : null}

      {currentView === 'diary' && (
        <DiaryViewer initialId={currentId} onBack={() => window.location.hash = 'home'} handleLogout={handleLogout} />
      )}

      {currentView === 'lesson' && (
        <LessonViewer initialId={currentId} onBack={() => window.location.hash = 'home'} />
      )}

      {currentView === 'admin_dashboard' && (
        <AdminDashboard handleLogout={handleLogout} />
      )}
      
      {currentView === 'test' && (
        <TestViewer initialId={currentId} onBack={() => window.location.hash = 'home'} handleLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
