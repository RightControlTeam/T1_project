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
            component: ResourcesPage
        },
        {
            path: '/login',
            name: 'login',
            component: LoginPage
        },
        {
            path: '/register',
            name: 'register',
            component: Register
        },
        {
            path: '/bookings',
            name: 'bookings',
            component: BookingsPage
        },
        {
            path: '/create_resource',
            name: 'create_resource',
            component: CreateResourcePage
        }
    ]
})

export default router