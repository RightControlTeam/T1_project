<script setup>
    import { useRouter, useRoute } from 'vue-router'
    import { computed, ref } from 'vue'
    import calendarIcon from '@/components/icons/calendar.svg'
    import katalogIcon from '@/components/icons/katalog.svg'
    const router = useRouter()
    const route = useRoute()
    const showHeader = computed(() => route.path !== '/login' && route.path !== '/register')

    const is_admin = ref(localStorage.getItem('is_admin') === 'true')


    function logout() {
        localStorage.removeItem('token')
        localStorage.removeItem('is_admin')
        window.location.href = '/login'
    }

    const Items = computed(() => {
        const base = [
            { path: '/', title: 'Каталог', icon: katalogIcon },
            { path: '/bookings', title: 'Мои брони', icon: calendarIcon },
        ]
        
        if (is_admin.value) {
            base.push({
                path: '/create_resource',
                title: 'Создать',
                icon: '/src/components/icons/add.svg'
            })
        }
        
        return base
    })


</script>

<template>
    <header v-if="showHeader">
        <nav>
            <RouterLink v-for="item in Items"
                :key="item.path"
                :to="item.path" 
                class="menu"
                active-class="active">
                <img :src="item.icon" :alt="item.title">
                <span>{{ item.title }}</span>
            </RouterLink>
            <button class="logout" @click="logout">Выйти</button>
        </nav>
    </header>
</template>


<style scoped>
    header {
        border-bottom: 2px solid #5D20ED;
        position: fixed;
        left: 0;
        top: 0;
        background: #fff;
        width: 100vw;
    }

    nav {
        display: flex;
        flex-direction: row;
        height: 80px;
        gap: 70px;
        margin: 0px auto;
        justify-content: center;
        align-items: center;
        width: calc(100% - 200px);
    }

    .menu {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        color: #505050
    }

    .menu.active span {
        color: #5D20ED;
    }

    .menu.active img {
        filter: brightness(0) saturate(100%) invert(18%) sepia(100%) saturate(2000%) hue-rotate(250deg);
    }
    .logout {
        margin-left: auto;
    }
    
</style>