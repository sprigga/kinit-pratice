<script setup lang="ts">
import { ElDrawer, ElDivider, ElMessage } from 'element-plus'
import { ref, unref } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import { ThemeSwitch } from '@/components/ThemeSwitch'
import { useCssVar } from '@vueuse/core'
import { useAppStore } from '@/store/modules/app'
import { trim, setCssVar, getCssVar } from '@/utils'
import ColorRadioPicker from './components/ColorRadioPicker.vue'
import InterfaceDisplay from './components/InterfaceDisplay.vue'
import LayoutRadioPicker from './components/LayoutRadioPicker.vue'
import { useStorage } from '@/hooks/web/useStorage'
import { useClipboard } from '@vueuse/core'
import { useDesign } from '@/hooks/web/useDesign'

const { clear: storageClear } = useStorage('localStorage')

const { getPrefixCls } = useDesign()

const prefixCls = getPrefixCls('setting')

const appStore = useAppStore()

const { t } = useI18n()

const drawer = ref(false)

// 主題色相关
const systemTheme = ref(appStore.getTheme.elColorPrimary)

const setSystemTheme = (color: string) => {
  setCssVar('--el-color-primary', color)
  appStore.setTheme({ elColorPrimary: color })
  const leftMenuBgColor = useCssVar('--left-menu-bg-color', document.documentElement)
  setMenuTheme(trim(unref(leftMenuBgColor)))
}

// 头部主題相关
const headerTheme = ref(appStore.getTheme.topHeaderBgColor || '')

const setHeaderTheme = (color: string) => {
  appStore.setHeaderTheme(color)
}

// 選單主題相关
const menuTheme = ref(appStore.getTheme.leftMenuBgColor || '')

const setMenuTheme = (color: string) => {
  appStore.setMenuTheme(color)
}

// watch(
//   () => layout.value,
//   (n) => {
//     if (n === 'top' && !appStore.getIsDark) {
//       headerTheme.value = '#fff'
//       setHeaderTheme('#fff')
//     } else {
//       setMenuTheme(unref(menuTheme))
//     }
//   }
// )

// 拷贝
const copyConfig = async () => {
  const { copy, copied, isSupported } = useClipboard({
    source: `
      // 面包屑
      breadcrumb: ${appStore.getBreadcrumb},
      // 面包屑圖標
      breadcrumbIcon: ${appStore.getBreadcrumbIcon},
      // 折叠圖標
      hamburger: ${appStore.getHamburger},
      // 全屏圖標
      screenfull: ${appStore.getScreenfull},
      // 尺寸圖標
      size: ${appStore.getSize},
      // 多語言圖標
      locale: ${appStore.getLocale},
      // 標籤頁
      tagsView: ${appStore.getTagsView},
      // 標籤頁圖標
      getTagsViewIcon: ${appStore.getTagsViewIcon},
      // logo
      logo: ${appStore.getLogo},
      // 選單手風琴
      uniqueOpened: ${appStore.getUniqueOpened},
      // 固定header
      fixedHeader: ${appStore.getFixedHeader},
      // 頁脚
      footer: ${appStore.getFooter},
      // 灰色模式
      greyMode: ${appStore.getGreyMode},
      // layout布局
      layout: '${appStore.getLayout}',
      // 暗黑模式
      isDark: ${appStore.getIsDark},
      // 组件尺寸
      currentSize: '${appStore.getCurrentSize}',
      // 主題相关
      theme: {
        // 主題色
        elColorPrimary: '${appStore.getTheme.elColorPrimary}',
        // 左侧選單边框颜色
        leftMenuBorderColor: '${appStore.getTheme.leftMenuBorderColor}',
        // 左侧選單背景颜色
        leftMenuBgColor: '${appStore.getTheme.leftMenuBgColor}',
        // 左侧選單浅色背景颜色
        leftMenuBgLightColor: '${appStore.getTheme.leftMenuBgLightColor}',
        // 左侧選單選中背景颜色
        leftMenuBgActiveColor: '${appStore.getTheme.leftMenuBgActiveColor}',
        // 左侧選單收起選中背景颜色
        leftMenuCollapseBgActiveColor: '${appStore.getTheme.leftMenuCollapseBgActiveColor}',
        // 左侧選單字体颜色
        leftMenuTextColor: '${appStore.getTheme.leftMenuTextColor}',
        // 左侧選單選中字体颜色
        leftMenuTextActiveColor: '${appStore.getTheme.leftMenuTextActiveColor}',
        // logo字体颜色
        logoTitleTextColor: '${appStore.getTheme.logoTitleTextColor}',
        // logo边框颜色
        logoBorderColor: '${appStore.getTheme.logoBorderColor}',
        // 头部背景颜色
        topHeaderBgColor: '${appStore.getTheme.topHeaderBgColor}',
        // 头部字体颜色
        topHeaderTextColor: '${appStore.getTheme.topHeaderTextColor}',
        // 头部悬停颜色
        topHeaderHoverColor: '${appStore.getTheme.topHeaderHoverColor}',
        // 头部边框颜色
        topToolBorderColor: '${appStore.getTheme.topToolBorderColor}'
      }
    `,
    legacy: true
  })
  if (!isSupported) {
    ElMessage.error(t('setting.copyFailed'))
  } else {
    await copy()
    if (unref(copied)) {
      ElMessage.success(t('setting.copySuccess'))
    }
  }
}

