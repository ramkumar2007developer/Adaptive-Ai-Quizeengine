import React from 'react';

export default function ProgressBar({ current, total }) {
  const percentage = Math.min(100, Math.max(0, (current / total) * 100));

  return (
    <div className="progress-container">
      <div className="progress-fill" style={{ width: `${percentage}%` }} />
    </div>
  );
}
