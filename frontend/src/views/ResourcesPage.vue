<script setup>
import { useRoute, useRouter } from 'vue-router'
import {  watch, ref, computed } from 'vue'
import { useResourcesPage } from '../components/logic_resource_page.js'
import deleteIcon from '@/components/icons/delete.svg'
import editIcon from '@/components/icons/edit.svg'

const route = useRoute()
const router = useRouter()

const {
  error,
  loading,
  admin_level,
  showModal,
  selectedResource,
  bookingIntervals,
  selectedDate,
  selectedStart,
  selectedEnd,
  errorMessage,
  minDate,
  maxDate,
  timeSlotsWithBreaks,
  canBook,
  totalBookingTime,
  truncate,
  openModal,
  closeModal,
  handleSlotClick,
  removeBookingInterval,
  handleSlotMouseEnter,
  handleGridMouseLeave,
  showBreakWarning,
  cancelSelection,
  onDateChange,
  bookResource,
  deleteResource,
  getSlotClass,
  selectedTypes,
  searchQuery,
  currentPage,
  totalPages,
  paginatedResources,
  goToPage,
  nextPage,
  prevPage,
  getVisiblePages,
  handleEditResource
} = useResourcesPage(route, router)

const userTimezone = computed(() => {
  try {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    const offset = -new Date().getTimezoneOffset() / 60
    const offsetString = offset >= 0 ? `+${offset}` : `${offset}`
    return `${timezone} (UTC${offsetString})`
  } catch (e) {
    const offset = -new Date().getTimezoneOffset() / 60
    const offsetString = offset >= 0 ? `+${offset}` : `${offset}`
    return `UTC${offsetString}`
  }
})

watch(showModal, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <div v-if="loading" class="loading">
    <div class="spinner"></div>
    <p>Загрузка ресурсов...</p>
  </div>
  
  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
    <button @click="getResources">Попробовать снова</button>
  </div>
  
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
    
    <div class="cards-block">
      <div class="cards">
        <div v-for="resource in paginatedResources" :key="resource.id" class="card">
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

      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" @click="prevPage" :disabled="currentPage === 1">←</button>
          
        <div v-for="page in getVisiblePages()" :key="page">
          <button v-if="page === '...'" class="page-dots" disabled>
            ...
          </button>
          <button v-else class="page-btn" :class="{ active: currentPage === page }" @click="goToPage(page)">
            {{ page }}
          </button>
        </div>
          
        <button class="page-btn" @click="nextPage" :disabled="currentPage === totalPages">→</button>
      </div>
    </div>
  </div>

  <div v-if="showModal" class="modal-overlay" @click="closeModal">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h2>{{ selectedResource?.name }}</h2>
        <button class="close-btn" @click="closeModal">✕</button>
      </div>
      
      <div class="modal-body">
        <p class="description">{{ selectedResource?.description || 'Нет описания' }}</p>
        
        <div class="warning">
          <span>
            Все временные интервалы указаны по <strong>Московскому времени (MSK, UTC+3)</strong>
            <br>Ваш часовой пояс: <strong>{{ userTimezone }}</strong>
          </span>
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
                'slot-disabled': !item.isBreak && getSlotClass(idx)['slot-disabled']
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
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div v-if="bookingIntervals.length > 0" class="selected-intervals">
          <div class="selected-title">Выбранные интервалы ({{ totalBookingTime }}):</div>
          <div class="intervals-list">
            <div v-for="(interval, idx) in bookingIntervals" :key="idx" class="interval-tag">
              {{ interval.start }} – {{ interval.end }}
              <button class="remove-interval" @click="removeBookingInterval(idx)">✕</button>
            </div>
          </div>
        </div>

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