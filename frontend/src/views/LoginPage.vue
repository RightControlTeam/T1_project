<script setup>
    import LoginForm from '@/components/LoginForm.vue'
    import { useRouter, RouterLink } from 'vue-router'

    const router = useRouter()
    
    function onLogin() {
        localStorage.setItem('auth', 'true')

        router.push('/')
    }
</script>

<template>
    <div class="background-circles">
        <div class="circle circle1"></div>
        <div class="circle circle2"></div>
        <div class="circle circle3"></div>
        <div class="circle circle4"></div>
        <div class="circle circle5"></div>
    </div>
    <div class="login-page">
        <div class="login-card">
            <h1>Вход</h1>
            <LoginForm @success="onLogin"/>
            <p class="to-register">Ещё нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink></p> <!--Надо вставить путь до регистрации-->
        </div>
    </div>
</template>

<style scoped>
h1 {
    text-align: center;
    color: white;
    font-size: 36px;
}

.login-page {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    min-height: 100vh;

    background: rgb(167, 201, 255); /*можно попробывать разные цвета*/
    
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-card {
    background: rgba(0, 98, 255, 0.35);
    backdrop-filter: blur(20px);            /* размытие фона */
    -webkit-backdrop-filter: blur(20px);    /* для Safari */
    box-shadow: 0 0 10px rgba(0, 98, 255, 0.35);

    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 400px;
    padding: 16px;
    margin: 16px; /*от края экрана должны быть отступы до формы*/
    border-radius: 16px;
}

.to-register {
    color: white;
    font-size: 14px;
}

a {
    color: #5D20ED;
    text-decoration: none;  /* убирает подчеркивание */
}


</style>