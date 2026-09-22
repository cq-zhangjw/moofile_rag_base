<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { DatabaseInfo } from '../mock/store'
import { state } from '../mock/store'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; db: DatabaseInfo | null }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'confirmed', id: string): void }>()
const { t, locale } = useI18n()
const confirmName = ref('')

watch(
  () => props.visible,
  (v) => { if (v) confirmName.value = '' }
)

const canConfirm = computed(() => props.db && confirmName.value === props.db.name)
const close = () => emit('update:visible', false)
const submit = () => {
  if (!props.db || !canConfirm.value) return
  emit('confirmed', props.db.id)
}
</script>

<template>
  <n-modal :show="visible" @close="close" preset="card" style="width:480px;" :bordered="false" :closable="false">
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="width:48px;height:48px;border-radius:12px;background:#FEF2F2;display:flex;align-items:center;justify-content:center;color:#DC2626;font-size:24px;flex-shrink:0;">⚠</div>
      <div>
        <div style="font-size:16px;font-weight:600;color:#DC2626;">{{ t('deleteDatabase.irreversible') }}</div>
        <div style="font-size:13px;color:#374151;margin-top:4px;">{{ t('deleteDatabase.will', { name: db?.name }) }}</div>
        <ul style="font-size:13px;color:#6B7280;padding-left:18px;line-height:1.9;margin:8px 0;">
          <li>{{ t('deleteDatabase.records', { count: db?.recordCount.toLocaleString(locale) }) }}</li>
          <li>{{ t('deleteDatabase.documents', { count: state.documents[db?.id || '']?.length || 0 }) }}</li>
          <li>{{ t('deleteDatabase.index') }}</li>
          <li>{{ t('deleteDatabase.storage', { size: db?.sizeMB }) }}</li>
        </ul>
        <div style="font-size:13px;color:#374151;margin-top:8px;">{{ t('deleteDatabase.prompt') }}</div>
        <n-input v-model:value="confirmName" :placeholder="db?.name" style="margin-top:6px;" :status="canConfirm ? undefined : 'error'" />
      </div>
    </div>
    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="error" :disabled="!canConfirm" @click="submit">{{ t('deleteDatabase.confirm') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>
