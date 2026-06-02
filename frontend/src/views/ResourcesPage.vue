<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref, computed } from 'vue'
import { useResourcesPage } from '../components/logic_resource_page.js'
import deleteIcon from '@/components/icons/delete.svg'
import editIcon from '@/components/icons/edit.svg'

const route = useRoute()
const router = useRouter()

const selectedTypes = ref([])
const searchQuery = ref('')


onMounted(async () => {
  await getResources()
  
  // Если есть параметр book - открываем модалку
  const resourceId = route.query.book
  if (resourceId) {
    const resource = resources.value.find(r => r.id == resourceId)
    if (resource) {
      openModal(resource)
    }
  }
})

const {
  resources,
  error,
  loading,
  admin_level,
  showModal,
  selectedResource,
  bookingIntervals,
  selectedDate,
  selectedStart,
  selectedEnd,
  hoverEnd,
  errorMessage,
  bookedSlots,
  minDate,
  maxDate,
  timeSlotsWithBreaks,
  breaks,
  canBook,
  totalBookingTime,
  getResources,
  truncate,
  openModal,
  closeModal,
  handleSlotClick,
  removeBookingInterval,
  handleSlotMouseEnter,
  handleGridMouseLeave,
  showBreakWarning,
  resetSelection,
  cancelSelection,
  onDateChange,
  bookResource,
  deleteResource,
  editResource,
  getSlotClass,
  findSlotIndexByTime
} = useResourcesPage()

async function handleEditResource(resourceId) {
  const shouldEdit = await editResource(resourceId)
  if (shouldEdit) {
    router.push({
      path: '/create_resource',
      query: { resourceId: resourceId }
    })
  }
}


const filteredResources = computed(() => {
  let result = resources.value
  
  if (selectedTypes.value.length > 0) {
    result = result.filter(resource => selectedTypes.value.includes(resource.type))
  }
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(resource => 
      resource.name.toLowerCase().includes(query) ||
      (resource.description && resource.description.toLowerCase().includes(query))
    )
  }
  
  return result
})

</script>

