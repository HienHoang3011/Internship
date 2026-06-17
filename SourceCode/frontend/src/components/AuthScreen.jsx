import React, { useState } from 'react';
import './AuthScreen.css';
import thienImg from '../assets/thien.png';
const AuthScreen = ({ 
  currentView, 
  setCurrentView, 
  handleAuthSubmit, 
  authError,
  authUsername, setAuthUsername,
  authFullName, setAuthFullName,
  authEmail, setAuthEmail,
  authPassword, setAuthPassword,
  authConfirmPassword, setAuthConfirmPassword,
  switchAuthMode
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="auth-screen">
      <div className="ambient-light light-1"></div>
      <div className="ambient-light light-2"></div>

      <div className="auth-layout">
        <div className="auth-brand">
          <div className="auth-logo-container" onClick={() => setCurrentView('home')} style={{ marginBottom: '1rem' }}>
            <img src={thienImg} alt="Meditation" className="auth-logo-icon" style={{ width: '250px', height: 'auto', objectFit: 'contain' }} />
          </div>
          <h1 className="auth-brand-slogan">Bắt đầu hành trình<br />chữa lành tâm hồn.</h1>
        </div>

        <div className="auth-card">
          <h2>{currentView === 'login' ? 'Đăng nhập vào tài khoản' : 'Tạo tài khoản mới'}</h2>
          <p className="auth-subtitle">
            {currentView === 'login' ? 'Chào mừng bạn quay trở lại với MindCareAI' : 'Bắt đầu hành trình chăm sóc sức khỏe tinh thần cùng chúng tôi'}
          </p>

          {authError && <div style={{ color: 'red', marginBottom: '10px', fontSize: '0.9rem' }}>{authError}</div>}
          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {currentView === 'register' && (
              <>
                <div className="form-group">
                  <label>Tên người dùng (Username)</label>
                  <input type="text" placeholder="nguyenvana123" value={authUsername} onChange={e => setAuthUsername(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label>Họ và tên</label>
                  <input type="text" placeholder="Nguyễn Văn A" value={authFullName} onChange={e => setAuthFullName(e.target.value)} required />
                </div>
              </>
            )}
            <div className="form-group">
              <label>Email</label>
              <input type="email" placeholder="email@example.com" value={authEmail} onChange={e => setAuthEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Mật khẩu</label>
              <div className="password-input-wrapper">
                <input type={showPassword ? "text" : "password"} placeholder="••••••••" value={authPassword} onChange={e => setAuthPassword(e.target.value)} required autoComplete="new-password" />
                <span className="eye-icon" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/></svg>
                  ) : (
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  )}
                </span>
              </div>
            </div>
            {currentView === 'register' && (
              <div className="form-group">
                <label>Xác nhận mật khẩu</label>
                <div className="password-input-wrapper">
                  <input type={showPassword ? "text" : "password"} placeholder="••••••••" value={authConfirmPassword} onChange={e => setAuthConfirmPassword(e.target.value)} required autoComplete="new-password" />
                  <span className="eye-icon" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    )}
                  </span>
                </div>
              </div>
            )}

            <button type="submit" className="auth-submit-btn" style={{ marginTop: '1rem', width: '100%' }}>
              {currentView === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}
            </button>
          </form>

          <div className="auth-switch">
            {currentView === 'login' ? (
              <p>Chưa có tài khoản? <button type="button" onClick={() => switchAuthMode('register')} className="auth-link">Đăng ký ngay</button></p>
            ) : (
              <p>Đã có tài khoản? <button type="button" onClick={() => switchAuthMode('login')} className="auth-link">Đăng nhập</button></p>
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
    </div>
  );
};

export default AuthScreen;
