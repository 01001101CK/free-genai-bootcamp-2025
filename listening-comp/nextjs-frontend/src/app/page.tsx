'use client'

import { useState } from 'react'
import { useChat } from 'ai/react'
import Image from "next/image";

export default function ListeningComprehension() {
  const [videoUrl, setVideoUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleVideoSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch('/api/transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoUrl })
      })
      const data = await response.json()
      // Handle transcript data
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Language Listening Comprehension</h1>
      
      <form onSubmit={handleVideoSubmit} className="mb-6">
        <input
          type="text"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="Enter YouTube URL"
          className="w-full p-2 border rounded"
        />
        <button 
          type="submit"
          disabled={loading}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          {loading ? 'Processing...' : 'Generate Questions'}
        </button>
      </form>
    </div>
  )
}
