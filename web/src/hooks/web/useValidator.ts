import { useI18n } from '@/hooks/web/useI18n'
import { isEmpty, isNullOrUnDef } from '@/utils/is'
import { FormItemRule } from 'element-plus'

const { t } = useI18n()

type Callback = (error?: string | Error | undefined) => void

interface LengthRange {
  min: number
  max: number
  message?: string
}

export const useValidator = () => {
  const required = (message?: string): FormItemRule => {
    return {
      required: true,
      message: message || t('common.required')
    }
  }

  const lengthRange = (options: LengthRange): FormItemRule => {
    const { min, max, message } = options

    return {
      min,
      max,
      message: message || t('common.lengthRange', { min, max })
    }
  }

  const notSpace = (message?: string): FormItemRule => {
    return {
      validator: (_, val, callback) => {
        if (val?.indexOf(' ') !== -1) {
          callback(new Error(message || t('common.notSpace')))
        } else {
          callback()
        }
      }
    }
  }

  const notSpecialCharacters = (message?: string): FormItemRule => {
    return {
      validator: (_, val, callback) => {
        if (/[`~!@#$%^&*()_+<>?:"{},.\/;'[\]]/gi.test(val)) {
          callback(new Error(message || t('common.notSpecialCharacters')))
        } else {
          callback()
        }
      }
    }
  }

  const isEmail = (rule: any, val: any, callback: Callback) => {
    if (isEmpty(val) || isNullOrUnDef(val)) {
      callback()
    }
    // 判断是否為郵箱地址
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
      callback()
    } else {
      callback(new Error('請填寫正確的郵箱地址'))
    }
  }

  const isTelephone = (rule: any, val: any, callback: Callback) => {
    if (isEmpty(val) || isNullOrUnDef(val)) {
      callback()
    }
    // 判断是否為大于六碼英文或數字混合
    if (/^[a-zA-Z0-9]{3,}$/.test(val)) {
      callback() // 如果匹配成功，調用回調函數，表示驗證通過
    } else {
      callback(new Error('請輸入大于三碼英文或數字混合')) // 如果匹配失敗，調用回調函數，返回错误信息
    }
  }

  const isAmount = (rule: any, val: any, callback: Callback) => {
    if (isEmpty(val) || isNullOrUnDef(val)) {
      callback()
    }
    // 判断是否為正確金額
    if (/^\d+(\.\d{1,2})?$/.test(val)) {
      callback()
    } else {
      callback(new Error('請填寫正確的金額格式'))
    }
  }

  return {
    required,
    lengthRange,
    notSpace,
    notSpecialCharacters,
    isEmail,
    isTelephone,
    isAmount
  }
}
