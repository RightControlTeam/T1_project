<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/api/index'

const SLOTS_PER_HOUR = 2
const MAX_HOUR_PER_DAY = 24 
const TOTAL_SLOTS = MAX_HOUR_PER_DAY * SLOTS_PER_HOUR

const daysOfWeek = [
  { value: 0, name: 'Пн' },
  { value: 1, name: 'Вт' },
  { value: 2, name: 'Ср' },
  { value: 3, name: 'Чт' },
  { value: 4, name: 'Пт' },
  { value: 5, name: 'Сб' },
  { value: 6, name: 'Вс' }
]

const activeDay = ref(0)
const errorMessage = ref('')
const form = ref({
    name: '',
    type: '',
    description: '',
    is_active: true 
})

const schedulesByDay = ref({
  0: new Set(), 1: new Set(), 2: new Set(), 3: new Set(), 4: new Set(), 5: new Set(), 6: new Set()
})

// Состояния для выделения
const selectedStart = ref(null)
const hoverEnd = ref(null)

function indexToLabel(index) {
  if (index === 48) return '23:59'
  const time = new Date()
  time.setHours(0, 0, 0, 0)
  time.setMinutes(index * 30)
  return time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function indexToApi(index) {
  if (index === 48) return '23:59:00'
  const time = new Date()
  time.setHours(0, 0, 0, 0)
  time.setMinutes(index * 30)
  return time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit'})
}

// Функция конвертации schedulesByDay в формат для API
function convertSchedulesToApiFormat() {
  const schedules = []
  
  for (let day = 0; day <= 6; day++) {
    const ranges = schedulesByDay.value[day]
    
    for (const range of ranges) {
      const [startIndex, endIndex] = range.split('-').map(Number)
      
      schedules.push({
        day_of_week: day,
        start_time: indexToApi(startIndex),
        end_time: indexToApi(endIndex)
      })
    }
  }
  
  return schedules
}

const timeSlots = computed(() => {
  const slots = []
  for (let i = 0; i <= TOTAL_SLOTS; i++) {
    slots.push({
      index: i,
      label: indexToLabel(i)
    })
  }
  return slots
})

// Проверка, входит ли слот в сохранённый диапазон
function isSlotInSavedRange(day, slotIndex) {
  const ranges = schedulesByDay.value[day]
  for (const range of ranges) {
    const [start, end] = range.split('-').map(Number)
    if (slotIndex >= start && slotIndex <= end) {
      return { inRange: true, isStart: slotIndex === start, isEnd: slotIndex === end }
    }
  }
  return { inRange: false, isStart: false, isEnd: false }
}

// Проверка на пересечение с существующими диапазонами
function checkRangeOverlap(day, newStart, newEnd) {
  const ranges = schedulesByDay.value[day]
  
  for (const range of ranges) {
    const [existingStart, existingEnd] = range.split('-').map(Number)

    if (newStart <= existingEnd && newEnd >= existingStart) {
      return {
        overlaps: true,
        overlappingRange: range,
        startLabel: indexToLabel(existingStart),
        endLabel: indexToLabel(existingEnd)
      }
    }
  }
  
  return { overlaps: false }
}

// Проверка, входит ли слот в превью диапазон
function isSlotInPreviewRange(slotIndex) {
  if (selectedStart.value === null || hoverEnd.value === null) return false
  const start = Math.min(selectedStart.value, hoverEnd.value)
  const end = Math.max(selectedStart.value, hoverEnd.value)
  return slotIndex >= start && slotIndex <= end
}

function getSlotClass(slotIndex) {
  const saved = isSlotInSavedRange(activeDay.value, slotIndex)
  const inPreview = isSlotInPreviewRange(slotIndex)
  
  return {
    'slot-selected': saved.inRange,
    'slot-start': saved.isStart,
    'slot-end': saved.isEnd,
    'slot-preview': inPreview && !saved.inRange
  }
}

// Обработчик клика по ячейке
function handleSlotClick(slotIndex) {
  if (selectedStart.value === null) {
    selectedStart.value = slotIndex
    hoverEnd.value = slotIndex
    errorMessage.value = ''
  } else {
    const start = Math.min(selectedStart.value, slotIndex)
    const end = Math.max(selectedStart.value, slotIndex)
    
    const overlapCheck = checkRangeOverlap(activeDay.value, start, end)
    
    if (overlapCheck.overlaps) {
      errorMessage.value = `Нельзя создать диапазон! Он пересекается с уже существующим: ${overlapCheck.startLabel} – ${overlapCheck.endLabel}`
      
      selectedStart.value = null
      hoverEnd.value = null
      
      // Автоматически скрываем ошибку через 3 секунды
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
      
      return 
    }
    
    schedulesByDay.value[activeDay.value].add(`${start}-${end}`)
    
    selectedStart.value = null
    hoverEnd.value = null
    errorMessage.value = ''
  }
}


// Обработчик наведения
function handleSlotMouseEnter(slotIndex) {
  if (selectedStart.value !== null) {
    hoverEnd.value = slotIndex
  }
}

// Обработчик ухода мыши с сетки
function handleGridMouseLeave() {
  if (selectedStart.value !== null) {
    hoverEnd.value = null
  }
}

// Удаление диапазона по клику с Ctrl
function removeRange(day, range) {
  schedulesByDay.value[day].delete(range)
}

// Смена активного дня со сбросом выделения
function changeActiveDay(dayValue) {
  activeDay.value = dayValue
  selectedStart.value = null
  hoverEnd.value = null
}

// Получение списка сохранённых диапазонов для отображения
const savedRangesForActiveDay = computed(() => {
  const ranges = Array.from(schedulesByDay.value[activeDay.value])
  return ranges.map(range => {
    const [start, end] = range.split('-').map(Number)
    return {
      range,
      startLabel: indexToLabel(start),
      endLabel: indexToLabel(end)
    }
  }).sort((a, b) => {
    const [startA] = a.range.split('-').map(Number)
    const [startB] = b.range.split('-').map(Number)
    return startA - startB
  })
})

// Добавим функцию для отмены выделения (по Escape)
function cancelSelection() {
  selectedStart.value = null
  hoverEnd.value = null
  errorMessage.value = ''
}

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    cancelSelection()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

async function submit() {
  try {
    console.log(schedulesByDay.value)
    const resourceResponse = await api.post('/resource', form.value)
    console.log("Отправлено")

    const shedules = convertSchedulesToApiFormat()
    for (const time of shedules) {
      await api.post(`/resource/${resourceResponse.data.id}/schedule`, time)
    }
    console.log("Расписание добавлено")

    const request = await api.get('/resource')
    console.log(request.data)
  } catch (e) {
    console.log(e)
  }
}
</script>

<template>
  <div class="content-container">
    <h1>Создание ресурса</h1>
    <form @submit.prevent="submit">
      <div class="group-input">
        <label for="name">Название</label>
        <input id="name" v-model="form.name" placeholder="Введите название">
      </div>
      <div class="choose">
        <label>Выберите категорию</label>
        <select v-model="form.type">
          <option value="" disabled>Не выбрано</option>
          <option value="laptop">Ноутбук</option>
          <option value="room">Переговорная</option>
          <option value="projector">Проектор</option>
          <option value="other">Другое</option>
        </select>
      </div>
      <div class="group-input">
        <label for="description">Описание</label>
        <textarea id="description" v-model="form.description" placeholder="Опишите ресурс коротко"></textarea>
      </div>
      
      <div class="schedule">
        <div>Для каждого нужного вам дня выберите рабочие часы ресурса:</div>
        
        <div class="days">
          <div 
            v-for="day in daysOfWeek"
            :key="day.value"
            role="tab"
            :aria-selected="activeDay === day.value"
            class="day-tab"
            :class="{ active: activeDay === day.value }"
            @click="changeActiveDay(day.value)"
          >
            {{ day.name }}
          </div>
        </div>
        
        <!-- Сообщение об ошибке пересечения -->
        <div v-if="errorMessage" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ errorMessage }}
        </div>
        
        <div v-if="savedRangesForActiveDay.length > 0" class="saved-ranges">
          <div class="saved-ranges-label">Выбранные интервалы:</div>
          <div class="ranges-list">
            <span 
              v-for="item in savedRangesForActiveDay" 
              :key="item.range"
              class="range-tag"
              @click="removeRange(activeDay, item.range)"
              title="Нажмите для удаления"
            >
              {{ item.startLabel }} – {{ item.endLabel }}
              <span class="remove-icon">×</span>
            </span>
          </div>
        </div>
        
        <div 
          class="time-grid" 
          @mouseleave="handleGridMouseLeave"
        >
          <div 
            v-for="slot in timeSlots"
            :key="slot.index"
            class="time-slot"
            :class="getSlotClass(slot.index)"
            @click="handleSlotClick(slot.index)"
            @mouseenter="handleSlotMouseEnter(slot.index)"
          >
            {{ slot.label }}
          </div>
        </div>
        
        <div class="selection-info">
          <div class="selection-hint" v-if="selectedStart !== null">
            Нажмите на конечную ячейку для завершения выделения
            <button class="cancel-selection" @click="cancelSelection" type="button">
              Отмена (Esc)
            </button>
          </div>
        </div>
      </div>
      
      <button class="create" type="submit">Создать</button>
    </form>
  </div>
