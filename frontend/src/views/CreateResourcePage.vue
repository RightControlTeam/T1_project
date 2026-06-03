<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/index'

const router = useRouter()

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

const errors = ref({
  name: '',
  type: '',
  schedules: ''
})

const schedulesByDay = ref({
  0: new Set(),
  1: new Set(),
  2: new Set(),
  3: new Set(),
  4: new Set(),
  5: new Set(),
  6: new Set()
})

const selectedStart = ref(null)
const hoverEnd = ref(null)

const showScheduleModal = ref(false)

const isEditMode = ref(false)
const editingResourceId = ref(null)

function timeToIndex(timeStr) {
  const [hours, minutes] = timeStr.split(':').map(Number)
  return (hours * 60 + minutes) / 30
}

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

function cancelSelection() {
  selectedStart.value = null
  hoverEnd.value = null
  errorMessage.value = ''
}

function handleSlotClick(slotIndex) {
  if (selectedStart.value === slotIndex) {
    errorMessage.value = `Выберите другую ячейку для завершения интервала (${indexToLabel(slotIndex)} уже выбрана как начало)`
    
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
    
    return
  }
  
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
  
  else {
    const start = Math.min(selectedStart.value, slotIndex)
    const end = Math.max(selectedStart.value, slotIndex)
    
    const overlapCheck = checkRangeOverlap(activeDay.value, start, end)
    
    if (overlapCheck.overlaps) {
      errorMessage.value = `Нельзя создать диапазон! Он пересекается с уже существующим: ${overlapCheck.startLabel} – ${overlapCheck.endLabel}`
      
      selectedStart.value = null
      hoverEnd.value = null
      
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
      
      return 
    }
    
    schedulesByDay.value[activeDay.value].add(`${start}-${end}`)
    
    selectedStart.value = null
    hoverEnd.value = null
  }
}

function handleSlotMouseEnter(slotIndex) {
  if (selectedStart.value !== null) {
    hoverEnd.value = slotIndex
  }
}

function handleGridMouseLeave() {
  if (selectedStart.value !== null) {
    hoverEnd.value = null
  }
}

function removeRange(day, range) {
  schedulesByDay.value[day].delete(range)
}

function changeActiveDay(dayValue) {
  activeDay.value = dayValue
  selectedStart.value = null
  hoverEnd.value = null
}

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    cancelSelection()
  }
}

function validate() {
  errors.value = {
    name: '',
    type: '',
    schedules: ''
  }
  
  let is_valid = true
  
  if (!form.value.name || form.value.name.trim() === '') {
    errors.value.name = 'Обязательное поле!'
    is_valid = false
  }
  
  if (!form.value.type) {
    errors.value.type = 'Обязательное поле!'
    is_valid = false
  }
  
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

  isEditMode.value = false
  editingResourceId.value = null
  sessionStorage.removeItem('editingResourceId')
}

async function loadResourceForEdit(resourceId) {
  try {
    const resourceResponse = await api.get(`/resource/${resourceId}`)
    const resource = resourceResponse.data
    
    form.value = {
      name: resource.name,
      type: resource.type,
      description: resource.description || '',
      is_active: resource.is_active !== undefined ? resource.is_active : true
    }
    
    const schedules = resource.schedules
    
    for (let day = 0; day <= 6; day++) {
      schedulesByDay.value[day].clear()
    }
    
    schedules.forEach(schedule => {
      const startIndex = timeToIndex(schedule.start_time.slice(0, 5))
      const endIndex = timeToIndex(schedule.end_time.slice(0, 5))
      schedulesByDay.value[schedule.day_of_week].add(`${startIndex}-${endIndex}`)
    })
    
  } catch (e) {
    console.error('Ошибка загрузки ресурса для редактирования:', e)
    alert('Не удалось загрузить данные ресурса')
    router.push('/')
  }
}

async function submit() {
  if (validate()) {
    if (isEditMode.value) {
      const confirmed = confirm('Вы уверены, что хотите изменить ресурс? Старый ресурс будет удален, а все его бронирования отменены. Новый ресурс будет создан с новым ID.')
      
      if (!confirmed) return
      
      try {
        const resourceResponse = await api.post('/resource', form.value)
        console.log("Новый ресурс создан, ID:", resourceResponse.data.id)
        
        const schedules = convertSchedulesToApiFormat()
        for (const time of schedules) {
          await api.post(`/resource/${resourceResponse.data.id}/schedule`, time)
        }

        await api.delete(`/resource/${editingResourceId.value}`)
        console.log("Старый ресурс удален")
        
        clean_form()
        alert('Ресурс успешно изменен!')
        
        router.push('/')
        
      } catch (e) {
        console.log(e)
        alert('Ошибка при изменении ресурса: ' + (e.response?.data?.detail || e.message))
      }
    } else {
      try {
        const resourceResponse = await api.post('/resource', form.value)
        console.log("Ресурс создан")
        
        const schedules = convertSchedulesToApiFormat()
        for (const time of schedules) {
          await api.post(`/resource/${resourceResponse.data.id}/schedule`, time)
        }
        
        clean_form()
        alert('Ресурс успешно создан!')
        
      } catch (e) {
        const error = e.response
        console.log('response: ', error)
        
        if (!error) {
          alert('Сервер не отвечает')
        } else if (error.status === 401) {
          alert('Войдите заново...')
        } else {
          alert('Ошибка при создании ресурса: ' + (error.msg || e.message))
        }
      }
    }
  }
}

function cancelEdit() {
  if (isEditMode.value) {
    const confirmed = confirm('Отменить редактирование? Все изменения будут потеряны.')
    if (confirmed) {
      clean_form()
      router.push('/')
    }
  }
}

function viewAllSchedule() {
  showScheduleModal.value = true
}

function closeScheduleModal() {
  showScheduleModal.value = false
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)

  const editingId = sessionStorage.getItem('editingResourceId')
  if (editingId) {
    isEditMode.value = true
    editingResourceId.value = parseInt(editingId)
    loadResourceForEdit(editingResourceId.value)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

</script>

<template>
  <div class="content-container">
     <h1>{{ isEditMode ? 'Редактирование ресурса' : 'Создание ресурса' }}</h1>
     <div v-if="isEditMode" class="edit-warning">
      Вы редактируете ресурс. После сохранения старый ресурс будет удален и создан новый с новым ID. Все старые бронирования будут отменены.
    </div>
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
      
       <div class="form-buttons">
        <button class="create" type="submit">
          {{ isEditMode ? 'Изменить ресурс' : 'Создать' }}
        </button>
        <button v-if="isEditMode" type="button" class="cancel-edit-btn" @click="cancelEdit">
          Отменить
        </button>
      </div>
    </form>
  </div>

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
.edit-warning {
  background: #FFF8E1;
  border-left: 3px solid #FFC107;
  border-right: 3px solid #FFC107;
  padding: 12px 16px;
  border-radius: 8px;
  color: #F57F17;
  font-size: 14px;
  width: 100%;
  max-width: 900px;
}

.form-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 900px;
}

.cancel-edit-btn {
  flex: 1;
  padding: 12px 0;
  background: #F5F5F5;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  font-size: 16px;
  color: #505050;
  cursor: pointer;
  font-family: inherit;
}

.cancel-edit-btn:hover {
  background: #FFEBEE;
  border-color: #D32F2F;
  color: #D32F2F;
}

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