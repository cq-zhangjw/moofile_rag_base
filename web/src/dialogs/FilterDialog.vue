<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NButton, NSelect, NInput, NIcon } from 'naive-ui'
import { Add } from '@vicons/ionicons5'
import { OPERATORS } from '../constants/status'
import type { FilterGroup } from '../mock/services'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ visible: boolean; fields: string[]; value: FilterGroup | null }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'apply', g: FilterGroup): void }>()
const { t } = useI18n()

const logic = ref<'AND' | 'OR'>('AND')
const conditions = ref<Array<{ field: string; operator: string; value: string }>>([])

watch(
  () => props.visible,
  (v) => {
    if (v) {
      logic.value = props.value?.logic || 'AND'
      conditions.value = props.value?.conditions?.length
        ? props.value.conditions.map((c) => ({ ...c }))
        : []
    }
  }
)

const operatorOptions = computed(() => OPERATORS.map((o) => ({ label: t(o.label), value: o.key })))
const logicOptions = computed(() => [
  { label: t('filters.allConditions'), value: 'AND' },
  { label: t('filters.anyCondition'), value: 'OR' },
])

const addCondition = () => {
  conditions.value.push({ field: props.fields[0] || '', operator: 'eq', value: '' })
}
const removeCondition = (i: number) => conditions.value.splice(i, 1)

const preview = computed(() => {
  const cond: any[] = []
  for (const c of conditions.value) {
    if (!c.field || c.operator === 'exists' || c.operator === 'not_exists') {
      cond.push(c.operator === 'exists' ? { [c.field]: { $exists: true } } : { [c.field]: { $exists: false } })
      continue
    }
    const v = c.value
    switch (c.operator) {
      case 'eq': cond.push({ [c.field]: v }); break
      case 'ne': cond.push({ [c.field]: { $ne: v } }); break
      case 'contains': cond.push({ [c.field]: { $regex: v, $options: 'i' } }); break
      case 'not_contains': cond.push({ [c.field]: { $not: { $regex: v, $options: 'i' } } }); break
      case 'gt': cond.push({ [c.field]: { $gt: Number(v) } }); break
      case 'gte': cond.push({ [c.field]: { $gte: Number(v) } }); break
      case 'lt': cond.push({ [c.field]: { $lt: Number(v) } }); break
      case 'lte': cond.push({ [c.field]: { $lte: Number(v) } }); break
      case 'regex': cond.push({ [c.field]: { $regex: v } }); break
      case 'array_contains': cond.push({ [c.field]: { $in: [v] } }); break
    }
  }
  const obj = cond.length === 1 ? cond[0] : logic.value === 'AND' ? { $and: cond } : { $or: cond }
  return JSON.stringify(obj, null, 2)
})

const close = () => emit('update:visible', false)
const apply = () => {
  emit('apply', { logic: logic.value, conditions: [...conditions.value] })
  close()
}
const opType = (key: string) => OPERATORS.find((o) => o.key === key)?.type || 'input'
</script>

<template>
  <n-modal :show="visible" @update:show="(v: boolean) => emit('update:visible', v)" @close="close" preset="card" style="width:640px;" :title="t('filters.title')" :bordered="false">
    <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:#374151;">
      {{ t('filters.match') }}
      <n-select v-model:value="logic" :options="logicOptions" style="width:120px;" size="small" />
      {{ t('filters.conditions') }} <span style="color:#9CA3AF;">({{ logic }})</span>
    </div>

    <div style="margin-top:16px;display:flex;flex-direction:column;gap:8px;">
      <div v-for="(c, i) in conditions" :key="i" style="display:flex;gap:8px;align-items:center;">
        <n-select v-model:value="c.field" :options="fields.map((f) => ({ label: f, value: f }))" style="width:200px;" size="small" />
        <n-select v-model:value="c.operator" :options="operatorOptions" style="width:130px;" size="small" />
        <n-input v-if="opType(c.operator) === 'input'" v-model:value="c.value" :placeholder="t('filters.value')" size="small" />
        <n-input v-else-if="opType(c.operator) === 'number'" v-model:value="c.value" :placeholder="t('filters.number')" size="small" />
        <span v-else style="flex:1;"></span>
        <n-button size="small" quaternary circle style="color:#DC2626;" @click="removeCondition(i)">✕</n-button>
      </div>
      <div v-if="!conditions.length" style="text-align:center;color:#9CA3AF;font-size:13px;padding:16px 0;">{{ t('filters.empty') }}</div>
    </div>

    <div style="display:flex;gap:12px;margin:16px 0;">
      <n-button size="small" tertiary @click="addCondition"><n-icon><Add /></n-icon> {{ t('filters.add') }}</n-button>
    </div>

    <div style="font-size:12px;color:#6B7280;margin-bottom:6px;">{{ t('filters.preview') }}</div>
    <pre class="preview">{{ preview }}</pre>

    <template #footer>
      <div style="display:flex;justify-content:flex-end;gap:8px;">
        <n-button @click="close">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :disabled="!conditions.length" @click="apply">{{ t('filters.apply') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.preview {
  background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px;
  padding: 12px 16px; font-family: Consolas, monospace; font-size: 12px;
  line-height: 1.6; color: #374151; margin: 0; overflow: auto; max-height: 160px;
}
</style>
