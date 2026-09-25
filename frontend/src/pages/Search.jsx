import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import MovieCard from '../components/MovieCard.jsx'
import { moviesApi } from '../api.js'

export default function Search() {
  const [params] = useSearchParams()
  const q = params.get('q') || ''
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!q) return
    setLoading(true)
    moviesApi.search(q).then((res) => setResults(res.data)).finally(() => setLoading(false))
  }, [q])

  return (
    <div className="container">
      <h2 className="section-title">Results for "{q}"</h2>
      {loading ? (
        <div className="empty-state">Searching…</div>
      ) : results.length === 0 ? (
        <div className="empty-state">No movies found.</div>
      ) : (
        <div className="grid">
          {results.map((m) => <MovieCard key={m.id} movie={m} />)}
        </div>
      )}
    </div>
  )
}
