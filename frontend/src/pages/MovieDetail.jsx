import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import MovieCard from '../components/MovieCard.jsx'
import { moviesApi, recommendApi, userApi } from '../api.js'

const TMDB_IMG_BASE = 'https://image.tmdb.org/t/p/w500'

export default function MovieDetail({ user }) {
  const { id } = useParams()
  const [movie, setMovie] = useState(null)
  const [similar, setSimilar] = useState([])
  const [myRating, setMyRating] = useState(0)
  const [inWatchlist, setInWatchlist] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    moviesApi.get(id).then((res) => setMovie(res.data))
    recommendApi.similar(id, 8).then((res) => setSimilar(res.data.map((r) => r.movie))).catch(() => setSimilar([]))
  }, [id])

  async function handleRate(stars) {
    if (!user) { setMessage('Please login to rate movies.'); return }
    setMyRating(stars)
    await userApi.rate(Number(id), stars)
    setMessage('Rating saved!')
    setTimeout(() => setMessage(''), 2000)
  }

  async function handleWatchlist() {
    if (!user) { setMessage('Please login to use watchlist.'); return }
    if (inWatchlist) {
      await userApi.removeFromWatchlist(Number(id))
      setInWatchlist(false)
    } else {
      await userApi.addToWatchlist(Number(id))
      setInWatchlist(true)
    }
  }

  if (!movie) return <div className="container empty-state">Loading…</div>

  return (
    <div className="container">
      <div className="detail-hero">
        <div className="detail-poster">
          {movie.poster_path ? (
            <img
              src={`${TMDB_IMG_BASE}${movie.poster_path}`}
              alt={movie.title}
              onError={(e) => {
                e.target.onerror = null
                e.target.replaceWith(Object.assign(document.createElement('span'), {
                  className: 'poster-fallback-text',
                  textContent: movie.title,
                }))
              }}
            />
          ) : (
            <span className="poster-fallback-text">{movie.title}</span>
          )}
        </div>
        <div>
          <h1>{movie.title} {movie.release_year && <span style={{ color: '#9a9aa8', fontWeight: 400 }}>({movie.release_year})</span>}</h1>
          <div style={{ margin: '12px 0' }}>
            {(movie.genres || '').split('|').filter(Boolean).map((g) => (
              <span key={g} className="genre-pill">{g}</span>
            ))}
          </div>
          <p style={{ color: '#c8c8d0', maxWidth: 560 }}>{movie.overview}</p>

          <div className="star-row">
            {[1, 2, 3, 4, 5].map((s) => (
              <span
                key={s}
                className={`star ${s <= myRating ? 'filled' : ''}`}
                onClick={() => handleRate(s)}
              >★</span>
            ))}
          </div>

          <button className="btn" onClick={handleWatchlist}>
            {inWatchlist ? '✓ In Watchlist' : '+ Add to Watchlist'}
          </button>
          {message && <div style={{ marginTop: 10, color: '#9a9aa8', fontSize: 13 }}>{message}</div>}
        </div>
      </div>

      <h2 className="section-title">Similar movies</h2>
      {similar.length === 0 ? (
        <div className="empty-state">No recommendations yet — build the FAISS index first (see README).</div>
      ) : (
        <div className="grid">
          {similar.map((m) => <MovieCard key={m.id} movie={m} />)}
        </div>
      )}
    </div>
  )
}
