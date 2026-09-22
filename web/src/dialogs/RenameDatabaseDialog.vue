<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { renameDatabase } from '../mock/services'
import type { DatabaseInfo } from '../mock/store'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; db: DatabaseInfo | null }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'renamed', db: DatabaseInfo): void }>()
const message = useMessage()
const { t } = useI18n()
const name = ref('')
const submitting = ref(false)
const nameError = computed(() => {
  if (!name.value) return t('wizard.nameRequired')
  if (!/^[a-zA-Z0-9_]{2,64}$/.test(name.value)) return t('wizard.nameInvalid')
  return ''
})
watch(
  () => props.visible,
  (v) => { if (v && props.db) name.value = props.db.name }
)
const close = () => emit('update:visible', false)
const submit = async () => {
  if (!props.db) return
  if (nameError.value) { message.error(nameError.value); return }
  submitting.value = true
  try {
    const renamed = await renameDatabase(props.db.id, name.value.trim())
    message.success(t('renameDatabase.success'))
    emit('renamed', renamed)
    close()
  } catch (error: any) {
    message.error(error?.message || t('common.operationFailed'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:400px;" :title="t('renameDatabase.title')" :bordered="false">
    <n-input v-model:value="name" :placeholder="t('renameDatabase.placeholder')" :status="nameError && name ? 'error' : undefined" />
    <div v-if="nameError && name" style="font-size:12px;color:#DC2626;margin-top:6px;">{{ nameError }}</div>
    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="submitting" @click="submit">{{ t('common.confirm') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>
