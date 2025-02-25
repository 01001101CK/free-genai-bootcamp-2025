'use client'

import { useState, useEffect } from 'react'
import QuestionGenerator from '@/components/QuestionGenerator'
import AudioPlayer from '@/components/AudioPlayer'
import Sidebar from '@/components/Sidebar'
import { Question, PracticeType, Topic } from '@/types'

export default function ListeningPractice() {
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<any>(null)
  const [audioFile, setAudioFile] = useState<string | null>(null)
  const [practiceType, setPracticeType] = useState<PracticeType>('Dialogue Practice')
  const [topic, setTopic] = useState<Topic>('Daily Conversation')

  const topics = {
    "Dialogue Practice": ["Daily Conversation", "Shopping", "Restaurant", "Travel", "School/Work"],
    "Phrase Matching": ["Announcements", "Instructions", "Weather Reports", "News Updates"]
  }

  const handleGenerateQuestion = async () => {
    try {
      const response = await fetch('/api/questions/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ practiceType, topic })
      })
      const data = await response.json()
      setCurrentQuestion(data)
      setFeedback(null)
      setSelectedAnswer(null)
      setAudioFile(null)
    } catch (error) {
      console.error('Error generating question:', error)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer) return

    try {
      const response = await fetch('/api/questions/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentQuestion,
          selectedAnswer
        })
      })
      const data = await response.json()
      setFeedback(data)
    } catch (error) {
      console.error('Error getting feedback:', error)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar 
        onQuestionSelect={(question) => {
          setCurrentQuestion(question)
          setFeedback(null)
          setSelectedAnswer(null)
        }}
      />
      
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8">JLPT Listening Practice</h1>
        
        <div className="mb-6">
          <select 
            value={practiceType}
            onChange={(e) => setPracticeType(e.target.value as PracticeType)}
            className="mr-4 p-2 border rounded"
          >
            <option value="Dialogue Practice">Dialogue Practice</option>
            <option value="Phrase Matching">Phrase Matching</option>
          </select>

          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value as Topic)}
            className="p-2 border rounded"
          >
            {topics[practiceType].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleGenerateQuestion}
          className="mb-8 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Generate New Question
        </button>

        {currentQuestion && (
          <QuestionGenerator
            question={currentQuestion}
            selectedAnswer={selectedAnswer}
            setSelectedAnswer={setSelectedAnswer}
            feedback={feedback}
            onSubmit={handleSubmitAnswer}
          />
        )}

        {currentQuestion && (
          <AudioPlayer
            questionId={currentQuestion.id}
            audioFile={audioFile}
            setAudioFile={setAudioFile}
          />
        )}
      </main>
    </div>
  )
} 