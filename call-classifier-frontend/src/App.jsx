import { useState } from 'react'
import './App.css'

function App() {
  const [transcript, setTranscript] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!transcript.trim()) return
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/classify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Backend error: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ reason: `Error classifying call: ${error.message}`, category: 'error' })
    }
    setLoading(false)
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Call Classifier</h1>
      </header>
      <main className="App-main">
        <div className="container">
          <h2>Enter Call Transcript</h2>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste the call transcript here..."
            rows="10"
            cols="50"
          />
          <br />
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Classifying...' : 'Classify Call'}
          </button>
          {result && (
            <div className="result">
              <h3>Classification Result</h3>
              <p><strong>Reason:</strong> {result.reason}</p>
              <p><strong>Category:</strong> {result.category}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
