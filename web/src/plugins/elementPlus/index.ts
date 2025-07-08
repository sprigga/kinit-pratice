import type { App } from 'vue'

// 需要全局引入一些组件，如ElScrollbar，不然一些下拉項樣式有問題
import { ElLoading, ElScrollbar } from 'element-plus'

const plugins = [ElLoading]

const components = [ElScrollbar]

export const setupElementPlus = (app: App<Element>) => {
  plugins.forEach((plugin) => {
    app.use(plugin)
  })

  // 為了開發環境啟動更快，一次性引入所有樣式
  if (import.meta.env.VITE_USE_ALL_ELEMENT_PLUS_STYLE === 'true') {
    import('element-plus/dist/index.css')
    return
  }

  components.forEach((component) => {
    app.component(component.name!, component)
  })
}
