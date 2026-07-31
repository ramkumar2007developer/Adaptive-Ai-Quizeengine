/**
 * Sanitize and parse LLM generated response into structured Question JSON object
 */
export function formatQuestionResponse(rawResponse, defaultId = 'q-1', expectedDifficulty = 'Medium') {
  try {
    let cleanText = rawResponse.trim();
    
    // Remove markdown code block fences if present (e.g. ```json ... ```)
    if (cleanText.startsWith('```')) {
      cleanText = cleanText.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
    }

    const parsed = JSON.parse(cleanText);

    return {
      id: parsed.id || defaultId,
      difficulty: parsed.difficulty || expectedDifficulty,
      question: parsed.question || 'What is the correct answer for this topic question?',
      options: Array.isArray(parsed.options) && parsed.options.length === 4 
        ? parsed.options 
        : ['Option A', 'Option B', 'Option C', 'Option D'],
      correctAnswerIndex: typeof parsed.correctAnswerIndex === 'number' ? parsed.correctAnswerIndex : 0,
      explanation: parsed.explanation || 'No explanation provided.'
    };
  } catch (err) {
    console.error('Failed to parse LLM JSON response:', err, rawResponse);
    return {
      id: defaultId,
      difficulty: expectedDifficulty,
      question: `Sample ${expectedDifficulty} question regarding the chosen topic`,
      options: [
        'Correct answer demonstrating key concept',
        'Incorrect plausible distractor A',
        'Incorrect plausible distractor B',
        'Incorrect plausible distractor C'
      ],
      correctAnswerIndex: 0,
      explanation: `This is a fallback formatted question for ${expectedDifficulty} level.`
    };
  }
}
