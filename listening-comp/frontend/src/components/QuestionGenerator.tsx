import { Question, Feedback } from '@/types'

interface Props {
  question: Question
  selectedAnswer: number | null
  setSelectedAnswer: (answer: number | null) => void
  feedback: Feedback | null
  onSubmit: () => void
}

export default function QuestionGenerator({
  question,
  selectedAnswer,
  setSelectedAnswer,
  feedback,
  onSubmit
}: Props) {
  return (
    <div className="mb-8">
      <div className="mb-4">
        {question.introduction && (
          <>
            <h3 className="font-bold">Introduction:</h3>
            <p>{question.introduction}</p>
          </>
        )}
        
        {question.conversation && (
          <>
            <h3 className="font-bold mt-4">Conversation:</h3>
            <p>{question.conversation}</p>
          </>
        )}
        
        {question.situation && (
          <>
            <h3 className="font-bold mt-4">Situation:</h3>
            <p>{question.situation}</p>
          </>
        )}

        <h3 className="font-bold mt-4">Question:</h3>
        <p>{question.question}</p>
      </div>

      {feedback ? (
        <div>
          <h3 className="font-bold">Your Answer:</h3>
          {question.options.map((option, i) => (
            <div 
              key={i}
              className={`p-2 my-1 rounded ${
                i === feedback.correctAnswer - 1 && i === selectedAnswer - 1
                  ? 'bg-green-100'
                  : i === feedback.correctAnswer - 1
                  ? 'bg-green-50'
                  : i === selectedAnswer - 1
                  ? 'bg-red-100'
                  : ''
              }`}
            >
              {i + 1}. {option}
              {i === feedback.correctAnswer - 1 && ' ✓'}
              {i === selectedAnswer - 1 && i !== feedback.correctAnswer - 1 && ' ✗'}
            </div>
          ))}
          
          <div className={`mt-4 p-4 rounded ${
            feedback.correct ? 'bg-green-100' : 'bg-red-100'
          }`}>
            <h3 className="font-bold">Explanation:</h3>
            <p>{feedback.explanation}</p>
          </div>
        </div>
      ) : (
        <div>
          {question.options.map((option, i) => (
            <div 
              key={i}
              className={`p-2 my-1 rounded cursor-pointer hover:bg-gray-100 ${
                selectedAnswer === i + 1 ? 'bg-blue-100' : ''
              }`}
              onClick={() => setSelectedAnswer(i + 1)}
            >
              {i + 1}. {option}
            </div>
          ))}
          
          <button
            onClick={onSubmit}
            disabled={!selectedAnswer}
            className="mt-4 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300"
          >
            Submit Answer
          </button>
        </div>
      )}
    </div>
  )
} 