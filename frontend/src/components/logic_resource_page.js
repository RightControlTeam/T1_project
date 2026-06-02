import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import api from '@/api/index'

export function useResourcesPage(route, router) {
  const MSK_OFFSET_HOURS = 3
  const SLOT_INTERVAL_MINUTES = 30
  const slotsCache = new Map()
  
  const resources = ref([])
  const error = ref('')
  const loading = ref(true)
  const admin_level = ref(localStorage.getItem('admin_level'))

  const showModal = ref(false)
  const selectedResource = ref(null)
  const bookingIntervals = ref([])

  const selectedDate = ref('')
  const selectedStart = ref(null)
  const selectedEnd = ref(null)
  const hoverEnd = ref(null)
  const errorMessage = ref('')
  const bookedSlots = ref([])

  const selectedTypes = ref([])
  const searchQuery = ref('')
  const currentPage = ref(1)
  const itemsPerPage = ref(12)

  async function getResources() {
    try {
      error.value = ''
      loading.value = true
      
      const request = await api.get('/resource')
      resources.value = request.data.items || request.data
      
    } catch (e) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки ресурсов'
    } finally {
      loading.value = false
    }
  }

  function truncate(str, maxLength) {
    if (!str) return 'Нет описания'
    if (str.length <= maxLength) return str
    return str.slice(0, maxLength) + '...'
  }

  function getDayOfWeek(date) {
    const dateObj = new Date(date)
    const dayOfWeek = dateObj.getDay()
    return dayOfWeek === 0 ? 6 : dayOfWeek - 1
  }

  function cleanTimeString(timeStr) {
    if (!timeStr) return ''
    return timeStr.split('.')[0]
  }

  function formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  function findIntervals(date) {
    const dayIndex = getDayOfWeek(date)
    return selectedResource.value?.schedules.filter(
      schedule => schedule.day_of_week === dayIndex
    ).map(schedule => ({
      ...schedule,
      start_time: cleanTimeString(schedule.start_time),
      end_time: cleanTimeString(schedule.end_time)
    })) || []
  }

  function findBreaks(date) {
    const schedules = findIntervals(date)
    const breaks = []
    
    for (let i = 0; i < schedules.length - 1; i++) {
      const endTime = schedules[i].end_time.slice(0, 5)
      const startTime = schedules[i + 1].start_time.slice(0, 5)
      
      breaks.push({
        start: endTime,
        end: startTime,
        label: `${endTime} – ${startTime}`
      })
    }
    return breaks
  }

  function computeTimeSlotsWithBreaks(date) {
    const schedules = findIntervals(date)
    const breaks = findBreaks(date)
    
    if (schedules.length === 0) return []
    
    const allItems = []
    
    for (let i = 0; i < schedules.length; i++) {
      const range = schedules[i]
      
      const startTime = new Date(`${date}T${range.start_time}`)
      const endTime = new Date(`${date}T${range.end_time}`)
      
      let current = new Date(startTime)
      while (current <= endTime) {
        const hours = current.getHours().toString().padStart(2, '0')
        const minutes = current.getMinutes().toString().padStart(2, '0')
        allItems.push({
          type: 'slot',
          time: `${hours}:${minutes}`,
          isBreak: false
        })
        current.setMinutes(current.getMinutes() + SLOT_INTERVAL_MINUTES)
      }

      const endHour = endTime.getHours()
      const endMinute = endTime.getMinutes()

      if (endHour === 23 && endMinute > 30) {
        allItems.push({
          type: 'slot',
          time: '23:59',
          isBreak: false
        })
      }
      
      if (i < schedules.length - 1) {
        const breakItem = breaks[i]
        allItems.push({
          type: 'break',
          start: breakItem.start,
          end: breakItem.end,
          label: breakItem.label,
          isBreak: true
        })
      }
    }
    
    return allItems
  }

  function getTimeSlotsWithBreaks(date) {
    if (!selectedResource.value) return []
    
    const cacheKey = `${selectedResource.value.id}_${date}`
    
    if (slotsCache.has(cacheKey)) {
      return slotsCache.get(cacheKey)
    }
    
    const result = computeTimeSlotsWithBreaks(date)
    slotsCache.set(cacheKey, result)
    
    return result
  }

  function formatToMoscow(utc_time) {
    const date = new Date(utc_time)
    return date.toLocaleString('ru-RU', {
      timeZone: 'Europe/Moscow',
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  async function loadBookedSlots(date, resourceId) {
    try {
      const response = await api.get(`/booking/?resource_id=${resourceId}`)
      const dateStr = typeof date === 'string' ? date : formatDate(date)

      const filterBooking = response.data.filter(booking => {
        const bookingDate = new Date(booking.start_time)
        const bookingDateMSK = new Date(bookingDate.toLocaleString('en-US', {
          timeZone: 'Europe/Moscow'
        }))
        const bookingDateStr = formatDate(bookingDateMSK)
        return bookingDateStr === dateStr && !booking.is_cancelled
      })
      
      bookedSlots.value = filterBooking.map(booking => ({
        start: formatToMoscow(new Date(booking.start_time)),
        end: formatToMoscow(new Date(booking.end_time))
      }))
    } catch (e) {
      console.error('Ошибка загрузки броней:', e)
      bookedSlots.value = []
    }
  }

  function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number)
    return hours * 60 + minutes
  }

  function isSlotBooked(slotTime) {
    const slotMinutes = timeToMinutes(slotTime)
    return bookedSlots.value.some(booking => 
      slotMinutes > timeToMinutes(booking.start) && slotMinutes < timeToMinutes(booking.end)
    )
  }

  function isSlotInSelectedIntervals(slotTime) {
    const slotMinutes = timeToMinutes(slotTime)
    return bookingIntervals.value.some(interval => 
      slotMinutes > timeToMinutes(interval.start) && slotMinutes < timeToMinutes(interval.end)
    )
  }

  const minDate = computed(() => formatDate(new Date()))

  const maxDate = computed(() => {
    const date = new Date()
    date.setMonth(date.getMonth() + 6)
    return formatDate(date)
  })

  const timeSlotsWithBreaks = computed(() => {
    if (!selectedDate.value || !selectedResource.value) return []
    return getTimeSlotsWithBreaks(selectedDate.value)
  })

  const breaks = computed(() => {
    if (!selectedDate.value || !selectedResource.value) return []
    return findBreaks(selectedDate.value)
  })

  const canBook = computed(() => bookingIntervals.value.length > 0)

  const totalBookingTime = computed(() => {
    if (bookingIntervals.value.length === 0) return ''
    const totalMinutes = bookingIntervals.value.reduce((sum, interval) => {
      const [startHour, startMin] = interval.start.split(':').map(Number)
      const [endHour, endMin] = interval.end.split(':').map(Number)
      const minutes = (endHour * 60 + endMin) - (startHour * 60 + startMin)
      return sum + minutes
    }, 0)
    const hours = Math.floor(totalMinutes / 60)
    const minutes = totalMinutes % 60
    return hours > 0 ? `${hours} ч ${minutes} мин` : `${minutes} мин`
  })

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

  const paginatedResources = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredResources.value.slice(start, end)
  })

  const totalPages = computed(() => Math.ceil(filteredResources.value.length / itemsPerPage.value))

  function resetPage() {
    currentPage.value = 1
  }

  function goToPage(page) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  function prevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  function getVisiblePages() {
    const delta = 2
    const range = []
    const rangeWithDots = []
    let l

    for (let i = 1; i <= totalPages.value; i++) {
      if (i === 1 || i === totalPages.value || (i >= currentPage.value - delta && i <= currentPage.value + delta)) {
        range.push(i)
      }
    }

    range.forEach((i) => {
      if (l) {
        if (i - l === 2) {
          rangeWithDots.push(l + 1)
        } else if (i - l !== 1) {
          rangeWithDots.push('...')
        }
      }
      rangeWithDots.push(i)
      l = i
    })

    return rangeWithDots
  }

  async function handleEditResource(resourceId) {
    try {
      const shouldEdit = await editResource(resourceId)
      if (shouldEdit && router) {
        router.push({
          path: '/create_resource',
          query: { resourceId: resourceId }
        })
      }
    } catch (e) {
      alert('Ошибка при подготовке к редактированию')
    }
  }

  async function openModal(resource) {
    selectedResource.value = resource
    showModal.value = true
    selectedDate.value = minDate.value
    resetSelection()
    await loadBookedSlots(selectedDate.value, resource.id)

    if (window.bookingRefreshInterval) {
      clearInterval(window.bookingRefreshInterval)
    }
    window.bookingRefreshInterval = setInterval(async () => {
      if (showModal.value && selectedDate.value && selectedResource.value) {
        await loadBookedSlots(selectedDate.value, selectedResource.value.id)
      }
    }, 30000)
  }

  function closeModal() {
    showModal.value = false
    selectedResource.value = null
    selectedDate.value = ''
    resetSelection()
    slotsCache.clear()

    if (window.bookingRefreshInterval) {
      clearInterval(window.bookingRefreshInterval)
      window.bookingRefreshInterval = null
    }
  }

  function checkBreakOverlap(startIndex, endIndex) {
    if (!breaks.value.length) return false
    
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = timeToMinutes(startItem.time)
    const endTime = timeToMinutes(endItem.time)
    
    for (const breakItem of breaks.value) {
      if (startTime < timeToMinutes(breakItem.end) && endTime > timeToMinutes(breakItem.start)) {
        errorMessage.value = `Выбранное время пересекается с перерывом (${breakItem.start} – ${breakItem.end})`
        return true
      }
    }
    return false
  }

  function checkBookedOverlap(startIndex, endIndex) {
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = timeToMinutes(startItem.time)
    const endTime = timeToMinutes(endItem.time)
    
    for (const booked of bookedSlots.value) {
      if (startTime < timeToMinutes(booked.end) && endTime > timeToMinutes(booked.start)) {
        errorMessage.value = `Выбранное время уже забронировано (${booked.start} – ${booked.end})`
        return true
      }
    }
    return false
  }

  function checkIntervalOverlap(startIndex, endIndex) {
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = timeToMinutes(startItem.time)
    const endTime = timeToMinutes(endItem.time)
    
    for (const interval of bookingIntervals.value) {
      if (startTime < timeToMinutes(interval.end) && endTime > timeToMinutes(interval.start)) {
        errorMessage.value = `Выбранный интервал пересекается с уже выбранным (${interval.start} – ${interval.end})`
        return true
      }
    }
    return false
  }

  function isTimeInPast(dateString, timeString) {
    const nowUTC = Date.now()
    const [year, month, day] = dateString.split('-').map(Number)
    const [hours, minutes] = timeString.split(':').map(Number)
    const slotUTC = Date.UTC(year, month - 1, day, hours - MSK_OFFSET_HOURS, minutes)
    return slotUTC < nowUTC
  }

  function isSlotSelectable(slotIndex) {
    if (!selectedDate.value) return true
    
    const slotTime = timeSlotsWithBreaks.value[slotIndex]
    if (!slotTime || slotTime.isBreak) return false
    
    if (isTimeInPast(selectedDate.value, slotTime.time)) return false
    
    return !isSlotBooked(slotTime.time) && !isSlotInSelectedIntervals(slotTime.time)
  }

  function isSlotDisabled(slotIndex) {
    const slotItem = timeSlotsWithBreaks.value[slotIndex]
    if (!slotItem || slotItem.isBreak) return true
    if (!isSlotSelectable(slotIndex)) return true
    return isSlotBooked(slotItem.time) || isSlotInSelectedIntervals(slotItem.time)
  }

  function isSlotInRange(slotIndex) {
    if (selectedStart.value === null || selectedEnd.value === null) return false
    return slotIndex >= selectedStart.value && slotIndex <= selectedEnd.value
  }

  function isSlotInPreviewRange(slotIndex) {
    if (selectedStart.value === null || hoverEnd.value === null) return false
    if (selectedEnd.value !== null) return false
    const start = Math.min(selectedStart.value, hoverEnd.value)
    const end = Math.max(selectedStart.value, hoverEnd.value)
    return slotIndex >= start && slotIndex <= end
  }

  function getSlotClass(slotIndex) {
    if (slotIndex === -1 || !timeSlotsWithBreaks.value[slotIndex]) {
      return {}
    }
    
    const inRange = isSlotInRange(slotIndex)
    const inPreview = isSlotInPreviewRange(slotIndex)
    const disabled = isSlotDisabled(slotIndex)
    
    if (disabled) {
      return { 'slot-disabled': true }
    }
    
    return {
      'slot-selected': inRange,
      'slot-start': inRange && slotIndex === selectedStart.value,
      'slot-end': inRange && slotIndex === selectedEnd.value,
      'slot-preview': inPreview && !inRange
    }
  }

  function handleSlotClick(slotIndex) {
    errorMessage.value = ''
    
    if (!selectedDate.value) {
      errorMessage.value = 'Сначала выберите дату'
      setTimeout(() => { errorMessage.value = '' }, 2000)
      return
    }
    
    if (timeSlotsWithBreaks.value.length === 0) {
      errorMessage.value = 'В этот день ресурс не работает'
      setTimeout(() => { errorMessage.value = '' }, 2000)
      return
    }
    
    if (isSlotDisabled(slotIndex)) {
      errorMessage.value = 'Это время уже недоступно для бронирования'
      setTimeout(() => { errorMessage.value = '' }, 2000)
      return
    }
    
    if (selectedStart.value === slotIndex && selectedEnd.value === null) {
      errorMessage.value = 'Выберите другую ячейку для завершения интервала'
      setTimeout(() => { errorMessage.value = '' }, 2000)
      return
    }
    
    if (selectedStart.value !== null && selectedEnd.value !== null) {
      selectedStart.value = slotIndex
      selectedEnd.value = null
      hoverEnd.value = slotIndex
      return
    }
    
    if (selectedStart.value === null) {
      selectedStart.value = slotIndex
      hoverEnd.value = slotIndex
    } else {
      const start = Math.min(selectedStart.value, slotIndex)
      const end = Math.max(selectedStart.value, slotIndex)
      
      if (checkBreakOverlap(start, end) || checkBookedOverlap(start, end) || checkIntervalOverlap(start, end)) {
        selectedStart.value = null
        selectedEnd.value = null
        hoverEnd.value = null
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }
      
      const startItem = timeSlotsWithBreaks.value[start]
      const endItem = timeSlotsWithBreaks.value[end]
      
      bookingIntervals.value.push({
        start: startItem.time,
        end: endItem.time
      })
      
      selectedStart.value = null
      selectedEnd.value = null
      hoverEnd.value = null
    }
  }

  function removeBookingInterval(index) {
    bookingIntervals.value.splice(index, 1)
  }

  function handleSlotMouseEnter(slotIndex) {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      const slotItem = timeSlotsWithBreaks.value[slotIndex]
      if (slotItem && !slotItem.isBreak && !isSlotDisabled(slotIndex)) {
        hoverEnd.value = slotIndex
      }
    }
  }

  function handleGridMouseLeave() {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      hoverEnd.value = null
    }
  }

  function showBreakWarning(breakItem) {
    errorMessage.value = `Время ${breakItem.start} – ${breakItem.end} - это перерыв. Ресурс не работает!`
    setTimeout(() => { errorMessage.value = '' }, 3000)
  }

  function resetSelection() {
    selectedStart.value = null
    selectedEnd.value = null
    hoverEnd.value = null
    bookingIntervals.value = []
    bookedSlots.value = []
    errorMessage.value = ''
  }

  function cancelSelection() {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      selectedStart.value = null
      hoverEnd.value = null
      errorMessage.value = ''
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Escape') {
      cancelSelection()
    }
  }

  async function onDateChange() {
    resetSelection()
    if (selectedDate.value && selectedResource.value) {
      await loadBookedSlots(selectedDate.value, selectedResource.value.id)
    }
  }

  async function bookResource() {
    if (!canBook.value) return
    
    try {
      for (const interval of bookingIntervals.value) {
        const startTimeStr = `${selectedDate.value}T${interval.start}:00+03:00`
        const endTimeStr = `${selectedDate.value}T${interval.end}:00+03:00`
        
        await api.post('/booking/', {
          resource_id: selectedResource.value.id,
          start_time: startTimeStr,
          end_time: endTimeStr
        })
      }
      
      alert(`Успешно забронировано ${bookingIntervals.value.length} интервал(ов) для ресурса "${selectedResource.value.name}"!`)
      closeModal()
    } catch (e) {
      alert(`Ошибка бронирования: ${e.response?.data?.detail || 'Неизвестная ошибка'}`)
    }
  }

  async function deleteResource(resourceId) {
    const confirmed = confirm('Вы уверены, что хотите удалить этот ресурс? Все бронирования будут удалены вместе с ним!')
    if (!confirmed) return
    
    try {
      await api.delete(`/resource/${resourceId}`)
      await getResources()
    } catch (e) {
      alert('Ошибка при удалении ресурса')
    }
  }

  async function editResource(resourceId) {
    try {
      sessionStorage.setItem('editingResourceId', resourceId)
      return true
    } catch (e) {
      alert('Ошибка при подготовке к редактированию')
      return false
    }
  }

  watch([selectedTypes, searchQuery], () => {
    resetPage()
  })

  onMounted(async () => {
    window.addEventListener('keydown', handleKeyDown)
    await getResources()
    
    if (route && route.value?.query?.book) {
      const resourceId = route.value.query.book
      const resource = resources.value.find(r => r.id == resourceId)
      if (resource) {
        openModal(resource)
      }
    }
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })

  return {
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
  }
}