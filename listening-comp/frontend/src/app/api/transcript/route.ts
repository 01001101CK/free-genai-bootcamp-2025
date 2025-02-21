import { NextResponse } from 'next/server'

const API_URL = 'http://localhost:5001' // Updated port

export async function POST(req: Request) {
  try {
    const { videoUrl } = await req.json()
    console.log('Processing video URL:', videoUrl)

    // Test backend connection first
    try {
      await fetch(`${API_URL}/test`)
    } catch (e) {
      throw new Error('Backend server is not running')
    }

    const response = await fetch(`${API_URL}/process-video`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ videoUrl })
    })

    const data = await response.json()
    
    if (!response.ok) {
      console.error('Backend error:', data)
      throw new Error(data.detail || 'Backend error')
    }

    console.log('Response data:', data)
    return NextResponse.json(data)
  } catch (error) {
    console.error('API route error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to process video' },
      { status: 500 }
    )
  }
} 