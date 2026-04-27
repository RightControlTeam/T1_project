<script setup>
import api from '@/api/index'
import { ref, onMounted } from 'vue'

const admins = ref([])
const page = ref(1)
const total_pages = ref(3)
// TODO: get total pages from backend
// TODO: catch errors
let limit = 10

async function get_admins() {
  try {
    const users = await api.get('/user', 
    { params: { admins: true, skip: (page.value - 1) * limit, limit } })
    admins.value = users.data
    console.log(users.data)
  }
  catch(e) {
    console.log(e)
  }
}

async function delete_admin(adminId) {
  try {
    const response = await api.delete(`/user/${adminId}`)
    console.log('success')
    await get_admins()
  }
  catch(e) {
    console.log(e)
  }
}

async function next_page() {
  if (page.value < total_pages.value) {
    page.value++
    await get_admins()
  }
}

async function prev_page() {
  if (page.value > 1) {
    page.value--
    await get_admins()
  }
}

onMounted(() => {
  get_admins()
})
</script>

<template>
  <div class="booking-page">
    <h1>AdminListPage</h1>
    <div>
      <button @click="prev_page" :disabled="page===1"><</button>
      <span>{{ page }}</span>
      <button @click="next_page" :disabled="page===total_pages">></button>
    </div>
    <div class="admin_list" v-for="admin in admins" :key="admin.id">
      {{ admin.username }}
      <button @click="delete_admin(admin.id)">Удалить</button>
    </div>
  </div>
</template>

<style scoped>
.bookings-page {
    padding-left: 0;
}


</style>