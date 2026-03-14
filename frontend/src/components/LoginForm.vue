<script setup>
import { ref } from 'vue'
import { authApi } from '@/api/auth'

const login = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const emit = defineEmits(['success'])

async function handleSubmit() {
    // очищаем предыдущую ошибку
    error.value = ''
    loading.value = true

    try {
        await authApi.login(login.value, password.value)

        emit('success')
    } catch (e) {
        error.value = e.message || 'Неверный логин или пароль'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <form @submit.prevent="handleSubmit">
        <div class="group-input">
            <label for="login">Логин</label>
            <input id="login" v-model="login" placeholder="Введите логин">
        </div>
        <div class="group-input">
            <label for="password">Пароль</label>
            <input id="password" type="password" v-model="password" placeholder="Введите пароль">
        </div>
        <div class="group-input">
        <button type="submit">Войти</button>
        <p v-if="error" class="error">{{ error }}</p>
        </div>
    </form>
</template>

<style scoped>
form {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.group-input {
    flex: 1;
    display: flex;
    gap: 8px;
    flex-direction: column;
}

input {
    flex: 1;
    padding: 12px 16px;
    background: none;
    border: 2px solid white;
    border-radius: 8px;
    outline: none; /*Убираем стандартные обводки браузера*/
    color: white;
    font-size: 16px;
}

input:hover {
    border: 2px solid #5D20ED;
}

input:focus {
    border: 2px solid #5D20ED;
}

input::placeholder {
    color: white;
    font-size: 16px;
    font-weight: 500;
}

label {
    color: white;
    font-size: 16px;
}

button {
    flex: 1;
    padding: 12px 0;
    background: #5D20ED; /*5D20ED  4c00ff*/
    color: #ffffff;
    border-radius: 8px;
    border: none;
    font-size: 16px;
    font-weight: 500;
}

.error {
    font-size: 14px;
    text-align: center;
    color: rgb(255, 0, 0);
}
</style>