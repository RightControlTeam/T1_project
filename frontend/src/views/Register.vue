<script setup>
import { ref } from 'vue'
import api from '@/api/index'
import { useRouter, RouterLink } from 'vue-router' 

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  is_admin: false
})

const error = ref('')
const valid_errors = ref({
    username: '',
    password: ''
})

function validate_form() {
    valid_errors.value.username = ""
    valid_errors.value.password = ""
    let is_valid = true
    if (!form.value.username) {
        valid_errors.value.username = "Логин обязателен!"
        is_valid = false
    }
    else if (form.value.username.length < 5 || form.value.username.length > 25) {
        valid_errors.value.username = "Длина логина должна быть от 5 до 25 символов!"
        is_valid = false
    }
    else if (!/^\w+$/.test(form.value.username)) {
        valid_errors.value.username = "Логин может содержать только буквы, цифры и нижнее подчёркивание"
        is_valid = false
    }
    else if (/^[0-9_]/.test(form.value.username)) {
        valid_errors.value.username = "Логин не может начинаться с цифры или нижнего подчёркивания"
        is_valid = false
    }

    if (!form.value.password) {
        valid_errors.value.password = "Пароль обязателен!"
        is_valid = false
    }
    else if (form.value.password.length < 8 || form.value.password.length > 40) {
        valid_errors.value.password = "Длина пароля должна быть от 8 до 40 символов"
        is_valid = false
    }
    return is_valid
}

async function register() {
  if (validate_form()) {
    try {
    const response = await api.post('/user/register', form.value)
    console.log('Данные отправлены')
    localStorage.setItem('token', response.data.access_token)
    const response2 = await api.get('/user/list/')
    console.log(response2.data)
    router.push('/')
    setTimeout(() => {
        window.location.reload()
    }, 100)
    }
    catch (e) {
        console.log(e)
        error.value = e
    }
  }
}

</script>

<template>
    <div class="register-page">
        <div class="background-circles">
            <div class="circle circle1"></div>
            <div class="circle circle2"></div>
            <div class="circle circle3"></div>
            <div class="circle circle4"></div>
            <div class="circle circle5"></div>
        </div>
        <div class="register-card">
            <h1>Регистрация</h1>
            <form @submit.prevent="register">
                <div class="group-input">
                    <label for="register">Логин</label>
                    <input id="register" v-model="form.username" placeholder="Придумайте логин">
                    <p v-if="valid_errors.username" class="error">{{ valid_errors.username }}</p>
                </div>
                <div class="group-input">
                    <label for="password">Пароль</label>
                    <input id="password" type="password" v-model="form.password" placeholder="Придумайте пароль">
                    <p v-if="valid_errors.password" class="error">{{ valid_errors.password }}</p>
                </div>
                <div class="group-input">
                <button type="submit">Зарегистрироваться</button>
                <p v-if="error" class="error">{{ error }}</p>
                </div>
            </form>
            <p class="to-register">Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink></p>
        </div>
    </div>
</template>

<style scoped>

.register-page {
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

.register-card {
    background-color: rgba(0, 98, 255, 0.35);
    backdrop-filter: blur(20px);            /* размытие фона */
    -webkit-backdrop-filter: blur(20px);    /* для Safari */
    box-shadow: 0 0 10px rgba(0, 98, 255, 0.35);

    display: flex;
    flex-direction: column;
    gap: 16px;
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

.circle {
    border-radius: 50%;
}

.circle1 {
    position: absolute;
    width: 482.15px;
    height: 472.06px;
    left: -94px;
    top: -154px;

    background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
    filter: blur(7.5px);
    transform: rotate(153.5deg);
}

.circle2 {
    position: absolute;
    width: 426.47px;
    height: 417.45px;
    left: 112.66px;
    top: 418px;

    background: linear-gradient(304.34deg, #E4D5FF 5.87%, #570FD4 94.13%);
    filter: blur(7.5px);
    transform: rotate(-92deg);
}

.circle3 {
    position: absolute;
    width: 280.26px;
    height: 274.33px;
    left: 835px;
    top: 25px;

    background: linear-gradient(291.08deg, #E4D5FF 8.43%, #570FD4 91.57%);
    filter: blur(7.5px);
    transform: rotate(-92deg);
}

.circle4 {
    position: absolute;
    width: 230px;
    height: 219px;
    left: 1086px;
    top: -3px;

    background: linear-gradient(228.4deg, #53F4FF 0.49%, #0044B8 99.51%);
    filter: blur(7.5px);
}

.circle5 {
    position: absolute;
    width: 523px;
    height: 488px;
    left: 880.28px;
    top: 326.12px;

    background: linear-gradient(259.37deg, #53F4FF 8.06%, #0044B8 92.09%);
    filter: blur(7.5px);
    transform: rotate(173.29deg);
}

</style>