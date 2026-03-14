<script setup>
import { ref } from 'vue'
import api from '@/api/index'


const form = ref({
  username: '',
  password: '',
  is_admin: false
})

async function register() {
  try {
    const response = await api.post('/user/register', form.value)
    console.log('Данные отправлены')
    localStorage.setItem('token', response.data.access_token)
    const response2 = await api.get('/user/list/')
    console.log(response2.data)
  }
  catch (error) {
    console.log(error)
  }
}

</script>

<template>
  <body>
    <div class="background-circles">
        <div class="circle circle1"></div>
        <div class="circle circle2"></div>
        <div class="circle circle3"></div>
        <div class="circle circle4"></div>
        <div class="circle circle5"></div>
    </div>
    <div class="register">
        <h1>Регистрация</h1>
        <div>
            <span>Логин</span>
            <input v-model = 'form.username' type = 'text' placeholder="Придумайте логин">
        </div>
        <div>
            <span>Пароль</span>
            <input v-model = 'form.password' type = 'password' placeholder="Придумайте пароль">
        </div>
        <button @click="register()">Зарегистироваться</button>
        <div>
            <h2><router-link to="/login">Войти</router-link></h2>
        </div>
    </div>
</body>

</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

h1{
  color: #fff;
}

span {
  color:#fff;
  display: block;
  margin-bottom: 8px;
}

input {
  display: block;
  background: none;
  border: 1px solid #fff;
  margin-bottom: 24px;
  color: #fff;
  height: 48px;
  width: 100%;
  box-sizing: border-box;
  border-radius: 8px;
  padding-left: 16px;
}

input::placeholder{
    color: #fff;
}

input:focus{
    outline: none;
}

button {
  background: #5D20ED;
  color: #fff;
  border: none;
  height: 48px;
  border-radius: 8px;
  font-weight: medium;
  font-size: 16px;
}

.register {
    height: 406px;
    width: 450px;
    display: flex;
    flex-direction: column;
    background: rgba(0, 80, 208, 0.35);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0px 0px 10px rgba(0, 80, 208, 0.4)
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    background: #BCCDFF;
    height: 100vh;
    margin: 0px;
    font-family: 'Inter', sans-serif;
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