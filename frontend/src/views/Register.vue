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

const handleRegister = () => {
  register(validate_form, '/user/register-user', form, error, valid_errors)
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
            <div class="circle circle6"></div>
        </div>
        <div class="register-card">
            <h1>Регистрация</h1>
            <form @submit.prevent="handleRegister">
                <div class="group-input">
                    <label for="register">Логин</label>
                    <input id="register" v-model="form.username" placeholder="Придумайте логин">
                    <p v-if="valid_errors.username" class="error valid">{{ valid_errors.username }}</p>
                </div>
                <div class="group-input">
                    <label for="password">Пароль</label>
                    <input id="password" type="password" v-model="form.password" placeholder="Придумайте пароль">
                    <p v-if="valid_errors.password" class="error valid">{{ valid_errors.password }}</p>
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

    background: #BCCDFF;
    
    display: flex;
    align-items: center;
    justify-content: center;
}

.register-card {
    background-color: rgba(0, 98, 255, 0.35);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 0 10px rgba(0, 98, 255, 0.35);

    display: flex;
    flex-direction: column;
    gap: 24px;
    width: clamp(300px, 90vw, 400px);
    padding: clamp(12px, 4vw, 16px);
    margin: 16px;
    border-radius: 16px;
}

h1 {
    text-align: center;
    font-size: clamp(24px, 8vw, 32px);
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
    font-size: clamp(14px, 4vw, 16px);
    color: white;
    font-weight: 400;
}

input {
    flex: 1;
    padding: clamp(10px, 3vw, 12px) clamp(12px, 4vw, 16px);
    background: none;
    border: 2px solid white;
    border-radius: 8px;
    outline: none;
    font-size: clamp(14px, 4vw, 16px);
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
    font-size: clamp(14px, 4vw, 16px);
    color: white;
    font-weight: 400;
}

button {
    flex: 1;
    padding: clamp(10px, 3vw, 12px) 0;
    background: #5D20ED;
    border-radius: 8px;
    border: none;
    font-size: clamp(14px, 4vw, 16px);
    color: white;
    font-weight: 400;
}

.error {
    font-size: clamp(12px, 3vw, 14px);
    text-align: center;
    color: rgb(255, 0, 0);
    font-weight: 400;
}

.error.valid {
    text-align: left;
    padding-left: 8px;
}

.to-register {
    font-size: clamp(12px, 3vw, 14px);
    color: white;
    font-weight: 400;
}

a {
    font-size: clamp(12px, 3vw, 14px);
    color: #5D20ED;
    text-decoration: none;
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
  left: -50px;
  top: -30px;
  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(7.5px);
  transform: rotate(153.5deg);
  animation: float1 12s ease-in-out infinite;
}

