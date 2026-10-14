<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, NInput, NDropdown, NBadge, NTooltip, NButton, NPopconfirm, useMessage } from 'naive-ui'
import { Add, Search, TrashBinOutline, FolderOutline, DocumentTextOutline, ChevronDown } from '@vicons/ionicons5'
import { listDatabases, deleteDatabase } from '../../mock/services'
import { state } from '../../mock/store'
import type { DatabaseInfo } from '../../mock/store'
import { relativeTime, formatBytes } from '../../utils/format'
import MFTypeTag from '../../components/MFTypeTag.vue'
import NewDatabaseWizardDialog from '../../dialogs/NewDatabaseWizardDialog.vue'
import RenameDatabaseDialog from '../../dialogs/RenameDatabaseDialog.vue'
import DeleteDatabaseDialog from '../../dialogs/DeleteDatabaseDialog.vue'
import { useI18n } from 'vue-i18n'

const emit = defineEmits<{ (e: 'toggle-collapse'): void }>()
const router = useRouter()
const route = useRoute()
const message = useMessage()
const { t, locale } = useI18n()

const dbs = ref<DatabaseInfo[]>([])
const keyword = ref('')
const wizardVisible = ref(false)
const renameVisible = ref(false)
const renameTarget = ref<DatabaseInfo | null>(null)
const deleteVisible = ref(false)
const deleteTarget = ref<DatabaseInfo | null>(null)

const load = async () => {
  try {
    dbs.value = await listDatabases()
  } catch (e) {
    console.error('[MFSidebar] load failed', e)
  }
}
onMounted(() => {
  load()
  window.addEventListener('mf:refresh', load)
})
onUnmounted(() => window.removeEventListener('mf:refresh', load))

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return dbs.value
  return dbs.value.filter((d) =>
    d.name.toLowerCase().includes(kw) ||
    (d.description || '').toLowerCase().includes(kw)
  )
})

const groups = computed(() => {
  const vector = filtered.value.filter((d) => d.type === 'vector')
  const normal = filtered.value.filter((d) => d.type !== 'vector')
  const out: { key: string; label: string; items: DatabaseInfo[] }[] = []
  if (vector.length) out.push({ key: 'vector', label: t('sidebar.groupVector'), items: vector })
  if (normal.length) out.push({ key: 'normal', label: t('sidebar.groupNormal'), items: normal })
  return out
})

const collapsed = ref<Set<string>>(new Set())
const toggleGroup = (key: string) => {
  const next = new Set(collapsed.value)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  collapsed.value = next
}

const currentId = computed(() => (route.params.id as string) || '')

const openDb = (id: string) => router.push(`/db/${id}`)

const rowOptions = (db: DatabaseInfo) => [
  { label: t('common.rename'), key: 'rename', props: { onClick: () => { renameTarget.value = db; renameVisible.value = true } } },
  { label: t('common.delete'), key: 'delete', props: { onClick: () => { deleteTarget.value = db; deleteVisible.value = true } } },
]

const onDeleted = async (id: string) => {
  await deleteDatabase(id)
  message.success(t('sidebar.deleted'))
  deleteVisible.value = false
  await load()
  if (currentId.value === id) router.push('/')
}

const onRenamed = async (renamed: DatabaseInfo) => {
  const previousId = renameTarget.value?.id
  await load()
  if (previousId && currentId.value === previousId && renamed.id !== previousId) {
    await router.replace(`/db/${renamed.id}`)
  }
}
</script>

