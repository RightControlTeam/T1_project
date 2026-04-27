<script setup>
  import api from '@/api/index'
  import { computed, onMounted, ref } from 'vue'
  import deleteIcon from '@/components/icons/delete.svg'
  import editIcon from '@/components/icons/edit.svg'

  const resources = ref([])
  const error = ref('')
  const show_modal = ref(false);
  const selected_resource = ref(null);
  const loading = ref(true)
  const user_time = (-180 - new Date().getTimezoneOffset()) / 60
  const booking_form = ref({
    resource_id: 0,
    start_time: '',
    end_time: ''
  })
  const errorMessage = ref('')
  const errors = ref({
    date: '',
    schedules: ''
  })
  const date = ref('')
  const admin_level = ref(localStorage.getItem('admin_level'))
  
  async function get_resources() {
    try {
        error.value = ''
        const request = await api.get('/resource')
        resources.value = request.data
    }
    catch (e) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки'
    }
    finally {
      loading.value = false
    }

  }
  onMounted(get_resources)

  // cut str to 150 chars
  const truncate = (str, maxLength) => {
    if (str.length <= maxLength) {
      return str;
    }
    return str.slice(0, maxLength) + '...';
  };

  function open_modal(resource) {
    show_modal.value = true
    selected_resource.value = resource
    
  }

  function close_modal() {
    show_modal.value = false
    selected_resource.value = null
  }

  async function book() {
    try {
      const response = await api.post('/booking/', booking_form.value)
      alert(`Забронирован ресурс ${selected_resource.value.name}`)
      close_modal()
      resetSelection()
      console.log(response.data)
      console.log('success')
    }
    catch (e) {
      console.log(e)
    }
  }

  function get_day_of_week(date) {
    const dateObj = new Date(date)
    const day_of_week = dateObj.getDay()
    return day_of_week === 0 ? 6 : day_of_week - 1
  }

  function find_intervals(date) {
    let index = get_day_of_week(date)
    console.log(index)
    return selected_resource.value.schedules.filter(schedule => schedule.day_of_week === index)
  }

  function find_breaks(date) {
    const schedules = find_intervals(date)
    console.log(schedules)
    const breaks = []
    for (let i = 0; i < schedules.length - 1; i++) {
      breaks.push(`${schedules[i].end_time}-${schedules[i + 1].start_time}`)
    }
    console.log(breaks)
    return breaks
  }

  function get_time_slots(date) {
    const schedules = find_intervals(date)
    console.log(schedules)
    const slots = []
    for (const range of schedules) {
      const current = new Date(`${date}T${range.start_time}`)
      const end = new Date(`${date}T${range.end_time}`)
      console.log(current, end)
      while (current <= end) {
        const hours = current.getHours().toString().padStart(2, '0')
        const minutes = current.getMinutes().toString().padStart(2, '0')
        slots.push(`${hours}:${minutes}`)
        current.setMinutes(current.getMinutes() + 30)
        console.log(current)
        }
    }
    console.log(slots)
    return slots
  }
  const time_slots = computed(() => {
    if (!date.value || !selected_resource.value) return []
    return get_time_slots(date.value)
  })

  const breaks = computed(() => {
    if (!date.value || !selected_resource.value) return []
    return find_breaks(date.value)
  })
  console.log(breaks)

  const selectedStart = ref(null)
  const selectedEnd = ref(null)
  //const hoverEnd = ref(null)


function handleSlotClick(slotIndex) {
    if (selectedStart.value === slotIndex) {
        errorMessage.value = `Выберите другую ячейку для завершения интервала`
        return
    }
    
    if (selectedStart.value === null) {
        selectedStart.value = slotIndex
    } else {
        const start = Math.min(selectedStart.value, slotIndex)
        const end = Math.max(selectedStart.value, slotIndex)
        for (const break_item of breaks.value) {
          const [break_start, break_end] = break_item.split('-')
          const break_start_value = new Date(`${date.value}T${break_start}`)
          const break_end_value = new Date(`${date.value}T${break_end}`)
          const start_value = new Date(`${date.value}T${time_slots.value[start]}`)
          const end_value = new Date(`${date.value}T${time_slots.value[end]}`)
          if ((start_value < break_start_value && end_value > break_start_value) || 
              (start_value < break_end_value && end_value > break_end_value) || 
              (start_value >= break_start_value && end_value <= break_end_value)) {
            errorMessage.value = `Выбранный интервал пересекается с перерывом ${break_item}`
            return
          }

        }
        booking_form.value.start_time = `${date.value}T${time_slots.value[start]}:00`
        booking_form.value.end_time = `${date.value}T${time_slots.value[end]}:00`
        booking_form.value.resource_id = selected_resource.value.id
        selectedStart.value = start
        selectedEnd.value = slotIndex
    }
}