.circle2 {
  width: 420px;
  height: 420px;
  left: clamp(100px, 150px, 250px);
  top: 418px;
  background: linear-gradient(304.34deg, #E4D5FF 5.87%, #570FD4 94.13%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float2 10s ease-in-out infinite;
}

.circle3 {
  width: 275px;
  height: 275px;
  left: 860px;
  top: 50px;
  background: linear-gradient(291.08deg, #E4D5FF 8.43%, #570FD4 91.57%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float3 9s ease-in-out infinite;
}

.circle6 {
  width: 310px;
  height: 310px;
  right: 50px;
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
  animation: float4 11s ease-in-out infinite;
}

.circle5 {
  width: clamp(430px, 480px, 520px);
  height: clamp(430px, 480px, 520px);
  left: auto;
  right: clamp(60px,  110px, 150px);
  top: 400px;
  background: linear-gradient(259.37deg, #53F4FF 8.06%, #0044B8 92.09%);
  filter: blur(7.5px);
  transform: rotate(173.29deg);
  animation: float5 13s ease-in-out infinite;
}
/* АНИМАЦИИ */

/* Круг 1 - плавное движение по диагонали */
@keyframes float1 {
  0%, 100% {
    transform: rotate(153.5deg) translate(0, 0);
  }
  25% {
    transform: rotate(153.5deg) translate(clamp(15px, 2vw, 40px), clamp(-10px, -1.5vw, -30px));
  }
  50% {
    transform: rotate(153.5deg) translate(clamp(30px, 4vw, 80px), clamp(10px, 1.5vw, 20px));
  }
  75% {
    transform: rotate(153.5deg) translate(clamp(-10px, -1vw, -20px), clamp(15px, 2vw, 40px));
  }
}

/* Круг 2 - движение по треугольнику (вправо-вниз → влево-вниз → назад) */
@keyframes float2 {
  0% {
    transform: rotate(-92deg) translate(0, 0);
  }
  33% {
    transform: rotate(-92deg) translate(clamp(30px, 4vw, 80px), clamp(30px, 4vw, 80px));
  }
  66% {
    transform: rotate(-92deg) translate(clamp(-30px, -4vw, -80px), clamp(30px, 4vw, 80px));
  }
  100% {
    transform: rotate(-92deg) translate(0, 0);
  }
}

/* Круг 3 - восьмёрка/бесконечность */
@keyframes float3 {
  0%, 100% {
    transform: rotate(-92deg) translate(0, 0);
  }
  25% {
    transform: rotate(-92deg) translate(clamp(20px, 3vw, 50px), clamp(-15px, -2vw, -30px));
  }
  50% {
    transform: rotate(-92deg) translate(0, clamp(-25px, -3vw, -50px));
  }
  75% {
    transform: rotate(-92deg) translate(clamp(-20px, -3vw, -50px), clamp(-15px, -2vw, -30px));
  }
}

/* Круг 4 - плавное масштабирование с движением */
@keyframes float4 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(clamp(15px, 2vw, 30px), clamp(10px, 1.5vw, 25px)) scale(1.05);
  }
  50% {
    transform: translate(clamp(-10px, -1.5vw, -20px), clamp(15px, 2vw, 30px)) scale(0.95);
  }
  75% {
    transform: translate(clamp(20px, 2.5vw, 40px), clamp(-10px, -1.5vw, -20px)) scale(1.02);
  }
}

/* Круг 5 - большой круг с вращением */
@keyframes float5 {
  0%, 100% {
    transform: rotate(173.29deg) translate(0, 0);
  }
  20% {
    transform: rotate(178.29deg) translate(clamp(-15px, -2vw, -30px), clamp(-15px, -2vw, -30px));
  }
  40% {
    transform: rotate(173.29deg) translate(clamp(-25px, -3.5vw, -50px), clamp(10px, 1.5vw, 25px));
  }
  60% {
    transform: rotate(168.29deg) translate(clamp(15px, 2vw, 30px), clamp(20px, 2.5vw, 40px));
  }
  80% {
    transform: rotate(173.29deg) translate(clamp(20px, 2.5vw, 40px), clamp(-10px, -1.5vw, -20px));
  }
}

@media (max-width: 1750px) {
  .circle6 {
    display: none;
  }
}

@media (max-width: 1280px) {
  .circle1 {
  width: 380px;
  height: 380px;
  left: -50px;
  top: -30px;
  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(7.5px);
  transform: rotate(153.5deg);
  animation: float1 12s ease-in-out infinite;
}

.circle2 {
  width: 380px;
  height: 380px;
  left: 40px;
  top: 418px;
  background: linear-gradient(304.34deg, #E4D5FF 5.87%, #570FD4 94.13%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float2 10s ease-in-out infinite;
}

.circle3 {
  width: 275px;
  height: 275px;
  left: auto;
  right: 180px;
  top: 50px;
  background: linear-gradient(291.08deg, #E4D5FF 8.43%, #570FD4 91.57%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float3 9s ease-in-out infinite;
}

.circle4 {
  width: 225px;
  height: 225px;
  left: auto;
  right: 40px;
  top: -3px;
  background: linear-gradient(228.4deg, #53F4FF 0.49%, #0044B8 99.51%);
  filter: blur(7.5px);
  animation: float4 11s ease-in-out infinite;
}

.circle5 {
  width: 320px;
  height: 320px;
  left: auto;
  right: clamp(60px,  110px, 150px);
  top: 480px;
  background: linear-gradient(259.37deg, #53F4FF 8.06%, #0044B8 92.09%);
  filter: blur(7.5px);
  transform: rotate(173.29deg);
  animation: float5 13s ease-in-out infinite;
}
}

@media (max-width: 960px) {
  .circle4 {
    display: none;
  } 
  .circle2 {
  width: 340px;
  height: 340px;
  left: 40px;
  top: 418px;
  background: linear-gradient(304.34deg, #E4D5FF 5.87%, #570FD4 94.13%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float2 10s ease-in-out infinite;
}
  .circle3 {
  width: 275px;
  height: 275px;
  left: auto;
  right: 70px;
  top: 50px;
  background: linear-gradient(291.08deg, #E4D5FF 8.43%, #570FD4 91.57%);
  filter: blur(7.5px);
  transform: rotate(-92deg);
  animation: float3 9s ease-in-out infinite;
}

  .circle5 {
  width: 320px;
  height: 320px;
  left: auto;
  right: 45px;
  top: 460px;
  background: linear-gradient(259.37deg, #53F4FF 8.06%, #0044B8 92.09%);
  filter: blur(7.5px);
  transform: rotate(173.29deg);
  animation: float5 13s ease-in-out infinite;
}
}

@media (max-width: 768px) {
  .circle2,
  .circle4 {
    display: none;
  }
  .circle6{
    display: block;
  }

.circle1 {
  width: 270px;
  height: 270px;
  left: -100.65px;
  top: 75.97px;

  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(4px);
}

.circle3 {
  width: 300px;
  height: 300px;
  top: 360px;
  left: auto;
  right: -20px;
  background: linear-gradient(258.41deg, #E4D5FF 6.69%, #570FD4 93.31%);
  filter: blur(4px);
}

.circle6 {
  width: 330px;
  height: 330px;
  left: -113.18px;
  right: auto;
  top: 540.94px;

  background: linear-gradient(258.41deg, #E4D5FF 6.69%, #570FD4 93.31%);
  filter: blur(4px);
}


.circle5 {
  width: 220px;
  height: 220px;
  left: auto;
  right: 100px;
  top: 20px;

  background: linear-gradient(77.41deg, #53F4FF 9.17%, #0044B8 91.41%);
  filter: blur(4px);
}
}


@media (max-width: 480px) {
  .circle2,
  .circle4 {
    display: none;
  }
  .register-card {
    padding: 40px 32px; 
    width: 300px;
    gap: 24px;
  }
  

.circle1 {
  width: 239px;
  height: 234px;
  left: -140.65px;
  top: 128.97px;

  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(4px);
}

.circle3 {
  width: 143px;
  height: 136px;
  left: auto;
  right: -10px;
  top: 390px;

  background: linear-gradient(180deg, #53F4FF 0%, #0044B8 100%);
  filter: blur(4px);
}

.circle6 {
  width: 331px;
  height: 324px;
  left: -113.18px;
  top: 540.94px;

  background: linear-gradient(258.41deg, #E4D5FF 6.69%, #570FD4 93.31%);
  filter: blur(4px);
}


.circle5 {
  width: 237px;
  height: 221px;
  left: 218px;
  top: 66px;

  background: linear-gradient(77.41deg, #53F4FF 9.17%, #0044B8 91.41%);
  filter: blur(4px);
}
}

</style>