import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../api.js'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      const res = await authApi.login(email, password)
      localStorage.setItem('token', res.data.access_token)
      const me = await authApi.me()
      onLogin(me.data)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="form-card">
      <h2>Login</h2>
      {error && <div className="error-text">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button className="btn" style={{ width: '100%' }} type="submit">Login</button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13, color: '#9a9aa8' }}>
        No account? <Link to="/signup" style={{ color: '#e63946' }}>Sign up</Link>
      </p>
    </div>
  )
}
