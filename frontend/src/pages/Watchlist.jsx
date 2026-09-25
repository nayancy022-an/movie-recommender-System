import { useEffect, useState } from 'react'
import MovieCard from '../components/MovieCard.jsx'
import { userApi } from '../api.js'

export default function Watchlist() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    userApi.myWatchlist().then((res) => setItems(res.data)).finally(() => setLoading(false))
  }, [])

  return (
    <div className="container">
      <h2 className="section-title">My Watchlist</h2>
      {loading ? (
        <div className="empty-state">Loading…</div>
      ) : items.length === 0 ? (
        <div className="empty-state">Your watchlist is empty. Go add some movies!</div>
      ) : (
        <div className="grid">
          {items.map((w) => <MovieCard key={w.id} movie={w.movie} />)}
        </div>
      )}
    </div>
  )
}
