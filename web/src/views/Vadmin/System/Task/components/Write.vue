<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { useDictStore } from '@/store/modules/dict'
import { getTaskGroupOptionsApi } from '@/api/vadmin/system/task'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  }
})

const formSchema = reactive<FormSchema[]>([
  {
    field: 'name',
    label: '任務名稱',
    component: 'Input',
    colProps: {
      span: 12
    },
    componentProps: {
      style: {
        width: '100%'
      }
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'group',
    label: '任務分組',
    colProps: {
      span: 12
    },
    component: 'Select',
    componentProps: {
      style: {
        width: '100%'
      },
      allowCreate: true,
      filterable: true,
      defaultFirstOption: true,
      placeholder: '請選擇任務分組，支持直接輸入添加'
    },
    optionApi: async () => {
      const res = await getTaskGroupOptionsApi()
      return res.data
    }
  },
  {
    field: 'job_class',
    label: '調用目標',
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: '調用示例：test.main.Test("kinit", 1314)；參數僅支持字串，整數，浮點數，布爾值。'
    },
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'exec_strategy',
    label: '執行策略',
    colProps: {
      span: 24
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      }
    },
    value: 'interval',
    formItemProps: {
      rules: [required()]
    },
    optionApi: async () => {
      const dictStore = useDictStore()
      const dictOptions = await dictStore.getDictObj(['vadmin_system_task_exec_strategy'])
      return dictOptions.vadmin_system_task_exec_strategy
    }
    // formItemProps: {
    //   slots: {
    //     default: (data) => {
    //       return (
    //         <>
    //           <ElRadioGroup v-model={data['exec_strategy']} onChange={handleChange(form)}></>
    //     <ElRadio v-for="(item, $index) in execStrategyOptions" :key="" :label="item.value">{{
    //       item.label
    //     }}</ElRadio>
    //     {}
    //   </ElRadioGroup>
    //         </>
    //       )
    //     }
    //   }
    // }
  },
  {
    field: 'expression',
    label: '表達式',
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder:
        'interval 表達式，五位，分別為：秒 分 時 天 周，例如：10 * * * * 表示每隔 10 秒執行一次任務。'
    },
    ifshow: (values) => values.exec_strategy === 'interval',
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'expression',
    label: '表達式',
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: 'cron 表達式，六位或七位，分别表示秒、分钟、小時、天、月、星期幾、年(可選)'
    },
    ifshow: (values) => values.exec_strategy === 'cron',
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'expression',
    label: '執行時間',
    component: 'DatePicker',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      type: 'datetime',
      format: 'YYYY-MM-DD HH:mm:ss',
      valueFormat: 'YYYY-MM-DD HH:mm:ss'
    },
    ifshow: (values) => values.exec_strategy === 'date',
    formItemProps: {
      rules: [required()]
    }
  },
  {
    field: 'start_date',
    label: '開始時間',
    colProps: {
      span: 12
    },
    component: 'DatePicker',
    componentProps: {
      style: {
        width: '100%'
      },
      type: 'datetime',
      format: 'YYYY-MM-DD HH:mm:ss',
      valueFormat: 'YYYY-MM-DD HH:mm:ss'
    },
    ifshow: (values) => values.exec_strategy !== 'date'
  },
  {
    field: 'end_date',
    label: '結束時間',
    colProps: {
      span: 12
    },
    component: 'DatePicker',
    componentProps: {
      style: {
        width: '100%'
      },
      type: 'datetime',
      format: 'YYYY-MM-DD HH:mm:ss',
      valueFormat: 'YYYY-MM-DD HH:mm:ss'
    },
    ifshow: (values) => values.exec_strategy !== 'date'
  },
  {
    field: 'is_active',
    label: '任務狀態',
    colProps: {
      span: 8
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '正常',
          value: true
        },
        {
          label: '停用',
          value: false
        }
      ]
    },
    value: true
  },
  {
    field: '',
    label: '',
    colProps: {
      span: 16
    },
    component: 'Text',
    value:
      '創建或更新任務完成後，如果任務狀態與設置的不符，請嘗試刷新數據或查看調度日誌，任務狀態可能會有延遲(幾秒)。'
  },
  {
    field: 'remark',
    label: '備註說明',
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      maxlength: '1000',
      showWordLimit: true,
      type: 'textarea',
      rows: '3'
    }
  }
])

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
  <Form @register="formRegister" :schema="formSchema" />
</template>
