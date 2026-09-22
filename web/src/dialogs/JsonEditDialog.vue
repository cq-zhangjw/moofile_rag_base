<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import MFJsonEditor from '../components/MFJsonEditor.vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; initial: Record<string, any> | null }>()
const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'save', json: string): void
}>()
const message = useMessage()
const { t } = useI18n()
const text = ref('')
const editorRef = ref<InstanceType<typeof MFJsonEditor> | null>(null)

watch(
  () => props.visible,
  (v) => {
    if (v) {
      text.value = props.initial ? JSON.stringify(props.initial, null, 2) : '{\n  \n}'
    }
  }
)
const close = () => emit('update:visible', false)
const save = () => {
  const ok = editorRef.value?.validate()
  if (!ok) {
    message.error(t('jsonDialog.invalid'))
    return
  }
  emit('save', text.value)
  message.success(t('common.saved'))
  close()
}
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:800px;" :title="t('jsonDialog.title')" :bordered="false">
    <MFJsonEditor ref="editorRef" v-model="text" :height="400" />
    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:16px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" @click="save">{{ t('common.save') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>
