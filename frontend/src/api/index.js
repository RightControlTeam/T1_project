import axios from 'axios'
import router from '@/router'

const api = axios.create({
    baseURL: 'http://localhost:8000',
})

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    response => response,  // успех — просто возвращаем
    error => {
        // Если токен истёк (401)
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('admin_level')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

export default api