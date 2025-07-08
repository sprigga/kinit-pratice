import { defineStore } from 'pinia'
import { store } from '../index'
import zhCn from 'element-plus/es/locale/lang/zh-Cn'
import zhTw from 'element-plus/es/locale/lang/zh-TW'
import en from 'element-plus/es/locale/lang/en'
import { useStorage } from '@/hooks/web/useStorage'
import { LocaleDropdownType } from '@/components/LocaleDropdown'

const { getStorage, setStorage } = useStorage('localStorage')

const elLocaleMap = {
  'zh-TW': zhTw,
  'zh-CN': zhCn,
  en: en
}
interface LocaleState {
  currentLocale: LocaleDropdownType
  localeMap: LocaleDropdownType[]
}

export const useLocaleStore = defineStore('locales', {
  state: (): LocaleState => {
    return {
      currentLocale: {
        lang: getStorage('lang') || 'zh-TW',
        elLocale: elLocaleMap[getStorage('lang') || 'zh-TW']
      },
      // 多語言
      localeMap: [
        {
          lang: 'zh-TW',
          name: '繁體中文'
        },
        {
          lang: 'zh-CN',
          name: '简体中文'
        },
        {
          lang: 'en',
          name: 'English'
        }
      ]
    }
  },
  getters: {
    getCurrentLocale(): LocaleDropdownType {
      return this.currentLocale
    },
    getLocaleMap(): LocaleDropdownType[] {
      return this.localeMap
    }
  },
  actions: {
    setCurrentLocale(localeMap: LocaleDropdownType) {
      // this.locale = Object.assign(this.locale, localeMap)
      this.currentLocale.lang = localeMap?.lang
      this.currentLocale.elLocale = elLocaleMap[localeMap?.lang]
      setStorage('lang', localeMap?.lang)
    }
  },
  persist: true
})

export const useLocaleStoreWithOut = () => {
  return useLocaleStore(store)
}
