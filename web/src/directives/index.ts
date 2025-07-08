import type { App } from 'vue'
import { setupPermissionDirective } from './permission/hasPermi'

/**
 * 導出指令：v-xxx
 * @methods hasPermi 按钮權限，用法: v-hasPermi
 */
export const setupPermission = (app: App<Element>) => {
  setupPermissionDirective(app)
}
