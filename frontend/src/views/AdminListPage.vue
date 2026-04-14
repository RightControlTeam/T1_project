<script setup>
import api from '@/api/index'
import { ref } from 'vue'

const admins = ref([])

async function get_admins() {
  try {
    const users = await api.get('user/list')
    admins.value = users.data.filter(user => user.admin_level === 1)
    console.log(admins.value)
  }
  catch(e) {
    console.log(e)
  }
}

async function delete_admin() {
  try {
    
  }
  catch(e) {
    console.log(e)
  }
}
get_admins()
</script>

<template>
  <div class="booking-page">
    <h1>AdminListPage</h1>
    <div class="admin_list" v-for="admin in admins" :key="admin.id">
      {{ admin.username }}
      <button @click="delete_admin">Удалить</button>
    </div>
  </div>
</template>

<style scoped>
.bookings-page {
    padding-left: 0;
}


</style>