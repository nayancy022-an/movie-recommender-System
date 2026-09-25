import { useEffect, useState } from 'react'
import MovieCard from '../components/MovieCard.jsx'
import { moviesApi, recommendApi } from '../api.js'

export default function Home({ user }) {
  const [movies, setMovies] = useState([])
  const [forYou, setForYou] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    moviesApi.list().then((res) => setMovies(res.data)).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (user) {
      recommendApi.forYou(user.id, 8).then((res) => setForYou(res.data.map((r) => r.movie)))
    }
  }, [user])

  return (
    <div className="container">
      {user && forYou.length > 0 && (
        <>
          <h2 className="section-title">Recommended for you</h2>
          <div className="grid">
            {forYou.map((m) => <MovieCard key={m.id} movie={m} />)}
          </div>
        </>
      )}

      <h2 className="section-title">{user ? 'Browse all' : 'Trending'}</h2>
      {loading ? (
        <div className="empty-state">Loading movies…</div>
      ) : (
        <div className="grid">
          {movies.map((m) => <MovieCard key={m.id} movie={m} />)}
        </div>
      )}
    </div>
  )
}
