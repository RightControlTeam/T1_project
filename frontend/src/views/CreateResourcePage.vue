<script setup>
import { ref } from 'vue'
import api from '@/api/index'

const form = ref({
    name: '',
    type: '',
    description: '',
    is_active: true 
})

async function submit() {
  try {
    const response = await api.post('/resource', form.value)
    console.log(response.data)
    const request = await api.get('/resource')
    console.log(request.data)
    form.value = {
      name: '',
      type: '',
      description: '',
      is_active: true
    }
  } catch (e) {
    console.log(e)
  }
}

</script>

<template>
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
    <button type="submit">Создать</button>
  </form>
</template>

<style scoped>



.choose{
  display: flex;
  flex-direction: column;
  gap: 8px;
}

h1{
  margin: 20px 0;
}

form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 70%
}

.group-input {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

label {
    font-size: 18px;
    font-weight: 400;
}

select {
  width: 200px;
}

select,
textarea,
input {
    flex: 1;
    padding: 12px 16px;
    background: none;
    border: 2px solid #D9D9D9;
    border-radius: 8px;
    outline: none;
    font-size: 16px;
    color: black;
    font-weight: 400;
}

button {
    flex: 1;
    padding: 12px 0;
    background: #5D20ED;
    border-radius: 8px;
    border: none;
    font-size: 16px;
    color: white;
    font-weight: 400;
}

</style>