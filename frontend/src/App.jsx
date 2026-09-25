import { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Home from './pages/Home.jsx'
import Search from './pages/Search.jsx'
import MovieDetail from './pages/MovieDetail.jsx'
import Watchlist from './pages/Watchlist.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import { authApi } from './api.js'

export default function App() {
  const [user, setUser] = useState(null)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      authApi.me().then((res) => setUser(res.data)).catch(() => localStorage.removeItem('token')).finally(() => setChecked(true))
    } else {
      setChecked(true)
    }
  }, [])

  function handleLogout() {
    localStorage.removeItem('token')
    setUser(null)
  }

  if (!checked) return null

  return (
    <>
      <Navbar isAuthed={!!user} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/search" element={<Search />} />
        <Route path="/movie/:id" element={<MovieDetail user={user} />} />
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/signup" element={<Signup onLogin={setUser} />} />
        <Route
          path="/watchlist"
          element={
            <ProtectedRoute isAuthed={!!user}>
              <Watchlist />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  )
}
