<script setup>
  import api from '@/api/index'
  import { onMounted, ref } from 'vue'

  const resources = ref([])
  const error = ref('')
  const show_modal = ref(false);
  const selected_resource = ref(null);
  const loading = ref(true)
  const user_time = (-180 - new Date().getTimezoneOffset()) / 60
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

  function book() {
    alert(`Забронирован ресурс ${selected_resource.value.name}`)
    close_modal()
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
      <button @click="open_modal(resource)">Забронировать</button>
    </div>
  </div>
  <div v-if="show_modal" @click="close_modal" class="modal-overlay">
    <div @click.stop class="modal">
      <h3>{{ selected_resource.name }}</h3>
      <p>{{ selected_resource.description }}</p>
      <p class="warning">Бронирование происходит по московскому времени. Ваше смещение относительно Москвы: {{ user_time }} часов</p>
      <button @click="book">Забронировать</button>
    </div>
  </div>
</template>

<style scoped>
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
    margin: 16px auto;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    border: 2px solid #5D20ED;
    font-size: 16px;
    color: #5D20ED;
    font-weight: 400;
}
</style>