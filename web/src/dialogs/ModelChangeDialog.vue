<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { changeIndexModel, rebuildIndex, listModels } from '../mock/services'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; dbId: string }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'changed'): void }>()
const message = useMessage()
const { t } = useI18n()
const model = ref('')
const modelOptions = ref<{ label: string; value: string }[]>([])
const submitting = ref(false)
watch(() => props.visible, async (v) => {
  if (v) {
    try {
      const models = await listModels()
      modelOptions.value = models.map((m) => ({
        label: m.dims ? `${m.name} (${t('modelChange.dimensions', { count: m.dims })})` : m.name,
        value: m.name,
      }))
      const def = models.find((m) => m.default) || models[0]
      model.value = def ? def.name : ''
    } catch {
      modelOptions.value = []
    }
  }
})
const close = () => emit('update:visible', false)
const submit = async () => {
  submitting.value = true
  try {
    await changeIndexModel(props.dbId, model.value)
    await rebuildIndex(props.dbId)
    message.success(t('modelChange.success'))
    emit('changed')
    close()
  } finally { submitting.value = false }
}
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:480px;" :title="t('modelChange.title')" :bordered="false">
    <n-select v-model:value="model" :options="modelOptions" :placeholder="t('modelChange.placeholder')" />
    <n-alert style="margin-top:16px;" type="warning" :title="t('modelChange.warningTitle')" :show-icon="true">
      {{ t('modelChange.warning') }}
    </n-alert>
    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="submitting" @click="submit">{{ t('modelChange.confirm') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>
