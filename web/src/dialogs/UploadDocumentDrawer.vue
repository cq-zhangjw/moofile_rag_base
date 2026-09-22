<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMessage, NIcon } from 'naive-ui'
import { CloudUploadOutline } from '@vicons/ionicons5'
import { addUploadedDocument } from '../mock/services'
import { formatBytes } from '../utils/format'
import { FILE_TYPE_COLORS } from '../constants/status'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; dbId: string }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'uploaded'): void }>()
const message = useMessage()
const { t } = useI18n()

interface PendingFile { name: string; size: number; file: File | null; progress: number; status: 'waiting' | 'uploading' | 'done' | 'error' }
const files = ref<PendingFile[]>([])
const uploading = ref(false)

watch(
  () => props.visible,
  (v) => {
    if (v) {
      files.value = []
      uploading.value = false
    }
  }
)

const onUploadChange = (options: { file: any; fileList: any[] }) => {
  const list = options.fileList || []
  for (const f of list) {
    const real: File | undefined = f.file
    const size = real?.size || 0
    files.value.push({
      name: real?.name || f.name || `document_${Date.now()}.txt`,
      size,
      file: real || null,
      progress: 0,
      status: size > 50 * 1024 * 1024 ? 'error' : 'waiting',
    })
  }
}
const removeFile = (i: number) => files.value.splice(i, 1)
const clearAll = () => (files.value = [])

const startUpload = async () => {
  if (!files.value.length) { message.warning(t('upload.chooseFirst')); return }
  uploading.value = true
  let doneCount = 0
  let failCount = 0
  for (let i = 0; i < files.value.length; i++) {
    const f = files.value[i]
    if (f.status === 'error') { failCount++; continue }
    f.status = 'uploading'
    for (let p = 0; p <= 100; p += 10) {
      f.progress = p
      await new Promise((r) => setTimeout(r, 40))
    }
    try {
      const fileToUpload = f.file || new File([new Blob([''] as any)], f.name)
      await addUploadedDocument(props.dbId, fileToUpload)
      f.status = 'done'
      doneCount++
    } catch (e: any) {
      f.status = 'error'
      failCount++
      message.error(t('upload.failed', { name: f.name, message: e?.message || t('upload.unknownError') }))
    }
  }
  uploading.value = false
  if (doneCount > 0) {
    message.success(t('upload.success', { count: doneCount }))
  }
  emit('uploaded')
  if (failCount === 0) emit('update:visible', false)
}
const close = () => emit('update:visible', false)
</script>

<template>
  <n-drawer :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" :width="420">
    <n-drawer-content :title="t('upload.title')" closable>
      <n-upload multiple :default-upload="false" :show-file-list="false" @change="onUploadChange" style="margin-bottom:16px;">
        <n-upload-dragger>
          <div style="padding:24px;text-align:center;">
            <n-icon :size="32" style="color:#4F46E5;margin-bottom:8px;"><CloudUploadOutline /></n-icon>
            <div style="font-size:14px;color:#374151;">{{ t('upload.drop') }} <a style="color:#4F46E5;">{{ t('upload.choose') }}</a></div>
            <div style="font-size:12px;color:#6B7280;margin-top:6px;">{{ t('upload.support') }}</div>
          </div>
        </n-upload-dragger>
      </n-upload>

      <div v-if="files.length" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-size:13px;color:#374151;">{{ t('upload.selected', { count: files.length }) }}</span>
        <a style="font-size:12px;color:#6B7280;cursor:pointer;" @click="clearAll">{{ t('upload.clear') }}</a>
      </div>
      <div v-for="(f, i) in files" :key="i" class="file-row">
        <div style="flex:1;min-width:0;">
          <div style="font-size:13px;color:#111827;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ f.name }}</div>
          <div v-if="f.status === 'error'" style="font-size:12px;color:#DC2626;">{{ t('upload.tooLarge') }}</div>
          <div v-else style="font-size:12px;color:#6B7280;">{{ formatBytes(f.size) }}</div>
          <n-progress v-if="f.status === 'uploading' || f.status === 'done'" type="line" :percentage="f.progress" :show-indicator="false" style="margin-top:4px;" />
        </div>
        <n-button size="tiny" quaternary circle @click="removeFile(i)">✕</n-button>
      </div>

      <template #footer>
        <div style="display:flex;gap:8px;justify-content:flex-end;">
          <n-button :disabled="uploading" @click="close">{{ t('common.cancel') }}</n-button>
          <n-button type="primary" :loading="uploading" @click="startUpload">{{ t('upload.start') }}</n-button>
        </div>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.file-row { display:flex; align-items:center; gap:8px; background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:8px 12px; margin-bottom:8px; }
</style>
