<script lang="tsx">
import { PropType, defineComponent, ref, computed, unref, watch, onMounted } from 'vue'
import {
  ElForm,
  ElFormItem,
  ElRow,
  ElCol,
  FormRules,
  ComponentSize,
  ElTooltip
  // FormItemProp
} from 'element-plus'
import { componentMap } from './helper/componentMap'
import { propTypes } from '@/utils/propTypes'
import { getSlot } from '@/utils/tsxHelper'
import {
  setTextPlaceholder,
  setGridProp,
  setComponentProps,
  setItemComponentSlots,
  initModel
} from './helper'
import { useRenderSelect } from './components/useRenderSelect'
import { useRenderRadio } from './components/useRenderRadio'
import { useRenderCheckbox } from './components/useRenderCheckbox'
import { useDesign } from '@/hooks/web/useDesign'
import { findIndex } from '@/utils'
import { get, set } from 'lodash-es'
import { FormProps } from './types'
import {
  FormSchema,
  FormSetProps,
  ComponentNameEnum,
  SelectComponentProps,
  RadioGroupComponentProps,
  CheckboxGroupComponentProps
} from './types'
import { Icon } from '@/components/Icon'

const { renderSelectOptions } = useRenderSelect()
const { renderRadioOptions } = useRenderRadio()
const { renderCheckboxOptions } = useRenderCheckbox()

const { getPrefixCls } = useDesign()

const prefixCls = getPrefixCls('form')

