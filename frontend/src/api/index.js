import axios from 'axios'

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
})

// Добавляем токен к каждому запросу
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    
    // Для запроса логина НЕ добавляем токен (там еще нет токена)
    if (token && !config.url.includes('/login/')) {
        config.headers.Authorization = `Bearer ${token}`
    }
    
    // Для запроса логина не меняем Content-Type (он будет form-data)
    if (config.url.includes('/login/')) {
        // Убираем JSON заголовок для логина, т.к. там form-data
        delete config.headers['Content-Type']
    }
    
    return config
})

// Обработка ошибок
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            console.error('API Error:', {
                status: error.response.status,
                data: error.response.data,
                url: error.config?.url
            })
            
            // Если 401 (неавторизован) - удаляем токен
            if (error.response.status === 401) {
                localStorage.removeItem('token')
                localStorage.removeItem('isAuth')
                if (!error.config?.url?.includes('/login/')) {
                    window.location.href = '/login'
                }
            }
            
            // Формируем понятное сообщение об ошибке
            const message = error.response.data?.detail || 
                           error.response.data?.message || 
                           `Ошибка ${error.response.status}`
            throw new Error(message)
        } else if (error.request) {
            console.error('No response from server:', error.request)
            throw new Error('Сервер не отвечает. Проверьте подключение к бекенду.')
        } else {
            console.error('Request error:', error.message)
            throw new Error('Ошибка при отправке запроса')
        }
    }
)

export default apiClient