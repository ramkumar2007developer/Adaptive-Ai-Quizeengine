import React, { useEffect, useState } from 'react';
import TopicCard from '../components/TopicCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchTopics } from '../services/api';

export default function TopicSelection({ onSelectTopic }) {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTopics()
      .then(data => {
        setTopics(data.topics || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to connect to backend server. Ensure backend is running.');
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingSpinner message="Loading available quiz topics..." />;

  return (
    <div className="topic-container fade-in">
      <div className="topic-header">
        <h2>Select Your Challenge Topic</h2>
        <p>Choose a domain to start your personalized adaptive learning quiz</p>
      </div>

      {error && (
        <div style={{ color: 'var(--hard-color)', marginBottom: '1.5rem', fontWeight: 600 }}>
          {error}
        </div>
      )}

      <div className="topics-grid">
        {topics.map(topic => (
          <TopicCard key={topic.id} topic={topic} onSelect={onSelectTopic} />
        ))}
      </div>
    </div>
  );
}
