import React from 'react';
import Home from './pages/Home';
import TopicSelection from './pages/TopicSelection';
import Quiz from './pages/Quiz';
import Result from './pages/Result';

export default function AppRouter({
  currentPage,
  onNavigateTopicSelection,
  onTopicSelected,
  activeSession,
  onQuizCompleted,
  onRestart
}) {
  switch (currentPage) {
    case 'home':
      return <Home onStartClick={onNavigateTopicSelection} />;
    case 'topic':
      return <TopicSelection onSelectTopic={onTopicSelected} />;
    case 'quiz':
      return <Quiz sessionData={activeSession} onQuizComplete={onQuizCompleted} />;
    case 'result':
      return <Result summary={activeSession?.summary} onRestart={onRestart} />;
    default:
      return <Home onStartClick={onNavigateTopicSelection} />;
  }
}
