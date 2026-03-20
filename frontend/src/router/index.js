import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import Register from '@/views/Register.vue'
import ResourcesPage from '@/views/ResourcesPage.vue'
import BookingsPage from '../views/BookingsPage.vue'
import CreateResourcePage from '../views/CreateResourcePage.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: ResourcesPage,
            meta: { requires_auth: true }
        },
        {
            path: '/login',
            name: 'login',
            component: LoginPage,
            meta: { requires_auth: false }
        },
        {
            path: '/register',
            name: 'register',
            component: Register,
            meta: { requires_auth: false }
        },
        {
            path: '/bookings',
            name: 'bookings',
            component: BookingsPage,
            meta: { requires_auth: true }
        },
        {
            path: '/create_resource',
            name: 'create_resource',
            component: CreateResourcePage,
            meta: {
                requires_auth: true,
                admin_only: true
            }
        }
    ]
})

router.beforeEach((to, from) => {
    const is_auth = !!localStorage.getItem('token')
    const is_admin = !!localStorage.getItem('is_admin')

    if (to.meta.requires_auth && !is_auth) {
        return { name: 'login' }
    } else if (!to.meta.requires_auth && is_auth) {
        return { name: 'home' }
    } else if (to.meta.admin_only && !is_admin) {
        return { name: 'home' }
    }
    
    return true
})

export default router