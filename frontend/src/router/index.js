import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import Register from '@/views/Register.vue'
import ResourcesPage from '@/views/ResourcesPage.vue'
import BookingsPage from '../views/BookingsPage.vue'
import CreateResourcePage from '../views/CreateResourcePage.vue'
import CreateAdminPage from '../views/CreateAdminPage.vue'
import AdminListPage from '../views/AdminListPage.vue'

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
        },
        {
            path: '/create_admin',
            name: 'create_admin',
            component: CreateAdminPage,
            meta: {
                requires_auth: true,
                creator_only: true
            }
        },
        {
            path: '/admin_list',
            name: 'admin_list',
            component: AdminListPage,
            meta: {
                requires_auth: true,
                creator_only: true
            }
        },
        // добавить просмотр админов и удаление
    ]
})

router.beforeEach((to, from) => {
    const is_auth = !!localStorage.getItem('token')
    const admin_level = localStorage.getItem('admin_level')

    if (to.meta.requires_auth && !is_auth) {
        return { name: 'login' }
    } else if (!to.meta.requires_auth && is_auth) {
        return { name: 'home' }
    } else if (to.meta.creator_only && admin_level !== '2') {
        return { name: 'home' }
    } else if (to.meta.admin_only && admin_level !== '1') {
        return { name: 'home' }
    }
    // Придумать что-то с superuser
    return true
})

export default router