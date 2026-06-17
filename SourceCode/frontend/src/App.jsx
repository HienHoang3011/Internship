import { useState, useEffect, useRef } from 'react';
import './App.css';
import AdminDashboard from './components/AdminDashboard';
import TestViewer from './components/TestViewer';
import DiaryViewer from './components/DiaryViewer';
import LessonViewer from './components/LessonViewer';
import AuthScreen from './components/AuthScreen';
import HomeScreen from './components/HomeScreen';
import ChatScreen from './components/ChatScreen';
function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home' | 'chat' | 'login' | 'register' | 'diary'
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
    if (localStorage.getItem("accessToken")) {
      setIsLoggedIn(true);
      const email = localStorage.getItem("email") || '';
      setUserInfo({
        username: localStorage.getItem("username") || '',
        email: email,
        fullName: localStorage.getItem("fullName") || ''
      });
      if (email === 'admin@gmail.com') {
        setCurrentView('admin_dashboard');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    localStorage.removeItem("fullName");
    setIsLoggedIn(false);
    setUserInfo({ username: '', email: '', fullName: '' });
    setSessions([]);
    setActiveSessionId(null);
    setIsChatLoaded(false);
    setCurrentView('home');
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
      const token = localStorage.getItem("accessToken");
      const res = await fetch("http://localhost:8000/api/chat/", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.status === 401) {
        handleLogout();
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        return;
      }
      if (res.ok) {
        let data = await res.json();
        if (data.length === 0) {
          data = [{ id: 'temp', title: 'Cuộc trò chuyện mới', messages: [] }];
        }
        setSessions(data);
        setActiveSessionId(data[0].id);
        setIsChatLoaded(true);
      }
    } catch (err) {
      console.error("Lỗi khi tải chat:", err);
    }
  };

  useEffect(() => {
    if (currentView === 'chat' && !isChatLoaded) {
      fetchChats();
    }
  }, [currentView, isChatLoaded, isLoggedIn]);


  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const currentInput = inputValue;
    const newUserMsg = { id: Date.now(), text: currentInput, sender: 'user' };
    const botLoadingId = Date.now() + 1;

    let targetSessionId = activeSessionId;

    if (targetSessionId === 'temp') {
      try {
        const token = localStorage.getItem("accessToken");
        const createRes = await fetch("http://localhost:8000/api/chat/", {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
        });
        if (createRes.ok) {
          const newSession = await createRes.json();
          targetSessionId = newSession.id;
          setActiveSessionId(targetSessionId);
        } else {
          return;
        }
      } catch (err) {
        console.error("Lỗi tạo chat mới:", err);
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
      const token = localStorage.getItem("accessToken");
      const response = await fetch(`http://localhost:8000/api/chat/${targetSessionId}/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ text: currentInput })
      });

      if (response.status === 401) {
        handleLogout();
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        // data has user_message, bot_message, session_title
        const botText = data.bot_message.text;
        const newTitle = data.session_title;

        // Replace tin nhắn Loading bằng kết quả thật
        setSessions(prevSessions => prevSessions.map(session => {
          if (session.id === targetSessionId) {
            const updatedMessages = session.messages.map(m =>
              m.id === botLoadingId ? { ...m, id: data.bot_message.id, text: botText, isLoading: false } : m
            );
            return { ...session, title: newTitle, messages: updatedMessages };
          }
          return session;
        }));
      } else {
        throw new Error("Lỗi Server");
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
    }
  };

  const handleNewChat = () => {
    const emptySession = sessions.find(s => s.id === 'temp' || (s.messages && s.messages.length === 0));
    if (emptySession) {
      setActiveSessionId(emptySession.id);
      return;
    }
    const newSession = { id: 'temp', title: 'Cuộc trò chuyện mới', messages: [] };
    setSessions([newSession, ...sessions]);
    setActiveSessionId('temp');
  };

  useEffect(() => {
    if (messagesEndRef.current && currentView === 'chat') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
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
        setIsLoggedIn(true);
        setUserInfo({
          username: data.username || '',
          email: data.email || '',
          fullName: data.full_name || ''
        });
        if (data.email === 'admin@gmail.com') {
          setCurrentView('admin_dashboard');
        } else {
          setCurrentView('home');
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
    setCurrentView(mode);
  };



  return (
    <div className="app-container">
      {currentView === 'home' ? (
        <HomeScreen 
          setCurrentView={setCurrentView}
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
          setCurrentView={setCurrentView}
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
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          handleNewChat={handleNewChat}
          sessions={sessions}
          activeSessionId={activeSessionId}
          setActiveSessionId={setActiveSessionId}
          setCurrentView={setCurrentView}
          isLoggedIn={isLoggedIn}
          handleLogout={handleLogout}
          activeSession={activeSession}
          userInfo={userInfo}
          messagesEndRef={messagesEndRef}
          inputValue={inputValue}
          setInputValue={setInputValue}
          handleSendMessage={handleSendMessage}
        />
      ) : null}

      {currentView === 'diary' && (
        <DiaryViewer onBack={() => setCurrentView('home')} handleLogout={handleLogout} />
      )}

      {currentView === 'lesson' && (
        <LessonViewer onBack={() => setCurrentView('home')} />
      )}

      {currentView === 'admin_dashboard' && (
        <AdminDashboard handleLogout={handleLogout} />
      )}
      
      {currentView === 'test' && (
        <TestViewer onBack={() => setCurrentView('home')} handleLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
