<script setup>
import { ref } from 'vue'
import { register, validate_form } from '@/components/register.js'

const form = ref({
  username: '',
  password: '',
  admin_level: 1
}); 

const error = ref({
    status: '',
    msg: ''
});

const valid_errors = ref({
    username: '',
    password: ''
});

const handleRegisterAdmin = () => {
  register(validate_form, '/user/register-admin', form, error, valid_errors)
}

</script>

<template>
    <div class="register-page">
        <div class="register-card">
            <h1>Регистрация</h1>
            <form @submit.prevent="handleRegisterAdmin">
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
                <p v-if="error.msg" class="error">{{ error.msg }}</p>
                </div>
            </form>
        </div>
    </div>
</template>

<style scoped>

.register-page {
    position: fixed;
    top: 82px;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;

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

</style>