import 'vue/jsx'

// 引入windi css
import '@/plugins/unocss'

// 導入全局的svg圖標
import '@/plugins/svgIcon'

// 初始化多語言
import { setupI18n } from '@/plugins/vueI18n'

// 引入狀態管理
import { setupStore } from '@/store'

// 全局组件
import { setupGlobCom } from '@/components'

// 引入element-plus
import { setupElementPlus } from '@/plugins/elementPlus'

// 引入全局樣式
import '@/styles/index.less'

// 引入動畫
import '@/plugins/animate.css'

// 路由
import { setupRouter } from './router'

// 權限
import { setupPermission } from './directives'

import { createApp } from 'vue'

import App from './App.vue'

import './permission'

// 創建實例
const setupAll = async () => {
  const app = createApp(App)

  await setupI18n(app)

  setupStore(app)

  setupGlobCom(app)

  setupElementPlus(app)

  setupRouter(app)

  setupPermission(app)

  app.mount('#app')
}

setupAll()
