<script setup lang="ts">
import { ref, computed } from 'vue'
import NewDatabaseWizardDialog from '../dialogs/NewDatabaseWizardDialog.vue'
import { useI18n } from 'vue-i18n'

const wizardVisible = ref(false)
const { t } = useI18n()
const features = computed(() => [
  { title: t('welcome.featureJson'), desc: t('welcome.featureJsonDesc') },
  { title: t('welcome.featureVector'), desc: t('welcome.featureVectorDesc') },
  { title: t('welcome.featureTasks'), desc: t('welcome.featureTasksDesc') },
])
</script>

<template>
  <div class="welcome">
    <h1 style="font-size:24px;font-weight:600;color:#111827;margin:0;">{{ t('welcome.title') }}</h1>
    <p style="font-size:14px;color:#6B7280;margin:8px 0 24px;">{{ t('welcome.subtitle') }}</p>
    <n-button type="primary" size="large" @click="wizardVisible = true">＋ {{ t('sidebar.newDatabase') }}</n-button>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:32px;max-width:960px;">
      <div v-for="f in features" :key="f.title" class="feat">
        <div style="font-size:15px;font-weight:600;color:#111827;">{{ f.title }}</div>
        <div style="font-size:13px;color:#6B7280;margin-top:6px;line-height:1.6;">{{ f.desc }}</div>
      </div>
    </div>
    <NewDatabaseWizardDialog v-model:visible="wizardVisible" />
  </div>
</template>

<style scoped>
.welcome { max-width: 960px; margin: 24px auto; text-align: center; }
.feat { background:#fff; border:1px solid #E5E7EB; border-radius:12px; padding:20px; text-align:left; box-shadow: 0 1px 2px rgba(17,24,39,0.05); }
</style>
