import { defineStore } from 'pinia'
import { store } from '../index'
import { setCssVar, humpToUnderline } from '@/utils'
import { ElMessage, ComponentSize } from 'element-plus'
import { colorIsDark, hexToRGB, lighten, mix } from '@/utils/color'
import { useCssVar } from '@vueuse/core'
import { unref } from 'vue'
import { useDark } from '@vueuse/core'

interface AppState {
  breadcrumb: boolean
  breadcrumbIcon: boolean
  collapse: boolean
  uniqueOpened: boolean
  hamburger: boolean
  screenfull: boolean
  size: boolean
  locale: boolean
  tagsView: boolean
  tagsViewIcon: boolean
  logo: boolean
  fixedHeader: boolean
  greyMode: boolean
  dynamicRouter: boolean
  serverDynamicRouter: boolean
  pageLoading: boolean
  layout: LayoutType
  title: string
  isDark: boolean
  currentSize: ComponentSize
  sizeMap: ComponentSize[]
  mobile: boolean
  footer: boolean
  theme: ThemeTypes
  fixedMenu: boolean

  logoImage: string
  footerContent: string
  icpNumber: string
}

export const useAppStore = defineStore('app', {
  state: (): AppState => {
    return {
      sizeMap: ['default', 'large', 'small'],
      mobile: false, // 是否是移動端
      title: import.meta.env.VITE_APP_TITLE, // 標題
      pageLoading: false, // 路由跳轉loading
      breadcrumb: true, // 面包屑
      breadcrumbIcon: true, // 面包屑圖標
      collapse: false, // 折叠選單
      uniqueOpened: true, // 是否只保持一个子選單的展開
      hamburger: true, // 折叠圖標
      screenfull: true, // 全屏圖標
      size: true, // 尺寸圖標
      locale: true, // 多語言圖標
      tagsView: true, // 標籤頁
      tagsViewIcon: true, // 是否顯示標籤圖標
      logo: true, // logo
      fixedHeader: true, // 固定toolheader
      footer: true, // 顯示頁脚
      greyMode: false, // 是否開始灰色模式，用于特殊悼念日
      dynamicRouter: true, // 是否動態路由
      serverDynamicRouter: true, // 是否服務端渲染動態路由
      fixedMenu: false, // 是否固定選單

      layout: 'classic', // layout布局
      isDark: false, // 是否是暗黑模式
      currentSize: 'default', // 组件尺寸
      theme: {
        // 主題色
        elColorPrimary: '#409eff',
        // 左侧選單边框颜色
        leftMenuBorderColor: 'inherit',
        // 左侧選單背景颜色
        leftMenuBgColor: '#001529',
        // 左侧選單浅色背景颜色
        leftMenuBgLightColor: '#0f2438',
        // 左侧選單選中背景颜色
        leftMenuBgActiveColor: 'var(--el-color-primary)',
        // 左侧選單收起選中背景颜色
        leftMenuCollapseBgActiveColor: 'var(--el-color-primary)',
        // 左侧選單字体颜色
        leftMenuTextColor: '#bfcbd9',
        // 左侧選單選中字体颜色
        leftMenuTextActiveColor: '#fff',
        // logo字体颜色
        logoTitleTextColor: '#fff',
        // logo边框颜色
        logoBorderColor: 'inherit',
        // 头部背景颜色
        topHeaderBgColor: '#fff',
        // 头部字体颜色
        topHeaderTextColor: 'inherit',
        // 头部悬停颜色
        topHeaderHoverColor: '#f6f6f6',
        // 头部边框颜色
        topToolBorderColor: '#eee'
      },

      logoImage: '', // logo圖片
      footerContent: '', // 頁脚内容
      icpNumber: '' // 備案號
    }
  },
  getters: {
    getBreadcrumb(): boolean {
      return this.breadcrumb
    },
    getBreadcrumbIcon(): boolean {
      return this.breadcrumbIcon
    },
    getCollapse(): boolean {
      return this.collapse
    },
    getUniqueOpened(): boolean {
      return this.uniqueOpened
    },
    getHamburger(): boolean {
      return this.hamburger
    },
    getScreenfull(): boolean {
      return this.screenfull
    },
    getSize(): boolean {
      return this.size
    },
    getLocale(): boolean {
      return this.locale
    },
    getTagsView(): boolean {
      return this.tagsView
    },
    getTagsViewIcon(): boolean {
      return this.tagsViewIcon
    },
    getLogo(): boolean {
      return this.logo
    },
    getFixedHeader(): boolean {
      return this.fixedHeader
    },
    getGreyMode(): boolean {
      return this.greyMode
    },
    getDynamicRouter(): boolean {
      return this.dynamicRouter
    },
    getServerDynamicRouter(): boolean {
      return this.serverDynamicRouter
    },
    getFixedMenu(): boolean {
      return this.fixedMenu
    },
    getPageLoading(): boolean {
      return this.pageLoading
    },
    getLayout(): LayoutType {
      return this.layout
    },
    getTitle(): string {
      return this.title
    },
    getIsDark(): boolean {
      return this.isDark
    },
    getCurrentSize(): ComponentSize {
      return this.currentSize
    },
    getSizeMap(): ComponentSize[] {
      return this.sizeMap
    },
    getMobile(): boolean {
      return this.mobile
    },
    getTheme(): ThemeTypes {
      return this.theme
    },
    getFooter(): boolean {
      return this.footer
    },

    getLogoImage(): string {
      return this.logoImage
    },
    getFooterContent(): string {
      return this.footerContent
    },
    getIcpNumber(): string {
      return this.icpNumber
    }
  },
  actions: {
    setBreadcrumb(breadcrumb: boolean) {
      this.breadcrumb = breadcrumb
    },
    setBreadcrumbIcon(breadcrumbIcon: boolean) {
      this.breadcrumbIcon = breadcrumbIcon
    },
    setCollapse(collapse: boolean) {
      this.collapse = collapse
    },
    setUniqueOpened(uniqueOpened: boolean) {
      this.uniqueOpened = uniqueOpened
    },
    setHamburger(hamburger: boolean) {
      this.hamburger = hamburger
    },
    setScreenfull(screenfull: boolean) {
      this.screenfull = screenfull
    },
    setSize(size: boolean) {
      this.size = size
    },
    setLocale(locale: boolean) {
      this.locale = locale
    },
    setTagsView(tagsView: boolean) {
      this.tagsView = tagsView
    },
    setTagsViewIcon(tagsViewIcon: boolean) {
      this.tagsViewIcon = tagsViewIcon
    },
    setLogo(logo: boolean) {
      this.logo = logo
    },
    setFixedHeader(fixedHeader: boolean) {
      this.fixedHeader = fixedHeader
    },
    setGreyMode(greyMode: boolean) {
      this.greyMode = greyMode
    },
    setDynamicRouter(dynamicRouter: boolean) {
      this.dynamicRouter = dynamicRouter
    },
    setServerDynamicRouter(serverDynamicRouter: boolean) {
      this.serverDynamicRouter = serverDynamicRouter
    },
    setFixedMenu(fixedMenu: boolean) {
      this.fixedMenu = fixedMenu
    },
    setPageLoading(pageLoading: boolean) {
      this.pageLoading = pageLoading
    },
    setLayout(layout: LayoutType) {
      if (this.mobile && layout !== 'classic') {
        ElMessage.warning('移動端模式下不支持切換其它布局')
        return
      }
      this.layout = layout
    },
    setTitle(title: string) {
      this.title = title
    },
    setIsDark(isDark: boolean) {
      this.isDark = isDark
      if (this.isDark) {
        document.documentElement.classList.add('dark')
        document.documentElement.classList.remove('light')
      } else {
        document.documentElement.classList.add('light')
        document.documentElement.classList.remove('dark')
      }
      this.setPrimaryLight()
    },
    setCurrentSize(currentSize: ComponentSize) {
      this.currentSize = currentSize
    },
    setMobile(mobile: boolean) {
      this.mobile = mobile
    },
    setTheme(theme: ThemeTypes) {
      this.theme = Object.assign(this.theme, theme)
    },
    setCssVarTheme() {
      for (const key in this.theme) {
        setCssVar(`--${humpToUnderline(key)}`, this.theme[key])
      }
      this.setPrimaryLight()
    },
    setFooter(footer: boolean) {
      this.footer = footer
    },

    setLogoImage(logoImage: string) {
      this.logoImage = logoImage
    },
    setFooterContent(footerContent: string) {
      this.footerContent = footerContent
    },
    setIcpNumber(icpNumber: string) {
      this.icpNumber = icpNumber
    },
    setPrimaryLight() {
      if (this.theme.elColorPrimary) {
        const elColorPrimary = this.theme.elColorPrimary
        const color = this.isDark ? '#000000' : '#ffffff'
        const lightList = [3, 5, 7, 8, 9]
        lightList.forEach((v) => {
          setCssVar(`--el-color-primary-light-${v}`, mix(color, elColorPrimary, v / 10))
        })
        setCssVar(`--el-color-primary-dark-2`, mix(color, elColorPrimary, 0.2))
      }
    },
    setMenuTheme(color: string) {
      const primaryColor = useCssVar('--el-color-primary', document.documentElement)
      const isDarkColor = colorIsDark(color)
      const theme: Recordable = {
        // 左侧選單边框颜色
        leftMenuBorderColor: isDarkColor ? 'inherit' : '#eee',
        // 左侧選單背景颜色
        leftMenuBgColor: color,
        // 左侧選單浅色背景颜色
        leftMenuBgLightColor: isDarkColor ? lighten(color!, 6) : color,
        // 左侧選單選中背景颜色
        leftMenuBgActiveColor: isDarkColor
          ? 'var(--el-color-primary)'
          : hexToRGB(unref(primaryColor), 0.1),
        // 左侧選單收起選中背景颜色
        leftMenuCollapseBgActiveColor: isDarkColor
          ? 'var(--el-color-primary)'
          : hexToRGB(unref(primaryColor), 0.1),
        // 左侧選單字体颜色
        leftMenuTextColor: isDarkColor ? '#bfcbd9' : '#333',
        // 左侧選單選中字体颜色
        leftMenuTextActiveColor: isDarkColor ? '#fff' : 'var(--el-color-primary)',
        // logo字体颜色
        logoTitleTextColor: isDarkColor ? '#fff' : 'inherit',
        // logo边框颜色
        logoBorderColor: isDarkColor ? color : '#eee'
      }
      this.setTheme(theme)
      this.setCssVarTheme()
    },
    setHeaderTheme(color: string) {
      const isDarkColor = colorIsDark(color)
      const textColor = isDarkColor ? '#fff' : 'inherit'
      const textHoverColor = isDarkColor ? lighten(color!, 6) : '#f6f6f6'
      const topToolBorderColor = isDarkColor ? color : '#eee'
      setCssVar('--top-header-bg-color', color)
      setCssVar('--top-header-text-color', textColor)
      setCssVar('--top-header-hover-color', textHoverColor)
      this.setTheme({
        topHeaderBgColor: color,
        topHeaderTextColor: textColor,
        topHeaderHoverColor: textHoverColor,
        topToolBorderColor
      })
      if (this.getLayout === 'top') {
        this.setMenuTheme(color)
      }
    },
    initTheme() {
      const isDark = useDark({
        valueDark: 'dark',
        valueLight: 'light'
      })
      isDark.value = this.getIsDark
    }
  },
  persist: true
})

export const useAppStoreWithOut = () => {
  return useAppStore(store)
}
