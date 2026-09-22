<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  suffix?: string
  icon?: string
  clickable?: boolean
}>()
</script>

<template>
  <div class="mf-stat" :class="{ clickable }">
    <div class="title">{{ title }}</div>
    <div class="value">{{ value }}<span v-if="suffix" class="suffix">{{ suffix }}</span></div>
  </div>
</template>

<style scoped>
.mf-stat {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(17,24,39,0.05);
  padding: 16px 20px;
  height: 84px;
  transition: all 200ms;
}
.mf-stat.clickable { cursor: pointer; }
.mf-stat.clickable:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(17,24,39,0.07); }
.title { font-size: 12px; color: #6B7280; font-weight: 500; }
.value {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  font-variant-numeric: tabular-nums;
}
.suffix { font-size: 12px; color: #6B7280; font-weight: 400; margin-left: 4px; }
</style>
