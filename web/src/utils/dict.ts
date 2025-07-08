/**
 * 回顯數據字典
 *
 * @param   Recordable[] datas   數據集
 * @param   String       value   數據值
 * @return  string
 */
export interface DictDetail {
  label: string
  value: string
  disabled?: boolean
  is_default?: boolean
}

// export const selectDictLabel = (datas: DictDetail[], value: string) => {
//   if (!value) {
//     return ''
//   } else {
//     const result = datas.find((item) => item.value === value)?.label
//     if (result === undefined) {
//       return '獲取失敗'
//     } else {
//       return result
//     }
//   }
// }

export const selectDictLabel = (datas: DictDetail[], value: string) => {
  if (!value) {
    return '' // 如果 value 为空，返回空字符串
  } else {
    const result = datas.find((item) => item.value === value)?.label
    return result === undefined ? value : result // 找不到匹配项时返回原始值
  }
}
