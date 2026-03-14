import { useState } from 'react'
import { invokeEdgeFunction } from './api'

function App() {
  const [input, setInput] = useState({ x: 0.5, t: 0.2 })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await invokeEdgeFunction('predict-flow', input)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>PhysicsAI • Flow Prediction</h1>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <label>
          x:
          <input
            type="number"
            step="0.1"
            value={input.x}
            onChange={(e) => setInput({ ...input, x: parseFloat(e.target.value) })}
          />
        </label>
        <label>
          t:
          <input
            type="number"
            step="0.1"
            value={input.t}
            onChange={(e) => setInput({ ...input, t: parseFloat(e.target.value) })}
          />
        </label>
        <button onClick={handlePredict} disabled={loading}>
          {loading ? 'Predicting...' : 'Predict'}
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {result && (
        <div style={{ border: '1px solid #ccc', padding: '1rem' }}>
          <h3>Prediction Result</h3>
          <p><strong>u:</strong> {result.u.toFixed(4)}</p>
          <p><strong>confidence:</strong> {result.confidence}</p>
        </div>
      )}
    </div>
  )
}

export default App
