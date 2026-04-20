<script setup>
import api from '@/api/index'
import { ref } from 'vue'

const bookings = ref([])
const currentUserId = ref(null)

async function get_user_id() {
  try {
    const response = await api.get('/user/profile')
    currentUserId.value = response.data.id
    console.log('Текущий пользователь:', currentUserId.value)
    return currentUserId.value
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
    return null
  }
}
async function get_bookings() {
  try {
    const user_id = await get_user_id()
    const response = await api.get('/booking/', {
            params: { user_id: user_id }
        })
    bookings.value = response.data
    console.log(bookings.value)
  } catch (e) {
    console.log(e)
  }
}
get_user_id()
get_bookings()
</script>

<template>
  <div class="booking-page">
    <h1>BookingsPage</h1>
    <div v-for="(booking, index) in bookings" :key="index">
      <p v-if="booking.is_cancelled == false">Booking {{ booking}}</p>
    </div>
  </div>
</template>

<style scoped>
.bookings-page {
    padding-left: 0;
}


</style>
