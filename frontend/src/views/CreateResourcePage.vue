<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/api/index'


const SLOTS_PER_HOUR = 2           // 2 слота в час (каждые 30 минут)
const MAX_HOUR_PER_DAY = 24        // 24 часа в сутках
const TOTAL_SLOTS = MAX_HOUR_PER_DAY * SLOTS_PER_HOUR  // 48 слотов

// Дни недели: 0-ПН, 1-ВТ, 2-СР, 3-ЧТ, 4-ПТ, 5-СБ, 6-ВС
const daysOfWeek = [
  { value: 0, name: 'Пн' },
  { value: 1, name: 'Вт' },
  { value: 2, name: 'Ср' },
  { value: 3, name: 'Чт' },
  { value: 4, name: 'Пт' },
  { value: 5, name: 'Сб' },
  { value: 6, name: 'Вс' }
]


// UI состояние
const activeDay = ref(0)           // Какой день сейчас выбран (0-6)
const errorMessage = ref('')       // Текст ошибки для показа пользователю

// Состояние формы
const form = ref({
  name: '',                        // Название ресурса
  type: '',                        // Тип ресурса (laptop/room/projector/other)
  description: '',                 // Описание ресурса
  is_active: true                  // Активен ли ресурс
})

// Ошибки валидации формы
const errors = ref({
  name: '',                        // Ошибка поля "Название"
  type: '',                        // Ошибка поля "Тип"
  schedules: ''                    // Ошибка поля "Расписание"
})

// Хранилище расписания для всех дней
// Ключ: день недели (0-6)
// Значение: Set из строк-диапазонов вида "начало-конец". Начало и конец индексы ячеек.
const schedulesByDay = ref({
  0: new Set(),  // Понедельник
  1: new Set(),  // Вторник
  2: new Set(),  // Среда
  3: new Set(),  // Четверг
  4: new Set(),  // Пятница
  5: new Set(),  // Суббота
  6: new Set()   // Воскресенье
})

// Состояния для выделения интервалов мышкой
const selectedStart = ref(null)    // Начальный слот выделения (индекс)
const hoverEnd = ref(null)         // Конечный слот при наведении (индекс)

//Для показа всего расписания, доп окно
const showScheduleModal = ref(false)


