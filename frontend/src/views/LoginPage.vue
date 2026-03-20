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
    const error = ref({
        status: '',
        msg: ''
    });
    const valid_errors = ref({
        username: '',
        password: ''
    })

    function validate_form() {
        valid_errors.value.username = ''
        valid_errors.value.password = ''
        let is_valid = true
        
        if (!form.value.username) {
            valid_errors.value.username = 'Логин обязателен!'
            is_valid = false
        } else if (!/^\w+$/.test(form.value.username)) {
            valid_errors.value.username = "Логин может содержать только буквы, цифры и _"
            is_valid = false
        } else if (/^[0-9_]/.test(form.value.username)) {
            valid_errors.value.username = "Логин не может начинаться с цифры и _"
            is_valid = false
        } else if (form.value.username.length < 5 || form.value.username.length > 25) {
            valid_errors.value.username = "Длина логина должна быть от 5 до 25 символов"
            is_valid = false
        }

        if (!form.value.password) {
            valid_errors.value.password = "Пароль обязателен!"
            is_valid = false
        } else if (form.value.password.length < 8 || form.value.password.length > 40) {
            valid_errors.value.password = "Длина пароля должна быть от 8 до 40 символов"
            is_valid = false
        }

        return is_valid
    }

    async function login() {
        error.value.status = ''
        error.value.msg = ''

        if (validate_form()) {
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
                if (!e.response) {
                    error.value.msg = 'Сервер не отвечает'
                    console.log('response: ', e.response)
                } else {
                    error.value.status = e.response.status
                    console.log(`Статус ошибки ${error.value.status}`)
                    if (error.value.status == 401) {
                        error.value.msg = 'Неверный логин или пароль'
                    } else if (error.value.status === 403) {
                        error.value.msg = 'Доступ запрещен'
                    } else {
                        error.value.msg = 'Произошла ошибка'
                    }
                    // потом удалить
                    const response2 = await api.get('/user/list')
                    console.log(response2)
                }
            }
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
                    <p v-if="valid_errors.username" class="error valid">{{ valid_errors.username }}</p>
                </div>
                <div class="group-input">
                    <label for="password">Пароль</label>
                    <input id="password" type="password" v-model="form.password" placeholder="Введите пароль">
                    <p v-if="valid_errors.password" class="error valid">{{ valid_errors.password }}</p>
                </div>
                <div class="group-input">
                <button type="submit">Войти</button>
                <p v-if="error.msg" class="error">{{ error.msg }}</p>
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

.error.valid {
    text-align: left;
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