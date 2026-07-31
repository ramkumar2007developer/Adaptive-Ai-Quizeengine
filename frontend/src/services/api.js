const BASE_URL = '/api/quiz';

/**
 * Fetch the list of available quiz topics from the backend.
 */
export async function fetchTopics() {
  const res = await fetch(`${BASE_URL}/topics`);
  if (!res.ok) throw new Error('Failed to fetch available topics');
  return res.json();
}

/**
 * Start a new quiz session.
 * @param {string} subject - The topic/subject name
 * @param {string} difficulty - "Easy" | "Medium" | "Hard"
 * @param {number} numQuestions - Number of questions (default 10)
 */
export async function startQuizSession(subject, difficulty = 'Medium', numQuestions = 10) {
  const res = await fetch(`${BASE_URL}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      subject,
      difficulty,
      num_questions: numQuestions,
      use_rag: false,
    }),
  });
  if (!res.ok) throw new Error('Failed to start quiz session');
  return res.json();
}

/**
 * Submit an answer for the current question.
 * @param {object} payload
 * @param {string} payload.quizId - Quiz session ID
 * @param {string} payload.questionId - Current question ID
 * @param {number} payload.selectedIndex - Index of the chosen option (0-3)
 * @param {string} payload.selectedAnswer - Text of the chosen option
 * @param {number} payload.responseTimeSeconds - Time taken to answer in seconds
 */
export async function submitQuizAnswer({ quizId, questionId, selectedIndex, selectedAnswer, responseTimeSeconds }) {
  const res = await fetch(`${BASE_URL}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quiz_id: quizId,
      question_id: questionId,
      selected_index: selectedIndex,
      selected_answer: selectedAnswer ?? '',
      response_time_seconds: responseTimeSeconds ?? 10,
    }),
  });
  if (!res.ok) throw new Error('Failed to submit answer');
  return res.json();
}
