<script setup lang="ts">
import { useI18n } from 'vue-i18n'
defineProps<{ type: 'normal' | 'vector' }>()
const { t } = useI18n()
</script>

<template>
  <span class="mf-type" :class="type">
    <span class="dot" />
    {{ t(type === 'vector' ? 'database.vector' : 'database.normal') }}
  </span>
</template>

<style scoped>
.mf-type {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}
.mf-type .dot { width: 6px; height: 6px; border-radius: 50%; margin-right: 4px; }
.mf-type.normal { background: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; }
.mf-type.normal .dot { background: #6B7280; }
.mf-type.vector { background: #F5F3FF; color: #7C3AED; border: 1px solid #DDD6FE; }
.mf-type.vector .dot { background: #7C3AED; }
</style>
