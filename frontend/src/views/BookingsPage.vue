<script setup>
import api from '@/api/index'
import { useRouter } from 'vue-router'
import { ref, onMounted, computed, onUnmounted } from 'vue'
import timeIcon from '@/components/icons/time.svg'
import calendar2Icon from '@/components/icons/calendar2.svg'

const bookings = ref([])
const currentUserId = ref(null)
const is_loading = ref(true)
const today = ref('')
const router = useRouter() 
let interval = null

const update = () => {
  const now = new Date()
  const day = String(now.getDate()).padStart(2, '0')
  today.value = day
}

const is_today = (booking_day) => {
  return booking_day === today.value
}

async function editBooking(booking) {
  const confirmed = confirm('Изменить бронирование? Старое будет удалено.')
  if (!confirmed) return
  try {
    await api.delete(`/booking/${booking.id}`)
    router.push({
      path: '/',
      query: { book: booking.resource_id,  openModal: 'true' }
    })
  } catch (e) {
    console.error(e)
  }
}



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
    const sortedBookings = response.data.sort((a, b) => 
      new Date(a.start_time) - new Date(b.start_time)
    );
    bookings.value = sortedBookings
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
    .filter(booking => !booking.is_cancelled && !booking.is_ended)
    .map(booking => ({
      ...booking,
      resource: booking.resource
    }))
})


onMounted(async () => {
  await get_bookings()
  is_loading.value = false
  console.log(bookings.value)
  update()
  interval = setInterval(update, 60000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

</script>

<template>
  <h2>Мои брони</h2>
  <div class="booking-page">
    <div v-if="is_loading">
      Загрузка...
    </div>
    <div v-else class="cards">
      <div v-for="(booking, index) in activeBookings " :key="index">
        <div class="card_book">
          <h3>{{ booking.resource?.name }}</h3>
          <div>
            <span class="description">Описание:</span>
            <p>{{ booking.resource?.description }}</p>
          </div>
          <div class="line"></div>
          <div class="mark">
            <div class="book-box">
              <div class="circle"></div>
              <span class="book">Забронировано</span>
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
          <div class="buttons">
            <button @click="delete_booking(booking.id)" class="cancelled">Отменить</button>
            <button @click="editBooking(booking)">Изменить</button>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
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
  width: 100px;
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

.modal {
  width: 60%;
  display: flex;
  background: white;
  display: flex;
  flex-direction:column;
  padding: 16px;
  border-radius: 16px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.booking-page {
  position: relative;
  margin: 0 auto;
  padding-bottom: 100px;
  width: 100%;
}

@media (max-width: 1255px) {
  .cards {
    grid-template-columns: repeat(2, minmax(340px, 1fr));
  }
}

@media (max-width: 890px) {
  .cards {
    grid-template-columns: repeat(1, minmax(340px, 1fr));
  }
}

.error-state {
  text-align: center;
  padding: 40px;
}

.error-state button {
  margin-top: 16px;
  padding: 8px 16px;
  background: #5D20ED;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #1A1A1A;
}

.date-input {
  padding: 10px 12px;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.date-input:focus {
  outline: none;
  border-color: #5D20ED;
}

/* Сетка времени */
.time-section {
  margin: 20px 0;
}

.time-title {
  margin-bottom: 12px;
  font-weight: 500;
  color: #1A1A1A;
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  background: #F8F8F8;
  padding: 16px;
  border-radius: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.time-grid::-webkit-scrollbar {
  width: 6px;
}

.time-slot {
  padding: 8px 6px;
  text-align: center;
  font-size: 13px;
  background: white;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #505050;
}

.time-slot:hover:not(.slot-disabled):not(.break-slot) {
  background: #F0E6FF;
  border-color: #5D20ED;
}

.time-slot.slot-selected {
  background: #5D20ED;
  color: white;
  border-color: #5D20ED;
}

.time-slot.slot-selected:hover {
  background: #4A1ACC;
}

.time-slot.slot-start {
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
}

.time-slot.slot-end {
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
}

.time-slot.slot-preview {
  background: #D4BFFF;
  border-color: #5D20ED;
  color: #505050;
}

.time-slot.break-slot {
  background: #FFE5E5;
  border-color: #FF6B6B;
  color: #D32F2F;
  cursor: not-allowed;
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  grid-column: span 2; 
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-slot.break-slot:hover {
  background: #FFD6D6;
  border-color: #D32F2F;
  transform: none;
}

.time-slot.slot-disabled {
  background: #F5F5F5;
  border-color: #E0E0E0;
  color: #CCC;
  cursor: not-allowed;
}

/* Специальный стили для полностью заблокированных слотов  */
.time-slot.slot-completely-disabled {
  text-decoration: line-through;
  color: #AAA;
}

.time-slot.slot-disabled:hover {
  background: #F5F5F5;
  border-color: #E0E0E0;
  transform: none;
}

/* Сообщения */
.no-slots {
  text-align: center;
  padding: 20px;
  background: #F5F5F5;
  border-radius: 8px;
  color: #999;
  margin: 20px 0;
}

.error-message {
  background: #FFEBEE;
  color: #C62828;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 16px 0;
  font-size: 13px;
}

/* Выбранные интервалы */
.selected-intervals {
  background: #E8F5E9;
  padding: 16px;
  border-radius: 12px;
  margin: 20px 0;
}

.selected-title {
  font-weight: 500;
  margin-bottom: 12px;
  color: #2E7D32;
}

.intervals-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.interval-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #2E7D32;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.remove-interval {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  margin: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.remove-interval:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Подсказка по выделению */
.selection-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: #5D20ED;
  font-style: italic;
  margin-top: 12px;
  padding: 8px 12px;
  background: #F0E6FF;
  border-radius: 8px;
}

.cancel-selection {
  padding: 4px 10px;
  background: none;
  border: 1px solid #5D20ED;
  border-radius: 6px;
  font-size: 12px;
  color: #5D20ED;
  cursor: pointer;
  transition: all 0.15s ease;
  font-style: normal;
}

.cancel-selection:hover {
  background: #5D20ED;
  color: white;
}

/* Футер модального окна */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 2px solid #F0F0F0;
  flex-shrink: 0;
}

.cancel-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  border-color: #D32F2F;
  color: #D32F2F;
}

.submit-btn {
  padding: 10px 24px;
  background: #5D20ED;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #4A1ACC;
}

.submit-btn:disabled {
  background: #CCC;
  cursor: not-allowed;
}

/* Адаптация */
@media (max-width: 768px) {
  .card {
    width: calc(50% - 16px);
    min-width: 200px;
  }
  
  .modal {
    width: 95%;
  }
  
  .time-grid {
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  }
}

@media (max-width: 480px) {
  .card {
    width: 100%;
  }
}
</style>
