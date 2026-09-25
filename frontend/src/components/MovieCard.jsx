import { Link } from 'react-router-dom'

const TMDB_IMG_BASE = 'https://image.tmdb.org/t/p/w342'

export default function MovieCard({ movie }) {
  return (
    <Link to={`/movie/${movie.id}`} className="movie-card">
      <div className="poster">
        {movie.poster_path ? (
          <img
            src={`${TMDB_IMG_BASE}${movie.poster_path}`}
            alt={movie.title}
            loading="lazy"
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
      <div className="info">
        <div className="title">{movie.title}</div>
        <div className="meta">{movie.release_year || ''} · {(movie.genres || '').split('|')[0]}</div>
      </div>
    </Link>
  )
}
