import React from 'react';

export default function OptionButton({ index, optionText, isSelected, isSubmitted, isCorrect, isTargetCorrect, onClick }) {
  const letters = ['A', 'B', 'C', 'D'];

  let statusClass = '';
  if (isSelected) statusClass = 'selected';
  if (isSubmitted) {
    if (isSelected && isCorrect) statusClass = 'correct';
    else if (isSelected && !isCorrect) statusClass = 'incorrect';
    else if (isTargetCorrect) statusClass = 'correct';
  }

  return (
    <button
      className={`option-btn ${statusClass}`}
      onClick={() => onClick(index)}
      disabled={isSubmitted}
    >
      <div className="option-prefix">{letters[index]}</div>
      <div style={{ flex: 1 }}>{optionText}</div>
      {isSubmitted && isTargetCorrect && <span>✓</span>}
      {isSubmitted && isSelected && !isCorrect && <span>✕</span>}
    </button>
  );
}
