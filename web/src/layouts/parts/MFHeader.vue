<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { NIcon } from 'naive-ui'
import { ReloadOutline, HelpCircleOutline } from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { LOCALE_STORAGE_KEY, type AppLocale } from '../../i18n'
import { VueMarkdownIt } from '@f3ve/vue-markdown-it'
import { getHelpDocument } from '../../mock/services'
import 'github-markdown-css/github-markdown.css'

defineEmits<{ (e: 'refresh'): void }>()
const router = useRouter()
const { t, locale } = useI18n()
const refreshing = ref(false)
const helpVisible = ref(false)
const helpLoading = ref(false)
const helpContent = ref('')
const onRefresh = () => {
  refreshing.value = true
  setTimeout(() => (refreshing.value = false), 800)
  window.dispatchEvent(new Event('mf:refresh'))
}
const openHelp = async () => {
  helpVisible.value = true
  helpLoading.value = true
  try {
    helpContent.value = (await getHelpDocument(locale.value as AppLocale)).content
  } finally {
    helpLoading.value = false
  }
}

// Live clock (current time, updates every second)
const now = ref(new Date())
let timer: number | undefined
onMounted(() => { timer = window.setInterval(() => (now.value = new Date()), 1000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
const clockText = computed(() =>
  now.value.toLocaleString(locale.value, { hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
)
const weekText = computed(() => new Intl.DateTimeFormat(locale.value, { weekday: 'short' }).format(now.value))

const userOptions = computed(() => [
  { label: t('header.account'), key: 'account' },
  { label: t('header.logout'), key: 'logout' },
])
const languageOptions = [
  { label: '中文', key: 'zh' },
  { label: '日本語', key: 'ja' },
  { label: 'English', key: 'en' },
]
const languageLabel = computed(() => languageOptions.find((item) => item.key === locale.value)?.label || 'English')
const onLanguageSelect = (value: AppLocale) => {
  locale.value = value
  localStorage.setItem(LOCALE_STORAGE_KEY, value)
  document.documentElement.lang = value
}
const onUserSelect = (key: string) => {
  if (key === 'logout') router.push('/')
}
</script>

<template>
  <header class="mf-header">
    <div class="logo">
      <div class="logo-mark">M</div>
      <span class="logo-text">MooFile</span>
    </div>
    <div class="right">
      <span class="sys-status"><span class="dot" />{{ weekText }} {{ clockText }}</span>
      <n-tooltip>
        <template #trigger>
          <n-button quaternary circle :loading="refreshing" @click="onRefresh">
            <n-icon :size="16"><ReloadOutline /></n-icon>
          </n-button>
        </template>
        {{ t('header.refreshData') }}
      </n-tooltip>
      <n-tooltip>
        <template #trigger>
          <n-button quaternary circle @click="openHelp">
            <n-icon :size="16"><HelpCircleOutline /></n-icon>
          </n-button>
        </template>
        {{ t('header.help') }}
      </n-tooltip>
      <n-dropdown :options="languageOptions" @select="onLanguageSelect">
        <n-button quaternary size="small">{{ languageLabel }}</n-button>
      </n-dropdown>
      <n-divider vertical />
      <n-dropdown :options="userOptions" @select="onUserSelect">
        <div class="user">
          <n-avatar round size="small" style="background: linear-gradient(135deg,#4F46E5,#7C3AED); color:#fff;">A</n-avatar>
          <span class="user-name">Admin</span>
        </div>
      </n-dropdown>
    </div>
    <n-modal v-model:show="helpVisible" preset="card" :title="t('header.help')" class="help-modal" :bordered="false">
      <n-spin :show="helpLoading">
        <div class="help-content">
          <VueMarkdownIt v-if="helpContent" :source="helpContent" md-wrapper-class="markdown-body" />
        </div>
      </n-spin>
    </n-modal>
  </header>
</template>

<style scoped>
.mf-header {
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #E5E7EB;
  box-shadow: 0 1px 2px rgba(17,24,39,0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo { display: flex; align-items: center; gap: 10px; }
.logo-mark {
  width: 28px; height: 28px; border-radius: 8px;
  background: #4F46E5; color: #fff; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.logo-text { font-size: 16px; font-weight: 600; color: #111827; }
.right { display: flex; align-items: center; gap: 12px; }
.sys-status { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #374151; font-variant-numeric: tabular-nums; }
.sys-status .dot {
  width: 8px; height: 8px; border-radius: 50%; background: #4F46E5;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(79,70,229,.4); } 50% { box-shadow: 0 0 0 4px rgba(79,70,229,0); } }
.user { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.user-name { font-size: 13px; color: #374151; }
:global(.help-modal) { width: min(1040px, calc(100vw - 48px)); }
.help-content { min-height: 240px; max-height: calc(100vh - 180px); overflow-y: auto; }
.help-content :deep(.markdown-body) { padding: 8px 20px 24px; background: #fff; color: #24292f; }
</style>
