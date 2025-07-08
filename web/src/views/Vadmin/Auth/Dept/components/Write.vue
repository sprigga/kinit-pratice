<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { propTypes } from '@/utils/propTypes'
import { getDeptTreeOptionsApi } from '@/api/vadmin/auth/dept'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  },
  parentId: propTypes.number.def(undefined)
})

const formSchema = reactive<FormSchema[]>([
  {
    field: 'parent_id',
    label: '上级部門',
    colProps: {
      span: 24
    },
    component: 'TreeSelect',
    componentProps: {
      style: {
        width: '100%'
      },
      checkStrictly: true,
      placeholder: '請選擇上级部門',
      nodeKey: 'value',
      defaultExpandAll: true
    },
    optionApi: async () => {
      const res = await getDeptTreeOptionsApi()
      return res.data
    },
    value: props.parentId
  },
  {
    field: 'name',
    label: '部門名稱',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'dept_key',
    label: '部門標識',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'owner',
    label: '負責人',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'phone',
    label: '聯絡電話',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'email',
    label: '郵箱',
    component: 'Input',
    colProps: {
      span: 12
    }
  },
  {
    field: 'desc',
    label: '描述',
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
    field: 'disabled',
    label: '是否禁用',
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
    value: false
  }
])

const rules = reactive({
  name: [required()],
  dept_key: [required()],
  disabled: [required()],
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
