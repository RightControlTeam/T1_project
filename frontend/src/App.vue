<script setup>
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
</script>

<template>
    <Header></Header>
    <div id="app">
        <main>
            <RouterView />
        </main>
    </div>
</template>

<style>
    #app {
        padding: 40px 50px 0;       
        margin: 0;
    }
</style>

