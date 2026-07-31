import { generateQuestion } from '../services/llmService.js';

// In-memory session state storage for demonstration / active sessions
const sessions = new Map();

const AVAILABLE_TOPICS = [
  { id: 'dsa', name: 'Data Structures & Algorithms', description: 'Trees, Graphs, Sorting, Dynamic Programming & Big-O' },
  { id: 'webdev', name: 'Web Development & React', description: 'Modern JS, React Hooks, HTML5/CSS, DOM & Web Performance' },
  { id: 'ml', name: 'Machine Learning & AI', description: 'Neural Networks, Supervised/Unsupervised Learning & Transformers' }
];

export const getTopics = (req, res) => {
  return res.status(200).json({ success: true, topics: AVAILABLE_TOPICS });
};

export const startQuiz = async (req, res) => {
  try {
    const { topic = 'Data Structures & Algorithms', initialDifficulty = 'Medium' } = req.body;
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const initialQuestion = await generateQuestion(topic, initialDifficulty, 1);

    const sessionData = {
      sessionId,
      topic,
      currentDifficulty: initialDifficulty,
      currentQuestionIndex: 1,
      totalScore: 0,
      history: [],
      streak: 0,
      createdAt: new Date()
    };

    sessions.set(sessionId, sessionData);

    return res.status(200).json({
      success: true,
      sessionId,
      topic,
      currentDifficulty: initialDifficulty,
      questionNumber: 1,
      totalQuestions: 10,
      question: {
        id: initialQuestion.id,
        difficulty: initialQuestion.difficulty,
        question: initialQuestion.question,
        options: initialQuestion.options
      }
    });
  } catch (err) {
    console.error('Error starting quiz:', err);
    return res.status(500).json({ success: false, message: 'Failed to start quiz session' });
  }
};

export const getSession = (sessionId) => sessions.get(sessionId);
export const saveSession = (sessionId, data) => sessions.set(sessionId, data);
