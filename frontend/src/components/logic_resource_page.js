import { computed, onMounted, onUnmounted, ref } from 'vue'
import api from '@/api/index'

export function useResourcesPage() {

  // Список всех ресурсов, полученных с сервера
  const resources = ref([])
  // Сообщение об ошибке для отображения в интерфейсе
  const error = ref('')
  // Флаг загрузки данных
  const loading = ref(true)
  // Уровень администратора из localStorage
  const admin_level = ref(localStorage.getItem('admin_level'))

  // Состояние модального окна бронирования
  const showModal = ref(false)
  // Выбранный для бронирования ресурс
  const selectedResource = ref(null)

  // Выбранные интервалы бронирования
  const bookingIntervals = ref([])

  // Состояние выбора времени в модальном окне
  const selectedDate = ref('')
  const selectedStart = ref(null)
  const selectedEnd = ref(null)
  const hoverEnd = ref(null)
  const errorMessage = ref('')

  // Список уже забронированных слотов дня
  const bookedSlots = ref([])


  // ЗАГРУЗКА ДАННЫХ

  // Получение списка ресурсов из API, обработка ошибок
  async function getResources() {
    try {
      error.value = ''
      const request = await api.get('/resource')
      resources.value = request.data.map(resource => {
        resource.schedules.sort((a, b) => {
          if (a.day_of_week !== b.day_of_week) {
            return a.day_of_week - b.day_of_week
          }

          return a.start_time.localeCompare(b.start_time)
        })
        return resource
      })
      console.log(request.data)
    } catch (e) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки ресурсов'
    } finally {
      loading.value = false
    }
  }

  // Первоначальная загрузка данных при монтировании компонента
  onMounted(getResources)


  // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

  // Обрезает строку до заданной длины с добавлением многоточия
  function truncate(str, maxLength) {
    if (!str) return 'Нет описания'
    if (str.length <= maxLength) return str
    return str.slice(0, maxLength) + '...'
  }

  // Возвращает индекс дня недели (0 = понедельник, 6 = воскресенье)
  function getDayOfWeek(date) {
    const dateObj = new Date(date)
    const dayOfWeek = dateObj.getDay()
    return dayOfWeek === 0 ? 6 : dayOfWeek - 1
  }

  // Удаляет миллисекунды из строки времени
  function cleanTimeString(timeStr) {
    if (!timeStr) return ''
    return timeStr.split('.')[0]
  }

  // Форматирует объект даты в строку YYYY-MM-DD
  function formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }


  // РАБОТА С РАСПИСАНИЕМ

  // Находит временные интервалы работы ресурса для выбранной даты
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

  // Вычисляет перерывы между временными интервалами работы ресурса
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

  // Создает массив временных слотов с учетом рабочих интервалов и перерывов
  function getTimeSlotsWithBreaks(date) {
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
        current.setMinutes(current.getMinutes() + 30)
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


  // ЗАГРУЗКА БРОНЕЙ

  // Загружает существующие бронирования для ресурса на выбранную дату
  async function loadBookedSlots(date, resourceId) {
    try {
      console.log('получаем текущие брони')
      const response = await api.get(`/booking/?resource_id=${resourceId}`)
      const dateStr = typeof date === 'string' ? date : formatDate(date)
      console.log('Брони получены', response)
      const filterBooking = response.data.filter(booking => {
        const bookingDate = booking.start_time.split('T')[0]
        return bookingDate === dateStr && !booking.is_cancelled
      })
      bookedSlots.value = filterBooking.map(booking => ({
        start: booking.start_time.split('T')[1]?.slice(0, 5) || '',
        end: booking.end_time.split('T')[1]?.slice(0, 5) || ''
      }))
      console.log('Брони', bookedSlots.value)
    } catch (e) {
      console.error('Ошибка загрузки броней:', e)
      bookedSlots.value = []
    }
  }

  // Проверяет, занят ли временной слот существующими бронированиями
  function isSlotBooked(slotTime) {
    return bookedSlots.value.some(booking => {
      return slotTime >= booking.start && slotTime < booking.end
    })
  }

  // Проверяет, входит ли слот в уже выбранные интервалы бронирования
  function isSlotInSelectedIntervals(slotTime) {
    return bookingIntervals.value.some(interval => {
      return slotTime >= interval.start && slotTime < interval.end
    })
  }


  // ВЫЧИСЛЯЕМЫЕ СВОЙСТВА
  
  // Минимальная доступная дата (сегодня)
  const minDate = computed(() => formatDate(new Date()))

  // Максимальная дата бронирования (через 6 месяцев)
  const maxDate = computed(() => {
    const date = new Date()
    date.setMonth(date.getMonth() + 6)
    return formatDate(date)
  })

  // Генерирует отображаемые временные слоты с перерывами для выбранной даты
  const timeSlotsWithBreaks = computed(() => {
    if (!selectedDate.value || !selectedResource.value) return []
    return getTimeSlotsWithBreaks(selectedDate.value)
  })

  // Список перерывов для текущей даты и ресурса
  const breaks = computed(() => {
    if (!selectedDate.value || !selectedResource.value) return []
    return findBreaks(selectedDate.value)
  })

  // Проверяет, можно ли выполнить бронирование (выбран хотя бы один интервал)
  const canBook = computed(() => bookingIntervals.value.length > 0)

  // Вычисляет общую продолжительность выбранных интервалов бронирования
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


  // МОДАЛЬНОЕ ОКНО

  // Открывает модальное окно бронирования для выбранного ресурса
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

  // Закрывает модальное окно и сбрасывает все состояния
  function closeModal() {
    showModal.value = false
    selectedResource.value = null
    selectedDate.value = ''
    resetSelection()

    if (window.bookingRefreshInterval) {
      clearInterval(window.bookingRefreshInterval)
      window.bookingRefreshInterval = null
    }
  }


  // ЛОГИКА ВЫБОРА ВРЕМЕНИ

  // Проверяет пересечение выбранного диапазона с перерывами в работе ресурса
  function checkBreakOverlap(startIndex, endIndex) {
    if (!breaks.value.length) return false
    
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = startItem.time
    const endTime = endItem.time
    
    for (const breakItem of breaks.value) {
      if (startTime < breakItem.end && endTime > breakItem.start) {
        errorMessage.value = `Выбранное время пересекается с перерывом (${breakItem.start} – ${breakItem.end})`
        return true
      }
    }
    return false
  }

  // Проверяет пересечение выбранного диапазона с уже забронированными слотами
  function checkBookedOverlap(startIndex, endIndex) {
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = startItem.time
    const endTime = endItem.time
    
    for (const booked of bookedSlots.value) {
      if (startTime < booked.end && endTime > booked.start) {
        errorMessage.value = `Выбранное время уже забронировано (${booked.start} – ${booked.end})`
        return true
      }
    }
    return false
  }

  // Проверяет пересечение с уже выбранными интервалами текущего бронирования
  function checkIntervalOverlap(startIndex, endIndex) {
    const startItem = timeSlotsWithBreaks.value[startIndex]
    const endItem = timeSlotsWithBreaks.value[endIndex]
    
    if (!startItem || startItem.isBreak) return false
    if (!endItem || endItem.isBreak) return false
    
    const startTime = startItem.time
    const endTime = endItem.time
    
    for (const interval of bookingIntervals.value) {
      if (startTime < interval.end && endTime > interval.start) {
        errorMessage.value = `Выбранный интервал пересекается с уже выбранным (${interval.start} – ${interval.end})`
        return true
      }
    }
    return false
  }

  // Проверяет, заблокирован ли слот (занят или является перерывом)
  function isSlotDisabled(slotIndex) {
    const slotItem = timeSlotsWithBreaks.value[slotIndex]
    if (!slotItem || slotItem.isBreak) return true
    return isSlotBooked(slotItem.time) || isSlotInSelectedIntervals(slotItem.time)
  }

  // Проверяет, находится ли слот в выбранном диапазоне
  function isSlotInRange(slotIndex) {
    if (selectedStart.value === null || selectedEnd.value === null) return false
    return slotIndex >= selectedStart.value && slotIndex <= selectedEnd.value
  }

  // Подсвечивает предварительный диапазон при наведении курсора
  function isSlotInPreviewRange(slotIndex) {
    if (selectedStart.value === null || hoverEnd.value === null) return false
    if (selectedEnd.value !== null) return false
    const start = Math.min(selectedStart.value, hoverEnd.value)
    const end = Math.max(selectedStart.value, hoverEnd.value)
    return slotIndex >= start && slotIndex <= end
  }

  // Возвращает CSS-классы для временного слота в зависимости от его состояния
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

  // Находит индекс слота по времени
  function findSlotIndexByTime(time) {
    return timeSlotsWithBreaks.value.findIndex(item => 
      !item.isBreak && item.time === time
    )
  }

  // Обрабатывает клик по временному слоту для выбора диапазона бронирования
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
      
      if (checkBreakOverlap(start, end)) {
        selectedStart.value = null
        selectedEnd.value = null
        hoverEnd.value = null
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }
      
      if (checkBookedOverlap(start, end)) {
        selectedStart.value = null
        selectedEnd.value = null
        hoverEnd.value = null
        setTimeout(() => { errorMessage.value = '' }, 3000)
        return
      }
      
      if (checkIntervalOverlap(start, end)) {
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

  // Удаляет интервал бронирования из выбранных
  function removeBookingInterval(index) {
    bookingIntervals.value.splice(index, 1)
  }

  // Обрабатывает наведение мыши на слот для предварительного просмотра диапазона
  function handleSlotMouseEnter(slotIndex) {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      const slotItem = timeSlotsWithBreaks.value[slotIndex]
      if (slotItem && !slotItem.isBreak && !isSlotDisabled(slotIndex)) {
        hoverEnd.value = slotIndex
      }
    }
  }

  // Сбрасывает предварительный просмотр при уходе мыши с сетки слотов
  function handleGridMouseLeave() {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      hoverEnd.value = null
    }
  }

  // Показывает предупреждение при наведении на перерыв
  function showBreakWarning(breakItem) {
    errorMessage.value = `Время ${breakItem.start} – ${breakItem.end} - это перерыв. Ресурс не работает!`
    setTimeout(() => { errorMessage.value = '' }, 3000)
  }

  // Полный сброс выбора времени
  function resetSelection() {
    selectedStart.value = null
    selectedEnd.value = null
    hoverEnd.value = null
    bookingIntervals.value = []
    bookedSlots.value = []
    errorMessage.value = ''
  }

  // Отменяет текущий выбор начального слота без завершения диапазона
  function cancelSelection() {
    if (selectedStart.value !== null && selectedEnd.value === null) {
      selectedStart.value = null
      hoverEnd.value = null
      errorMessage.value = ''
    }
  }

  // Обрабатывает нажатие клавиш (Escape для отмены выбора)
  function handleKeyDown(event) {
    if (event.key === 'Escape') {
      cancelSelection()
    }
  }

  // Обрабатывает изменение даты и перезагружает данные бронирования
  async function onDateChange() {
    resetSelection()
    if (selectedDate.value && selectedResource.value) {
      await loadBookedSlots(selectedDate.value, selectedResource.value.id)
    }
  }


  // БРОНИРОВАНИЕ

  // Отправляет запрос на бронирование выбранных интервалов
  async function bookResource() {
    if (!canBook.value) return
    
    try {
      for (const interval of bookingIntervals.value) {
        const startDateTime = new Date(`${selectedDate.value}T${interval.start}:00`)
        const endDateTime = new Date(`${selectedDate.value}T${interval.end}:00`)
      
        startDateTime.setHours(startDateTime.getHours() - 3)
        endDateTime.setHours(endDateTime.getHours() - 3)
        
        const bookingData = {
            resource_id: selectedResource.value.id,
            start_time: startDateTime.toISOString(),
            end_time: endDateTime.toISOString()
        }

        console.log('Бронирование:', {
        resource_id: bookingData.resource_id,
        start_local: `${selectedDate.value} ${interval.start}`,
        start_utc: bookingData.start_time,
        end_local: `${selectedDate.value} ${interval.end}`,
        end_utc: bookingData.end_time
      })

        await api.post('/booking/', bookingData)
        console.log('Забронировано')
      }
      
      alert(`Успешно забронировано ${bookingIntervals.value.length} интервал(ов) для ресурса "${selectedResource.value.name}"!`)
      closeModal()
    } catch (e) {
      console.error(e)
      alert(`Ошибка бронирования: ${e.response?.data?.detail || 'Неизвестная ошибка'}`)
    }
  }


  // УДАЛЕНИЕ РЕСУРСА

  // Удаляет ресурс с подтверждением и обновляет список ресурсов
  async function deleteResource(resourceId) {
    const confirmed = confirm('Вы уверены, что хотите удалить этот ресурс? Все бронирования будут удалены вместе с ним!')
    if (!confirmed) return
    
    try {
      await api.delete(`/resource/${resourceId}`)
      await getResources()
    } catch (e) {
      console.error(e)
      alert('Ошибка при удалении ресурса')
    }
  }


  // ЖИЗНЕННЫЙ ЦИКЛ

  // Добавляет обработчик клавиш при монтировании компонента
  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  // Удаляет обработчик клавиш при демонтировании для предотвращения утечек памяти
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })

  return {
    // Состояние
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

    // Вычисляемые свойства
    minDate,
    maxDate,
    timeSlotsWithBreaks,
    breaks,
    canBook,
    totalBookingTime,

    // Методы
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
    getSlotClass,
    findSlotIndexByTime
  }
}