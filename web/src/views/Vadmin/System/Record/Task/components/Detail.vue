<script setup lang="tsx">
import { PropType, reactive, ref } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { selectDictLabel, DictDetail } from '@/utils/dict'
import { useDictStore } from '@/store/modules/dict'
import 'vue3-json-viewer/dist/index.css'

defineProps({
  currentRow: {
    type: Object as PropType<Nullable<any>>,
    default: () => null
  }
})

const execStrategyOptions = ref<DictDetail[]>([])

const getOptions = async () => {
  const dictStore = useDictStore()
  const dictOptions = await dictStore.getDictObj(['vadmin_system_task_exec_strategy'])
  execStrategyOptions.value = dictOptions.vadmin_system_task_exec_strategy
}

getOptions()

const detailSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'job_id',
    label: '任務編號',
    width: '240px',
    span: 24
  },
  {
    field: 'name',
    label: '任務名稱',
    span: 24
  },
  {
    field: 'group',
    label: '任務分组',
    span: 24
  },
  {
    field: 'job_class',
    label: '調用目標',
    span: 24
  },
  {
    field: 'exec_strategy',
    label: '執行策略',
    span: 24,
    slots: {
      default: (data: any) => {
        const row = data
        return (
          <>
            <div>{selectDictLabel(execStrategyOptions.value, row.exec_strategy)}</div>
          </>
        )
      }
    }
  },
  {
    field: 'expression',
    label: '表達式',
    span: 24
  },
  {
    field: 'start_time',
    label: '開始執行時間',
    width: '200px',
    span: 24
  },
  {
    field: 'end_time',
    label: '執行完成時間',
    width: '200px',
    span: 24
  },
  {
    field: 'process_time',
    label: '耗時(秒)',
    width: '110px',
    span: 24
  },
  {
    field: 'retval',
    label: '任務返回值',
    span: 24,
    slots: {
      default: (data: any) => {
        const row = data
        return JSON.parse(row.retval)
      }
    }
  },
  {
    field: 'exception',
    label: '異常信息',
    span: 24
  },
  {
    field: 'traceback',
    label: '堆棧跟踪',
    width: '100px',
    span: 24
  }
])
</script>

<template>
  <Descriptions :schema="detailSchema" :data="currentRow || {}" />
</template>
