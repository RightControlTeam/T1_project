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
    const resource = await api.post('/resource', form.value)
    console.log("Отправлено")
    console.log(resource)

    const request = await api.get('/resource')
    console.log(request.data)
  } catch (e) {
    console.log(e)
  }
}

</script>

<template>
  <div class="content-container">
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
  </div>
</template>

<style scoped>

.content-container {
  min-height: 100vh;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  padding: 20px;
  box-sizing: border-box;
}

h1{
  color: black;
}

form {
  width: 100%;
  max-width: 1024px;
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
    font-family: Inter,
    -apple-system,
    BlinkMacSystemFont,  /* для Mac */
    'Segoe UI',   /* для Windows */
    Roboto,     /* для Android */
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
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

.choose{
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