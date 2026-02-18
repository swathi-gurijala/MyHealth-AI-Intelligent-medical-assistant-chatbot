const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Request failed')
  }
  return res.json()
}

export const api = {
  health: () => request('/api/health'),
  chat: (payload) =>
    request('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  aiQuery: (payload) =>
    request('/api/ai-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  recommendations: (payload) =>
    request('/api/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  history: (userId) => request(`/api/history/${encodeURIComponent(userId)}`),
  analyzeReport: (userId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/api/analyze-report?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      body: form,
    })
  },
}
