<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { createDatabase, listDatabases } from '../mock/services'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'created'): void }>()
const message = useMessage()
const { t, tm } = useI18n()

const step = ref(1)
const type = ref<'normal' | 'vector'>('normal')
const name = ref('')
const submitting = ref(false)
const existed = ref<string[]>([])

watch(
  () => props.visible,
  async (v) => {
    if (v) {
      step.value = 1
      type.value = 'normal'
      name.value = ''
      existed.value = (await listDatabases()).map((d) => d.name)
    }
  }
)

const nameError = computed(() => {
  if (!name.value) return t('wizard.nameRequired')
  if (!/^[a-zA-Z0-9_]{2,64}$/.test(name.value)) return t('wizard.nameInvalid')
  if (existed.value.includes(name.value)) return t('wizard.nameExists')
  return ''
})

const close = () => emit('update:visible', false)
const next = async () => {
  if (step.value === 1) { step.value = 2; return }
  if (step.value === 2) {
    if (nameError.value) { message.error(nameError.value); return }
    step.value = 3
    return
  }
  await submit()
}
const submit = async () => {
  submitting.value = true
  try {
    await createDatabase(name.value, type.value)
    message.success(t('database.created'))
    emit('created')
    close()
  } catch (error: any) {
    message.error(error?.message || t('common.operationFailed'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:640px;" :bordered="false">
    <template #header>{{ t('wizard.title') }}</template>
    <n-steps :current="step" size="small" style="margin-bottom:20px;">
      <n-step :title="t('wizard.selectType')" />
      <n-step :title="t('wizard.basicInfo')" />
      <n-step :title="t('wizard.confirm')" />
    </n-steps>

    <!-- Step 1 -->
    <div v-if="step === 1">
      <div style="font-size:13px;color:#6B7280;margin-bottom:12px;">{{ t('wizard.chooseType') }}</div>
      <div style="display:flex;gap:16px;">
        <div class="type-card" :class="{ selected: type==='normal', selectedNormal: type==='normal' }" @click="type='normal'">
          <div style="font-weight:600;font-size:16px;margin-bottom:8px;">{{ t('database.normalJson') }}</div>
          <div style="font-size:13px;color:#6B7280;margin-bottom:12px;">{{ t('wizard.normalDesc') }}</div>
          <div v-for="f in (tm('wizard.normalFeatures') as string[])" :key="f" class="feat">√ {{ f }}</div>
        </div>
        <div class="type-card" :class="{ selected: type==='vector', selectedVector: type==='vector' }" @click="type='vector'">
          <div style="font-weight:600;font-size:16px;margin-bottom:8px;">{{ t('database.vector') }}</div>
          <div style="font-size:13px;color:#6B7280;margin-bottom:12px;">{{ t('wizard.vectorDesc') }}</div>
          <div v-for="f in (tm('wizard.vectorFeatures') as string[])" :key="f" class="feat">√ {{ f }}</div>
        </div>
      </div>
    </div>

    <!-- Step 2 -->
    <div v-else-if="step === 2">
      <n-form label-placement="top">
        <n-form-item :label="t('wizard.name')">
          <n-input v-model:value="name" :placeholder="t('wizard.namePlaceholder')" size="large" />
          <div v-if="nameError && name" style="font-size:12px;color:#DC2626;margin-top:4px;">{{ nameError }}</div>
        </n-form-item>
      </n-form>
    </div>

    <!-- Step 3 -->
    <div v-else>
      <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:16px;">
        <div style="font-size:14px;color:#374151;">
          <span style="color:#6B7280;">{{ t('wizard.type') }}</span>{{ t(type === 'vector' ? 'database.vector' : 'database.normalJson') }}
        </div>
        <div style="font-size:14px;color:#374151;margin-top:8px;">
          <span style="color:#6B7280;">{{ t('wizard.name') }}:</span> <span style="font-family:monospace;font-weight:600;">{{ name }}</span>
        </div>
        <div style="font-size:12px;color:#6B7280;margin-top:12px;">
          {{ t(type === 'vector' ? 'wizard.vectorSummary' : 'wizard.normalSummary') }}
        </div>
      </div>
    </div>

    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button v-if="step > 1" @click="step--">{{ t('common.previous') }}</n-button>
        <n-button type="primary" :loading="submitting" @click="next">
          {{ t(step === 3 ? 'common.create' : 'common.next') }}
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.type-card {
  flex: 1; border: 1px solid #E5E7EB; border-radius: 12px; padding: 16px;
  cursor: pointer; transition: all 200ms; background: #fff;
}
.type-card:hover { box-shadow: 0 4px 6px -1px rgba(17,24,39,0.07); }
.type-card.selected { border-width: 2px; background: #F9FAFB; }
.type-card.selectedNormal { border-color: #4F46E5; background: #EEF2FF; }
.type-card.selectedVector { border-color: #7C3AED; background: #F5F3FF; }
.feat { font-size: 13px; color: #374151; margin-top: 6px; }
</style>
