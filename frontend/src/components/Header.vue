<script setup>
    import { useRouter, useRoute } from 'vue-router'
    import { computed } from 'vue'

    const router = useRouter()
    const route = useRoute()
    const showHeader = computed(() => route.path !== '/login' && route.path !== '/register')

    function logout() {
        localStorage.removeItem('token')
        router.push('/login')
    }

</script>

<template>
    <header v-if="showHeader">
        <nav>
            <RouterLink to="/resources">
                <img src="@/components/icons/katalog.svg">
                <span>Каталог</span>
            </RouterLink>
            <RouterLink to="/bookings">
                <img src="@/components/icons/calendar.svg">
                <span>Мои брони</span>
            </RouterLink>
            <button @click="logout">Выйти</button>
        </nav>
    </header>
</template>

<style>
    
</style>