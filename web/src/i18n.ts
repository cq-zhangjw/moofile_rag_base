import { createI18n, type I18nOptions } from 'vue-i18n';

type LocaleMessages = Record<string, any>;

const loadLocaleMessages = async (): Promise<LocaleMessages> => {
  const locales = await Promise.all([
    import('../public/locales/en.json'),
    import('../public/locales/zh.json'),
    import('../public/locales/ja.json'),
  ]);
  const messages: LocaleMessages = {};
  const langCodes = ['en', 'zh', 'ja'];
  locales.forEach((locale, index) => {
    messages[langCodes[index]] = locale.default;
  });
  return messages;
};

export type AppLocale = 'zh' | 'ja' | 'en';
export const LOCALE_STORAGE_KEY = 'moofile.locale';

const normalizeLocale = (value?: string | null): AppLocale | null => {
  const language = value?.toLowerCase();
  if (language?.startsWith('zh')) return 'zh';
  if (language?.startsWith('ja')) return 'ja';
  if (language?.startsWith('en')) return 'en';
  return null;
};

const savedLocale = normalizeLocale(localStorage.getItem(LOCALE_STORAGE_KEY));
const browserLocale = navigator.languages
  .map(normalizeLocale)
  .find((locale): locale is AppLocale => locale !== null);
export const initialLocale: AppLocale = savedLocale || browserLocale || 'en';
document.documentElement.lang = initialLocale;

const i18nOptions: I18nOptions = {
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: await loadLocaleMessages()
};

const i18n = createI18n(i18nOptions);
export default i18n;
