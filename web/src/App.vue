<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { themeOverrides } from './styles/theme'
import { enUS, dateEnUS, jaJP, dateJaJP, zhCN, dateZhCN } from 'naive-ui'

const { locale } = useI18n()
const naiveLocale = computed(() => ({ zh: zhCN, ja: jaJP, en: enUS }[locale.value] || enUS))
const naiveDateLocale = computed(() => ({ zh: dateZhCN, ja: dateJaJP, en: dateEnUS }[locale.value] || dateEnUS))
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="naiveLocale" :date-locale="naiveDateLocale">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
#app {
  min-width: 1024px;
  height: 100vh;
}
</style>
