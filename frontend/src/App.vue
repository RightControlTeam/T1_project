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
        padding: 40px 50px 0px;       
        width: 100%;
    }
    @media (max-width: 650px) {
        #app {
            padding: 40px 20px 0px;
        }
    }   
    @media (max-width: 450px) {
        #app {
            padding: 40px 10px 0px;
        }
    }
</style>

