<script setup>
  import api from '@/api/index'
  import { onMounted, ref } from 'vue'

  const resources = ref([])
  const error = ref('')
  const loading = ref(true)
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
        <p>{{ resource.description }}</p>
      </div>
      <button>Забронировать</button>
    </div>
  </div>
</template>

<style scoped>
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