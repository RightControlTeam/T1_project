<script setup>
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
</script>

<template>
    <div>
        <Header></Header>
        <main>
            <RouterView />
        </main>
    </div>
</template>



<!-- <style scoped>
header {
    background: #42b883;
    padding: 1rem;
    color: rgb(104, 104, 104);
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

a {
    color: rgb(0, 0, 0);
    text-decoration: none;
}

button {
    padding: 5px 10px;
    background: rgb(0, 0, 0);
    color: #42b883;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style> -->
