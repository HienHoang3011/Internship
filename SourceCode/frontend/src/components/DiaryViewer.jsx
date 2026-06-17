import React, { useState, useEffect } from 'react';

const DiaryViewer = ({ onBack, handleLogout }) => {
  const [diaries, setDiaries] = useState([]);
  const [activeDiary, setActiveDiary] = useState(null);
  const [diaryForm, setDiaryForm] = useState({ title: '', content: '', emotion: 'Vui vẻ', intensity: 5, tags: [] });
  const [tagInput, setTagInput] = useState('');
  const [isDiariesLoaded, setIsDiariesLoaded] = useState(false);
  const [isDiarySidebarOpen, setIsDiarySidebarOpen] = useState(false);

  useEffect(() => {
    const fetchDiaries = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const res = await fetch("http://localhost:8000/api/diaries/", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.status === 401) {
          handleLogout();
          alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setDiaries(data);
          setIsDiariesLoaded(true);
        }
      } catch (err) {
        console.error("Lỗi khi tải nhật ký:", err);
      }
    };

    if (!isDiariesLoaded) {
      fetchDiaries();
    }
  }, [isDiariesLoaded, handleLogout]);

  const handleSaveDiary = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const method = activeDiary ? "PUT" : "POST";
      const url = activeDiary
        ? `http://localhost:8000/api/diaries/${activeDiary.id}/`
        : "http://localhost:8000/api/diaries/";

      const res = await fetch(url, {
        method,
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(diaryForm)
      });

      if (res.status === 401) {
        handleLogout();
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        return;
      }

      if (res.ok) {
        const savedDiary = await res.json();
        if (activeDiary) {
          setDiaries(diaries.map(d => d.id === savedDiary.id ? savedDiary : d));
        } else {
          setDiaries([savedDiary, ...diaries]);
        }
        setActiveDiary(savedDiary);
        alert("Đã lưu nhật ký thành công!");
      }
    } catch (err) {
      console.error("Lỗi lưu nhật ký:", err);
      alert("Có lỗi xảy ra khi lưu nhật ký.");
    }
  };

  const startNewDiary = () => {
    setActiveDiary(null);
    setDiaryForm({ title: '', content: '', emotion: 'Vui vẻ', intensity: 5, tags: [] });
  };

  const openDiary = (diary) => {
    setActiveDiary(diary);
    setDiaryForm({
      title: diary.title || '',
      content: diary.content || '',
      emotion: diary.emotion || 'Vui vẻ',
      intensity: diary.intensity || 5,
      tags: diary.tags || []
    });
  };

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!diaryForm.tags.includes(tagInput.trim())) {
        setDiaryForm({ ...diaryForm, tags: [...diaryForm.tags, tagInput.trim()] });
      }
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setDiaryForm({ ...diaryForm, tags: diaryForm.tags.filter(t => t !== tagToRemove) });
  };

  const handleDeleteDiary = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Bạn có chắc muốn xóa nhật ký này?")) return;
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`http://localhost:8000/api/diaries/${id}/`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.status === 401) {
        handleLogout();
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        return;
      }
      if (res.ok) {
        setDiaries(diaries.filter(d => d.id !== id));
        if (activeDiary && activeDiary.id === id) {
          startNewDiary();
        }
      }
    } catch (err) {
      console.error("Lỗi xóa nhật ký:", err);
    }
  };

  return (
    <div className="gpt-chat-screen">
      <div className={`gpt-sidebar ${isDiarySidebarOpen ? 'open' : 'closed'}`} style={{ width: isDiarySidebarOpen ? '300px' : '0', overflow: 'hidden', transition: 'width 0.3s' }}>
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 'bold', fontSize: '1.2rem', color: 'var(--text-primary)' }}>Lịch sử nhật ký</span>
          <button className="icon-btn hide-sidebar-btn" onClick={() => setIsDiarySidebarOpen(false)} title="Ẩn menu">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
        <div style={{ padding: '0 1rem 1rem 1rem' }}>
          <button className="back-home-btn" onClick={onBack} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface)', border: '1px solid var(--border-color)', padding: '0.75rem 1rem', borderRadius: '8px', color: 'var(--text-primary)', cursor: 'pointer', transition: 'background 0.2s' }}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M9 22V12h6v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Quay lại Trang chủ
          </button>
        </div>
        <div className="history-list" style={{ padding: 0 }}>
          {diaries.map((diary) => (
            <div key={diary.id} className={`history-item ${activeDiary?.id === diary.id ? 'active' : ''}`} onClick={() => openDiary(diary)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', position: 'relative', height: 'auto', borderRadius: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                <span style={{ fontWeight: 'bold', fontSize: '1rem', color: 'var(--text-primary)' }}>{diary.title || `Nhật ký ${new Date(diary.created_at).toLocaleDateString('vi-VN')}`}</span>
                <button className="delete-btn" onClick={(e) => handleDeleteDiary(diary.id, e)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0 0.5rem' }}>✕</button>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)', alignItems: 'center' }}>
                <span style={{ background: 'var(--surface)', padding: '0.2rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>{diary.emotion}</span>
                <span>{new Date(diary.created_at).toLocaleDateString('vi-VN')}</span>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', textOverflow: 'ellipsis', width: '100%', whiteSpace: 'normal' }}>
                {diary.content || 'Chưa có nội dung...'}
              </p>
            </div>
          ))}
        </div>

      </div>

      <div className="gpt-main-area" style={{ position: 'relative' }}>
        {!isDiarySidebarOpen && (
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 2rem', borderBottom: '1px solid var(--border-color)', alignItems: 'center', background: 'var(--surface)', zIndex: 10 }}>
            <button className="show-sidebar-btn" onClick={() => setIsDiarySidebarOpen(true)} style={{ position: 'static', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-primary)', padding: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span style={{ fontSize: '1rem', fontWeight: 'bold' }}>Lịch sử</span>
            </button>
          </div>
        )}
        <div className="diary-editor" style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '2rem', boxSizing: 'border-box', overflowY: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '1rem', fontWeight: '500' }}>
              {activeDiary ? `Ngày viết: ${new Date(activeDiary.created_at).toLocaleDateString('vi-VN')}` : `Ngày viết: ${new Date().toLocaleDateString('vi-VN')}`}
            </div>
            <button className="btn-primary" onClick={handleSaveDiary} disabled={!diaryForm.content.trim()} style={{ opacity: diaryForm.content.trim() ? 1 : 0.5, cursor: diaryForm.content.trim() ? 'pointer' : 'not-allowed', padding: '0.75rem 2rem', fontSize: '1rem', fontWeight: 'bold', boxShadow: '0 4px 10px rgba(27, 122, 138, 0.3)' }}>
              Lưu nhật ký
            </button>
          </div>
          <input
            type="text"
            className="diary-title-input"
            placeholder="Tiêu đề nhật ký..."
            value={diaryForm.title}
            onChange={(e) => setDiaryForm({ ...diaryForm, title: e.target.value })}
            style={{ fontSize: '2rem', fontWeight: 'bold', border: 'none', borderBottom: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-primary)', outline: 'none', padding: '0.5rem 0', marginBottom: '1.5rem' }}
          />

          <div className="diary-meta" style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <div className="meta-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '600' }}>Cảm xúc của bạn:</label>
              <select
                value={diaryForm.emotion}
                onChange={(e) => setDiaryForm({ ...diaryForm, emotion: e.target.value })}
                style={{ padding: '0.5rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--surface)', color: 'var(--text-primary)', cursor: 'pointer', outline: 'none' }}
              >
                <option value="Vui vẻ">😄 Vui vẻ</option>
                <option value="Bình thường">😐 Bình thường</option>
                <option value="Buồn">😢 Buồn</option>
                <option value="Tức giận">😡 Tức giận</option>
                <option value="Lo lắng">😰 Lo lắng</option>
                <option value="Căng thẳng">🤯 Căng thẳng</option>
              </select>
            </div>

            <div className="meta-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1, minWidth: '200px' }}>
              <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '600' }}>Mức độ ({diaryForm.intensity}/10):</label>
              <input
                type="range"
                min="1" max="10"
                value={diaryForm.intensity}
                onChange={(e) => setDiaryForm({ ...diaryForm, intensity: parseInt(e.target.value) })}
                style={{ cursor: 'pointer' }}
              />
            </div>
          </div>

          <div className="meta-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '2rem' }}>
            <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '600' }}>Tags (Nhấn Enter để thêm):</label>
            <div className="tags-container" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
              {diaryForm.tags.map(tag => (
                <span key={tag} className="diary-tag" style={{ background: 'var(--primary)', color: 'white', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {tag}
                  <button type="button" onClick={() => removeTag(tag)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: 0, fontSize: '1rem', lineHeight: 1 }}>✕</button>
                </span>
              ))}
              <input
                type="text"
                className="tag-input"
                placeholder="VD: study, relationship..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleAddTag}
                style={{ border: 'none', outline: 'none', padding: '0.25rem 0.5rem', background: 'transparent', color: 'var(--text-primary)', fontSize: '0.9rem', minWidth: '150px' }}
              />
            </div>
          </div>

          <textarea
            className="diary-content-input"
            placeholder="Hãy viết ra những suy nghĩ của bạn ngày hôm nay..."
            value={diaryForm.content}
            onChange={(e) => setDiaryForm({ ...diaryForm, content: e.target.value })}
            style={{ flex: 1, border: '1px solid var(--border-color)', borderRadius: '12px', background: 'white', color: 'var(--text-primary)', fontSize: '1.05rem', lineHeight: 1.6, outline: 'none', resize: 'none', minHeight: '60vh', padding: '1.5rem', boxShadow: '0 8px 24px rgba(27, 122, 138, 0.08), inset 0 2px 4px rgba(0,0,0,0.02)', transition: 'box-shadow 0.3s' }}
          ></textarea>

          <div style={{ flex: 1, paddingBottom: '6rem' }}></div>
        </div>

        {/* Nút Tạo nhật ký góc dưới phải */}
        <button
          onClick={startNewDiary}
          style={{ position: 'absolute', bottom: '2rem', right: '2rem', width: '64px', height: '64px', borderRadius: '50%', background: 'var(--primary)', color: 'white', border: 'none', boxShadow: '0 4px 15px rgba(27, 122, 138, 0.4)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, transition: 'transform 0.2s, background 0.2s' }}
          title="Tạo nhật ký mới"
          onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.background = 'var(--primary-hover)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.background = 'var(--primary)'; }}
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="32" height="32">
            <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default DiaryViewer;
