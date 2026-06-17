import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils/api';

const LessonViewer = ({ initialId, onBack }) => {
  const [lessons, setLessons] = useState([]);
  const [activeVideoId, setActiveVideoId] = useState(null);
  const [isLessonsLoaded, setIsLessonsLoaded] = useState(false);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const res = await apiFetch("http://localhost:8000/api/lessons/");
        if (res.status === 401) return;
        if (res.ok) {
          const data = await res.json();
          setLessons(data);
        }
      } catch (err) {
        console.error("Lỗi khi tải bài học:", err);
      }
    };

    if (!isLessonsLoaded) {
      fetchLessons();
      setIsLessonsLoaded(true);
    }
  }, [isLessonsLoaded]);

  useEffect(() => {
    if (isLessonsLoaded) {
      if (initialId) {
        setActiveVideoId(initialId);
      } else {
        setActiveVideoId(null);
      }
    }
  }, [initialId, isLessonsLoaded]);

  const handleSelectVideo = (id) => {
    setActiveVideoId(id);
    window.location.hash = `lesson/${id}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="lesson-container" style={{ position: 'relative', padding: '80px 2rem 4rem 2rem', background: 'var(--background)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--primary)', fontSize: '2.5rem' }}>Thư Viện Bài Học Chữa Lành</h1>

      {/* Main Video Player */}
      {activeVideoId && (
        <div className="main-player" style={{ width: '100%', maxWidth: '1000px', marginBottom: '3rem', background: 'var(--surface)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center' }}>
            <button onClick={() => { setActiveVideoId(null); window.location.hash = 'lesson'; }} style={{ background: 'none', border: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text-primary)', fontWeight: 'bold', fontSize: '1rem', padding: '0.5rem' }}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
                <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Quay lại Thư viện
            </button>
          </div>
          {(() => {
            const activeLesson = lessons.find(l => l.id == activeVideoId);
            if (!activeLesson) return null;
            const videoIdMatch = activeLesson.youtube_url ? activeLesson.youtube_url.match(/(?:v=|youtu\.be\/)([^&]+)/) : null;
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
                <div style={{ padding: '2rem' }}>
                  <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>{activeLesson.title}</h2>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.8', fontSize: '1.1rem' }}>{activeLesson.description}</p>
                </div>
              </>
            );
          })()}
        </div>
      )}

      {/* Video Grid */}
      <div style={{ width: '100%', maxWidth: '1200px', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Chọn một bài học dưới đây để bắt đầu hoặc tiếp tục hành trình của bạn.</p>
        </div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
          {lessons.map(lesson => {
            const videoIdMatch = lesson.youtube_url ? lesson.youtube_url.match(/(?:v=|youtu\.be\/)([^&]+)/) : null;
            const videoId = videoIdMatch ? videoIdMatch[1] : '';
            
            return (
              <div 
                key={lesson.id} 
                className="lesson-card"
                onClick={() => handleSelectVideo(lesson.id)}
                style={{ 
                  background: 'var(--surface)', 
                  borderRadius: '12px', 
                  overflow: 'hidden', 
                  boxShadow: '0 4px 6px rgba(0,0,0,0.05)', 
                  cursor: 'pointer', 
                  transition: 'transform 0.2s, boxShadow 0.2s',
                  display: 'flex',
                  flexDirection: 'column'
                }}
                onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-5px)'; e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)'; }}
                onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)'; }}
              >
                <div style={{ position: 'relative', width: '100%', paddingTop: '56.25%' }}>
                  <img 
                    src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`} 
                    alt={lesson.title} 
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ width: '48px', height: '48px', background: 'rgba(255,255,255,0.9)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <svg viewBox="0 0 24 24" fill="var(--primary-color)" width="24" height="24" style={{ marginLeft: '4px' }}>
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                  </div>
                </div>
                <div style={{ padding: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontSize: '1.25rem', lineHeight: '1.4' }}>{lesson.title}</h3>
                  <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', flex: 1, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {lesson.description}
                  </p>
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
