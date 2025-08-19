<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  }
})

const formSchema = reactive<FormSchema[]>([
  {
    field: 'id',
    label: '編號',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      disabled: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'serial_number',
    label: '表單序號',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'it_manager',
    label: 'IT主管',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'dept',
    label: '部門',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'apply_date',
    label: '申請日期',
    colProps: {
      span: 12
    },
    component: 'DatePicker',
    componentProps: {
      readonly: true,
      type: 'date',
      placeholder: '请选择日期',
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'extension',
    label: '分機號碼',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'fillman',
    label: '填表人',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'main_apply_item',
    label: '申請項目',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'sub_apply_item',
    label: '子申請項目',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'request_desc',
    label: '需求描述',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'it_undertaker',
    label: 'IT承辦人',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'treatment',
    label: '處理方式',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'is_delete',
    label: '狀態',
    colProps: {
      span: 12
    },
    component: 'Input',
    componentProps: {
      readonly: true,
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'create_datetime',
    label: '創建時間',
    colProps: {
      span: 12
    },
    component: 'DatePicker',
    componentProps: {
      readonly: true,
      type: 'date',
      placeholder: '请选择日期',
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'update_datetime',
    label: '更新時間',
    colProps: {
      span: 12
    },
    component: 'DatePicker',
    componentProps: {
      readonly: true,
      type: 'date',
      placeholder: '请选择日期',
      style: {
        width: '100%'
      }
    }
  }
])

const rules = reactive({})

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