</template>

<style scoped>
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #FFE5E5;
  border: 1px solid #FF6B6B;
  border-radius: 8px;
  color: #D32F2F;
  font-size: 14px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 16px;
}

.selection-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.selection-hint {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #5D20ED;
  font-style: italic;
}

.cancel-selection {
  padding: 4px 10px;
  background: none;
  border: 1px solid #D9D9D9;
  border-radius: 6px;
  font-size: 12px;
  color: #505050;
  cursor: pointer;
  transition: all 0.15s ease;
  font-style: normal;
}

.cancel-selection:hover {
  background: #F5F5F5;
  border-color: #5D20ED;
  color: #5D20ED;
}

.schedule {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  width: 100%;
}

.day-tab {
  padding: 8px 8px;
  text-align: center;
  cursor: pointer;
  border: 2px solid #D9D9D9;
  border-radius: 8px;
  background: none;
  font-weight: 400;
  transition: all 0.2s ease;
  user-select: none;
}

.day-tab:hover {
  border-color: #5D20ED;
}

.day-tab.active {
  background: #5D20ED;
  color: white;
  border-color: #5D20ED;
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(85px, 1fr));
  width: 100%;
  gap: 4px;
  background: #F5F5F5;
  padding: 12px;
  border-radius: 12px;
  margin-top: 8px;
}

