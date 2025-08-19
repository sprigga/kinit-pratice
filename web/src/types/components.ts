// 組件類型定義
import { ComponentInternalInstance } from 'vue'

export interface ComponentProps {
  [key: string]: any
}

export interface ComponentRef {
  $: ComponentInternalInstance
}

export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any) => string
}

export interface FormItem {
  prop: string
  label: string
  type?: string
  required?: boolean
  rules?: any[]
  options?: any[]
}

export interface SearchFormData {
  [key: string]: any
}

export interface WriteFormData {
  [key: string]: any
}
