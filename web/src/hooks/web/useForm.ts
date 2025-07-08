import type { Form, FormExpose } from '@/components/Form'
import type { ElForm, ElFormItem } from 'element-plus'
import { ref, unref, nextTick } from 'vue'
import { FormSchema, FormSetProps, FormProps } from '@/components/Form'
import { isEmptyVal, isObject } from '@/utils/is'

export const useForm = () => {
  // From實例
  const formRef = ref<typeof Form & FormExpose>()

  // ElForm實例
  const elFormRef = ref<ComponentRef<typeof ElForm>>()

  /**
   * @param ref Form實例
   * @param elRef ElForm實例
   */
  const register = (ref: typeof Form & FormExpose, elRef: ComponentRef<typeof ElForm>) => {
    formRef.value = ref
    elFormRef.value = elRef
  }

  const getForm = async () => {
    await nextTick()
    const form = unref(formRef)
    if (!form) {
      console.error('The form is not registered. Please use the register method to register')
    }
    return form
  }

  // 一些内置的方法
  const methods = {
    /**
     * @description 設置form组件的props
     * @param props form组件的props
     */
    setProps: async (props: FormProps = {}) => {
      const form = await getForm()
      form?.setProps(props)
      if (props.model) {
        form?.setValues(props.model)
      }
    },

    /**
     * @description 設置form的值
     * @param data 需要設置的數據
     */
    setValues: async (data: Recordable) => {
      const form = await getForm()
      form?.setValues(data)
    },

    /**
     * @description 設置formitem的值
     * @param key 需要設置的formitem
     * @param value 需要設置的數據
     */
    setValue: async (key: string, value: any) => {
      const form = await getForm()
      form?.setValue(key, value)
    },

    /**
     * @description 設置schema
     * @param schemaProps 需要設置的schemaProps
     */
    setSchema: async (schemaProps: FormSetProps[]) => {
      const form = await getForm()
      form?.setSchema(schemaProps)
    },

    /**
     * @description 新增schema
     * @param formSchema 需要新增數據
     * @param index 在哪裡新增
     */
    addSchema: async (formSchema: FormSchema, index?: number) => {
      const form = await getForm()
      form?.addSchema(formSchema, index)
    },

    /**
     * @description 删除schema
     * @param field 删除哪个數據
     */
    delSchema: async (field: string) => {
      const form = await getForm()
      form?.delSchema(field)
    },

    /**
     * @description 獲取表單數據
     * @returns form data
     */
    getFormData: async <T = Recordable>(filterEmptyVal = true): Promise<T> => {
      const form = await getForm()
      const model = form?.formModel as any
      if (filterEmptyVal) {
        // 使用reduce過滤空值，並返回一个新對象
        return Object.keys(model).reduce((prev, next) => {
          const value = model[next]
          if (!isEmptyVal(value)) {
            if (isObject(value)) {
              if (Object.keys(value).length > 0) {
                prev[next] = value
              }
            } else {
              prev[next] = value
            }
          }
          return prev
        }, {}) as T
      } else {
        return model as T
      }
    },

    /**
     * @description 獲取表單组件的實例
     * @param field 表單項唯一標識
     * @returns component instance
     */
    getComponentExpose: async (field: string) => {
      const form = await getForm()
      return form?.getComponentExpose(field)
    },

    /**
     * @description 獲取formItem组件的實例
     * @param field 表單項唯一標識
     * @returns formItem instance
     */
    getFormItemExpose: async (field: string) => {
      const form = await getForm()
      return form?.getFormItemExpose(field) as ComponentRef<typeof ElFormItem>
    },

    /**
     * @description 獲取ElForm组件的實例
     * @returns ElForm instance
     */
    getElFormExpose: async () => {
      await getForm()
      return unref(elFormRef)
    },

    getFormExpose: async () => {
      await getForm()
      return unref(formRef)
    }
  }

  return {
    formRegister: register,
    formMethods: methods
  }
}
