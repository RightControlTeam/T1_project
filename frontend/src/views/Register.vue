<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router' 
import { register, validate_form } from '@/components/register.js'


const form = ref({
  username: '',
  password: ''
});

const error = ref({
    status: '',
    msg: ''
});

const valid_errors = ref({
    username: '',
    password: ''
});

const handleRegisterUser = async () => {
  await register(validate_form, '/user/register-user', form, error, valid_errors)
}

</script>

<template>
    <div class="register-page">
        <div class="circles-container">
            <div class="circle circle1"></div>
            <div class="circle circle2"></div>
            <div class="circle circle3"></div>
            <div class="circle circle4"></div>
            <div class="circle circle5"></div>
        </div>
        <div class="register-card">
            <h1>Регистрация</h1>
            <form @submit.prevent="handleRegisterUser">
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

.circles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
}

.circle1 {
  width: 480px;
  height: 480px;
  left: -94px;
  top: -154px;
  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(7.5px);
  transform: rotate(153.5deg);
  animation: float1 8s ease-in-out infinite;
}

.circle2 {
  width: 420px;
  height: 420px;
  left: 112.66px;
  top: 418px;
  background: linear-gradient(304.34deg, #E4D5FF 5.87%, #570FD4 94.13%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float2 10s ease-in-out infinite;
}

.circle3 {
  width: 275px;
  height: 275px;
  left: 835px;
  top: 25px;
  background: linear-gradient(291.08deg, #E4D5FF 8.43%, #570FD4 91.57%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float3 8s ease-in-out infinite;
}

.circle4 {
  width: 225px;
  height: 225px;
  left: 1086px;
  top: -3px;
  background: linear-gradient(228.4deg, #53F4FF 0.49%, #0044B8 99.51%);
  filter: blur(7.5px);
  animation: float4 9s ease-in-out infinite;
}

.circle5 {
  width: 520px;
  height: 520px;
  left: 880.28px;
  top: 326.12px;
  background: linear-gradient(259.37deg, #53F4FF 8.06%, #0044B8 92.09%);
  filter: blur(7.5px);
  transform: rotate(173.29deg);
  animation: float5 11s ease-in-out infinite;
}

/* Анимации плавания */
@keyframes float1 {
  0%, 100% {
    transform: rotate(153.5deg) translate(0, 0);
  }
  25% {
    transform: rotate(158.5deg) translate(20px, -15px);
  }
  50% {
    transform: rotate(153.5deg) translate(40px, 10px);
  }
  75% {
    transform: rotate(148.5deg) translate(-10px, 25px);
  }
}

@keyframes float2 {
  0%, 100% {
    transform: rotate(-92deg) translate(0, 0);
  }
  25% {
    transform: rotate(-87deg) translate(-25px, 20px);
  }
  50% {
    transform: rotate(-92deg) translate(-15px, -20px);
  }
  75% {
    transform: rotate(-97deg) translate(15px, -10px);
  }
}

@keyframes float3 {
  0%, 100% {
    transform: rotate(-92deg) translate(0, 0);
  }
  33% {
    transform: rotate(-87deg) translate(30px, 15px);
  }
  66% {
    transform: rotate(-97deg) translate(-15px, -25px);
  }
}

@keyframes float4 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, 15px) scale(1.05);
  }
  50% {
    transform: translate(-15px, 20px) scale(0.95);
  }
  75% {
    transform: translate(25px, -15px) scale(1.02);
  }
}

@keyframes float5 {
  0%, 100% {
    transform: rotate(173.29deg) translate(0, 0);
  }
  20% {
    transform: rotate(178.29deg) translate(-20px, -20px);
  }
  40% {
    transform: rotate(173.29deg) translate(-35px, 15px);
  }
  60% {
    transform: rotate(168.29deg) translate(15px, 25px);
  }
  80% {
    transform: rotate(173.29deg) translate(25px, -10px);
  }
}

</style>