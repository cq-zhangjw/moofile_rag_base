<script setup lang="ts">
import MFHeader from './parts/MFHeader.vue'
import MFSidebar from './parts/MFSidebar.vue'
</script>

<template>
  <div class="mf-layout">
    <MFHeader />
    <div class="mf-body">
      <MFSidebar />
      <main class="mf-main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.mf-layout { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
.mf-body { flex: 1; display: flex; overflow: hidden; }
.mf-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #F9FAFB;
}
.page-enter-active, .page-leave-active { transition: opacity 200ms; }
.page-enter-from, .page-leave-to { opacity: 0; }
</style>
