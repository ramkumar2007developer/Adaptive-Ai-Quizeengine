import React from 'react';

/**
 * Renders a single topic card in the topic selection grid.
 * topic shape: { id, name, description, icon }
 */
export default function TopicCard({ topic, onSelect }) {
  return (
    <div className="topic-card" onClick={() => onSelect(topic)}>
      <div>
        <div className="topic-icon-badge">{topic.icon ?? '🧠'}</div>
        <h3 className="topic-title">{topic.name}</h3>
        <p className="topic-desc">{topic.description}</p>
      </div>

      <div className="topic-action-btn">
        <span>Start Quiz</span>
        <span>→</span>
      </div>
    </div>
  );
}
