'use client'

import { useState, useEffect } from 'react'

export default function ListeningComprehension() {
  const [videoUrl, setVideoUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [transcript, setTranscript] = useState<any>(null)
  const [mounted, setMounted] = useState(false)

  // Handle hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  const handleVideoSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setTranscript(null)
    
    try {
      console.log('Submitting URL:', videoUrl)
      
      const response = await fetch('/api/transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoUrl })
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process video')
      }

      console.log('Response data:', data)
      setTranscript(data.transcript)
    } catch (error) {
      console.error('Error:', error)
      setError(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  // Don't render until client-side hydration is complete
  if (!mounted) {
    return null
  }

  return (
    <main className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Language Listening Comprehension</h1>
        
        <form onSubmit={handleVideoSubmit} className="mb-6">
          <input
            type="text"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="Enter YouTube URL (e.g., https://www.youtube.com/watch?v=...)"
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

        {error && (
          <div className="p-4 mb-4 bg-red-100 text-red-700 rounded">
            Error: {error}
          </div>
        )}

        {transcript && (
          <div className="p-4 bg-green-100 rounded">
            <h2 className="font-bold mb-2">Transcript:</h2>
            <pre className="whitespace-pre-wrap">{JSON.stringify(transcript, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  )
} 