<template>
  <!-- Состояние загрузки -->
  <div v-if="loading" class="loading">
    <div class="spinner"></div>
    <p>Загрузка ресурсов...</p>
  </div>
  
  <!-- Сообщение об ошибке -->
  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
    <button @click="getResources">Попробовать снова</button>
  </div>
  
  <!-- Список ресурсов -->
  <div v-else class="resources-container">
    <div class="filters-block">
      <div class="search-box">
        <input 
          type="text"
          v-model="searchQuery" 
          placeholder="Поиск ресурсов..." 
          class="search-input"
        >
      </div>

      <div class="filters">
          <label>
          <input type="checkbox" value="laptop" v-model="selectedTypes">
          Ноутбук
        </label>
        <label>
          <input type="checkbox" value="room" v-model="selectedTypes">
          Переговорная
        </label>
        <label>
          <input type="checkbox" value="projector" v-model="selectedTypes">
          Проектор
        </label>
        <label>
          <input type="checkbox" value="other" v-model="selectedTypes">
          Другое
        </label>
      </div>
    </div>
    
    <div class="cards">
      <div v-for="resource in filteredResources" :key="resource.id" class="card">
        <div class="card-header">
          <h3 class="card-title">{{ resource.name }}</h3>
        </div>
        
        <div class="card-description">
          <span class="label">Описание</span>
          <p class="description-text">{{ truncate(resource.description, 60) }}</p>
        </div>
        
        <div class="card-actions">
          <button v-if="admin_level === '1'" class="icon-btn" @click="deleteResource(resource.id)" title="Удалить">
            <img :src="deleteIcon" alt="delete">
          </button>
          <button class="book-btn" @click="openModal(resource)">
            Забронировать
          </button>
          <button v-if="admin_level === '1'" class="icon-btn" @click="handleEditResource(resource.id)" title="Редактировать">
            <img :src="editIcon" alt="edit">
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно бронирования -->
  <div v-if="showModal" class="modal-overlay" @click="closeModal">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h2>{{ selectedResource?.name }}</h2>
        <button class="close-btn" @click="closeModal">✕</button>
      </div>
      
      <div class="modal-body">
        <p class="description">{{ selectedResource?.description || 'Нет описания' }}</p>
        
        <div class="warning">
          <span>ВНИМАНИЕ! Все временные интервалы указаны по <strong>Московскому времени (MSK, UTC+3)</strong></span>
        </div>
        
        <div class="form-group">
          <label>Выберите дату</label>
          <input 
            v-model="selectedDate" 
            type="date" 
            class="date-input"
            :min="minDate"
            :max="maxDate"
            @change="onDateChange">
        </div>
        
        <!-- Сетка времени -->
        <div v-if="selectedDate && timeSlotsWithBreaks.length > 0" class="time-section">
          <div class="time-title">Выберите время:</div>
          <div class="time-grid" @mouseleave="handleGridMouseLeave">
            <div 
              v-for="(item, idx) in timeSlotsWithBreaks" 
              :key="idx"
              :class="{
                'time-slot': true,
                'break-slot': item.isBreak,
                'slot-selected': !item.isBreak && getSlotClass(idx)['slot-selected'],
                'slot-start': !item.isBreak && getSlotClass(idx)['slot-start'],
                'slot-end': !item.isBreak && getSlotClass(idx)['slot-end'],
                'slot-preview': !item.isBreak && getSlotClass(idx)['slot-preview'],
                'slot-disabled': !item.isBreak && getSlotClass(idx)['slot-disabled'],
                'slot-completely-disabled': !item.isBreak && getSlotClass(idx)['slot-completely-disabled']
              }"
              @click="item.isBreak ? showBreakWarning(item) : handleSlotClick(idx)"
              @mouseenter="!item.isBreak && handleSlotMouseEnter(idx)"
            >
              <div v-if="!item.isBreak">
                {{ item.time }}
              </div>
              <div v-else>
                Перерыв: {{ item.start }}–{{ item.end }}
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedDate && timeSlotsWithBreaks.length === 0" class="no-slots">
          В выбранный день ресурс не работает
        </div>
        
        <!-- Сообщение об ошибке -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <!-- Выбранные интервалы -->
        <div v-if="bookingIntervals.length > 0" class="selected-intervals">
          <div class="selected-title">Выбранные интервалы ({{ totalBookingTime }}):</div>
          <div class="intervals-list">
            <div v-for="(interval, idx) in bookingIntervals" :key="idx" class="interval-tag">
              {{ interval.start }} – {{ interval.end }}
              <button class="remove-interval" @click="removeBookingInterval(idx)">✕</button>
            </div>
          </div>
        </div>

        <!-- Подсказка по выделению -->
        <div class="selection-hint" v-if="selectedStart !== null && selectedEnd === null">
          Нажмите на конечную ячейку для завершения выделения
          <button class="cancel-selection" @click="cancelSelection" type="button">
            Отмена (Esc)
          </button>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="submit-btn" @click="bookResource" :disabled="!canBook">
          Забронировать ({{ bookingIntervals.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<style src="../components/style_resource_page.css" scoped></style>

<style scoped>
.filters-block {
  flex-shrink: 0;
  width: 280px;
  overflow-y: visible;
}

.search-box {
  margin-bottom: 20px;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  font-size: 16px;
  outline: none;
  transition: all 0.2s;
  background: white;
}

.search-input:focus {
  border-color: #5D20ED;
  box-shadow: 0 2px 8px rgba(93, 32, 237, 0.041);
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filters label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 8px;
  accent-color: #5D20ED;
}

.filters input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  margin: 0;
}

/* Адаптация для мобильных */
@media (max-width: 768px) {
  .filters {
    flex-direction: row;  /* На мобильных горизонтально */
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .filters label {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>