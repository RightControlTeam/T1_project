import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import ResourcesPage from '@/views/ResourcesPage.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: ResourcesPage
        },
        {
            path: '/login',
            name: 'login',
            component: LoginPage
        }
    ]
})

// Проверка, что пользователь вошел
router.beforeEach((to, from) => {
    const isAuth = localStorage.getItem('auth') // обращаемся к хранилище браузера

    if (!isAuth && to.path !== '/login') {
        return '/login'
    }

    if (isAuth && to.path === '/login') {
    return '/'
    }
})

export default router