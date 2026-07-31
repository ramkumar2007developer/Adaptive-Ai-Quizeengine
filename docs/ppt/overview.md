# Adaptive Quiz Generator Presentation Outline 📊

## Slide 1: Introduction & Problem Statement
- Traditional quizzes use static, linear question sets regardless of student performance.
- Adaptive learning tailors question difficulty in real time to match learner capability.

## Slide 2: System Architecture
- **Frontend**: React 18 + Vite (Glassmorphic dark design tokens).
- **Backend**: Express REST API with Modular Controller Architecture.
- **Adaptive Engine**: Rule-based difficulty scaling algorithm.
- **AI Integration**: Prompt templates for Google Gemini LLM API.

## Slide 3: Adaptive Algorithm Matrix
| Condition | Difficulty Action | Points Multiplier |
|---|---|---|
| 2 Consecutive Correct | Upgrade (Easy -> Medium -> Hard) | 1.5x - 3x |
| 2 Consecutive Incorrect | Downgrade (Hard -> Medium -> Easy) | Base |
| Speed < 10 seconds | Speed Bonus Awarded | +1 to +10 pts |

## Slide 4: Key Features & Demonstration
- Real-time scoring, streaks, and progress indicator.
- Instant post-answer explanation popup & difficulty adjustment notifications.
- Complete performance analytics breakdown page.
