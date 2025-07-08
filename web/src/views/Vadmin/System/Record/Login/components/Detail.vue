<script setup lang="tsx">
import { PropType, reactive, ref } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { ElSwitch } from 'element-plus'
import { selectDictLabel, DictDetail } from '@/utils/dict'
import { useDictStore } from '@/store/modules/dict'
import { JsonViewer } from 'vue3-json-viewer'
import 'vue3-json-viewer/dist/index.css'

defineProps({
  currentRow: {
    type: Object as PropType<Nullable<any>>,
    default: () => null
  }
})

const platformOptions = ref<DictDetail[]>([])
const loginMethodOptions = ref<DictDetail[]>([])

const getOptions = async () => {
  const dictStore = useDictStore()
  const dictOptions = await dictStore.getDictObj(['sys_vadmin_platform', 'sys_vadmin_login_method'])
  platformOptions.value = dictOptions.sys_vadmin_platform
  loginMethodOptions.value = dictOptions.sys_vadmin_login_method
}

getOptions()

const detailSchema = reactive<DescriptionsSchema[]>([
  {
    field: 'id',
    label: '編號',
    minWidth: 100,
    span: 24
  },
  {
    field: 'telephone',
    label: '帳號',
    span: 24
  },
  {
    field: 'status',
    label: '登錄狀態',
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <>
            <ElSwitch modelValue={data.status} size="small" disabled />
          </>
        )
      }
    }
  },
  {
    field: 'platform',
    label: '登錄平台',
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <>
            <div>{selectDictLabel(platformOptions.value, data.platform)}</div>
          </>
        )
      }
    }
  },
  {
    field: 'login_method',
    label: '認證方式',
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <>
            <div>{selectDictLabel(loginMethodOptions.value, data.login_method)}</div>
          </>
        )
      }
    }
  },
  {
    field: 'ip',
    label: '登錄地址',
    span: 24
  },
  {
    field: 'address',
    label: '登錄地點',
    span: 24
  },
  {
    field: 'postal_code',
    label: '郵政編碼',
    span: 24
  },
  {
    field: 'area_code',
    label: '地區區號',
    span: 24
  },
  {
    field: 'browser',
    label: '瀏覽器',
    span: 24
  },
  {
    field: 'system',
    label: '操作系统',
    span: 24
  },
  {
    field: 'response',
    label: '響應信息',
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <>
            <JsonViewer value={JSON.parse(data.request)} copyable boxed sort />
          </>
        )
      }
    }
  },
  {
    field: 'request',
    label: '請求信息',
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <>
            <JsonViewer value={JSON.parse(data.request)} copyable boxed sort />
          </>
        )
      }
    }
  },
  {
    field: 'create_datetime',
    label: '創建時間',
    span: 24
  }
])
</script>

<template>
  <Descriptions :schema="detailSchema" :data="currentRow || {}" />
</template>
