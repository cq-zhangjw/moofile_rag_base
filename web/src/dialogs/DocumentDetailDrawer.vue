<script setup lang="ts">
import { computed } from 'vue'
import MFStatusTag from '../components/MFStatusTag.vue'
import { DOC_STATUS, VECTOR_STATUS } from '../constants/status'
import type { DocInfo } from '../mock/store'
import { formatBytes } from '../utils/format'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; doc: DocInfo | null; dbId: string }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'changed'): void }>()
const close = () => emit('update:visible', false)
const doc = computed(() => props.doc)
const { t, locale } = useI18n()
</script>

<template>
  <n-drawer :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" :width="560">
    <n-drawer-content :title="doc?.name || ''" closable>
      <n-descriptions :column="2" bordered size="small" label-placement="left">
        <n-descriptions-item :label="t('common.type')">{{ doc?.type }}</n-descriptions-item>
        <n-descriptions-item :label="t('common.size')">{{ doc ? formatBytes(doc.size) : '–' }}</n-descriptions-item>
        <n-descriptions-item :label="t('documentDetail.uploadTime')">{{ doc ? new Date(doc.uploadTime).toLocaleString(locale, { hour12: false }) : '–' }}</n-descriptions-item>
        <n-descriptions-item :label="t('common.status')">
          <MFStatusTag v-if="doc" :map="DOC_STATUS" :status="doc.docStatus" />
        </n-descriptions-item>
        <n-descriptions-item :label="t('documents.chunks')">{{ doc?.chunkCount || 0 }}</n-descriptions-item>
        <n-descriptions-item :label="t('documents.vectorStatus')">
          <MFStatusTag v-if="doc" :map="VECTOR_STATUS" :status="doc.vectorStatus" />
        </n-descriptions-item>
      </n-descriptions>

      <div v-if="doc?.errorMsg" style="margin-top:16px;">
        <n-alert type="error" :title="t('documentDetail.failure')" :show-icon="true">{{ doc.errorMsg }}</n-alert>
      </div>

      <div style="font-size:13px;font-weight:500;margin:20px 0 8px;">{{ t('documentDetail.chunkSummary') }}</div>
      <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:12px;font-size:13px;color:#374151;line-height:1.7;">
        {{ t('documentDetail.summary', { count: doc?.chunkCount || 0, size: doc?.chunkSize || 500, overlap: doc?.overlap ?? 20 }) }}
      </div>

      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px;">
          <n-button size="small" @click="close">{{ t('common.close') }}</n-button>
        </div>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>
