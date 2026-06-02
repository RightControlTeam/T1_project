<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import timeIcon from '@/components/icons/time.svg'
import calendar2Icon from '@/components/icons/calendar2.svg'
import api from '@/api/index'

const filter = ref(false)
const is_loading = ref(false)
const form = ref({
  name: '',
  description: '',
})
const error = ref('')
const resources = ref([])
let interval = null
const booking_resource = ref()
const usernames = ref({})
const bookings = ref([])
const today = ref('')

const update = () => {
  const now = new Date()
  const day = String(now.getDate()).padStart(2, '0')
  today.value = day
}

const is_today = (booking_day) => {
  return booking_day === today.value
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

async function get_username(user_id) {
    if (usernames.value[user_id]) {
        return usernames.value[user_id]
    }
    try {
        const response = await api.get(`/user/${user_id}`)
        return response.data.username
    }
    catch(e) {
        console.log(e)
    }
}

async function loadUsernamesForBookings() {
  const userIds = [...new Set(bookings.value.map(b => b.user_id))]
  
  for (const userId of userIds) {
    if (!usernames.value[userId]) {
      try {
        const response = await api.get(`/user/${userId}`)
        usernames.value[userId] = response.data.username
      } catch(e) {
        console.log(e)
        usernames.value[userId] = `Пользователь ${userId}`
      }
    }
  }
}

async function searchResources() {
  if (!form.value.name) return
  
  is_loading.value = true
  try {
    const response = await api.get('/resource/', {
      params: { name: form.value.name }
    })
    resources.value = response.data
    
    const searchTerm = form.value.name.toLowerCase()

    // Сортировка по релевантности
    const sorted = response.data.sort((a, b) => {
    const aName = a.name.toLowerCase()
    const bName = b.name.toLowerCase()
    
    // Полное совпадение
    if (aName === searchTerm) return -1
    if (bName === searchTerm) return 1
    
    // Начинается с...
    if (aName.startsWith(searchTerm) && !bName.startsWith(searchTerm)) return -1
    if (bName.startsWith(searchTerm) && !aName.startsWith(searchTerm)) return 1
    
    // Содержит...
    if (aName.includes(searchTerm) && !bName.includes(searchTerm)) return -1
    if (bName.includes(searchTerm) && !aName.includes(searchTerm)) return 1
    
    return aName.localeCompare(bName)
    })

    resources.value = sorted
    return sorted[0]

  } catch (error) {
    console.error('Ошибка поиска:', error)
  }
}

async function load_bookings() {
    error.value = ''
    filter.value = false
    bookings.value = []
    usernames.value = {}
    booking_resource.value = null
    is_loading.value = true
    booking_resource.value = await searchResources()
    if (!booking_resource.value) {
        error.value = "Нет ресурсов с таким именем"
        is_loading.value = false
        console.log("Ничего не найдено")
        return
    }
    const resource_id = booking_resource.value?.id
    try {
        const response = await api.get('/booking/', {
            params: { resource_id: resource_id }
        })
        if (response.data.length === 0) {
            error.value = "У этого ресурса пока нет броней"
            is_loading.value = false
            return
        }
        const sortedBookings = response.data.sort((a, b) => 
        new Date(a.start_time) - new Date(b.start_time)
        );
        bookings.value = sortedBookings
        bookings.value.forEach((booking, index) => {
            bookings.value[index].start_time = formatToMoscow(booking.start_time)
            bookings.value[index].end_time = formatToMoscow(booking.end_time)
        })
        await loadUsernamesForBookings()
        filter.value = true
        is_loading.value = false
        console.log(response.data)
    }
    catch (e) {
        console.log(e)
    }
}

async function delete_booking(booking_id) {
  try {
    const confirmed = confirm('Вы уверены, что хотите отменить эту бронь?')
    if (!confirmed) return
    await api.delete(`/booking/${booking_id}`)
    console.log('success')
    await load_bookings()
  }
  catch (e) {
    console.log(e)
  }
}

const activeBookings = computed(() => {
  const res = bookings.value
    .filter(booking => !booking.is_cancelled && !booking.is_ended)
    .map(booking => ({
      ...booking,
      resource: booking.resource
    }))
  if (res.length === 0) {
    error.value = " У этого ресурса нет активных броней"
  }
  return res
})

onMounted(async () => {
  update()
  interval = setInterval(update, 60000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

</script>

<template>
    <h2>Все брони</h2>
    <div class="booking-page">
    <div class="group-input">
        <label for="name">Введите имя ресурса
        </label>
        <input id="name" v-model="form.name" placeholder="Имя ресурса">
    </div>
    <button @click="load_bookings()">
        Загрузить
    </button>
    <div v-if="is_loading" class="loading">
      Загрузка...
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-else-if="filter" class="cards">
      <div v-for="(booking, index) in activeBookings " :key="index">
        <div class="card_book">
          <h3>{{ booking_resource?.name }}</h3>
          <div>
            <span class="description">Описание:</span>
            <p>{{ booking_resource?.description }}</p>
          </div>
          <div class="line"></div>
          <div class="mark">
            <div class="book-box">
              <div class="circle"></div>
              <span class="book">Забронировано пользователем {{ usernames[booking.user_id] }}</span>
            </div>
            <div v-if="is_today(booking.start_time.split(' ')[0].split('.')[0])" class="today">
              Сегодня
            </div>
          </div>
          <div class="block">
            <img :src="timeIcon" alt="time">
            <span>{{ booking.start_time.split(' ')[0].slice(0, 10)}}</span>
          </div>
          <div class="block">
            <img :src="calendar2Icon" alt="calendar2">
            <span>{{ booking.start_time.split(' ')[1] }} - {{ booking.end_time.split(' ')[1]}}</span>
          </div>
          <button @click="delete_booking(booking.id)" class="cancelled">Отменить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-message {
  margin-top: 20px;
  padding: 16px 20px;
  text-align: center;
  background: #F3E5F5;
  border-left: 4px solid #9C27B0;
  border-radius: 8px;
  color: #6A1B9A;
  font-size: 14px;
}
h2 {
    display: flex;
    justify-content: center;
    margin-top: 16px;
}
.today {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 4px 16px;
  gap: 8px;
  width: 90px;
  height: 22px;
  color: #66E66A;
  border: 1px solid #66E66A;
  border-radius: 20px;
}

.mark {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

h2 {
  text-align: center;
  margin-top: 16px;
}
input {
  padding: 6px 8px;
  width: 150px;
  background: none;
  border: 2px solid #D9D9D9;
  border-radius: 8px;
  outline: none; 
  font-size: 14px;
  color: black;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  font-weight: 400;
}

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

.group-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.warning {
  background: #FFF8E1;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #F57F17;
  margin-bottom: 20px;
  border-left: 3px solid #FFC107;
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
  display: grid;
  grid-template-columns: repeat(3, minmax(340px, 1fr));
  gap: 16px;
  margin-top: 20px;
  justify-content: center;
  max-width: 100%;
}

.card_book {
  display: flex;
  flex-direction:column;
  padding: 16px;
  box-shadow: 0 0 8px rgba(93, 32, 237, 0.2);
  border-radius: 16px;
  gap: 8px;
}

span {
  color: #505050;
}

.group-input label {
  font-size: 18px;
  font-weight: 500;
}

p {
  color: #505050;
  font-size: 14px;
  margin-top: 4px;
}

.text {
  color: black;
}

.buttons {
  position: relative;
  display: flex;
  flex-direction: row;
  gap: 12px;
}

button {
    margin: 16px auto;
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