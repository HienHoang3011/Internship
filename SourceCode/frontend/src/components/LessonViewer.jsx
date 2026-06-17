import React, { useState, useEffect } from 'react';

const LessonViewer = ({ onBack }) => {
  const [lessons, setLessons] = useState([]);
  const [activeVideoId, setActiveVideoId] = useState(null);
  const [isLessonsLoaded, setIsLessonsLoaded] = useState(false);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const res = await fetch("http://localhost:8000/api/lessons/", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.status === 401) {
          alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setLessons(data);
          setIsLessonsLoaded(true);
        }
      } catch (err) {
        console.error("Lỗi khi tải bài học:", err);
      }
    };

    if (!isLessonsLoaded) {
      fetchLessons();
    }
  }, [isLessonsLoaded]);

  return (
    <div className="lesson-container" style={{ padding: '80px 2rem 4rem 2rem', background: 'var(--background)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--primary)', fontSize: '2.5rem' }}>Thư Viện Bài Học Chữa Lành</h1>

      {/* Main Video Player */}
      {activeVideoId && (
        <div className="main-player" style={{ width: '100%', maxWidth: '1000px', marginBottom: '3rem', background: 'var(--surface)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center' }}>
            <button onClick={() => setActiveVideoId(null)} style={{ background: 'none', border: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text-primary)', fontWeight: 'bold', fontSize: '1rem', padding: '0.5rem' }}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
                <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Quay lại Thư viện
            </button>
          </div>
          {(() => {
            const activeLesson = lessons.find(l => l.id === activeVideoId);
            if (!activeLesson) return null;
            const videoIdMatch = activeLesson.youtube_url.match(/(?:v=|youtu\.be\/)([^&]+)/);
            const videoId = videoIdMatch ? videoIdMatch[1] : '';
            return (
              <>
                <iframe
                  width="100%"
                  height="500"
                  src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
                  title="YouTube video player"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
                <div style={{ padding: '1.5rem' }}>
                  <h2 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>{activeLesson.title}</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: 1.6, margin: 0 }}>{activeLesson.description}</p>
                </div>
              </>
            );
          })()}
        </div>
      )}

      {/* Video Grid */}
      <div style={{ width: '100%', maxWidth: '1200px', marginBottom: '2rem' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: '1.5rem', fontSize: '1.5rem', borderBottom: '2px solid var(--border-color)', paddingBottom: '0.5rem' }}>Danh sách bài học</h2>
        <div className="lesson-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem' }}>
          {lessons.map(lesson => {
            const videoIdMatch = lesson.youtube_url.match(/(?:v=|youtu\.be\/)([^&]+)/);
            const videoId = videoIdMatch ? videoIdMatch[1] : '';
            return (
              <div key={lesson.id} className="lesson-card" style={{ background: 'var(--surface)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', transition: 'transform 0.3s', cursor: 'pointer', border: activeVideoId === lesson.id ? '2px solid var(--primary)' : '2px solid transparent' }} onClick={() => { setActiveVideoId(lesson.id); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
                <div style={{ position: 'relative', height: '180px', overflow: 'hidden' }}>
                  <img
                    src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`}
                    alt={lesson.title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  <div style={{ position: 'absolute', bottom: '10px', right: '10px', background: 'rgba(0,0,0,0.8)', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <svg viewBox="0 0 24 24" fill="white" width="12" height="12"><path d="M8 5v14l11-7z" /></svg> Phát
                  </div>
                </div>
                <div style={{ padding: '1rem' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontSize: '1.1rem', lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{lesson.title}</h3>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <button className="btn-secondary" onClick={onBack}>Về trang chủ</button>
      </div>
    </div>
  );
};

export default LessonViewer;
