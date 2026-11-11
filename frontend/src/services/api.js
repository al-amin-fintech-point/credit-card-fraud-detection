const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
async function request(method, path, payload, options = {}) {
  const isForm = payload instanceof FormData
  const response = await fetch(`${baseURL}${path}`, {
    method,
    headers: payload && !isForm ? { 'Content-Type': 'application/json' } : {},
    body: payload ? (isForm ? payload : JSON.stringify(payload)) : undefined,
  })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try { detail = (await response.json()).detail || detail } catch { /* keep status message */ }
    const error = new Error(detail)
    error.response = { data: { detail }, status: response.status }
    throw error
  }
  return { data: options.responseType === 'blob' ? await response.blob() : await response.json() }
}
export const api = {
  get: (path) => request('GET', path),
  post: (path, payload, options) => request('POST', path, payload, options),
}
export const errorMessage = (error) => error.response?.data?.detail || error.message || 'Request failed'