// 清空緩存
const clear = () => {
  storageClear()
  window.location.reload()
}

const themeChange = () => {
  const color = getCssVar('--el-bg-color')
  setMenuTheme(color)
  setHeaderTheme(color)
}
</script>

<template>
  <div
    :class="prefixCls"
    class="fixed top-[45%] right-0 w-40px h-40px flex items-center justify-center bg-[var(--el-color-primary)] cursor-pointer z-10"
    @click="drawer = true"
  >
    <Icon icon="ant-design:setting-outlined" color="#fff" />
  </div>

  <ElDrawer v-model="drawer" direction="rtl" size="350px" :z-index="4000">
    <template #header>
      <span class="text-16px font-700">{{ t('setting.projectSetting') }}</span>
    </template>

    <div class="text-center">
      <!-- 主題 -->
      <ElDivider>{{ t('setting.theme') }}</ElDivider>
      <ThemeSwitch @change="themeChange" />

      <!-- 布局 -->
      <ElDivider>{{ t('setting.layout') }}</ElDivider>
      <LayoutRadioPicker />

      <!-- 系统主題 -->
      <ElDivider>{{ t('setting.systemTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="systemTheme"
        :schema="[
          '#409eff',
          '#009688',
          '#536dfe',
          '#ff5c93',
          '#ee4f12',
          '#0096c7',
          '#9c27b0',
          '#ff9800'
        ]"
        @change="setSystemTheme"
      />

      <!-- 头部主題 -->
      <ElDivider>{{ t('setting.headerTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="headerTheme"
        :schema="[
          '#fff',
          '#151515',
          '#5172dc',
          '#e74c3c',
          '#24292e',
          '#394664',
          '#009688',
          '#383f45'
        ]"
        @change="setHeaderTheme"
      />

      <!-- 選單主題 -->
      <ElDivider>{{ t('setting.menuTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="menuTheme"
        :schema="[
          '#fff',
          '#001529',
          '#212121',
          '#273352',
          '#191b24',
          '#383f45',
          '#001628',
          '#344058'
        ]"
        @change="setMenuTheme"
      />
    </div>

    <!-- 界面顯示 -->
    <ElDivider>{{ t('setting.interfaceDisplay') }}</ElDivider>
    <InterfaceDisplay />

    <ElDivider />
    <div>
      <BaseButton type="primary" class="w-full" @click="copyConfig">{{
        t('setting.copy')
      }}</BaseButton>
    </div>
    <div class="mt-5px">
      <BaseButton type="danger" class="w-full" @click="clear">
        {{ t('setting.clearAndReset') }}
      </BaseButton>
    </div>
  </ElDrawer>
</template>

<style lang="less" scoped>
@prefix-cls: ~'@{namespace}-setting';

.@{prefix-cls} {
  border-radius: 6px 0 0 6px;
}
</style>
