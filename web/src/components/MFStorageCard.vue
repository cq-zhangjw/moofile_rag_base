<script setup lang="ts">
import { computed } from 'vue'
import { state } from '../mock/store'
import { formatBytes } from '../utils/format'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const used = computed(() => state.storage.usedGB)
const total = computed(() => state.storage.quotaGB)
const pct = computed(() => Math.min(100, Math.round(state.storage.percent)))
const danger = computed(() => pct.value >= 90)
</script>

<template>
  <div class="mf-storage">
    <div class="row1">{{ t('storage.title') }}</div>
    <div class="row2">{{ t('storage.used', { used: formatBytes(used * 1024 * 1024), total: formatBytes(total * 1024 * 1024) }) }}</div>
    <div class="bar"><div class="fill" :style="{ width: pct + '%', background: danger ? '#F59E0B' : '#4F46E5' }" /></div>
    <div class="row3" :style="{ color: danger ? '#F59E0B' : '#6B7280' }">{{ pct }}%</div>
  </div>
</template>

<style scoped>
.mf-storage {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(17,24,39,0.05);
  padding: 12px 16px;
}
.row1 { font-size: 12px; color: #6B7280; font-weight: 500; }
.row2 { font-size: 13px; color: #374151; font-weight: 500; margin-top: 4px; }
.bar { height: 6px; background: #E5E7EB; border-radius: 3px; margin-top: 8px; overflow: hidden; }
.fill { height: 6px; border-radius: 3px; transition: width 300ms; }
.row3 { font-size: 12px; margin-top: 4px; }
</style>
