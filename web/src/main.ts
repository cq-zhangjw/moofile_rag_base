import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import axiosInstance from './utils/axios'

import { create } from 'naive-ui'
import {
  NButton, NIcon, NInput, NInputGroup, NInputNumber, NSelect, NTag,
  NDataTable, NPagination, NModal, NDrawer, NDrawerContent, NSpace,
  NSwitch, NSlider, NCheckbox, NCheckboxGroup, NRadio, NRadioGroup, NRadioButton,
  NPopconfirm, NPopover, NTooltip, NProgress, NEmpty, NSpin, NSkeleton,
  NAlert, NDescriptions, NDescriptionsItem, NDivider, NTabs, NTabPane,
  NForm, NFormItem, NUpload, NUploadDragger, NLog, NSteps, NStep,
  NAvatar, NBadge, NDropdown, NScrollbar, NGrid, NGi, NCard,
  NLayout, NLayoutHeader, NLayoutSider, NLayoutContent,
  NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider,
} from 'naive-ui'

const naive = create({
  components: [
    NButton, NIcon, NInput, NInputGroup, NInputNumber, NSelect, NTag,
    NDataTable, NPagination, NModal, NDrawer, NDrawerContent, NSpace,
    NSwitch, NSlider, NCheckbox, NCheckboxGroup, NRadio, NRadioGroup, NRadioButton,
    NPopconfirm, NPopover, NTooltip, NProgress, NEmpty, NSpin, NSkeleton,
    NAlert, NDescriptions, NDescriptionsItem, NDivider, NTabs, NTabPane,
    NForm, NFormItem, NUpload, NUploadDragger, NLog, NSteps, NStep,
    NAvatar, NBadge, NDropdown, NScrollbar, NGrid, NGi, NCard,
    NLayout, NLayoutHeader, NLayoutSider, NLayoutContent,
    NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider,
  ],
})

const app = createApp(App)
app.use(naive)
app.use(router)
app.use(i18n)
app.config.globalProperties.$axios = axiosInstance
app.mount('#app')
