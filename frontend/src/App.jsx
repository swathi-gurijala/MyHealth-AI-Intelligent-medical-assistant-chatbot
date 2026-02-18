import { useMemo, useState } from 'react'
import { api } from './api'
import SectionCard from './components/SectionCard'

const defaultUser = 'demo_user_001'

export default function App() {
  const [userId, setUserId] = useState(defaultUser)
  const [symptoms, setSymptoms] = useState('fever, cough')
  const [message, setMessage] = useState('I have fever and cough since two days')
  const [medicalQuery, setMedicalQuery] = useState('What should I do for high blood sugar trends?')
  const [chatResult, setChatResult] = useState(null)
  const [aiQueryResult, setAiQueryResult] = useState('')
  const [reportResult, setReportResult] = useState(null)
  const [history, setHistory] = useState([])
  const [recommendations, setRecommendations] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const parsedSymptoms = useMemo(
    () => symptoms.split(',').map((s) => s.trim()).filter(Boolean),
    [symptoms],
  )

  const submitChat = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.chat({ user_id: userId, symptoms: parsedSymptoms, message })
      setChatResult(res)
      const rec = await api.recommendations({
        user_id: userId,
        conditions: res.possible_conditions,
      })
      setRecommendations(rec)
    } catch (err) {
      setError(`Unable to analyze symptoms: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const submitMedicalQuery = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.aiQuery({ user_id: userId, query: medicalQuery })
      setAiQueryResult(res.answer)
    } catch (err) {
      setError(`Unable to get AI medical answer: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleReport = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const res = await api.analyzeReport(userId, file)
      setReportResult(res)
    } catch (err) {
      setError(`Unable to analyze report: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.history(userId)
      setHistory(res.entries)
    } catch (err) {
      setError(`Unable to load history: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <header>
        <h1>MyHealth AI: Intelligent Health Companion & Diagnostic Assistant</h1>
        <p>
          AI-powered triage, report analysis, personalized wellness suggestions, emergency risk
          alerts, and ClinicalBERT-backed medical Q&A.
        </p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <SectionCard title="User Setup">
        <label>
          User ID
          <input value={userId} onChange={(e) => setUserId(e.target.value)} />
        </label>
      </SectionCard>

      <SectionCard title="1) Symptom Chat">
        <label>
          Symptoms (comma-separated)
          <input value={symptoms} onChange={(e) => setSymptoms(e.target.value)} />
        </label>
        <label>
          Describe your condition
          <textarea rows={4} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <button onClick={submitChat} disabled={loading}>
          Analyze Symptoms
        </button>
        {chatResult && (
          <div className="result">
            <p>
              <strong>Urgency:</strong> {chatResult.urgency}
            </p>
            <p>{chatResult.response}</p>
            <p>
              <strong>Specialist:</strong> {chatResult.specialist}
            </p>
          </div>
        )}
      </SectionCard>

      <SectionCard title="2) AI Medical Query (ClinicalBERT + Generator)">
        <label>
          Ask any medical query
          <textarea rows={4} value={medicalQuery} onChange={(e) => setMedicalQuery(e.target.value)} />
        </label>
        <button onClick={submitMedicalQuery} disabled={loading}>
          Get AI Answer
        </button>
        {aiQueryResult && (
          <div className="result">
            <p style={{ whiteSpace: 'pre-wrap' }}>{aiQueryResult}</p>
          </div>
        )}
      </SectionCard>

      <SectionCard title="3) Medical Report Analysis">
        <input type="file" accept=".txt,.csv,.pdf,.json" onChange={handleReport} />
        {reportResult && (
          <div className="result">
            <p>{reportResult.summary}</p>
            <ul>
              {reportResult.alerts.map((alert) => (
                <li key={alert}>{alert}</li>
              ))}
            </ul>
          </div>
        )}
      </SectionCard>

      <SectionCard title="4) Personalized Recommendations">
        {recommendations ? (
          <div className="grid">
            {Object.entries(recommendations).map(([key, values]) => (
              <div key={key}>
                <h3>{key.replace('_', ' ')}</h3>
                <ul>
                  {values.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p>Run symptom chat first to generate personalized recommendations.</p>
        )}
      </SectionCard>

      <SectionCard title="5) History & Follow-Up">
        <button onClick={loadHistory} disabled={loading}>
          Load User History
        </button>
        <ul>
          {history.map((entry) => (
            <li key={`${entry.timestamp}-${entry.summary}`}>
              <strong>{new Date(entry.timestamp).toLocaleString()}:</strong> [{entry.interaction_type}]{' '}
              {entry.summary}
            </li>
          ))}
        </ul>
      </SectionCard>
    </main>
  )
}
