import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = ({ handleLogout }) => {
  const [activeTab, setActiveTab] = useState('lessons'); // 'lessons' | 'tests'
  
  // Lessons State
  const [lessons, setLessons] = useState([]);
  const [lessonForm, setLessonForm] = useState({ title: '', description: '', youtube_url: '' });
  const [editingLessonId, setEditingLessonId] = useState(null);
  
  // Tests State
  const [tests, setTests] = useState([]);
  const [testForm, setTestForm] = useState({ name: '', type: 'clinical', description: '', image_url: '', questions: [] });
  const [editingTestId, setEditingTestId] = useState(null);
  
  const token = localStorage.getItem("accessToken");

  async function fetchLessons() {
    try {
      const res = await fetch("http://localhost:8000/api/lessons/", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.status === 401) {
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        handleLogout();
        return;
      }
      if (res.ok) setLessons(await res.json());
    } catch (err) { console.error(err); }
  }

  async function fetchTests() {
    try {
      const res = await fetch("http://localhost:8000/api/tests/", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.status === 401) {
        alert("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại!");
        handleLogout();
        return;
      }
      if (res.ok) setTests(await res.json());
    } catch (err) { console.error(err); }
  }

  useEffect(() => {
    fetchLessons();
    fetchTests();
  }, [token]);

  const handleLessonSubmit = async (e) => {
    e.preventDefault();
    const isEdit = !!editingLessonId;
    const url = isEdit ? `http://localhost:8000/api/lessons/${editingLessonId}/` : "http://localhost:8000/api/lessons/";
    const method = isEdit ? "PUT" : "POST";
    try {
      const res = await fetch(url, {
        method: method,
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(lessonForm)
      });
      if (res.ok) {
        alert(isEdit ? "Cập nhật bài học thành công!" : "Thêm bài học thành công!");
        setLessonForm({ title: '', description: '', youtube_url: '' });
        setEditingLessonId(null);
        fetchLessons();
      } else {
        alert(isEdit ? "Lỗi khi cập nhật bài học" : "Lỗi khi thêm bài học");
      }
    } catch (err) { console.error(err); }
  };

  const handleEditLesson = (l) => {
    setEditingLessonId(l.id);
    setLessonForm({ title: l.title, description: l.description, youtube_url: l.youtube_url });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteLesson = async (id) => {
    if(!window.confirm("Xóa bài học này?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/lessons/${id}/`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if(res.ok) fetchLessons();
    } catch (err) { console.error(err); }
  };

  const addQuestion = () => {
    setTestForm({
      ...testForm,
      questions: [...testForm.questions, { question_text: '', dimension: '', order_number: testForm.questions.length + 1, options: [] }]
    });
  };

  const addOption = (qIndex) => {
    const newQuestions = [...testForm.questions];
    newQuestions[qIndex].options.push({ option_text: '', score: 0 });
    setTestForm({ ...testForm, questions: newQuestions });
  };

  const handleTestSubmit = async (e) => {
    e.preventDefault();
    const isEdit = !!editingTestId;
    const url = isEdit ? `http://localhost:8000/api/tests/${editingTestId}/` : "http://localhost:8000/api/tests/";
    const method = isEdit ? "PUT" : "POST";
    try {
      const res = await fetch(url, {
        method: method,
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(testForm)
      });
      if (res.ok) {
        alert(isEdit ? "Cập nhật bài kiểm tra thành công!" : "Thêm bài kiểm tra thành công!");
        setTestForm({ name: '', type: 'clinical', description: '', image_url: '', questions: [] });
        setEditingTestId(null);
        fetchTests();
      } else {
        alert(isEdit ? "Lỗi khi cập nhật bài kiểm tra" : "Lỗi khi thêm bài kiểm tra");
      }
    } catch (err) { console.error(err); }
  };

  const handleEditTest = (t) => {
    setEditingTestId(t.id);
    setTestForm({ name: t.name, type: t.type, description: t.description, image_url: t.image_url, questions: t.questions });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteTest = async (id) => {
    if(!window.confirm("Xóa bài test này?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/tests/${id}/`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if(res.ok) fetchTests();
    } catch (err) { console.error(err); }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h2>Admin Dashboard</h2>
        <button onClick={handleLogout} className="logout-btn" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#e74c3c', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>
          Đăng xuất
        </button>
      </div>
      
      <div className="tabs-container">
        <button className={`tab-btn ${activeTab === 'lessons' ? 'active' : 'inactive'}`} onClick={() => setActiveTab('lessons')}>
          Quản lý Bài học
        </button>
        <button className={`tab-btn ${activeTab === 'tests' ? 'active' : 'inactive'}`} onClick={() => setActiveTab('tests')}>
          Quản lý Bài Test
        </button>
      </div>

      <div className="admin-content-grid">
        {activeTab === 'lessons' && (
          <>
            <div className="admin-card">
              <h3>{editingLessonId ? 'Sửa Bài Học' : 'Thêm Bài Học Mới'}</h3>
              <form onSubmit={handleLessonSubmit} className="admin-form">
                <div className="admin-input-group">
                  <label>Tiêu đề bài học</label>
                  <input type="text" className="admin-input" placeholder="Nhập tiêu đề..." value={lessonForm.title} onChange={e => setLessonForm({...lessonForm, title: e.target.value})} required />
                </div>
                <div className="admin-input-group">
                  <label>Mô tả chi tiết</label>
                  <textarea className="admin-textarea" placeholder="Nhập mô tả bài học..." value={lessonForm.description} onChange={e => setLessonForm({...lessonForm, description: e.target.value})} required />
                </div>
                <div className="admin-input-group">
                  <label>YouTube URL</label>
                  <input type="url" className="admin-input" placeholder="https://youtube.com/watch?v=..." value={lessonForm.youtube_url} onChange={e => setLessonForm({...lessonForm, youtube_url: e.target.value})} required />
                </div>
                <div>
                  <button type="submit" className="admin-submit-btn">{editingLessonId ? 'CẬP NHẬT BÀI HỌC' : 'THÊM BÀI HỌC MỚI'}</button>
                  {editingLessonId && (
                    <button type="button" className="cancel-btn" onClick={() => { setEditingLessonId(null); setLessonForm({ title: '', description: '', youtube_url: '' }); }}>HỦY SỬA</button>
                  )}
                </div>
              </form>
            </div>

            <div className="admin-card">
              <h3>Danh sách Bài học</h3>
              <div className="list-container">
                {lessons.map(l => {
                  const videoIdMatch = l.youtube_url ? l.youtube_url.match(/(?:v=|youtu\.be\/)([^&]+)/) : null;
                  const videoId = videoIdMatch ? videoIdMatch[1] : '';
                  return (
                    <div key={l.id} className="list-item" style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '0.5rem 0' }}>
                      <img src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`} alt="thumbnail" style={{ width: '120px', height: '68px', objectFit: 'cover', borderRadius: '4px' }} />
                      <div style={{ flex: 1 }}>
                        <span className="item-title">{l.title}</span>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button onClick={() => handleEditLesson(l)} className="edit-btn">Sửa</button>
                        <button onClick={() => handleDeleteLesson(l.id)} className="delete-btn">Xóa</button>
                      </div>
                    </div>
                  );
                })}
                {lessons.length === 0 && <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Chưa có bài học nào.</p>}
              </div>
            </div>
          </>
        )}

        {activeTab === 'tests' && (
          <>
            <div className="admin-card">
              <h3>{editingTestId ? 'Sửa Bài Kiểm Tra' : 'Thêm Bài Kiểm Tra Mới'}</h3>
              <form onSubmit={handleTestSubmit} className="admin-form">
                <div className="admin-input-group">
                  <label>Tên bài test</label>
                  <input type="text" className="admin-input" placeholder="VD: Bài kiểm tra mức độ stress DASS-21" value={testForm.name} onChange={e => setTestForm({...testForm, name: e.target.value})} required />
                </div>
                <div className="admin-input-group">
                  <label>Loại bài test</label>
                  <select className="admin-select" value={testForm.type} onChange={e => setTestForm({...testForm, type: e.target.value})}>
                    <option value="clinical">Clinical (Đánh giá lâm sàng)</option>
                    <option value="personality">Personality (Khám phá tính cách)</option>
                  </select>
                </div>
                <div className="admin-input-group">
                  <label>Mô tả</label>
                  <textarea className="admin-textarea" placeholder="Nhập mô tả ngắn gọn về bài kiểm tra..." value={testForm.description} onChange={e => setTestForm({...testForm, description: e.target.value})} />
                </div>
                <div className="admin-input-group">
                  <label>URL Hình ảnh (Tùy chọn)</label>
                  <input type="url" className="admin-input" placeholder="https://example.com/image.jpg" value={testForm.image_url} onChange={e => setTestForm({...testForm, image_url: e.target.value})} />
                </div>
                
                <h4 style={{ marginTop: '1rem', marginBottom: '0', color: 'var(--text-primary)' }}>Danh sách Câu hỏi</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {testForm.questions.map((q, qIndex) => (
                    <div key={qIndex} className="question-box">
                      <h4>Câu hỏi {qIndex + 1}</h4>
                      <div className="admin-input-group" style={{ marginBottom: '1rem' }}>
                        <input type="text" className="admin-input" placeholder="Nhập nội dung câu hỏi..." value={q.question_text} onChange={e => {
                          const newQ = [...testForm.questions];
                          newQ[qIndex].question_text = e.target.value;
                          setTestForm({...testForm, questions: newQ});
                        }} required />
                      </div>
                      <div className="admin-input-group" style={{ marginBottom: '1rem' }}>
                        <input type="text" className="admin-input" placeholder="Dimension (Phân loại, VD: stress) - Tùy chọn" value={q.dimension} onChange={e => {
                          const newQ = [...testForm.questions];
                          newQ[qIndex].dimension = e.target.value;
                          setTestForm({...testForm, questions: newQ});
                        }} />
                      </div>
                      
                      <h5 style={{ marginTop: '0', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Tùy chọn trả lời:</h5>
                      {q.options.map((opt, optIndex) => (
                        <div key={optIndex} className="option-row">
                          <input type="text" className="admin-input" placeholder={`Đáp án ${optIndex + 1}`} value={opt.option_text} onChange={e => {
                            const newQ = [...testForm.questions];
                            newQ[qIndex].options[optIndex].option_text = e.target.value;
                            setTestForm({...testForm, questions: newQ});
                          }} required />
                          <input type="number" className="admin-input" placeholder="Điểm số" value={opt.score} onChange={e => {
                            const newQ = [...testForm.questions];
                            newQ[qIndex].options[optIndex].score = e.target.value;
                            setTestForm({...testForm, questions: newQ});
                          }} />
                        </div>
                      ))}
                      <button type="button" className="add-btn" onClick={() => addOption(qIndex)}>+ Thêm đáp án</button>
                    </div>
                  ))}
                </div>
                <button type="button" className="add-btn" onClick={addQuestion} style={{ alignSelf: 'flex-start', marginTop: '0.5rem' }}>+ Thêm câu hỏi mới</button>
                <div>
                  <button type="submit" className="admin-submit-btn" style={{ marginTop: '2rem' }}>{editingTestId ? 'CẬP NHẬT BÀI KIỂM TRA' : 'LƯU BÀI KIỂM TRA'}</button>
                  {editingTestId && (
                    <button type="button" className="cancel-btn" onClick={() => { setEditingTestId(null); setTestForm({ name: '', type: 'clinical', description: '', image_url: '', questions: [] }); }}>HỦY SỬA</button>
                  )}
                </div>
              </form>
            </div>

            <div className="admin-card">
              <h3>Danh sách Bài kiểm tra</h3>
              <div className="list-container">
                {tests.map(t => (
                  <div key={t.id} className="list-item" style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '0.5rem 0' }}>
                    {t.image_url ? (
                      <img src={t.image_url} alt="thumbnail" style={{ width: '120px', height: '68px', objectFit: 'cover', borderRadius: '4px' }} />
                    ) : (
                      <div style={{ width: '120px', height: '68px', background: '#e2e8f0', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.8rem' }}>No Image</div>
                    )}
                    <div style={{ flex: 1 }}>
                      <span className="item-title">{t.name}</span>
                      <span className="item-subtitle">{t.type}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => handleEditTest(t)} className="edit-btn">Sửa</button>
                      <button onClick={() => handleDeleteTest(t.id)} className="delete-btn">Xóa</button>
                    </div>
                  </div>
                ))}
                {tests.length === 0 && <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Chưa có bài kiểm tra nào.</p>}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
