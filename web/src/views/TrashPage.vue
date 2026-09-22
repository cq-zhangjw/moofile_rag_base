<script setup lang="ts">
import { ref, h, onMounted, computed } from 'vue'
import { useMessage, NButton, NEmpty, NTag } from 'naive-ui'
import { listTrash, restoreFromTrash, destroyTrashed, emptyTrash } from '../mock/services'
import type { DatabaseInfo } from '../mock/store'
import { relativeTime } from '../utils/format'
import MFTypeTag from '../components/MFTypeTag.vue'
import { useI18n } from 'vue-i18n'

const rows = ref<DatabaseInfo[]>([])
const message = useMessage()
const { t, locale } = useI18n()
const load = async () => { rows.value = await listTrash() }
onMounted(load)

const columns = computed(() => [
  {
    title: t('trash.databaseName'), key: 'name', width: 240,
    render: (r: DatabaseInfo) => h('span', { style: 'font-weight:500;color:#111827;' }, r.name),
  },
  { title: t('common.type'), key: 'type', width: 140, render: (r: DatabaseInfo) => h(MFTypeTag, { type: r.type }) },
  { title: t('database.records'), key: 'recordCount', width: 120, render: (r: DatabaseInfo) => r.recordCount.toLocaleString(locale.value) },
  { title: t('common.size'), key: 'sizeMB', width: 120, render: (r: DatabaseInfo) => r.sizeMB.toFixed(2) + ' MB' },
  { title: t('trash.deletedAt'), key: 'updatedAt', width: 140, render: (r: DatabaseInfo) => h('span', { style: 'font-size:12px;color:#6B7280;' }, relativeTime(r.updatedAt, locale.value)) },
  {
    title: t('common.actions'), key: 'actions', width: 200,
    render: (r: DatabaseInfo) => [
      h(NButton, { size: 'small', text: true, type: 'primary', onClick: () => onRestore(r.id) }, () => t('trash.restore')),
      h(NButton, { size: 'small', text: true, style: 'color:#DC2626;', onClick: () => onDestroy(r.id) }, () => t('trash.destroy')),
    ],
  },
])

const onRestore = async (id: string) => { await restoreFromTrash(id); message.success(t('trash.restored')); load() }
const onDestroy = async (id: string) => { await destroyTrashed(id); message.success(t('trash.destroyed')); load() }
const onEmpty = async () => { await emptyTrash(); message.success(t('trash.emptied')); load() }
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <div style="font-size:20px;font-weight:600;">{{ t('trash.title') }}</div>
      <n-button type="error" tertiary :disabled="!rows.length" @click="onEmpty">{{ t('trash.emptyTrash') }}</n-button>
    </div>
    <n-data-table
      :columns="columns"
      :data="rows"
      :bordered="false"
      :row-key="(r: DatabaseInfo) => r.id"
    >
      <template #empty>
        <n-empty :description="t('trash.empty')" />
      </template>
    </n-data-table>
  </div>
</template>
