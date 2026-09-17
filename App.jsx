import { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8000'

const RISK_STYLES = {
  'Safe': { bg: '#e6f4ea', text: '#1e7e34', border: '#1e7e34' },
  'Caution': { bg: '#fff8e1', text: '#a5690a', border: '#a5690a' },
  'High Risk': { bg: '#fde7e7', text: '#b02a2a', border: '#b02a2a' },
}

export default function App() {
  const [subject, setSubject] = useState('')
  const [senderEmail, setSenderEmail] = useState('')
  const [body, setBody] = useState('')
  const [samples, setSamples] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showEvidence, setShowEvidence] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/samples`)
      .then((r) => r.json())
      .then(setSamples)
      .catch(() => setSamples([]))
  }, [])

  function loadSample(sample) {
    setSubject(sample.subject)
    setSenderEmail(sample.sender_email)
    setBody(sample.body)
    setResult(null)
    setError('')
  }

  async function handleAnalyze() {
    if (!body.trim()) {
      setError('Message body cannot be empty.')
      return
    }
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject,
          sender_email: senderEmail,
          body,
        }),
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Request failed')
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const riskStyle = result ? RISK_STYLES[result.risk_level] || RISK_STYLES['Caution'] : null

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>🛡️ Phishing & Social Engineering Detector</h1>
        <p style={styles.subtitle}>
          Paste a message below to check for deceptive or manipulative signals.
        </p>

        <div style={styles.sampleRow}>
          {samples.map((s) => (
            <button key={s.label} style={styles.sampleBtn} onClick={() => loadSample(s)}>
              {s.label}
            </button>
          ))}
        </div>

        <div style={styles.card}>
          <label style={styles.label}>Sender email</label>
          <input
            style={styles.input}
            value={senderEmail}
            onChange={(e) => setSenderEmail(e.target.value)}
            placeholder="e.g. security@sbi-verify-secure.info"
          />

          <label style={styles.label}>Subject</label>
          <input
            style={styles.input}
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g. Urgent: Account Suspension Notice"
          />

          <label style={styles.label}>Message body</label>
          <textarea
            style={styles.textarea}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Paste the full message here..."
            rows={6}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button style={styles.analyzeBtn} onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze message'}
          </button>
        </div>

        {result && (
          <div style={{ ...styles.resultCard, borderColor: riskStyle.border }}>
            <div style={styles.resultHeader}>
              <span
                style={{
                  ...styles.riskBadge,
                  background: riskStyle.bg,
                  color: riskStyle.text,
                }}
              >
                {result.risk_level}
              </span>
              <span style={styles.confidence}>Confidence: {result.confidence}</span>
            </div>

            <h3 style={styles.sectionTitle}>Top factors</h3>
            <ul style={styles.factorList}>
              {result.top_factors.map((f, i) => (
                <li key={i} style={styles.factorItem}>{f}</li>
              ))}
            </ul>

            <h3 style={styles.sectionTitle}>Reasoning</h3>
            <p style={styles.reasoning}>{result.reasoning_summary}</p>

            <div style={styles.actionBox}>
              <strong>Recommended action:</strong> {result.recommended_action}
            </div>

            <button
              style={styles.evidenceToggle}
              onClick={() => setShowEvidence(!showEvidence)}
            >
              {showEvidence ? 'Hide' : 'Show'} raw evidence trail
            </button>

            {showEvidence && (
              <pre style={styles.evidencePre}>
                {JSON.stringify(result.evidence, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f4f5f7',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    padding: '2rem 1rem',
  },
  container: {
    maxWidth: 640,
    margin: '0 auto',
  },
  title: { fontSize: '1.5rem', fontWeight: 600, marginBottom: 4 },
  subtitle: { color: '#666', marginBottom: '1.25rem', fontSize: '0.95rem' },
  sampleRow: { display: 'flex', gap: 8, marginBottom: '1rem', flexWrap: 'wrap' },
  sampleBtn: {
    padding: '6px 12px',
    fontSize: '0.85rem',
    borderRadius: 20,
    border: '1px solid #ccc',
    background: '#fff',
    cursor: 'pointer',
  },
  card: {
    background: '#fff',
    borderRadius: 12,
    padding: '1.25rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
    marginBottom: '1.25rem',
  },
  label: { display: 'block', fontSize: '0.8rem', color: '#555', marginBottom: 4, marginTop: 10 },
  input: {
    width: '100%',
    padding: '8px 10px',
    fontSize: '0.9rem',
    borderRadius: 6,
    border: '1px solid #ddd',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    padding: '8px 10px',
    fontSize: '0.9rem',
    borderRadius: 6,
    border: '1px solid #ddd',
    boxSizing: 'border-box',
    resize: 'vertical',
    fontFamily: 'inherit',
  },
  error: { color: '#b02a2a', fontSize: '0.85rem', marginTop: 8 },
  analyzeBtn: {
    marginTop: '1rem',
    width: '100%',
    padding: '10px',
    fontSize: '0.95rem',
    fontWeight: 600,
    borderRadius: 8,
    border: 'none',
    background: '#2563eb',
    color: '#fff',
    cursor: 'pointer',
  },
  resultCard: {
    background: '#fff',
    borderRadius: 12,
    padding: '1.25rem',
    border: '2px solid',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  },
  resultHeader: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: '0.75rem' },
  riskBadge: { padding: '4px 14px', borderRadius: 20, fontWeight: 600, fontSize: '0.9rem' },
  confidence: { fontSize: '0.85rem', color: '#666' },
  sectionTitle: { fontSize: '0.85rem', color: '#555', marginTop: 14, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 },
  factorList: { margin: 0, paddingLeft: 18, fontSize: '0.9rem' },
  factorItem: { marginBottom: 4 },
  reasoning: { fontSize: '0.9rem', color: '#333', lineHeight: 1.5 },
  actionBox: {
    marginTop: 12,
    background: '#eef4ff',
    padding: '10px 12px',
    borderRadius: 8,
    fontSize: '0.9rem',
  },
  evidenceToggle: {
    marginTop: 14,
    background: 'none',
    border: 'none',
    color: '#2563eb',
    fontSize: '0.85rem',
    cursor: 'pointer',
    padding: 0,
  },
  evidencePre: {
    marginTop: 10,
    background: '#f4f5f7',
    padding: 10,
    borderRadius: 8,
    fontSize: '0.75rem',
    overflowX: 'auto',
    maxHeight: 300,
    overflowY: 'auto',
  },
}
