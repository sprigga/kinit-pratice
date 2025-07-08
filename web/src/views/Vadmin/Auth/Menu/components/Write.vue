<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { propTypes } from '@/utils/propTypes'
import { getMenuTreeOptionsApi } from '@/api/vadmin/auth/menu'
import { IconPicker } from '@/components/IconPicker'
import { BaseButton } from '@/components/Button'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  },
  parentId: propTypes.number.def(undefined)
})

const toIconify = () => {
  window.open('https://iconify.design/')
}

const formSchema = reactive<FormSchema[]>([
  {
    field: 'parent_id',
    label: '上级選單',
    colProps: {
      span: 24
    },
    component: 'TreeSelect',
    componentProps: {
      style: {
        width: '100%'
      },
      checkStrictly: true,
      placeholder: '請選擇上级選單',
      nodeKey: 'value',
      defaultExpandAll: true
    },
    optionApi: async () => {
      const res = await getMenuTreeOptionsApi()
      return res.data
    },
    value: props.parentId
  },
  {
    field: 'menu_type',
    label: '選單類型',
    colProps: {
      span: 24
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '目錄',
          value: '0'
        },
        {
          label: '選單',
          value: '1'
        },
        {
          label: '按钮',
          value: '2'
        }
      ]
    },
    value: '0'
  },
  {
    field: 'icon',
    label: '選單圖標',
    colProps: {
      span: 24
    },
    component: 'Input',
    formItemProps: {
      slots: {
        default: (data) => {
          return (
            <>
              <div style="display: flex; justify-content: space-between">
                <IconPicker style="width: 435px" input-disabled={false} v-model={data['icon']} />
                <div style="margin-left: 10px">
                  <BaseButton type="primary" onClick={toIconify}>
                    Iconify
                  </BaseButton>
                </div>
              </div>
            </>
          )
        }
      }
    },
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'title',
    label: '選單名稱',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'order',
    label: '顯示排序',
    component: 'InputNumber',
    colProps: {
      span: 12
    },
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'path',
    label: '路由地址',
    component: 'Input',
    colProps: {
      span: 12
    },
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'component',
    label: '组件路徑',
    component: 'Input',
    colProps: {
      span: 12
    },
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'redirect',
    label: '重定向',
    component: 'Input',
    colProps: {
      span: 12
    },
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'hidden',
    label: '顯示狀態',
    colProps: {
      span: 12
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '顯示',
          value: false
        },
        {
          label: '隱藏',
          value: true
        }
      ]
    },
    value: false,
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'disabled',
    label: '選單狀態',
    colProps: {
      span: 12
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '正常',
          value: false
        },
        {
          label: '停用',
          value: true
        }
      ]
    },
    value: false,
    ifshow: (formModel) => formModel.menu_type !== '2'
  },
  {
    field: 'perms',
    label: '權限標識',
    component: 'Input',
    colProps: {
      span: 12
    },
    ifshow: (formModel) => formModel.menu_type === '2'
  },
  {
    field: 'noCache',
    label: '頁面緩存',
    colProps: {
      span: 12
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '緩存',
          value: false
        },
        {
          label: '不緩存',
          value: true
        }
      ]
    },
    value: false,
    ifshow: (formModel) => formModel.menu_type === '1',
    labelMessage: '開啟頁面緩存,需要组件名稱必須與xx.vue頁面的name一致'
  }
])

const rules = reactive({
  title: [required()],
  menu_type: [required()],
  disabled: [required()],
  hidden: [required()],
  path: [required()],
  noCache: [required()],
  order: [required()]
})

const { formRegister, formMethods } = useForm()
const { setValues, getFormData, getElFormExpose } = formMethods

const submit = async () => {
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate()
  if (valid) {
    const formData = await getFormData()
    return formData
  }
}

watch(
  () => props.currentRow,
  (currentRow) => {
    if (!currentRow) return
    setValues(currentRow)
  },
  {
    deep: true,
    immediate: true
  }
)

defineExpose({
  submit
})
</script>

<template>
  <Form :rules="rules" @register="formRegister" :schema="formSchema" :labelWidth="100" />
</template>