function resetSelection() {
    selectedStart.value = null
    selectedEnd.value = null
    booking_form.value.start_time = ''
    booking_form.value.end_time = ''
    setTimeout(() => { errorMessage.value = '' }, 1500)
}


function isSlotInSavedRange(slotIndex) {
  if (selectedStart.value === null || selectedEnd.value === null) {
    return { inRange: false, isStart: false, isEnd: false }
  }
    
  return {
    inRange: slotIndex >= selectedStart.value && slotIndex <= selectedEnd.value,
    isStart: slotIndex === selectedStart.value,
    isEnd: slotIndex === selectedEnd.value
  }
}

function getSlotClass(slotIndex) {
  const saved = isSlotInSavedRange(slotIndex)
  return {
    'slot-selected': saved.inRange,
    'slot-start': saved.isStart,
    'slot-end': saved.isEnd,
  }
}

async function delete_resource(resource_id) {
  try {
    const confirmed = confirm('Вы уверены, что хотите удалить этот ресурс?')
    if (!confirmed) return
    await api.delete(`/resource/${resource_id}`)
    console.log("success")
  }
  catch (e) {
    console.log(e)
  }
}

</script>

<template>
  <h1>ResourcesPage</h1>
  <p v-if="loading">Загрузка...</p>
  <p v-else-if="error">{{ error }}</p>
  <div v-else class="cards">
    <div v-for="resource in resources" :key="resource.id" class="card">
      <h3>{{ resource.name }}</h3>
      <div>
        <span>Описание</span>
        <p>{{ truncate(resource.description, 150) }}</p>
      </div>
      <div class="book">
        <button @click="delete_resource" class="custom-button">
          <img v-if="admin_level === '1'" :src="editIcon" alt="edit">
        </button>
        <button @click="open_modal(resource)">Забронировать</button>
        <button @click="delete_resource(resource.id)" class="custom-button">
          <img v-if="admin_level === '1'" :src="deleteIcon" alt="delete">
        </button>
      </div>
    </div>
  </div>

  <div v-if="show_modal" @click="close_modal" class="modal-overlay">
    <div @click.stop class="modal">
      <h3>{{ selected_resource.name }}</h3>
      <p>{{ selected_resource.description }}</p>
      <p class="warning">Бронирование происходит по московскому времени. Ваше смещение относительно Москвы: {{ user_time }} часов</p>
      <span>Выберите дату (дд.мм.гггг) и время</span>
      <div class="group-input">
        <input v-model="date" type="date">
      </div>
      <div v-for="(break_item, index) in breaks" :key="index">
        <p>{{ break_item }}</p>
      </div>
      <div v-if="date" class="grid">
        <div v-for="(slot, index) in time_slots"
            :key="index"
            :class="getSlotClass(index)"
            @click="handleSlotClick(index)"
            class="time-slot">
            {{ slot }}
        </div>
      </div>
      <p v-if="errorMessage">{{ errorMessage }}</p>
      <button v-if="booking_form.end_time" @click="resetSelection">Отменить</button>
      {{ booking_form }}
      <div>
      </div>
      <button @click="book">Забронировать</button>
    </div>
  </div>
</template>

<style scoped>
.custom-button {
  border: none;
  margin: 0px;
  padding: 0px
}
.book {
  display: flex;
  align-items: center;
}

.grid {
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
  font-size: 14px;
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

.group-input {
  display: flex;
  gap: 16px;
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

.warning {
  color: black;
  font-style: italic;
  margin-top: 14px;
  text-align: left;
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


.cards {
  display: flex;
  flex-direction: row;
  width: 100%;
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
}
h3 {
  text-align: center;
  font-size: 18px;
  font-weight: medium;
}
p {
  color: #505050;
  font-size: 14px;
  margin-top: 4px;
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
</style>