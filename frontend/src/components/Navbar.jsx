import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function Navbar({ isAuthed, onLogout }) {
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  function handleSearch(e) {
    e.preventDefault()
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand">🎬 CineMatch</Link>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search movies..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </form>
      <div className="links">
        <Link to="/">Home</Link>
        {isAuthed ? (
          <>
            <Link to="/watchlist">Watchlist</Link>
            <button className="btn-secondary" onClick={onLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login" className="btn">Login</Link>
        )}
      </div>
    </nav>
  )
}