export default defineComponent({
  name: 'Form',
  props: {
    // 生成Form的布局结构數组
    schema: {
      type: Array as PropType<FormSchema[]>,
      default: () => []
    },
    // 是否需要栅格布局
    isCol: propTypes.bool.def(true),
    // 表單數據對象
    model: {
      type: Object as PropType<any>,
      default: () => ({})
    },
    // 是否自動設置placeholder
    autoSetPlaceholder: propTypes.bool.def(true),
    // 是否自定義内容
    isCustom: propTypes.bool.def(false),
    // 表單label宽度
    labelWidth: propTypes.oneOfType([String, Number]).def('auto'),
    rules: {
      type: Object as PropType<FormRules>,
      default: () => ({})
    },
    labelPosition: propTypes.oneOf(['left', 'right', 'top']).def('right'),
    labelSuffix: propTypes.string.def(''),
    hideRequiredAsterisk: propTypes.bool.def(false),
    requireAsteriskPosition: propTypes.oneOf(['left', 'right']).def('left'),
    showMessage: propTypes.bool.def(true),
    inlineMessage: propTypes.bool.def(false),
    statusIcon: propTypes.bool.def(false),
    validateOnRuleChange: propTypes.bool.def(true),
    size: {
      type: String as PropType<ComponentSize>,
      default: undefined
    },
    disabled: propTypes.bool.def(false),
    scrollToError: propTypes.bool.def(false),
    scrollToErrorOffset: propTypes.oneOfType([Boolean, Object]).def(undefined)
    // onValidate: {
    //   type: Function as PropType<(prop: FormItemProp, isValid: boolean, message: string) => void>,
    //   default: () => {}
    // }
  },
  emits: ['register'],
  setup(props, { slots, expose, emit }) {
    // element form 實例
    const elFormRef = ref<ComponentRef<typeof ElForm>>()

    const mergeProps = ref<FormProps>({})

    const getProps = computed(() => {
      const propsObj = { ...props }
      Object.assign(propsObj, unref(mergeProps))
      return propsObj
    })

    // 存储表單實例
    const formComponents = ref({})

    // 存储form-item實例
    const formItemComponents = ref({})

    // 表單數據
    const formModel = ref<Recordable>(props.model)

    // 加載表單 optionApi
    const renderFormItemOptions = () => {
      const { schema = [] } = unref(getProps)

      schema
        .filter((v) => {
          if (v.remove === true) {
            return false
          } else if (v.hidden === true) {
            return false
          } else if (v.optionApi) {
            return true
          }
          return false
        })
        .forEach((item) => {
          if (item.optionApi) {
            // 内部自動調用接口，不影響其它渲染
            getOptions(item.optionApi, item)
          }
        })
    }

    onMounted(() => {
      renderFormItemOptions()
      emit('register', unref(elFormRef)?.$parent, unref(elFormRef))
    })

    // 對表單赋值
    const setValues = (data: Recordable = {}) => {
      formModel.value = Object.assign(unref(formModel), data)
    }

    // 對表單項赋值
    const setValue = (key: string, value: any) => {
      formModel.value[key] = value
    }

    const setProps = (props: FormProps = {}) => {
      mergeProps.value = Object.assign(unref(mergeProps), props)
    }

    const delSchema = (field: string) => {
      const { schema } = unref(getProps)

      const index = findIndex(schema, (v: FormSchema) => v.field === field)
      if (index > -1) {
        schema.splice(index, 1)
      }
    }

    const addSchema = (formSchema: FormSchema, index?: number) => {
      const { schema } = unref(getProps)
      if (index !== void 0) {
        schema.splice(index, 0, formSchema)
        return
      }
      schema.push(formSchema)
    }

    const setSchema = (schemaProps: FormSetProps[]) => {
      const { schema } = unref(getProps)
      for (const v of schema) {
        for (const item of schemaProps) {
          if (v.field === item.field) {
            set(v, item.path, item.value)
          }
        }
      }
    }

    const getOptions = async (fn: Function, item: FormSchema) => {
      const options = await fn()
      setSchema([
        {
          field: item.field,
          path:
            item.component === ComponentNameEnum.TREE_SELECT
              ? 'componentProps.data'
              : 'componentProps.options',
          value: options
        }
      ])
    }

    /**
     * @description: 獲取表單组件實例
     * @param filed 表單字段
     */
    const getComponentExpose = (filed: string) => {
      return unref(formComponents)[filed]
    }

    /**
     * @description: 獲取formItem實例
     * @param filed 表單字段
     */
    const getFormItemExpose = (filed: string) => {
      return unref(formItemComponents)[filed]
    }

    const setComponentRefMap = (ref: any, filed: string) => {
      formComponents.value[filed] = ref
    }

    const setFormItemRefMap = (ref: any, filed: string) => {
      formItemComponents.value[filed] = ref
    }

    expose({
      setValues,
      setValue,
      formModel,
      setProps,
      delSchema,
      addSchema,
      setSchema,
      getComponentExpose,
      getFormItemExpose
    })

    // 监听表單结构化數组，重新生成formModel
    watch(
      () => unref(getProps).schema,
      (schema = []) => {
        formModel.value = initModel(schema, unref(formModel))
      },
      {
        immediate: true,
        deep: true
      }
    )

    // 渲染包裹標籤，是否使用栅格布局
    const renderWrap = () => {
      const { isCol } = unref(getProps)
      const content = isCol ? (
        <ElRow gutter={20}>{renderFormItemWrap()}</ElRow>
      ) : (
        renderFormItemWrap()
      )
      return content
    }

    // 是否要渲染el-col
    const renderFormItemWrap = () => {
      // hidden 屬性表示隱藏，不做渲染
      const { schema = [], isCol } = unref(getProps)

      return schema
        .filter((v) => {
          if (v.remove === true) {
            return false
          } else if (v.hidden === true) {
            return false
          } else if (v.ifshow) {
            return v.ifshow(formModel.value)
          }
          return true
        })
        .map((item) => {
          // 如果是 Divider 组件，需要自己占用一行
          const isDivider = item.component === 'Divider'
          const Com = componentMap['Divider'] as ReturnType<typeof defineComponent>
          return isDivider ? (
            <Com {...{ contentPosition: 'left', ...item.componentProps }}>{item?.label}</Com>
          ) : isCol ? (
            // 如果需要栅格，需要包裹 ElCol
            <ElCol {...setGridProp(item.colProps)}>{renderFormItem(item)}</ElCol>
          ) : (
            renderFormItem(item)
          )
        })
    }

    // 渲染formItem
    const renderFormItem = (item: FormSchema) => {
      const formItemSlots: Recordable = {
        default: () => {
          if (item?.formItemProps?.slots?.default) {
            return item?.formItemProps?.slots?.default(formModel.value)
          } else {
            const Com = componentMap[item.component as string] as ReturnType<typeof defineComponent>

            const { autoSetPlaceholder } = unref(getProps)

            const componentSlots = (item?.componentProps as any)?.slots || {}
            const slotsMap: Recordable = {
              ...setItemComponentSlots(componentSlots)
            }
            // // 如果是select组件，並且没有自定義模板，自動渲染options
            if (item.component === ComponentNameEnum.SELECT) {
              slotsMap.default = !componentSlots.default
                ? () => renderSelectOptions(item)
                : () => {
                    return componentSlots.default(
                      unref((item?.componentProps as SelectComponentProps)?.options)
                    )
                  }
            }

            // 虚拟列表
            if (item.component === ComponentNameEnum.SELECT_V2 && componentSlots.default) {
              slotsMap.default = ({ item }) => {
                return componentSlots.default(item)
              }
            }

            // 單選框组和按钮樣式
            if (
              item.component === ComponentNameEnum.RADIO_GROUP ||
              item.component === ComponentNameEnum.RADIO_BUTTON
            ) {
              slotsMap.default = !componentSlots.default
                ? () => renderRadioOptions(item)
                : () => {
                    return componentSlots.default(
                      unref((item?.componentProps as CheckboxGroupComponentProps)?.options)
                    )
                  }
            }

            // 多選框组和按钮樣式
            if (
              item.component === ComponentNameEnum.CHECKBOX_GROUP ||
              item.component === ComponentNameEnum.CHECKBOX_BUTTON
            ) {
              slotsMap.default = !componentSlots.default
                ? () => renderCheckboxOptions(item)
                : () => {
                    return componentSlots.default(
                      unref((item?.componentProps as RadioGroupComponentProps)?.options)
                    )
                  }
            }

            const Comp = () => {
              // 如果field是多層路徑，需要轉換成對象
              const itemVal = computed({
                get: () => {
                  return get(formModel.value, item.field)
                },
                set: (val) => {
                  set(formModel.value, item.field, val)
                }
              })

              return item.component === ComponentNameEnum.UPLOAD ? (
                <Com
                  vModel:file-list={itemVal.value}
                  ref={(el: any) => setComponentRefMap(el, item.field)}
                  {...(autoSetPlaceholder && setTextPlaceholder(item))}
                  {...setComponentProps(item)}
                  style={
                    item.componentProps?.style || {
                      width: '100%'
                    }
                  }
                >
                  {{ ...slotsMap }}
                </Com>
              ) : (
                <Com
                  vModel={itemVal.value}
                  ref={(el: any) => setComponentRefMap(el, item.field)}
                  {...(autoSetPlaceholder && setTextPlaceholder(item))}
                  {...setComponentProps(item)}
                  style={
                    item.componentProps?.style || {
                      width: '100%'
                    }
                  }
                >
                  {{ ...slotsMap }}
                </Com>
              )
            }

            return <>{Comp()}</>
          }
        }
      }

      // 如果有 labelMessage，自動使用插槽渲染
      if (item?.labelMessage) {
        formItemSlots.label = () => {
          return (
            <>
              <span>{item.label}</span>
              <ElTooltip placement="top" raw-content>
                {{
                  content: () => <span v-html={item.labelMessage}></span>,
                  default: () => (
                    <Icon
                      icon="ep:warning"
                      size={16}
                      color="var(--el-color-primary)"
                      class="ml-2px relative top-1px"
                    ></Icon>
                  )
                }}
              </ElTooltip>
            </>
          )
        }
      }
      if (item?.formItemProps?.slots?.label) {
        formItemSlots.label = (...args: any[]) => {
          return (item?.formItemProps?.slots as any)?.label(...args)
        }
      }
      if (item?.formItemProps?.slots?.error) {
        formItemSlots.error = (...args: any[]) => {
          return (item?.formItemProps?.slots as any)?.error(...args)
        }
      }

      return (
        <ElFormItem
          ref={(el: any) => setFormItemRefMap(el, item.field)}
          {...(item.formItemProps || {})}
          prop={item.field}
          label={item.label || ''}
        >
          {formItemSlots}
        </ElFormItem>
      )
    }

    // 過滤传入Form组件的屬性
    const getFormBindValue = () => {
      // 避免在標籤上出现多余的屬性
      const delKeys = ['schema', 'isCol', 'autoSetPlaceholder', 'isCustom', 'model']
      const props = { ...unref(getProps) }
      for (const key in props) {
        if (delKeys.indexOf(key) !== -1) {
          delete props[key]
        }
      }
      return props as FormProps
    }

    return () => (
      <ElForm
        ref={elFormRef}
        {...getFormBindValue()}
        model={unref(getProps).isCustom ? unref(getProps).model : formModel}
        class={prefixCls}
        // @ts-ignore
        onSubmit={(e: Event) => {
          e.preventDefault()
        }}
      >
        {{
          // 如果需要自定義，就什么都不渲染，而是提供默認插槽
          default: () => {
            const { isCustom } = unref(getProps)
            return isCustom ? getSlot(slots, 'default') : renderWrap()
          }
        }}
      </ElForm>
    )
  }
})
</script>

<style lang="less" scoped>
.@{elNamespace}-form.@{namespace}-form .@{elNamespace}-row {
  margin-right: 0 !important;
  margin-left: 0 !important;
}

.@{elNamespace}-form--inline {
  :deep(.el-form-item__content) {
    & > :first-child {
      min-width: 229.5px;
    }
  }
  .@{elNamespace}-input-number {
    // 229.5px是兼容el-input-number的最小宽度,
    min-width: 229.5px;
  }
}
</style>
