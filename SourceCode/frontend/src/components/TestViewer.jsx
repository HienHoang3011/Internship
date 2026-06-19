import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './TestViewer.css';
import gameBg1 from '../assets/game-bg1.jpg';
import logoWeb from '../assets/logo-web-transparent.png';
import { apiFetch } from '../utils/api';

const TestViewer = ({ initialId, onBack, handleLogout }) => {
  const [viewState, setViewState] = useState('list'); // 'list' | 'taking' | 'result'
  const [tests, setTests] = useState([]);
  const [activeTest, setActiveTest] = useState(null);
  const [answers, setAnswers] = useState({}); // { question_id: option_id }
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [testHistory, setTestHistory] = useState([]);
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  const [testResult, setTestResult] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showHistoryAnswers, setShowHistoryAnswers] = useState(false);

  const [isTestsLoaded, setIsTestsLoaded] = useState(false);

  useEffect(() => {
    async function fetchTests() {
      try {
        const res = await apiFetch("http://localhost:8000/api/tests/");
        if (res.status === 401) return;
        if (res.ok) {
          const data = await res.json();
          setTests(data);
          setIsTestsLoaded(true);
        }
      } catch (err) { console.error(err); }
    }
    if (!isTestsLoaded) {
      fetchTests();
    }
  }, [isTestsLoaded]);

  useEffect(() => {
    if (isTestsLoaded) {
      if (initialId) {
        const test = tests.find(t => t.id === parseInt(initialId));
        if (test) {
          handleViewTestDetail(test, false);
        } else {
          setViewState('list');
        }
      } else {
        setActiveTest(null);
        setViewState('list');
      }
    }
  }, [initialId, isTestsLoaded, tests]);

  const handleViewTestDetail = async (test, updateHash = true) => {
    setActiveTest(test);
    setViewState('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (updateHash) window.location.hash = `test/${test.id}`;
    
    // Fetch history
    try {
      const res = await apiFetch("http://localhost:8000/api/tests/results/");
      if (res.ok) {
        const data = await res.json();
        // Filter history for this specific test
        const historyForTest = data.filter(item => item.test === test.id);
        // Sort by created_at descending
        historyForTest.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setTestHistory(historyForTest);
      }
    } catch (err) { console.error(err); }
  };

  const handleStartTest = () => {
    setAnswers({});
    setCurrentQuestionIndex(0);
    setViewState('taking');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleViewHistoryDetail = (result) => {
    setTestResult(result);
    setAiAnalysis(result.ai_analysis || '');
    setShowHistoryAnswers(false);
    setViewState('result');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOptionSelect = (questionId, optionId) => {
    setAnswers({ ...answers, [questionId]: optionId });
  };

  const handleSubmitTest = async () => {
    if (Object.keys(answers).length < activeTest.questions.length) {
      alert("Vui lòng trả lời tất cả các câu hỏi!");
      return;
    }

    const answersPayload = [];
    let rawResult = {};
    
    activeTest.questions.forEach(q => {
      const selectedOptId = answers[q.id];
      const selectedOpt = q.options.find(o => o.id === parseInt(selectedOptId));
      
      answersPayload.push({
        question_id: q.id,
        question: q.question_text,
        answer: selectedOpt.option_text,
        score: selectedOpt.score
      });

      if (q.dimension && selectedOpt.score !== null) {
        if (!rawResult[q.dimension]) rawResult[q.dimension] = 0;
        
        let scoreVal = parseFloat(selectedOpt.score);
        // Nhân 2 điểm nếu là bài test DASS-21 để quy về thang đo DASS-42
        if (activeTest.name && activeTest.name.includes("DASS-21")) {
          scoreVal *= 2;
        }
        rawResult[q.dimension] += scoreVal;
      }
    });

    try {
      const res = await apiFetch("http://localhost:8000/api/tests/results/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          test: activeTest.id,
          answers: answersPayload,
          raw_result: rawResult
        })
      });
      if (res.ok) {
        const resultData = await res.json();
        setTestResult(resultData);
        setViewState('result');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        alert("Có lỗi xảy ra khi nộp bài!");
      }
    } catch (err) { console.error(err); }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const res = await apiFetch(`http://localhost:8000/api/tests/results/${testResult.id}/analyze/`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setAiAnalysis(data.analysis);
      } else {
        alert("Lỗi khi phân tích bằng AI");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const filteredTests = tests.filter(t => {
    const q = searchQuery.toLowerCase();
    const nameMatch = t.name && t.name.toLowerCase().includes(q);
    const descMatch = t.description && t.description.toLowerCase().includes(q);
    return nameMatch || descMatch;
  });
  
  const clinicalTests = filteredTests.filter(t => t.type && t.type.toLowerCase() === 'clinical');
  const personalityTests = filteredTests.filter(t => t.type && t.type.toLowerCase() === 'personality');

  return (
    <div className={`test-viewer-container ${viewState === 'taking' ? 'taking-mode' : ''}`} style={viewState === 'taking' ? { backgroundImage: `url(${gameBg1})` } : {}}>
      {viewState === 'list' && (
        <button onClick={onBack} className="btn-back-absolute" style={{ top: '1.5rem', left: '2rem', zIndex: 50, background: 'rgba(255, 255, 255, 0.5)', backdropFilter: 'blur(10px)' }} title="Trở về trang chính">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Quay lại
        </button>
      )}
      {viewState === 'detail' && (
        <button onClick={() => setViewState('list')} className="btn-back-absolute" style={{ zIndex: 20 }} title="Trở về danh sách Test">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Danh sách
        </button>
      )}
      
      {viewState === 'list' && (
        <div className="test-list-wrapper">
          <div className="test-hero-section">
            <div className="test-hero-content">
              <h1>Thư viện Bài Test Tâm lý</h1>
              <p>Khám phá bản thân qua các bài trắc nghiệm chuẩn khoa học</p>
              <form 
                className="test-search-form"
                onSubmit={(e) => { e.preventDefault(); setSearchQuery(searchInput); }}
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
                <input 
                  type="text" 
                  placeholder="Tìm kiếm bài test (ví dụ: Trầm cảm, lo âu...)"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                />
                <button type="submit">Tìm kiếm</button>
              </form>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1400px', margin: '-3rem auto 4rem auto', padding: '0 2rem', position: 'relative', zIndex: 10 }}>
            
            <div className="test-category-box">
              <div className="test-category-header">
                <h2 className="category-title" style={{ margin: 0 }}>Test tâm lý chuyên sâu</h2>
                <img src={logoWeb} alt="MindCareAI" className="category-logo" />
              </div>
              {clinicalTests.length > 0 ? (
                <div className="test-grid">
                  {clinicalTests.map(t => (
                    <div key={t.id} className="test-card">
                      {t.image_url && <img src={t.image_url} alt={t.name} className="test-card-img" />}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <div className="test-type-badge" style={{ marginBottom: 0 }}>{t.type}</div>
                        <div className="test-question-count">
                          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                          {t.questions ? t.questions.length : 21} câu hỏi
                        </div>
                      </div>
                      <h3>{t.name}</h3>
                      <p>{t.description}</p>
                      <button className="btn-test-card-start" onClick={() => handleViewTestDetail(t)}>
                        Bắt Đầu Làm Bài
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-category-note">Hiện tại chưa có bài test nào trong mục này. Sẽ có sẵn sau!</div>
              )}
            </div>

            <div className="test-category-box">
              <div className="test-category-header">
                <h2 className="category-title" style={{ margin: 0 }}>Trắc nghiệm tính cách</h2>
                <img src={logoWeb} alt="MindCareAI" className="category-logo" />
              </div>
              {personalityTests.length > 0 ? (
                <div className="test-grid">
                  {personalityTests.map(t => (
                    <div key={t.id} className="test-card">
                      {t.image_url && <img src={t.image_url} alt={t.name} className="test-card-img" />}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <div className="test-type-badge" style={{ marginBottom: 0 }}>{t.type}</div>
                        <div className="test-question-count">
                          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                          {t.questions ? t.questions.length : 10} câu hỏi
                        </div>
                      </div>
                      <h3>{t.name}</h3>
                      <p>{t.description}</p>
                      <button className="btn-test-card-start" onClick={() => handleViewTestDetail(t)}>
                        Bắt Đầu Làm Bài
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-category-note">Hiện tại chưa có bài test nào trong mục này. Sẽ có sẵn sau!</div>
              )}
            </div>

          </div>
        </div>
      )}

      {viewState === 'detail' && activeTest && (
        <div className="test-detail-page">
          <div className="test-detail-cover" style={{ backgroundImage: activeTest.image_url ? `url(${activeTest.image_url})` : 'linear-gradient(135deg, var(--primary) 0%, #299fa8 100%)' }}>
            <div className="test-detail-cover-overlay"></div>
          </div>
          
          <div className="test-detail-content-wrapper">
            <div className="test-detail-floating-card">
              <div className="floating-card-header">
                <div className="test-type-badge-large">{activeTest.type}</div>
                <div className="floating-meta">
                  <span className="meta-icon"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
                  {activeTest.questions.length} câu hỏi
                </div>
              </div>
              <h2 className="test-detail-title-large">{activeTest.name}</h2>
              <p className="test-detail-desc-large">{activeTest.description}</p>
              
              <button className="btn-start-massive" onClick={handleStartTest}>
                Bắt Đầu Làm Bài
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
            </div>

            <div className="test-history-section">
              <div className="history-section-header">
                <h3>Lịch sử của bạn</h3>
                <p>Xem lại sự tiến bộ của bản thân qua các lần làm bài trước đây.</p>
              </div>
              
              {testHistory.length > 0 ? (
                <div className="history-grid">
                  {testHistory.map((history, index) => (
                    <div key={history.id} className="history-card" onClick={() => handleViewHistoryDetail(history)}>
                      <div className="history-card-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                      </div>
                      <div className="history-card-content">
                        <h4>Lần {testHistory.length - index}</h4>
                        <span>{new Date(history.created_at).toLocaleDateString('vi-VN')}</span>
                      </div>
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#9ca3af" strokeWidth="2"><path d="M9 5l7 7-7 7"/></svg>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="history-empty-state">
                  <div className="empty-icon">📝</div>
                  <h4>Chưa có dữ liệu</h4>
                  <p>Bạn chưa từng làm bài test này. Hãy bắt đầu ngay để khám phá bản thân nhé!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {viewState === 'taking' && activeTest && (
        <div>
          <button onClick={() => setViewState('detail')} className="btn-back-absolute" style={{ top: '1rem', left: '1rem' }} title="Thoát khỏi bài">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
            Thoát
          </button>
          <div className="test-taking-header">
            <h2>{activeTest.name}</h2>
          </div>

          <div className="progress-container">
            <div className="progress-text">
              <span className="progress-label">Tiến trình</span>
              <span className="progress-percentage">{Math.round(((currentQuestionIndex) / activeTest.questions.length) * 100)}%</span>
            </div>
            <div className="progress-bar-bg">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${((currentQuestionIndex) / activeTest.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>

          {activeTest.questions.length > 0 && (
            <div className="wizard-question-card" key={currentQuestionIndex}>
              <h4 className="question-title">
                {activeTest.questions[currentQuestionIndex].question_text}
              </h4>
              <div className="options-grid">
                {activeTest.questions[currentQuestionIndex].options.map(opt => (
                  <label key={opt.id} className={`option-label ${answers[activeTest.questions[currentQuestionIndex].id] == opt.id ? 'selected' : ''}`}>
                    <input 
                      type="radio" 
                      name={`question_${activeTest.questions[currentQuestionIndex].id}`} 
                      value={opt.id}
                      checked={answers[activeTest.questions[currentQuestionIndex].id] == opt.id}
                      onChange={() => handleOptionSelect(activeTest.questions[currentQuestionIndex].id, opt.id)}
                      style={{ display: 'none' }}
                    />
                    <div className="radio-circle"></div>
                    {opt.option_text}
                  </label>
                ))}
              </div>

              <div className="wizard-navigation">
                <button 
                  className="btn-wizard-nav btn-wizard-prev" 
                  onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
                  disabled={currentQuestionIndex === 0}
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
                  Quay lại
                </button>

                {currentQuestionIndex === activeTest.questions.length - 1 ? (
                  <button 
                    className="btn-wizard-nav btn-wizard-next" 
                    onClick={handleSubmitTest}
                    disabled={Object.keys(answers).length < activeTest.questions.length}
                  >
                    Hoàn thành
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                  </button>
                ) : (
                  <button 
                    className="btn-wizard-nav btn-wizard-next" 
                    onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
                    disabled={!answers[activeTest.questions[currentQuestionIndex].id]}
                  >
                    Tiếp tục
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {viewState === 'result' && testResult && (
        <div className="result-container">
          <button onClick={() => setViewState('detail')} className="btn-back-normal" title="Trở về trang chi tiết">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Quay lại
          </button>
          <div className="result-icon">✨</div>
          <h2 className="result-title">Tuyệt vời! Bạn đã hoàn thành.</h2>
          <p className="result-subtitle">Hệ thống đã phân tích sơ bộ các câu trả lời của bạn.</p>

          {!aiAnalysis ? (
            <div className="analysis-box">
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>Khám phá ý nghĩa chuyên sâu</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>MindCareAI sẽ đọc chi tiết từng lựa chọn của bạn để đưa ra bức tranh toàn cảnh về sức khỏe tinh thần và gợi ý các bước tiếp theo dành riêng cho bạn.</p>
              <button className="btn-primary" onClick={handleAnalyze} disabled={isAnalyzing} style={{ padding: '1rem 2rem', fontSize: '1.1rem', borderRadius: '12px' }}>
                {isAnalyzing ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <svg className="spinner" viewBox="0 0 50 50" width="20" height="20" style={{ animation: 'spin 1s linear infinite' }}>
                      <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="4" strokeDasharray="90 150" strokeLinecap="round"></circle>
                    </svg>
                    Đang phân tích dữ liệu...
                  </span>
                ) : '🔮 Xem Phân Tích Của AI'}
              </button>
            </div>
          ) : (
            <div className="analysis-content">
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                Góc Nhìn Của Chuyên Gia AI
              </h3>
              <div style={{ lineHeight: '1.8', color: 'var(--text-primary)', fontSize: '1.05rem' }}>
                <ReactMarkdown>{aiAnalysis}</ReactMarkdown>
              </div>
            </div>
          )}

          <div style={{ marginTop: '2rem', textAlign: 'center' }}>
            <button 
              className="btn-back-normal" 
              onClick={() => setShowHistoryAnswers(!showHistoryAnswers)}
              style={{ margin: '0 auto' }}
            >
              {showHistoryAnswers ? 'Ẩn đáp án' : 'Xem chi tiết đáp án bạn đã chọn'}
            </button>
          </div>

          {showHistoryAnswers && testResult.answers && testResult.answers.length > 0 && (
            <div className="analysis-content" style={{ marginTop: '1.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: 'var(--primary)' }}>Chi tiết đáp án</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
                {testResult.answers.map((ans, idx) => (
                  <div key={idx} style={{ padding: '1rem', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                    <p style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#111827' }}>Câu {idx + 1}: {ans.question}</p>
                    <p style={{ color: '#4b5563', margin: 0 }}>
                      <span style={{ color: 'var(--primary)', fontWeight: '500' }}>Đã chọn:</span> {ans.answer} {ans.score !== null && `(${ans.score} điểm)`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TestViewer;
