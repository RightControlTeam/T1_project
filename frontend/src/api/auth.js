import apiClient from './index'

export const authApi = {
    // Основная функция для входа
    async login(username, password) {
        try {
            const formData = new URLSearchParams()
            formData.append('username', username)
            formData.append('password', password)
            
            //Отправляется запрос формат OAuth2
            const response = await apiClient.post('/user/login/', 
                formData,
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            )
            
            // Получили токен
            if (response.data?.access_token) {
                // Сохраняем токен (будет использоваться для всех запросов)
                localStorage.setItem('token', response.data.access_token)
                localStorage.setItem('isAuth', 'true')
                
                // Сразу после логина получаем профиль пользователя
                // await this.getUserProfile() //для входя не нужно
            }
            
            return response.data
        } catch (error) {
            throw error
        }
    },
    
}