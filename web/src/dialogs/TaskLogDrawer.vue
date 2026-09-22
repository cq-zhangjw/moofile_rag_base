<script setup lang="ts">
import { ref, watch } from 'vue'
import { getTaskLogs } from '../mock/services'
import { TASK_TYPES, TASK_STATUS } from '../constants/status'
import type { TaskInfo } from '../mock/store'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; task: TaskInfo | null; dbId: string }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>()
const lines = ref<string[]>([])
const { t, locale } = useI18n()

watch(
  () => props.visible,
  async (v) => {
    if (v && props.task) lines.value = await getTaskLogs(props.dbId, props.task.id)
  }
)
const close = () => emit('update:visible', false)
</script>

<template>
  <n-drawer :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" :width="560">
    <n-drawer-content :title="t('taskLog.title', { id: task?.id || '' })" closable>
      <n-descriptions :column="2" label-placement="left" bordered size="small" style="margin-bottom:16px;">
        <n-descriptions-item :label="t('common.type')">{{ task ? t(TASK_TYPES[task.type]?.label) : '–' }}</n-descriptions-item>
        <n-descriptions-item :label="t('tasks.target')">{{ task?.target || '–' }}</n-descriptions-item>
        <n-descriptions-item :label="t('common.status')">{{ task ? t(TASK_STATUS[task.status]?.label) : '–' }}</n-descriptions-item>
        <n-descriptions-item :label="t('tasks.startAt')">{{ task?.startAt ? new Date(task.startAt).toLocaleString(locale, { hour12: false }) : '–' }}</n-descriptions-item>
      </n-descriptions>

      <div style="background:#111827;border-radius:8px;padding:16px;font-family:Consolas,monospace;font-size:12px;line-height:1.8;">
        <div v-for="(l, i) in lines" :key="i" :style="{ color: l.includes('ERROR') ? '#f87171' : l.includes('WARN') ? '#fbbf24' : '#9ca3af' }">
          {{ l }}
        </div>
      </div>

      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px;">
          <n-button size="small" @click="close">{{ t('common.close') }}</n-button>
        </div>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>
