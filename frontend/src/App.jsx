import React, { useState } from 'react';
import Navbar from './components/Navbar';
import AppRouter from './routes';
import { startQuizSession } from './services/api';
import './styles/global.css';
import './styles/home.css';
import './styles/topic.css';
import './styles/quiz.css';
import './styles/result.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); // home, topic, quiz, result
  const [activeSession, setActiveSession] = useState(null);
  const [loadingSession, setLoadingSession] = useState(false);

  const handleNavigateHome = () => {
    setCurrentPage('home');
    setActiveSession(null);
  };

  /**
   * Called when user picks a topic. Starts a quiz session with the FastAPI backend.
   * Backend returns: { success, quiz_id, subject, current_difficulty, question_number,
   *                    total_questions, skill_score, question: { id, question_number,
   *                    question_type, difficulty, question_text, options, ... } }
   */
  const handleTopicSelected = async (topic) => {
    setLoadingSession(true);
    try {
      const data = await startQuizSession(topic.name, 'Medium', 10);
      if (data.success) {
        setActiveSession(data);
        setCurrentPage('quiz');
      }
    } catch (err) {
      console.error('Failed to initialize quiz session:', err);
      alert('Could not connect to backend server. Make sure the FastAPI backend is running on port 5000.');
    } finally {
      setLoadingSession(false);
    }
  };

  const handleQuizCompleted = (summaryData) => {
    setActiveSession(prev => ({ ...prev, summary: summaryData }));
    setCurrentPage('result');
  };

  return (
    <div className="app-wrapper">
      <Navbar
        onNavigateHome={handleNavigateHome}
        activeSessionTopic={activeSession?.subject}
      />
      <main className="main-content">
        {loadingSession ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
            <div className="glass-panel" style={{ padding: '2.5rem 3rem', textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🧠</div>
              <p style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Generating your first question...</p>
            </div>
          </div>
        ) : (
          <AppRouter
            currentPage={currentPage}
            onNavigateTopicSelection={() => setCurrentPage('topic')}
            onTopicSelected={handleTopicSelected}
            activeSession={activeSession}
            onQuizCompleted={handleQuizCompleted}
            onRestart={() => setCurrentPage('topic')}
          />
        )}
      </main>
    </div>
  );
}
