import React from 'react';
import './HomeScreen.css';
import logoWeb from '../assets/logo-web-transparent.png';
import heroBg from '../assets/smoky-watercolor-cloud-background.jpg';

const HomeScreen = ({
  setCurrentView,
  isLoggedIn,
  userInfo,
  handleLogout,
  isDropdownOpen,
  setIsDropdownOpen,
  isUtilitiesOpen,
  setIsUtilitiesOpen,
  handleNewChat
}) => {
  return (
    <div className="home-screen">
      {/* Background Elements */}
      <div className="ambient-light light-1"></div>
      <div className="ambient-light light-2"></div>

      <header className="navbar">
        <img src={logoWeb} alt="ViMind Logo" className="logo-img" onClick={() => setCurrentView('home')} style={{ cursor: 'pointer', height: '100px', mixBlendMode: 'multiply' }} />
        <div className="nav-right" style={{ display: 'flex', alignItems: 'center', gap: '3rem', marginLeft: 'auto' }}>
          <nav className="nav-links">
            <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView('home'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>Trang chủ</a>
            <a href="#faq">FAQ</a>
            <div className="utilities-dropdown-container" onMouseLeave={() => setIsUtilitiesOpen(false)} style={{ position: 'relative', display: 'flex', alignItems: 'center', height: '100%', padding: '20px 0', margin: '-20px 0' }}>
              <a href="#" onClick={(e) => {
                e.preventDefault();
                if (!isLoggedIn) {
                  setCurrentView('login');
                  return;
                }
                setIsUtilitiesOpen(!isUtilitiesOpen);
              }}
                onMouseEnter={() => { if (isLoggedIn) setIsUtilitiesOpen(true); }}
                style={{ display: 'flex', alignItems: 'center', height: '100%' }}
              >
                Tiện ích ▾
              </a>
              {isLoggedIn && isUtilitiesOpen && (
                <div className="user-dropdown-menu" style={{ minWidth: '130px', top: '100%', marginTop: '0' }}>
                  <button onClick={() => { setCurrentView('diary'); setIsUtilitiesOpen(false); }} className="dropdown-item" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📝</span> Nhật ký
                  </button>
                  <button onClick={() => { setCurrentView('lesson'); setIsUtilitiesOpen(false); }} className="dropdown-item" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📚</span> Bài học
                  </button>
                  <button onClick={() => { setCurrentView('test'); setIsUtilitiesOpen(false); }} className="dropdown-item" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📋</span> Test
                  </button>
                  <button onClick={() => { 
                    setCurrentView('chat'); 
                    setIsUtilitiesOpen(false); 
                    handleNewChat();
                  }} className="dropdown-item" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>🤖</span> Chatbot
                  </button>
                </div>
              )}
            </div>
          </nav>
          <div className="auth-buttons">
            {isLoggedIn ? (
              <div className="user-dropdown-container" onMouseLeave={() => setIsDropdownOpen(false)}>
                <button className="user-dropdown-btn" onMouseEnter={() => setIsDropdownOpen(true)} onClick={() => setIsDropdownOpen(!isDropdownOpen)} style={{ padding: '0.35rem 1rem 0.35rem 0.35rem', background: 'rgba(255, 255, 255, 0.7)', border: '1px solid rgba(27, 122, 138, 0.2)', backdropFilter: 'blur(10px)' }}>
                  <div className="author-avatar" style={{ width: '32px', height: '32px', fontSize: '1rem', margin: 0 }}>
                    {(userInfo.fullName || userInfo.username || userInfo.email || 'U').charAt(0).toUpperCase()}
                  </div>
                  <span style={{ marginLeft: '0.25rem', whiteSpace: 'nowrap' }}>{userInfo.username} ▾</span>
                </button>
                {isDropdownOpen && (
                  <div className="user-dropdown-menu">
                    {userInfo.email === 'admin@gmail.com' && (
                      <button onClick={() => setCurrentView('admin_dashboard')} className="dropdown-item" style={{ color: 'var(--primary)' }}>⚙️ Quản trị viên</button>
                    )}
                    <button onClick={handleLogout} className="dropdown-item logout">Đăng xuất</button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <button className="nav-btn" onClick={() => setCurrentView('login')}>Đăng nhập</button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="hero-section" style={{ backgroundImage: `url(${heroBg})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundAttachment: 'fixed', position: 'relative' }}>
        <div className="hero-content">
          <h1 className="hero-title">Khoảng Lặng Bình Yên <br /><span className="gradient-text">Cho Tâm Trí Bạn</span></h1>
          <p className="hero-subtitle">
            ViMind là chuyên gia tâm lý ảo luôn sẵn sàng lắng nghe, thấu hiểu khía cạnh cảm xúc của bạn một cách an toàn và riêng tư. Bất cứ khi nào bạn cần, chúng tôi luôn ở đây.
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={() => {
              if (isLoggedIn) {
                setCurrentView('chat');
                handleNewChat();
              } else {
                setCurrentView('login');
              }
            }}>Bắt đầu ngay</button>
            <a href="#faq" className="btn-secondary">Tìm hiểu thêm</a>
          </div>
        </div>
      </main>

      <section className="testimonials-section">
        <div className="testimonials-container">
          <h2 className="section-heading">Cảm Nhận Từ Người Dùng</h2>
          <div className="testimonials-grid">
            {[
              { name: 'Mai Tiến Đạt', text: 'Ứng dụng thực sự tuyệt vời! ViMind đã giúp tôi vượt qua những giai đoạn áp lực nhất trong công việc. Khả năng lắng nghe và tư vấn không khác gì một chuyên gia tâm lý thực thụ.' },
              { name: 'Lê Tuấn Dương', text: 'Lúc đầu tôi chỉ định dùng thử, nhưng những lời khuyên từ AI thực sự sâu sắc và thấu hiểu. Web rất mượt, giao diện đẹp và giúp tôi chữa lành được những tổn thương tâm lý.' },
              { name: 'Nguyễn Phạm Trung Hiếu', text: 'Một công cụ xuất sắc để giải tỏa căng thẳng. Bất cứ khi nào cảm thấy bế tắc, tôi lại vào đây tâm sự. Cảm giác như có một người bạn thân luôn sẵn sàng lắng nghe mọi lúc.' },
              { name: 'Nguyễn Mạnh Hùng', text: 'Chưa từng thấy một AI nào có khả năng đồng cảm tốt đến vậy. ViMind giúp tôi nhìn nhận lại bản thân và cải thiện sức khỏe tinh thần đáng kể. Rất đánh giá cao đội ngũ phát triển!' },
              { name: 'Phan Anh Minh Đức', text: 'Tôi từng gặp vấn đề về rối loạn lo âu và ngại chia sẻ với người thật. Không gian an toàn và bảo mật ở đây đã giúp tôi dần cởi mở và tìm lại được sự bình yên trong tâm trí.' },
              { name: 'Lê Minh Đức', text: 'Rất hữu ích! Các câu trả lời rất tự nhiên, logic và mang tính động viên cao. Đây chắc chắn là một bước tiến lớn trong việc ứng dụng AI vào chăm sóc sức khỏe tâm thần.' }
            ].map((testimonial, index) => (
              <div key={index} className="testimonial-card">
                <div className="stars">★★★★★</div>
                <p className="testimonial-text">"{testimonial.text}"</p>
                <div className="testimonial-author">
                  <div className="author-avatar">{testimonial.name.charAt(0)}</div>
                  <div className="author-info">
                    <span className="author-name">{testimonial.name}</span>
                    <span className="author-role">Người dùng ViMind</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="faq" className="faq-section">
        <div className="faq-container">
          <h2 className="faq-heading">Câu Hỏi Thường Gặp</h2>
          <div className="faq-list">
            <div className="faq-item">
              <h3>Trò chuyện với ViMind có được bảo mật không?</h3>
              <p>Hoàn toàn bảo mật. Mọi cuộc trò chuyện của bạn với AI đều được mã hóa và không chia sẻ cho bất kỳ bên thứ ba nào. Không gian này là của riêng bạn.</p>
            </div>
            <div className="faq-item">
              <h3>ViMind có thể thay thế bác sĩ tâm lý không?</h3>
              <p>Không. ViMind là một công cụ hỗ trợ cảm xúc sơ cấp, giúp bạn giải tỏa căng thẳng và thấu hiểu bản thân. Nếu bạn gặp các vấn đề nghiêm trọng, chúng tôi khuyến khích bạn tìm đến các chuyên gia tâm lý hoặc bác sĩ chuyên khoa.</p>
            </div>
            <div className="faq-item">
              <h3>ViMind hoạt động như thế nào?</h3>
              <p>Hệ thống sử dụng trí tuệ nhân tạo để phân tích ngôn ngữ tự nhiên, từ đó đưa ra các phản hồi mang tính đồng cảm và gợi mở, giúp bạn giải phóng những cảm xúc tiêu cực một cách tự nhiên nhất.</p>
            </div>
            <div className="faq-item">
              <h3>Làm sao để xóa lịch sử trò chuyện?</h3>
              <p>Bạn có thể nhấp vào biểu tượng "Đăng xuất" hoặc tạo "Trò chuyện mới". Dữ liệu hội thoại sẽ được đảm bảo tính ẩn danh và bạn có toàn quyền quản lý tài khoản của mình.</p>
            </div>
            <div className="faq-item">
              <h3>ViMind có tính phí không?</h3>
              <p>Hiện tại, ViMind cung cấp các tính năng hỗ trợ cơ bản hoàn toàn miễn phí. Đội ngũ mong muốn mang đến công cụ chăm sóc sức khỏe tinh thần dễ tiếp cận cho tất cả mọi người.</p>
            </div>
            <div className="faq-item">
              <h3>Tôi có thể dùng ViMind trên điện thoại không?</h3>
              <p>Có, giao diện của ViMind được thiết kế tương thích và tối ưu hóa hoàn toàn cho các thiết bị di động, giúp bạn dễ dàng tâm sự mọi lúc mọi nơi.</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <p>&copy; 2026 ViMind. Đồng hành cùng sức khỏe tinh thần của bạn.</p>
      </footer>
    </div>
  );
};

export default HomeScreen;
