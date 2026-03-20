<script setup>
    import { ref } from 'vue'
    import api from '@/api/index'
    import { useRouter, RouterLink } from 'vue-router'
    import qs from 'qs'     // библиотека, которая преобразует JavaScript объекты в формат application/x-www-form-urlencoded для OAuth 2.0 Password Grant

    const router = useRouter()

    const form = ref({
        username: '',
        password: ''
    })

    const error = ref('');

    async function login() {
        error.value = ''

        try {
            console.log('Отправляю')
            const response = await api.post('/user/login', 
                                            qs.stringify(form.value), 
                                            {headers: 
                                                {'Content-Type': 'application/x-www-form-urlencoded'}
                                            })
            console.log('Данные отправлены')
            localStorage.setItem('token', response.data.access_token)
            localStorage.setItem('is_admin', response.data.is_admin)
            console.log(response.data.is_admin)
            router.push('/')
        } catch (e) {
            const info = e.response.data.detail[0]
            console.log(e.response)
            error.value = `${e.response.status}: ${info.loc[1]} ${info.msg}`
            // потом удалить
            const response2 = await api.get('/user/list')
            console.log(response2)
        }
    }
</script>

<template>
    <div class="login-page">
        <div class="login-card">
            <h1>Вход</h1>
            <form @submit.prevent="login">
                <div class="group-input">
                    <label for="login">Логин</label>
                    <input id="login" v-model="form.username" placeholder="Введите логин">
                </div>
                <div class="group-input">
                    <label for="password">Пароль</label>
                    <input id="password" type="password" v-model="form.password" placeholder="Введите пароль">
                </div>
                <div class="group-input">
                <button type="submit">Войти</button>
                <p v-if="error" class="error">{{ error }}</p>
                </div>
            </form>
            <p class="to-register">Ещё нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink></p>
        </div>
    </div>
</template>

<style scoped>

.login-page {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    min-height: 100vh;

    background: rgb(167, 201, 255);
    
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-card {
    background-color: rgba(0, 98, 255, 0.35);
    backdrop-filter: blur(20px);            /* размытие фона */
    -webkit-backdrop-filter: blur(20px);    /* для Safari */
    box-shadow: 0 0 10px rgba(0, 98, 255, 0.35);

    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 400px;
    padding: 16px;
    margin: 16px;
    border-radius: 16px;
}

h1 {
    text-align: center;
    font-size: 32px;
    color: white;
    font-weight: 700;
}

form {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.group-input {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

label {
    font-size: 16px;
    color: white;
    font-weight: 400;
}

input {
    flex: 1;
    padding: 12px 16px;
    background: none;
    border: 2px solid white;
    border-radius: 8px;
    outline: none; /*Убираем стандартные обводки браузера*/
    font-size: 16px;
    color: white;
    font-weight: 400;
}

input:hover {
    border: 2px solid #5D20ED;
}

input:focus {
    border: 2px solid #5D20ED;
}

input::placeholder {
    font-size: 16px;
    color: white;
    font-weight: 400;
}

button {
    flex: 1;
    padding: 12px 0;
    background: #5D20ED; /*5D20ED  4c00ff*/
    border-radius: 8px;
    border: none;
    font-size: 16px;
    color: white;
    font-weight: 400;
}

.error {
    font-size: 14px;
    text-align: center;
    color: rgb(255, 0, 0);
    font-weight: 400;
}

.to-register {
    font-size: 14px;
    color: white;
    font-weight: 400;
}

a {
    font-size: 14px;
    color: #5D20ED;
    text-decoration: none;  /* убирает подчеркивание */
    font-weight: 400;
}



</style>