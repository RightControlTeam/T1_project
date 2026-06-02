<script setup>
import api from '@/api/index'
import { ref, onMounted } from 'vue'
import user from '@/components/icons/image.png'

const admins = ref([])
const page = ref(1)
const total_pages = ref(3)
let limit = 10

async function get_admins() {
  try {
    const users = await api.get('/user', 
    { params: { admins: true, skip: (page.value - 1) * limit, limit } })
    admins.value = users.data
    console.log(users.data)
    total_pages.value = Math.ceil(users.headers['x-total-count'] / limit)
  }
  catch(e) {
    console.log(e)
  }
}

async function delete_admin(adminId) {
  if (confirm('Вы уверены, что хотите удалить этого администратора?')) {
  try {
    const response = await api.delete(`/user/${adminId}`)
    console.log('success')
    await get_admins()
  }
  catch(e) {
    console.log(e)
  }
}
}

async function confirmDelete(adminId) {
  if (confirm('Вы уверены, что хотите удалить этого администратора?')) {
    await delete_admin(adminId)
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
    <h2>Администраторы сайта:</h2>
    <div v-if="total_pages !== 1" class="pagination">
      <button @click="prev_page" :disabled="page===1"><</button>
      <span>{{ page }}</span>
      <button @click="next_page" :disabled="page===total_pages">></button>
    </div>
    <div class="admin_list" v-for="admin in admins" :key="admin.id">
      <img :src="user" wigth=24 height=24 alt="user">
      {{ admin.username }}
      <button @click="confirmDelete(admin.id)" class="delete">Удалить</button>
    </div>
  </div>
</template>

<style scoped>

.pagination {
  margin: 15px 0px;
}

.pagination button {
  color:black;
  background: #fff;
}

span {
  margin: 0px 4px;
}

button.delete{
  margin: 16px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  border: 2px solid #ED2023;
  font-size: 16px;
  color: #ED2023;
  font-weight: 400;
}

.admin_list {
  display: flex;
  align-items: center;
  gap: 5px;
}


</style>