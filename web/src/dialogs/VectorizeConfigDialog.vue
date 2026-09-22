<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { startVectorization, listModels, getVectorConfig } from '../mock/services'
import type { DocInfo } from '../mock/store'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; dbId: string; documents: DocInfo[] }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'done'): void }>()
const message = useMessage()
const { t } = useI18n()

const model = ref('')
const modelOptions = ref<{ label: string; value: string }[]>([])
const chunkSize = ref(500)
const overlap = ref(20)
const submitting = ref(false)

watch(
  () => props.visible,
  async (v) => {
    if (v) {
      try {
        const [models, config] = await Promise.all([listModels(), getVectorConfig(props.dbId)])
        modelOptions.value = models.map((m) => ({
          label: m.dims ? `${m.name} (${t('vectorization.dimensions', { count: m.dims })})` : m.name,
          value: m.name,
        }))
        model.value = config.model
        chunkSize.value = config.chunkSize
        overlap.value = config.chunkOverlap
      } catch {
        modelOptions.value = []
        model.value = ''
      }
    }
  }
)

const overlapInvalid = computed(() => overlap.value >= chunkSize.value)

const close = () => emit('update:visible', false)
const submit = async () => {
  if (overlapInvalid.value) { message.error(t('vectorization.overlapInvalid')); return }
  submitting.value = true
  try {
    await startVectorization(props.dbId, props.documents.map((doc) => doc.id), { model: model.value, chunkSize: chunkSize.value, overlap: overlap.value })
    message.success(t('vectorization.created', { count: props.documents.length }))
    emit('done')
    close()
  } finally { submitting.value = false }
}
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:640px;" :title="t('vectorization.title')" :bordered="false">
    <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:10px 12px;font-size:13px;color:#374151;margin-bottom:16px;">
      <div>{{ t('vectorization.selectedConfirm', { count: documents.length }) }}</div>
      <ul class="selected-documents">
        <li v-for="doc in documents" :key="doc.id">{{ doc.name }}</li>
      </ul>
    </div>

    <n-form label-placement="top">
      <n-form-item label="Embedding Model">
        <n-select v-model:value="model" :options="modelOptions" :placeholder="t('vectorization.localModel')" />
      </n-form-item>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <n-form-item label="Chunk Size">
          <n-input-number v-model:value="chunkSize" :min="100" :max="2000" style="width:100%;" />
        </n-form-item>
        <n-form-item label="Chunk Overlap">
          <n-input-number v-model:value="overlap" :min="0" :max="500" style="width:100%;" :status="overlapInvalid ? 'error' : undefined" />
        </n-form-item>
      </div>
    </n-form>

    <div v-if="overlapInvalid" style="font-size:12px;color:#DC2626;margin-top:-8px;margin-bottom:8px;">{{ t('vectorization.overlapInvalid') }}</div>

    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="submitting" :disabled="overlapInvalid" @click="submit">{{ t('documents.startVectorization') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.selected-documents { max-height:120px; margin:8px 0 0; padding-left:20px; overflow-y:auto; color:#6B7280; }
.selected-documents li { margin-top:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
</style>
