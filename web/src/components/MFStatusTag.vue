<script setup lang="ts">
import { computed } from 'vue'
import type { StatusStyle } from '../constants/status'
import { NIcon, NSpin } from 'naive-ui'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  map: Record<string, StatusStyle>
  status: string
}>()
const { t } = useI18n()

const item = computed(() => props.map[props.status] || { label: props.status, color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' })
</script>

<template>
  <span
    class="mf-status-tag"
    :style="{
      background: item.soft,
      color: item.color,
      borderColor: item.border,
    }"
  >
    <n-spin v-if="item.spin" :size="10" style="display:inline-block;margin-right:4px;" />
    {{ item.label.startsWith('status.') ? t(item.label) : item.label }}
  </span>
</template>

<style scoped>
.mf-status-tag {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
</style>