<template>
  <aside class="mf-sidebar">
    <n-button type="primary" block round size="large" @click="wizardVisible = true">
      <template #icon><n-icon><Add /></n-icon></template>
      {{ t('sidebar.newDatabase') }}
    </n-button>

    <n-input v-model:value="keyword" :placeholder="t('sidebar.searchDb')" clearable style="margin-top:16px;">
      <template #prefix><n-icon><Search /></n-icon></template>
    </n-input>

    <div class="db-list">
      <div v-for="group in groups" :key="group.key">
        <div class="db-group-title" @click="toggleGroup(group.key)">
          <n-icon size="12" class="group-caret" :class="{ collapsed: collapsed.has(group.key) }">
            <ChevronDown />
          </n-icon>
          <span class="group-label">{{ group.label }}</span>
          <span class="group-count">{{ group.items.length }}</span>
        </div>
        <div v-show="!collapsed.has(group.key)">
          <div
            v-for="db in group.items"
            :key="db.id"
            class="db-item"
            :class="{ active: db.id === currentId }"
            @click="openDb(db.id)"
          >
            <div class="db-main">
              <span class="db-name">{{ db.name }}</span>
              <MFTypeTag :type="db.type" />
            </div>
            <div v-if="db.description" class="db-desc" :title="db.description">{{ db.description }}</div>
            <div class="db-sub">
              <span>{{ t('common.records', { count: (db.recordCount || 0).toLocaleString(locale) }) }} · {{ (db.sizeMB || 0).toFixed(2) }} MB</span>
              <span class="db-time">{{ relativeTime(db.updatedAt, locale) }}</span>
              <n-dropdown trigger="click" :options="rowOptions(db)" @click.stop>
                <n-button text size="tiny" class="row-more" @click.stop>···</n-button>
              </n-dropdown>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!filtered.length" class="empty">{{ t('sidebar.noMatch') }}</div>
    </div>

    <div class="db-item" style="margin-top:8px;" @click="router.push('/tasks')">
      <n-icon :size="16" style="margin-right:8px;color:#6B7280;"><DocumentTextOutline /></n-icon>
      <span style="flex:1;">{{ t('sidebar.taskCenter') }}</span>
    </div>
    <div class="db-item trash" @click="router.push('/trash')">
      <n-icon :size="16" style="margin-right:8px;"><TrashBinOutline /></n-icon>
      <span style="flex:1;">{{ t('sidebar.trash') }}</span>
      <n-badge :value="state.trash.length" :max="99" />
    </div>

    <NewDatabaseWizardDialog v-model:visible="wizardVisible" @created="load" />
    <RenameDatabaseDialog v-model:visible="renameVisible" :db="renameTarget" @renamed="onRenamed" />
    <DeleteDatabaseDialog v-model:visible="deleteVisible" :db="deleteTarget" @confirmed="onDeleted" />
  </aside>
</template>

<style scoped>
.mf-sidebar {
  width: 280px;
  background: #FFFFFF;
  border-right: 1px solid #E5E7EB;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.section-title {
  font-size: 12px; color: #6B7280; font-weight: 500;
  margin: 20px 0 8px 4px;
}
.db-group-title {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; color: #6B7280; font-weight: 600; letter-spacing: 0.03em;
  margin: 12px 4px 4px; padding: 3px 6px; border-radius: 6px;
  cursor: pointer; user-select: none;
}
.db-group-title:first-child { margin-top: 8px; }
.db-group-title:hover { color: #374151; background: #F3F4F6; }
.group-caret { transition: transform 0.15s ease; flex-shrink: 0; }
.group-caret.collapsed { transform: rotate(-90deg); }
.group-count {
  margin-left: auto; font-size: 10px; color: #9CA3AF; font-weight: 500;
  background: #F3F4F6; border-radius: 8px; padding: 0 6px; line-height: 16px;
}
.db-list { flex: 1; min-height: 0; overflow-y: auto; overscroll-behavior: contain; }
.db-item {
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 2px;
  cursor: pointer;
  transition: background 150ms;
  position: relative;
}
.db-item:hover { background: #F3F4F6; }
.db-item.active { background: #EEF2FF; }
.db-item.active::before {
  content: ''; position: absolute; left: 0; top: 8px; bottom: 8px;
  width: 3px; border-radius: 2px; background: #4F46E5;
}
.db-main { display: flex; align-items: center; gap: 8px; }
.db-name { font-size: 14px; font-weight: 500; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.db-desc {
  margin-top: 3px; font-size: 12px; color: #6B7280; line-height: 1.4;
  overflow: hidden; text-overflow: ellipsis; display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical; word-break: break-all;
}
.db-sub { display: flex; align-items: center; margin-top: 4px; font-size: 12px; color: #6B7280; }
.db-time { margin-left: auto; color: #9CA3AF; }
.row-more { opacity: 0; padding: 0 4px; margin-left: 4px; }
.db-item:hover .row-more { opacity: 1; }
.trash { display: flex; align-items: center; font-size: 14px; color: #374151; margin-top: 8px; }
.empty { text-align: center; color: #9CA3AF; font-size: 13px; padding: 24px 0; }
</style>
