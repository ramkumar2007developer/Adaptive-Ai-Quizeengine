import app from './src/app.js';

async function runBackendTests() {
  console.log('🧪 Starting Backend API & Adaptive Engine Tests...\n');

  // Start Express server locally for testing
  const server = app.listen(5001, async () => {
    try {
      const baseUrl = 'http://localhost:5001/api/quiz';

      // Test 1: Health check & Fetch Topics
      console.log('1️⃣ Testing GET /api/quiz/topics...');
      const topicsRes = await fetch(`${baseUrl}/topics`);
      const topicsData = await topicsRes.json();
      console.log('   Status:', topicsRes.status);
      console.log('   Topics received:', topicsData.topics.map(t => t.name).join(', '));
      if (!topicsData.success || topicsData.topics.length === 0) throw new Error('Topics test failed');
      console.log('   ✅ Test 1 Passed!\n');

      // Test 2: Start Quiz Session
      console.log('2️⃣ Testing POST /api/quiz/start...');
      const startRes = await fetch(`${baseUrl}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: 'Data Structures & Algorithms', initialDifficulty: 'Medium' })
      });
      const startData = await startRes.json();
      console.log('   Session ID:', startData.sessionId);
      console.log('   Initial Difficulty:', startData.currentDifficulty);
      console.log('   First Question:', startData.question.question);
      console.log('   Options:', startData.question.options);
      if (!startData.success || !startData.sessionId) throw new Error('Start quiz test failed');
      console.log('   ✅ Test 2 Passed!\n');

      const sessionId = startData.sessionId;
      let currentQ = startData.question;

      // Test 3: Answer Question Correctly (1st correct)
      console.log('3️⃣ Testing POST /api/quiz/answer (Correct Answer)...');
      const answer1Res = await fetch(`${baseUrl}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          selectedIndex: 1,
          timeTakenSeconds: 5,
          currentQuestionData: {
            ...currentQ,
            correctAnswerIndex: 1,
            explanation: 'In a balanced BST, each step halves the search space.'
          }
        })
      });
      const answer1Data = await answer1Res.json();
      console.log('   Answer Evaluation:', answer1Data.evaluation.isCorrect ? 'CORRECT' : 'INCORRECT');
      console.log('   Points Awarded:', answer1Data.evaluation.pointsAwarded);
      console.log('   Total Score:', answer1Data.evaluation.totalScore);
      console.log('   Streak:', answer1Data.evaluation.streak);
      console.log('   Difficulty Shift:', answer1Data.difficultyShift.reason);
      if (!answer1Data.success || !answer1Data.evaluation.isCorrect) throw new Error('Answer evaluation test failed');
      console.log('   ✅ Test 3 Passed!\n');

      // Test 4: Adaptive Shift UP (2nd consecutive correct answer -> Medium to Hard)
      console.log('4️⃣ Testing Adaptive Difficulty Shift UP (Medium -> Hard)...');
      currentQ = answer1Data.nextQuestion;
      const answer2Res = await fetch(`${baseUrl}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          selectedIndex: 2,
          timeTakenSeconds: 4,
          currentQuestionData: {
            ...currentQ,
            correctAnswerIndex: 2,
            explanation: 'Separate chaining uses a linked list for hash collisions.'
          }
        })
      });
      const answer2Data = await answer2Res.json();
      console.log('   Streak:', answer2Data.evaluation.streak);
      console.log('   New Difficulty:', answer2Data.difficultyShift.newDifficulty);
      console.log('   Shift Changed:', answer2Data.difficultyShift.changed);
      console.log('   Shift Reason:', answer2Data.difficultyShift.reason);
      if (answer2Data.difficultyShift.newDifficulty !== 'Hard') throw new Error('Adaptive shift UP test failed');
      console.log('   ✅ Test 4 (Adaptive Shift UP to Hard) Passed!\n');

      // Test 5: Adaptive Shift DOWN (2 consecutive wrong answers -> Hard to Medium)
      console.log('5️⃣ Testing Adaptive Difficulty Shift DOWN (Hard -> Medium)...');
      currentQ = answer2Data.nextQuestion;
      // Wrong answer 1
      const wrong1 = await fetch(`${baseUrl}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          selectedIndex: 0,
          timeTakenSeconds: 12,
          currentQuestionData: { ...currentQ, correctAnswerIndex: 1, explanation: 'Test explanation' }
        })
      });
      const wrong1Data = await wrong1.json();

      // Wrong answer 2
      const wrong2 = await fetch(`${baseUrl}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          selectedIndex: 0,
          timeTakenSeconds: 15,
          currentQuestionData: { ...wrong1Data.nextQuestion, correctAnswerIndex: 1, explanation: 'Test explanation' }
        })
      });
      const wrong2Data = await wrong2.json();
      console.log('   New Difficulty after 2 errors:', wrong2Data.difficultyShift.newDifficulty);
      console.log('   Shift Direction:', wrong2Data.difficultyShift.direction);
      console.log('   Shift Reason:', wrong2Data.difficultyShift.reason);
      if (wrong2Data.difficultyShift.newDifficulty !== 'Medium') throw new Error('Adaptive shift DOWN test failed');
      console.log('   ✅ Test 5 (Adaptive Shift DOWN to Medium) Passed!\n');

      console.log('🎉 ALL BACKEND API & ADAPTIVE ENGINE TESTS PASSED SUCCESSFULLY!');
    } catch (err) {
      console.error('❌ Test failed with error:', err.message);
      process.exitCode = 1;
    } finally {
      server.close();
    }
  });
}

runBackendTests();