.time-slot {
  padding: 10px 8px;
  text-align: center;
  font-size: 400;
  background: white;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  color: #505050;
}

.time-slot:hover {
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

/* Начало диапазона */
.time-slot.slot-start {
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
  position: relative;
}

/* Конец диапазона */
.time-slot.slot-end {
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
  position: relative;
}

.time-slot.slot-preview {
  background: #D4BFFF;
  border-color: #5D20ED;
  color: #505050;
}

.time-slot.slot-preview:hover {
  background: #C4A8FF;
}

/* Сохранённые диапазоны */
.saved-ranges {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 0;
}

.saved-ranges-label {
  font-size: 13px;
  color: #505050;
}

.ranges-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.range-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #5D20ED;
  color: white;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.range-tag:hover {
  background: #4A1ACC;
}

.remove-icon {
  font-size: 12px;
  line-height: 1;
  opacity: 0.8;
}

.range-tag:hover .remove-icon {
  opacity: 1;
}

.selection-hint {
  font-size: 13px;
  color: #5D20ED;
  font-style: italic;
}

.content-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
  box-sizing: border-box;
}

h1 {
  color: black;
}

form {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.group-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

select,
textarea,
input {
  padding: 12px 16px;
  background: none;
  border: 2px solid #D9D9D9;
  border-radius: 8px;
  outline: none; 
  font-size: 16px;
  color: black;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  font-weight: 400;
}

textarea:hover,
input:hover {
  border: 2px solid #5D20ED;
}

select:focus,
textarea:focus,
input:focus {
  border: 2px solid #5D20ED;
}

textarea::placeholder,
input::placeholder {
  font-size: 16px;
  color: #505050;
  font-weight: 400;
}

label {
  font-size: 16px;
  font-weight: 400;
}

input {
  flex: 1;
}

textarea {
  resize: vertical; 
  min-height: 80px; 
  max-height: 240px; 
}

.choose {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

select {
  width: 200px;
  flex: 1;
}

select option {
  padding: 12px;
  background: white;
  color: black;
}

select:invalid,
select option[value=""] {
  color: #505050;
}

select:valid {
  color: black;
}

.create {
  flex: 1;
  padding: 12px 0;
  background: #5D20ED;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  color: white;
  font-weight: 400;
  cursor: pointer;
}

.create:hover {
  background: #4A1ACC;
}
</style>