import express from 'express';
import { getTopics, startQuiz } from '../controllers/quizController.js';
import { submitAnswer } from '../controllers/answerController.js';

const router = express.Router();

router.get('/topics', getTopics);
router.post('/start', startQuiz);
router.post('/answer', submitAnswer);

export default router;
