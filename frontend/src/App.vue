<script setup lang="ts">
/** 留痕 · 根组件 */
import AppLayout from './layouts/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <router-view v-slot="{ Component }">
      <transition name="fade">
        <component :is="Component" />
      </transition>
    </router-view>
  </AppLayout>
</template>
