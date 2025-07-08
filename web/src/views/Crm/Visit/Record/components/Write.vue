<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { useDictStore } from '@/store/modules/dict'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  }
})

const formSchema = reactive<FormSchema[]>([
  {
    field: 'visit_period',
    label: '拜訪時段',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'name',
    label: '業務姓名',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'customer_type',
    label: '拜訪店類型',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'customer_name',
    label: '客戶名稱／交談對象',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      clearable: true,
      options: []
    }
  },
  {
    field: 'resolved_date',
    label: '結案時間',
    component: 'DatePicker',
    colProps: {
      span: 12
    },
    componentProps: {
      style: {
        width: '100%'
      },
      type: 'date',
      format: 'YYYY-MM-DD',
      valueFormat: 'YYYY-MM-DD'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'purpose',
    label: '拜訪目的',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'content',
    label: '拜訪內容／業界動態',
    colProps: {
      span: 24
    },
    component: 'Input', // 使用 Input
    componentProps: {
      type: 'textarea', // 關鍵在這
      rows: 4, // 顯示高度
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'issue_type',
    label: '問題類型',
    colProps: {
      span: 12
    },
    component: 'Select',
    componentProps: {
      style: {
        width: '100%'
      }
    },
    optionApi: async () => {
      const dictStore = useDictStore()
      const dictOptions = await dictStore.getDictObj(['crm_record_issue_type'])
      return dictOptions.crm_record_issue_type
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'assigned_user',
    label: '指派人員',
    colProps: {
      span: 12
    },
    component: 'Select',
    componentProps: {
      style: {
        width: '100%'
      }
    },
    optionApi: async () => {
      const dictStore = useDictStore()
      const dictOptions = await dictStore.getDictObj(['crm_record_assigned_user'])
      return dictOptions.crm_record_assigned_user
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'estimated_reply_date',
    label: '指定回覆時間',
    component: 'DatePicker',
    colProps: {
      span: 12
    },
    componentProps: {
      style: {
        width: '100%'
      },
      type: 'datetime',
      format: 'YYYY-MM-DD HH:mm:ss',
      valueFormat: 'YYYY-MM-DD HH:mm:ss'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'is_closed',
    label: '是否結案',
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
          label: '結案',
          value: true
        },
        {
          label: '未結案',
          value: false
        }
      ]
    },
    value: true
  }
])

const rules = reactive({
  visit_date: [required()],
  sales_name: [required()],
  client_name: [required()],
  visit_type: [required()],
  purpose: [required()],
  is_closed: [required()]
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
  <Form :rules="rules" @register="formRegister" :schema="formSchema" />
</template>
