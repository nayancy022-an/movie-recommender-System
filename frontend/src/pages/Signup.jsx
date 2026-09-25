import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../api.js'

export default function Signup({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await authApi.signup(email, password)
      const res = await authApi.login(email, password)
      localStorage.setItem('token', res.data.access_token)
      const me = await authApi.me()
      onLogin(me.data)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed')
    }
  }

  return (
    <div className="form-card">
      <h2>Create account</h2>
      {error && <div className="error-text">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        <button className="btn" style={{ width: '100%' }} type="submit">Sign up</button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13, color: '#9a9aa8' }}>
        Already have an account? <Link to="/login" style={{ color: '#e63946' }}>Login</Link>
      </p>
    </div>
  )
}
