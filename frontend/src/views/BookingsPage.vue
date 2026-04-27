<script setup>
import api from '@/api/index'
import { ref, onMounted, computed } from 'vue'
import timeIcon from '@/components/icons/time.svg'
import calendar2Icon from '@/components/icons/calendar2.svg'

const bookings = ref([])
const currentUserId = ref(null)
const is_loading = ref(true)

async function get_user_id() {
  try {
    const response = await api.get('/user/profile/')
    currentUserId.value = response.data.id
    return currentUserId.value
  } catch (error) {
    console.error('Ошибка получения пользователя:', error)
    return null
  }
}

function formatToMoscow(utc_time) {
  const date = new Date(utc_time)
  return date.toLocaleString('ru-RU', {
        timeZone: 'Europe/Moscow',
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

async function get_bookings() {
  try {
    const user_id = await get_user_id()
    const response = await api.get('/booking/', {
            params: { user_id: user_id }
        })
    bookings.value = response.data
    bookings.value.forEach((booking, index) => {
        bookings.value[index].start_time = formatToMoscow(booking.start_time)
        bookings.value[index].end_time = formatToMoscow(booking.end_time)
    })
    await load_resources()
  } catch (e) {
    console.log(e)
  }
}

async function load_resources() {
  if (!bookings.value.length) return
  const promises = bookings.value.map(async (booking) => {
    try {
      const response = await api.get(`/resource/${booking.resource_id}`)
      booking.resource = response.data
    }
    catch (e) {
      console.log(e)
    }
  })
  await Promise.all(promises)
}

async function delete_booking(booking_id) {
  try {
    const confirmed = confirm('Вы уверены, что хотите отменить эту бронь?')
    if (!confirmed) return
    await api.delete(`/booking/${booking_id}`)
    console.log('success')
    await get_bookings()
    await load_resources()
  }
  catch (e) {
    console.log(e)
  }
}

const activeBookings = computed(() => {
  return bookings.value
    .filter(booking => !booking.is_cancelled)
    .map(booking => ({
      ...booking,
      resource: booking.resource
    }))
})

onMounted(async () => {
  await get_bookings()
  is_loading.value = false
  console.log(bookings.value)
})
</script>

<template>
  <div>
    <div v-if="is_loading">
      Загрузка...
    </div>
    <div v-else class="cards">
      <div v-for="(booking, index) in activeBookings" :key="index">
      <div class="card">
        <h3>{{ booking.resource?.name }}</h3>
        <div>
          <span class="description">Описание:</span>
          <p>{{ booking.resource?.description }}</p>
        </div>
        <div class="line"></div>
        <div class="book-box">
          <div class="circle"></div>
          <span class="book">Забронировано</span>
        </div>
        <div class="block">
          <img :src="timeIcon" alt="time">
          <span>{{ booking.start_time.split(' ')[0].slice(0, 10)}}</span>
        </div>
        <div class="block">
          <img :src="calendar2Icon" alt="calendar2">
          <span>{{ booking.start_time.split(' ')[1] }} - {{ booking.end_time.split(' ')[1]}}</span>
        </div>
        <div class="buttons">
          <button @click="delete_booking(booking.id)" class="cancelled">Отменить</button>
          <button>Изменить</button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
.book-box {
  display: flex;
  align-items: center;
  gap: 4px;
}

.circle {
  width: 8px;
  height: 8px;
  background: #66E66A;
  border-radius: 50px;
}
.book {
  line-height: 1.4;
  font-style: italic;
  color:black;
}
.description{
  color:black;
}

.line{
  margin: auto;
  width: 128.43px;
  height: 0px;
  border: 1px solid #505050;
}

.block {
  gap: 5px;
  display: flex;
  align-items: center;
}

.block span {
  line-height: 1.4; /* фиксируем высоту строки */
}

.cards {
  display: flex;
  flex-direction: row;
  gap: 16px;
  margin-top: 20px;
  flex-wrap:wrap;
}

.card{
  display: flex;
  flex-direction:column;
  padding: 16px;
  box-shadow: 0 0 8px rgba(93, 32, 237, 0.2);
  border-radius: 16px;
  width: 744px;
  gap: 8px;
}

span {
  color: #505050;
}

p {
  color: #505050;
  font-size: 14px;
  margin-top: 4px;
}

.buttons {
  padding: 0px 220px;
  display: flex;
  flex-direction: row;
}

button {
    margin: 8px auto;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    border: 2px solid #5D20ED;
    font-size: 16px;
    color: #5D20ED;
    font-weight: 400;
}
.cancelled {
    margin: 8px auto;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    border: 2px solid #ED2023;
    font-size: 16px;
    color: #ED2023;
    font-weight: 400;
}
</style>
