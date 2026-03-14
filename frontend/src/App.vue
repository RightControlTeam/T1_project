<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

// Показывать шапку только НЕ на странице входа
const showHeader = computed(() => route.path !== '/login' && route.path !== '/register')
</script>

<template>
    <div>
        <!-- Шапка только если showHeader = true -->
        <header v-if="showHeader">
            <nav>
                <RouterLink to="/">Главная</RouterLink>
                <button @click="logout">Выйти</button>
            </nav>
        </header>
        
        <!-- Здесь показываются страницы -->
        <main>
            <RouterView />
        </main>
    </div>
</template>

<script>
// Отдельный скрипт для метода logout
export default {
    methods: {
        logout() {
            localStorage.removeItem('auth')
            this.$router.push('/login')
        }
    }
}
</script>

<style scoped>
header {
    background: #42b883;
    padding: 1rem;
    color: rgb(104, 104, 104);
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

a {
    color: rgb(0, 0, 0);
    text-decoration: none;
}

button {
    padding: 5px 10px;
    background: rgb(0, 0, 0);
    color: #42b883;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>
