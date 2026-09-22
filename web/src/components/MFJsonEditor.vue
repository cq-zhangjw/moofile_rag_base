<script setup lang="ts">
import { ref, watch } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { CheckmarkOutline, CloseOutline, CopyOutline, SparklesOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{ modelValue: string; height?: number }>(),
  { height: 360 }
)
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()
const message = useMessage()
const { t } = useI18n()

const status = ref<'idle' | 'ok' | 'err'>('idle')
const errorMsg = ref('')

function parse(): { ok: boolean } {
  const text = props.modelValue
  if (!text.trim()) { setErr(t('jsonEditor.empty')); return { ok: false } }
  try {
    JSON.parse(text)
    status.value = 'ok'
    errorMsg.value = ''
    return { ok: true }
  } catch (e: any) {
    const m = e?.message || t('jsonEditor.parseFailed')
    const lineMatch = /position (\d+)/.exec(m)
    setErr(lineMatch ? t('jsonEditor.nearLine', { line: lineMatch[1], message: m }) : m)
    return { ok: false }
  }
}
function setErr(m: string) { status.value = 'err'; errorMsg.value = m }
function onInput(v: string) {
  emit('update:modelValue', v)
  status.value = 'idle'
}
function format() {
  if (parse().ok) {
    emit('update:modelValue', JSON.stringify(JSON.parse(props.modelValue), null, 2))
    message.success(t('jsonEditor.formatted'))
  }
}
function copy() {
  navigator.clipboard.writeText(props.modelValue)
  message.success(t('jsonEditor.copied'))
}
watch(
  () => props.modelValue,
  () => { if (status.value === 'err') parse() }
)
defineExpose({ validate: parse, getError: () => errorMsg.value })
</script>

<template>
  <div class="json-editor">
    <div class="toolbar">
      <n-button size="small" tertiary @click="format"><n-icon><SparklesOutline /></n-icon>{{ t('jsonEditor.format') }}</n-button>
      <n-button size="small" tertiary @click="parse"><n-icon><CheckmarkOutline /></n-icon>{{ t('jsonEditor.validate') }}</n-button>
      <n-button size="small" tertiary @click="copy"><n-icon><CopyOutline /></n-icon>{{ t('jsonEditor.copy') }}</n-button>
    </div>
    <div v-if="status !== 'idle'" class="status" :class="status">
      <span v-if="status === 'ok'" class="mark">√</span>
      <span v-else class="mark">✕</span>
      <span v-if="status === 'ok'">{{ t('jsonEditor.valid') }}</span>
      <span v-else>{{ errorMsg }}</span>
    </div>
    <textarea
      class="area"
      :style="{ height: height + 'px' }"
      :value="modelValue"
      spellcheck="false"
      @input="onInput(($event.target as HTMLTextAreaElement).value)"
    />
  </div>
</template>

<style scoped>
.json-editor { border: 1px solid #E5E7EB; border-radius: 8px; overflow: hidden; }
.toolbar { display: flex; gap: 8px; padding: 8px 12px; border-bottom: 1px solid #E5E7EB; background: #F9FAFB; }
.status { display: flex; align-items: center; gap: 6px; padding: 6px 12px; font-size: 12px; }
.status.ok { color: #16A34A; background: #F0FDF4; }
.status.err { color: #DC2626; background: #FEF2F2; }
.area {
  width: 100%; border: none; outline: none; resize: vertical;
  padding: 12px 16px; font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 12px; line-height: 1.6; color: #374151; background: #fff;
}
</style>
