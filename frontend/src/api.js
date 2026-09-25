import axios from 'axios'

// Empty string = same-origin requests (used in the single-service deploy,
// where FastAPI serves this built frontend itself). For local dev with
// `npm run dev`, set VITE_API_BASE_URL=http://localhost:8000 in .env.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({ baseURL: API_BASE_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authApi = {
  signup: (email, password) => api.post('/auth/signup', { email, password }),
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/users/me'),
}

export const moviesApi = {
  search: (q) => api.get('/movies/search', { params: { q } }),
  list: (genre) => api.get('/movies', { params: genre ? { genre } : {} }),
  get: (id) => api.get(`/movies/${id}`),
}

export const recommendApi = {
  similar: (movieId, topK = 10) => api.get(`/recommend/${movieId}`, { params: { top_k: topK } }),
  forYou: (userId, topK = 10) => api.get('/recommend/for-you/list', { params: { user_id: userId, top_k: topK } }),
}

export const userApi = {
  rate: (movieId, rating) => api.post('/ratings', { movie_id: movieId, rating }),
  myRatings: () => api.get('/ratings/me'),
  addToWatchlist: (movieId) => api.post('/watchlist', { movie_id: movieId }),
  removeFromWatchlist: (movieId) => api.delete(`/watchlist/${movieId}`),
  myWatchlist: () => api.get('/watchlist/me'),
}

export default api
