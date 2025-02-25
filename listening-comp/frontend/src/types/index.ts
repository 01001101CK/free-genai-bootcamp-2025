export type PracticeType = 'Dialogue Practice' | 'Phrase Matching'

export type Topic = 
  | 'Daily Conversation' 
  | 'Shopping' 
  | 'Restaurant' 
  | 'Travel' 
  | 'School/Work'
  | 'Announcements'
  | 'Instructions'
  | 'Weather Reports'
  | 'News Updates'

export interface Question {
  id: string
  practiceType: PracticeType
  topic: Topic
  introduction?: string
  conversation?: string
  situation?: string
  question: string
  options: string[]
  correctAnswer: number
}

export interface Feedback {
  correct: boolean
  correctAnswer: number
  explanation: string
} 