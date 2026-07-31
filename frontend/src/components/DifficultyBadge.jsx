import React from 'react';

export default function DifficultyBadge({ difficulty }) {
  const getStyles = () => {
    switch (difficulty) {
      case 'Easy':
        return { color: 'var(--easy-color)', bg: 'var(--easy-bg)', label: '🌱 Easy' };
      case 'Medium':
        return { color: 'var(--medium-color)', bg: 'var(--medium-bg)', label: '⚡ Medium' };
      case 'Hard':
        return { color: 'var(--hard-color)', bg: 'var(--hard-bg)', label: '🔥 Hard' };
      default:
        return { color: 'var(--text-muted)', bg: 'rgba(255,255,255,0.1)', label: difficulty };
    }
  };

  const style = getStyles();

  return (
    <div style={{
      padding: '0.35rem 0.85rem',
      borderRadius: 'var(--radius-full)',
      fontSize: '0.85rem',
      fontWeight: 700,
      color: style.color,
      backgroundColor: style.bg,
      border: `1px solid ${style.color}`,
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.35rem'
    }}>
      {style.label}
    </div>
  );
}