// Функция: индекс слота → человеческое время (для отображения)
// Пример: 5 → "02:30"
function indexToLabel(index) {
  if (index === 48) return '23:59'
  const time = new Date()
  time.setHours(0, 0, 0, 0)
  time.setMinutes(index * 30)
  return time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

// Функция: индекс слота → время для API (с секундами)
// Пример: 5 → "02:30:00"
function indexToApi(index) {
  if (index === 48) return '23:59:00'
  const time = new Date()
  time.setHours(0, 0, 0, 0)
  time.setMinutes(index * 30)
  return time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit'})
}


// Создает массив всех временных слотов (0-48)
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

// Получает список сохраненных интервалов для активного дня
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

// Получить все интервалы в удобном формате для отображения
const allSchedulesFormatted = computed(() => {
  const result = []
  const daysNames = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
  
  for (let day = 0; day <= 6; day++) {
    const ranges = Array.from(schedulesByDay.value[day])
    
    if (ranges.length === 0) {
      result.push({
        day: day,
        dayName: daysNames[day],
        intervals: ['Нет интервалов']
      })
    } else {
      const intervals = ranges.map(range => {
        const [start, end] = range.split('-').map(Number)
        return `${indexToLabel(start)} – ${indexToLabel(end)}`
      }).sort()
      
      result.push({
        day: day,
        dayName: daysNames[day],
        intervals: intervals
      })
    }
  }
  
  return result
})


// Конвертирует внутреннее хранилище в формат для отправки на сервер
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

// Проверяет, входит ли слот в какой-либо сохраненный диапазон
// Возвращает: { inRange: true/false, isStart: true/false, isEnd: true/false }
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

// Проверяет, пересекается ли новый интервал с существующими
// Возвращает: { overlaps: true/false, overlappingRange, startLabel, endLabel }
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


// Проверяет, входит ли слот в превью-выделение (при наведении мыши)
function isSlotInPreviewRange(slotIndex) {
  if (selectedStart.value === null || hoverEnd.value === null) return false
  const start = Math.min(selectedStart.value, hoverEnd.value)
  const end = Math.max(selectedStart.value, hoverEnd.value)
  return slotIndex >= start && slotIndex <= end
}

// Определяет CSS классы для слота (цвет и стиль)
function getSlotClass(slotIndex) {
  const saved = isSlotInSavedRange(activeDay.value, slotIndex)
  const inPreview = isSlotInPreviewRange(slotIndex)
  
  return {
    'slot-selected': saved.inRange,              // Уже сохраненный интервал
    'slot-start': saved.isStart,                 // Начало сохраненного интервала
    'slot-end': saved.isEnd,                     // Конец сохраненного интервала
    'slot-preview': inPreview && !saved.inRange  // Временное выделение
  }
}


// Отмена текущего выделения
function cancelSelection() {
  selectedStart.value = null
  hoverEnd.value = null
  errorMessage.value = ''
}

// Обработчик клика по слоту (главная логика выделения)
function handleSlotClick(slotIndex) {
  // Случай 1: Кликнули на тот же слот, который уже выбран как начало
  if (selectedStart.value === slotIndex) {
    errorMessage.value = `Выберите другую ячейку для завершения интервала (${indexToLabel(slotIndex)} уже выбрана как начало)`
    
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
    
    return
  }
  
  // Случай 2: Начало еще не выбрано
  if (selectedStart.value === null) {
    if (isSlotInSavedRange(activeDay.value, slotIndex).inRange) {
      errorMessage.value = `Выберите другую ячейку для создания интервала (${indexToLabel(slotIndex)} уже выбрана в другом интервале)`
      
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
      
      return
    }
    selectedStart.value = slotIndex
    hoverEnd.value = slotIndex
  } 
  
  // Случай 3: Начало выбрано, завершаем выделение
  else {
    const start = Math.min(selectedStart.value, slotIndex)
    const end = Math.max(selectedStart.value, slotIndex)
    
    const overlapCheck = checkRangeOverlap(activeDay.value, start, end)
    
    // Если есть пересечение с существующими интервалами
    if (overlapCheck.overlaps) {
      errorMessage.value = `Нельзя создать диапазон! Он пересекается с уже существующим: ${overlapCheck.startLabel} – ${overlapCheck.endLabel}`
      
      selectedStart.value = null
      hoverEnd.value = null
      
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
      
      return 
    }
    
    // Нет пересечений - сохраняем интервал
    schedulesByDay.value[activeDay.value].add(`${start}-${end}`)
    
    selectedStart.value = null
    hoverEnd.value = null
  }
}

// Обработчик наведения мыши на слот
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

// Удаление диапазона по клику на тег
function removeRange(day, range) {
  schedulesByDay.value[day].delete(range)
}

// Смена активного дня
function changeActiveDay(dayValue) {
  activeDay.value = dayValue
  selectedStart.value = null
  hoverEnd.value = null
}


// Обработчик клавиатуры esc
function handleKeyDown(event) {
  if (event.key === 'Escape') {
    cancelSelection()
  }
}


// Проверка всех полей формы перед отправкой
function validate() {
  errors.value = {
    name: '',
    type: '',
    schedules: ''
  }
  
  let is_valid = true
  
  // Проверка названия
  if (!form.value.name || form.value.name.trim() === '') {
    errors.value.name = 'Обязательное поле!'
    is_valid = false
  }
  
  // Проверка типа
  if (!form.value.type) {
    errors.value.type = 'Обязательное поле!'
    is_valid = false
  }
  
  // Проверка расписания (должен быть хотя бы один интервал)
  const schedules = convertSchedulesToApiFormat()
  if (schedules.length === 0) {
    errors.value.schedules = 'Выберите хотя бы один временной интервал!'
    is_valid = false
  }
  
  return is_valid
}

function clean_form() {
  form.value = { name: '', type: '', description: '', is_active: true }
  errors.value = { name: '', type: '', schedules: '' }
    
  for (let day = 0; day <= 6; day++) {
    schedulesByDay.value[day].clear()
  }
  
  selectedStart.value = null
  hoverEnd.value = null
  errorMessage.value = ''
  activeDay.value = 0

  return 
}

// Отправка формы на сервер
async function submit() {
  if (validate()) {
    try {
      // Создаем ресурс
      const resourceResponse = await api.post('/resource', form.value)
      console.log("Ресурс создан")
      
      // Добавляем расписание для ресурса
      const schedules = convertSchedulesToApiFormat()
      for (const time of schedules) {
        await api.post(`/resource/${resourceResponse.data.id}/schedule`, time)
      }
      console.log("Расписание добавлено")
      
      // Получаем обновленный список (для проверки) потом удалить
      const request = await api.get('/resource')
      console.log(request.data)

      // Отчищаем все
      clean_form()

      alert('Ресурс успешно создан!')
      
    } catch (e) {
      console.log(e)
      alert('Ошибка при создании ресурса: ' + e.message)
    }
  }
}


// Функция для показа окна со всем расписанием
function viewAllSchedule() {
  showScheduleModal.value = true
}

// Функция для закрытия окна
function closeScheduleModal() {
  showScheduleModal.value = false
}

// При монтировании компонента - вешаем обработчик клавиатуры
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

// При размонтировании - убираем обработчик
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

</script>

<template>
  <div class="content-container">
    <h1>Создание ресурса</h1>
    <form @submit.prevent="submit">
      <div class="group-input">
        <label for="name">Название 
          <span class="required">* 
            <span v-if="errors.name" class="error valid">{{ errors.name }}</span>
          </span>
        </label>
        <input id="name" v-model="form.name" placeholder="Введите название">
        
      </div>
      <div class="choose">
        <label>Выберите категорию 
          <span class="required">* 
            <span v-if="errors.type" class="error valid">{{ errors.type }}</span>
          </span>
        </label>
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
        <div>Для каждого нужного вам дня выберите рабочие часы ресурса: 
          <span class="required">* 
            <span v-if="errors.schedules" class="error valid">{{ errors.schedules }}</span>
          </span>
        </div>
        
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
        
        <div class="saved-ranges">
          <div class="saved-ranges-label">Выбранные интервалы:</div>
          <div class="ranges-list">
            <span class="range-tag"
                  @click="viewAllSchedule"
                  title="Нажмите для просмотра всего расписания">
                  Все расписание
            </span>
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

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
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

  <!-- Доп окно всего расписания -->
  <div v-if="showScheduleModal" class="modal-overlay" @click="closeScheduleModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Расписание</h2>
        <button class="modal-close" @click="closeScheduleModal">✕</button>
      </div>
      
      <div class="modal-body">
        <div v-for="day in allSchedulesFormatted" :key="day.day" class="schedule-day">
          <div class="day-title">{{ day.dayName }}</div>
          <div class="day-intervals">
            <span 
              v-for="(interval, idx) in day.intervals" 
              :key="idx"
              class="interval-badge"
              :class="{ 'empty-interval': interval === 'Нет интервалов' }"
            >
              {{ interval }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.required {
  color: #D32F2F;
  margin-left: 4px;
}

.error.valid {
  color: #D32F2F;
  font-size: 13px;
  margin-top: 4px;
  margin-bottom: 0;
}

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

.time-slot.slot-start {
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
  position: relative;
}

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

/*Окно со всем расписанием*/
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid #F0F0F0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1A1A1A;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.schedule-day {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #EEEEEE;
}

.schedule-day:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.day-title {
  font-weight: 600;
  font-size: 16px;
  color: #5D20ED;
  margin-bottom: 10px;
  display: inline-block;
  background: #F0E6FF;
  padding: 4px 12px;
  border-radius: 20px;
}

.day-intervals {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.interval-badge {
  background: #5D20ED;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.empty-interval {
  background: #F5F5F5;
  color: #999;
  font-style: italic;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 2px solid #F0F0F0;
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  background: #5D20ED;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #4A1ACC;
}

/* Адаптация для мобильных для доп окошка*/
@media (max-width: 600px) {
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-header h2 {
    font-size: 18px;
  }
  
  .day-title {
    font-size: 14px;
  }
  
  .interval-badge {
    font-size: 12px;
    padding: 4px 10px;
  }
}
</style>