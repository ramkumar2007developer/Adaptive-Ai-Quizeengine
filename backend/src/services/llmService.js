import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { formatQuestionResponse } from '../utils/responseFormatter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Pre-packaged fallback questions database per topic and difficulty
const FALLBACK_BANK = {
  "Data Structures & Algorithms": {
    "Easy": [
      {
        question: "What is the time complexity of searching an element in a balanced Binary Search Tree (BST)?",
        options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        correctAnswerIndex: 1,
        explanation: "In a balanced BST, each step divides the search space in half, resulting in logarithmic O(log n) time complexity."
      },
      {
        question: "Which data structure follows the First-In, First-Out (FIFO) principle?",
        options: ["Stack", "Queue", "Tree", "Graph"],
        correctAnswerIndex: 1,
        explanation: "Queues operate on a FIFO (First-In, First-Out) basis, where the first element inserted is the first to be removed."
      }
    ],
    "Medium": [
      {
        question: "Which collision resolution technique in hash tables uses a linked list at each bucket?",
        options: ["Linear Probing", "Quadratic Probing", "Separate Chaining", "Double Hashing"],
        correctAnswerIndex: 2,
        explanation: "Separate Chaining handles collisions by maintaining a linked list of entries that hash to the same bucket index."
      },
      {
        question: "What is the worst-case time complexity of QuickSort when bad pivots are consistently selected?",
        options: ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
        correctAnswerIndex: 2,
        explanation: "When QuickSort picks the smallest or largest element as pivot repeatedly (e.g. sorted input with last element pivot), partition imbalance leads to O(n²) time complexity."
      }
    ],
    "Hard": [
      {
        question: "In a Floyd-Warshall all-pairs shortest path algorithm, what does the dynamic programming state matrix dp[i][j][k] represent?",
        options: [
          "Shortest path from i to j using at most k edges",
          "Shortest path from i to j using only vertices from set {1...k} as intermediate nodes",
          "Maximum flow from node i to node j passing through node k",
          "Subtree diameter between node i and node j after k steps"
        ],
        correctAnswerIndex: 1,
        explanation: "Floyd-Warshall iteratively computes the shortest path between all pairs (i, j) considering candidate intermediate vertices in {1...k}."
      }
    ]
  },
  "Web Development & React": {
    "Easy": [
      {
        question: "Which HTML5 tag is used to embed client-side JavaScript code directly into a webpage?",
        options: ["<js>", "<script>", "<code.js>", "<javascript>"],
        correctAnswerIndex: 1,
        explanation: "The <script> tag is standard HTML for placing JavaScript executable code."
      }
    ],
    "Medium": [
      {
        question: "In React, what is the primary purpose of the `useCallback` hook?",
        options: [
          "To fetch external API data asynchronously",
          "To memoize callback functions between renders to avoid unnecessary child re-renders",
          "To directly mutate state in class components",
          "To force a full component DOM re-render"
        ],
        correctAnswerIndex: 1,
        explanation: "useCallback returns a memoized version of a callback function that only changes when one of its dependencies changes."
      }
    ],
    "Hard": [
      {
        question: "What issue occurs when performing synchronous blocking computations directly inside a custom React `useLayoutEffect` hook?",
        options: [
          "Memory leak in server component hydration",
          "Blocks the browser painting thread, leading to visible UI lag before visual DOM updates",
          "Causes infinite state mutation loops automatically",
          "Bypasses Virtual DOM diffing completely"
        ],
        correctAnswerIndex: 1,
        explanation: "useLayoutEffect runs synchronously before browser paint; heavy synchronous tasks inside it block rendering execution."
      }
    ]
  },
  "Machine Learning & AI": {
    "Easy": [
      {
        question: "What type of learning uses labeled dataset pairs of inputs and ground truth targets?",
        options: ["Unsupervised Learning", "Supervised Learning", "Reinforcement Learning", "Self-Organizing Maps"],
        correctAnswerIndex: 1,
        explanation: "Supervised learning trains models on labeled input-output pairs to learn predictive mappings."
      }
    ],
    "Medium": [
      {
        question: "Which activation function suffers most severely from the vanishing gradient problem in deep neural networks?",
        options: ["ReLU", "Leaky ReLU", "Sigmoid", "ELU"],
        correctAnswerIndex: 2,
        explanation: "Sigmoid squashes outputs into (0, 1) and has derivatives strictly <= 0.25, causing gradients to vanish across deep layers."
      }
    ],
    "Hard": [
      {
        question: "What key advantage does Multi-Head Self-Attention in Transformer models offer over traditional Recurrent Neural Networks (RNNs)?",
        options: [
          "Zero memory consumption during inference",
          "Parallelized matrix computation across sequence tokens without sequential recurrence bottlenecks",
          "Guaranteed 100% convergence on un-normalized inputs",
          "Elimination of weight parameters in hidden layers"
        ],
        correctAnswerIndex: 1,
        explanation: "Self-attention enables parallel processing of all tokens in a sequence simultaneously, avoiding sequential loop constraints of RNNs."
      }
    ]
  }
};

export async function generateQuestion(topic, difficulty, questionNumber = 1) {
  const apiKey = process.env.GEMINI_API_KEY;

  if (apiKey && apiKey.trim().length > 0) {
    try {
      const genAI = new GoogleGenerativeAI(apiKey);
      const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

      const promptFileName = `${difficulty.toLowerCase()}Prompt.txt`;
      const promptPath = path.join(__dirname, '..', 'prompts', promptFileName);
      
      let promptTemplate = '';
      if (fs.existsSync(promptPath)) {
        promptTemplate = fs.readFileSync(promptPath, 'utf8');
      } else {
        promptTemplate = `Generate a ${difficulty} multiple choice question for topic {{topic}} in raw JSON format with question, options (array of 4), correctAnswerIndex (0-3), and explanation.`;
      }

      const prompt = promptTemplate
        .replace(/{{topic}}/g, topic)
        .replace(/{{id}}/g, `q-${questionNumber}`);

      const result = await model.generateContent(prompt);
      const rawText = result.response.text();
      return formatQuestionResponse(rawText, `q-${questionNumber}`, difficulty);
    } catch (err) {
      console.warn(`[llmService] AI call failed or timed out. Falling back to dynamic rule bank. Error:`, err.message);
    }
  }

  // Fallback engine
  const topicBank = FALLBACK_BANK[topic] || FALLBACK_BANK["Data Structures & Algorithms"];
  const levelQuestions = topicBank[difficulty] || topicBank["Medium"];
  const selected = levelQuestions[Math.floor(Math.random() * levelQuestions.length)];

  return {
    id: `q-${questionNumber}`,
    difficulty,
    question: selected.question,
    options: selected.options,
    correctAnswerIndex: selected.correctAnswerIndex,
    explanation: selected.explanation
  };
}
