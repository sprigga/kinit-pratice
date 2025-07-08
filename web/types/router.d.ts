import type { RouteRecordRaw } from 'vue-router'
import { defineComponent } from 'vue'

/**
* redirect: noredirect        當設置 noredirect 的時候该路由在面包屑導航中不可被點擊
* name:'router-name'          設定路由的名字，一定要填寫不然使用<keep-alive>時會出现各种問題
* meta : {
    hidden: true              當設置 true 的時候该路由不會再侧边欄出现 如404，login等頁面(默認 false)

    alwaysShow: true          當你一个路由下面的 children 声明的路由大于1个時，自動會变成嵌套的模式，
                              只有一个時，會將那个子路由當做根路由顯示在侧边欄，
                              若你想不管路由下面的 children 声明的个數都顯示你的根路由，
                              你可以設置 alwaysShow: true，這樣它就會忽略之前定義的规则，
                              一直顯示根路由(默認 false)

    title: 'title'            設置该路由在侧边欄和面包屑中展示的名字

    icon: 'svg-name'          設置该路由的圖標

    noCache: true             如果設置為true，则不會被 <keep-alive> 緩存(默認 false)

    breadcrumb: false         如果設置為false，则不會在breadcrumb面包屑中顯示(默認 true)

    affix: true               如果設置為true，则會一直固定在tag項中(默認 false)

    noTagsView: true          如果設置為true，则不會出现在tag中(默認 false)

    activeMenu: '/dashboard'  顯示高亮的路由路徑

    canTo: true               設置為true即使hidden為true，也依然可以進行路由跳轉(默認 false)

    permission: ['edit','add', 'delete']    設置该路由的權限
  }
**/

interface RouteMetaCustom extends Record<string | number | symbol, unknown> {
  hidden?: boolean
  alwaysShow?: boolean
  title?: string
  icon?: string
  noCache?: boolean
  breadcrumb?: boolean
  affix?: boolean
  activeMenu?: string
  noTagsView?: boolean
  canTo?: boolean
  permission?: string[]
}

declare module 'vue-router' {
  interface RouteMeta extends RouteMetaCustom {}
}

type Component<T = any> =
  | ReturnType<typeof defineComponent>
  | (() => Promise<typeof import('*.vue')>)
  | (() => Promise<T>)

declare global {
  declare interface AppRouteRecordRaw extends Omit<RouteRecordRaw, 'meta' | 'children'> {
    name: string
    meta: RouteMetaCustom
    component?: Component | string
    children?: AppRouteRecordRaw[]
    props?: Recordable
    fullPath?: string
  }

  declare interface AppCustomRouteRecordRaw
    extends Omit<RouteRecordRaw, 'meta' | 'component' | 'children'> {
    name: string
    meta: RouteMetaCustom
    component: string
    path: string
    redirect: string
    children?: AppCustomRouteRecordRaw[]
  }
}
