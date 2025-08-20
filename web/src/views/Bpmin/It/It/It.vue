<script setup lang="tsx">
import { reactive, ref, unref } from 'vue'
import {
  getBpminItListApi,
  addBpminItApi,
  delBpminItApi,
  putBpminItApi,
  getBpminItApi
} from '@/api/bpmin/it/it'
import {
  getBpminItDetailListApi,
  addBpminItDetailApi,
  delBpminItDetailApi
} from '@/api/bpmin/it/detail'

import { useTable } from '@/hooks/web/useTable'
import { useI18n } from '@/hooks/web/useI18n'
import { Table, TableColumn } from '@/components/Table'
import {
  ElRow,
  ElCol,
  ElMessage,
  ElMessageBox,
  ElInput,
  ElSelect,
  ElOption,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog
} from 'element-plus'
import { Search } from '@/components/Search'
import { FormSchema } from '@/components/Form'
import { ContentWrap } from '@/components/ContentWrap'
import Write from './components/Write.vue'
import { Dialog } from '@/components/Dialog'
import { useDictStore } from '@/store/modules/dict'
import { DictDetail } from '@/utils/dict'
import { BaseButton } from '@/components/Button'

defineOptions({
  name: 'BpminIt'
})

const { t } = useI18n()

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const { pageSize, currentPage } = tableState
    const res = await getBpminItListApi({
      page: unref(currentPage),
      limit: unref(pageSize),
      ...unref(searchParams)
    })
    return {
      list: res.data || [],
      total: res.count || 0
    }
  },
  fetchDelApi: async (value) => {
    const res = await delBpminItApi(value)
    return res.code === 200
  }
})

const { dataList, loading, total, pageSize, currentPage } = tableState
const { getList, delList } = tableMethods

const platformOptions = ref<DictDetail[]>([])

const getOptions = async () => {
  const dictStore = useDictStore()
  const dictOptions = await dictStore.getDictObj(['sys_vadmin_platform'])
  platformOptions.value = dictOptions.sys_vadmin_platform
}

getOptions()

// 初始化數據加載
const initData = async () => {
  await getList()
}

// 組件掛載後自動加載數據
initData()

const tableColumns = reactive<TableColumn[]>([
  // {
  //   field: 'id',
  //   label: '編號',
  //   width: '100px',
  //   show: true,
  //   disabled: true,
  //   align: 'center',
  //   headerAlign: 'center'
  // },
  {
    field: 'serial_number',
    label: '表單序號',
    width: '220px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'apply_date',
    label: '申請日期',
    width: '120px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'dept',
    label: '申請單位',
    width: '130px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'fillman',
    label: '申請人',
    width: '180px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'main_apply_item',
    label: '申請項目',
    width: '250px',
    show: true,
    disabled: true,
    showOverflowTooltip: false,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'request_desc',
    label: '需求描述',
    width: '150px',
    show: true,
    disabled: true,
    showOverflowTooltip: false,
    className: 'text-wrap-column',
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'it_undertaker',
    label: 'IT承辦人',
    width: '180px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  // {
  //   field: 'treatment',
  //   label: '處理方式',
  //   width: '150',
  //   show: true,
  //   disabled: true,
  //   align: 'center',
  //   headerAlign: 'center'
  // },
  {
    field: 'is_delete',
    label: '表單狀態',
    width: '100px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center',
    slots: {
      default: (data: any) => {
        const row = data.row
        const statusText = row.is_delete
        const isCompleted = statusText === '已結案'
        return <ElTag type={isCompleted ? 'success' : 'warning'}>{statusText || '未結案'}</ElTag>
      }
    }
  },
  {
    field: 'elapsed_days',
    label: '經過時間',
    width: '100px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center',
    slots: {
      default: (data: any) => {
        const row = data.row
        const days = row.elapsed_days
        if (days === undefined || days === null) return <span>-</span>
        return <span>{days} 天</span>
      }
    }
  },
  {
    field: 'latest_processing_status',
    label: '處理狀態',
    width: '100px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center',
    slots: {
      default: (data: any) => {
        const row = data.row
        const status = row.latest_processing_status
        if (!status) return <span style="color: #909399;">-</span>
        let statusType = 'info'
        if (status === '已完成') statusType = 'success'
        else if (status === '處理中') statusType = 'primary'
        else if (status === '已暫停') statusType = 'warning'
        else if (status === '已取消') statusType = 'danger'
        return <ElTag type={statusType as any}>{status}</ElTag>
      }
    }
  },
  {
    field: 'datediff',
    label: '處理天數',
    width: '100px',
    show: true,
    disabled: true,
    align: 'center',
    headerAlign: 'center'
  },
  {
    field: 'action',
    label: '操作',
    width: '200px',
    show: true,
    slots: {
      default: (data: any) => {
        const row = data.row
        const update = ['bpmin.it.it.update']
        const del = ['bpmin.it.it.delete']
        return (
          <>
            <BaseButton
              type="primary"
              v-hasPermi={update}
              link
              size="small"
              onClick={() => editAction(row)}
            >
              詳細
            </BaseButton>
            <BaseButton type="success" link size="small" onClick={() => viewHistoryAction(row)}>
              處理歷程
            </BaseButton>
            <BaseButton
              type="danger"
              v-hasPermi={del}
              loading={delLoading.value}
              link
              size="small"
              onClick={() => delData(row)}
            >
              删除
            </BaseButton>
          </>
        )
      }
    }
  }
])

const searchSchema = reactive<FormSchema[]>([
  {
    field: 'serial_number',
    label: '表單序號',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' },
      placeholder: '請輸入表單序號'
    }
  },
  {
    field: 'apply_date',
    label: '申請日期',
    component: 'DatePicker',
    componentProps: {
      clearable: true,
      type: 'date',
      format: 'YYYY-MM-DD',
      valueFormat: 'YYYY-MM-DD',
      style: { width: '214px' },
      placeholder: '請選擇申請日期'
    }
  },
  {
    field: 'it_undertaker',
    label: 'IT承辦人',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' },
      placeholder: '請輸入IT承辦人'
    }
  }
])

const searchParams = ref({})
const setSearchParams = (data: any) => {
  currentPage.value = 1
  searchParams.value = data
  getList()
}

const delLoading = ref(false)

const delData = async (row: any) => {
  delLoading.value = true
  await delList(true, [row.id]).finally(() => {
    delLoading.value = false
  })
}

const dialogVisible = ref(false)
const dialogTitle = ref('')

const currentRow = ref()
const actionType = ref('')

const writeRef = ref<any>()

const saveLoading = ref(false)

const editAction = async (row: any) => {
  const res = await getBpminItApi(row.id)
  if (res) {
    dialogTitle.value = '詳細資料'
    actionType.value = 'edit'
    currentRow.value = res.data
    dialogVisible.value = true
  }
}

const addAction = () => {
  dialogTitle.value = '新增資料'
  actionType.value = 'add'
  currentRow.value = undefined
  dialogVisible.value = true
}

const add = ['bpmin.it.it.create']

// 表單歷程相關變數
const historyDialogVisible = ref(false)
const historyDialogTitle = ref('')
const historyData = ref([])
const historyLoading = ref(false)
// const currentItId = ref<number>()

// 新增記錄表單數據
const newRecord = ref({
  work_desc: '',
  rsn: '',
  status: '',
  create_user: ''
})

// 查看表單歷程
const viewHistoryAction = async (row: any) => {
  // 獲取完整的資料用於歷程操作
  const res = await getBpminItApi(row.id)
  if (res) {
    currentRow.value = res.data
    // 設置新增記錄表單的參照序號和預設處理人員
    newRecord.value.rsn = res.data.serial_number
    newRecord.value.create_user = res.data.it_undertaker || '' // 設置IT承辦人為預設處理人員
    historyDialogTitle.value = `處理歷程 - ${row.serial_number}`
    historyDialogVisible.value = true
    await getHistoryList()
  }
}

// 獲取歷程列表
const getHistoryList = async () => {
  if (!currentRow.value?.serial_number) return

  historyLoading.value = true
  try {
    const requestParams = {
      rsn: currentRow.value.serial_number,
      page: 1,
      limit: 100
    }
    console.log('請求歷程數據的參數:', requestParams)

    const res = await getBpminItDetailListApi(requestParams)
    console.log('API返回的原始數據:', res)

    // 前端再次過濾確保數據正確性
    const filteredData =
      res.data?.filter((record: any) => record.rsn === currentRow.value?.serial_number) || []

    // console.log(`篩選前: ${res.data?.length || 0} 筆, 篩選後: ${filteredData.length} 筆`)
    // console.log('目標RSN:', currentRow.value.serial_number)

    historyData.value = filteredData
  } catch (error) {
    console.error('獲取表單歷程失敗:', error)
    historyData.value = []
  } finally {
    historyLoading.value = false
  }
}

// 新增歷程記錄
const addHistoryRecord = async (data: any) => {
  try {
    const res = await addBpminItDetailApi({
      ...data,
      rsn: currentRow.value?.serial_number // 使用主表的序號作為外鍵關聯
    })
    if (res.code === 200) {
      await getHistoryList() // 重新載入列表
      return true
    }
    return false
  } catch (error) {
    console.error('新增歷程記錄失敗:', error)
    return false
  }
}

// 提交新增記錄
const submitHistoryRecord = async () => {
  // 表單驗證
  if (!newRecord.value.create_user) {
    ElMessage.warning('請輸入處理人')
    return
  }
  if (!newRecord.value.status) {
    ElMessage.warning('請選擇狀態')
    return
  }
  if (!newRecord.value.work_desc) {
    ElMessage.warning('請輸入工作描述')
    return
  }

  const success = await addHistoryRecord(newRecord.value)
  if (success) {
    ElMessage.success('新增歷程記錄成功')
    // 清空表單但保留預設值
    newRecord.value = {
      work_desc: '',
      rsn: currentRow.value?.serial_number || '',
      status: '',
      create_user: currentRow.value?.it_undertaker || '' // 保持IT承辦人為預設處理人員
    }
  } else {
    ElMessage.error('新增歷程記錄失敗')
  }
}

// 刪除歷程記錄
const deleteHistoryRecord = async (row: any) => {
  if (!row.id) {
    ElMessage.error('無效的記錄ID')
    return
  }

  try {
    // 確認刪除
    await ElMessageBox.confirm(
      `確定要刪除這筆歷程記錄嗎？\n承辦人員: ${row.create_user}\n工作描述: ${row.work_desc}`,
      '確認刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // API 參數應該是 ids 數組，而不是包含 ids 屬性的對象
    const res = await delBpminItDetailApi([row.id])
    if (res && res.code === 200) {
      ElMessage.success('刪除歷程記錄成功')
      await getHistoryList() // 重新載入列表
    } else {
      ElMessage.error('刪除歷程記錄失敗')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('刪除歷程記錄失敗:', error)
      ElMessage.error('刪除歷程記錄失敗')
    }
  }
}

// 狀態標籤類型
const getStatusTagType = (status: string) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '處理中':
      return 'primary'
    case '已暫停':
      return 'warning'
    case '已取消':
      return 'danger'
    default:
      return 'info'
  }
}

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    try {
      const res = ref({})
      if (actionType.value === 'add') {
        res.value = await addBpminItApi(formData)
        if (res.value) {
          dialogVisible.value = false
          getList()
        }
      } else if (actionType.value === 'edit') {
        res.value = await putBpminItApi(formData)
        if (res.value) {
          dialogVisible.value = false
          getList()
        }
      }
    } finally {
      saveLoading.value = false
    }
  }
}
</script>

<template>
  <div>
    <ContentWrap>
      <Search :schema="searchSchema" @reset="setSearchParams" @search="setSearchParams" />
      <Table
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        showAction
        :columns="tableColumns"
        default-expand-all
        node-key="id"
        :data="dataList"
        :loading="loading"
        :pagination="{
          total
        }"
        @register="tableRegister"
        @refresh="getList"
      >
        <template #toolbar>
          <ElRow :gutter="10">
            <ElCol :span="1.5">
              <BaseButton type="primary" v-hasPermi="{ add }" @click="addAction"
                >新增資料</BaseButton
              >
            </ElCol>
          </ElRow>
        </template>
      </Table>
    </ContentWrap>
    <Dialog v-model="dialogVisible" :title="dialogTitle" :height="650">
      <Write ref="writeRef" :current-row="currentRow" />

      <template #footer>
        <BaseButton type="primary" :loading="saveLoading" @click="save">
          {{ t('exampleDemo.save') }}
        </BaseButton>
        <BaseButton @click="dialogVisible = false">{{ t('dialogDemo.close') }}</BaseButton>
      </template>
    </Dialog>

    <!-- 表單歷程 Dialog -->
    <ElDialog
      v-model="historyDialogVisible"
      :title="historyDialogTitle"
      :width="800"
      draggable
      :destroy-on-close="true"
      :close-on-click-modal="false"
    >
      <div v-loading="historyLoading">
        <!-- 新增歷程表單 -->
        <div
          style="margin-bottom: 20px; padding: 15px; border: 1px solid #e4e7ed; border-radius: 4px"
        >
          <h4 style="margin-top: 0">新增歷程記錄</h4>
          <ElRow :gutter="20">
            <ElCol :span="8">
              <label>承辦人員：</label>
              <ElInput v-model="newRecord.create_user" readonly placeholder="請輸入承辦人員" />
            </ElCol>
            <ElCol :span="5">
              <label>處理狀態：</label>
              <ElSelect v-model="newRecord.status" placeholder="請選擇狀態" style="width: 100%">
                <ElOption label="處理中" value="處理中" />
                <ElOption label="已完成" value="已完成" />
                <ElOption label="已暫停" value="已暫停" />
                <ElOption label="已取消" value="已取消" />
              </ElSelect>
            </ElCol>
            <ElCol :span="9">
              <label>參照序號：</label>
              <ElInput :value="currentRow?.serial_number" readonly placeholder="自動填入" />
            </ElCol>
          </ElRow>
          <ElRow style="margin-top: 15px">
            <ElCol :span="24">
              <label>工作描述：</label>
              <ElInput
                v-model="newRecord.work_desc"
                type="textarea"
                :rows="3"
                placeholder="請輸入工作描述"
              />
            </ElCol>
          </ElRow>
          <div style="margin-top: 15px; text-align: right">
            <BaseButton type="primary" @click="submitHistoryRecord">新增記錄</BaseButton>
          </div>
        </div>

        <!-- 歷程列表 -->
        <div>
          <h4>歷程記錄</h4>
          <ElTable :data="historyData" border style="width: 100%">
            <ElTableColumn prop="create_user" label="承辦人員" width="120" align="center" />
            <ElTableColumn prop="status" label="處理狀態" width="100" align="center">
              <template #default="{ row }">
                <ElTag :type="getStatusTagType(row.status)">{{ row.status }}</ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="rsn" label="參照序號" width="120" align="center" />
            <ElTableColumn prop="work_desc" label="工作描述" show-overflow-tooltip />
            <ElTableColumn prop="create_datetime" label="建立時間" width="160" align="center" />
            <ElTableColumn label="操作" width="80" align="center">
              <template #default="{ row }">
                <BaseButton type="danger" size="small" link @click="deleteHistoryRecord(row)">
                  刪除
                </BaseButton>
              </template>
            </ElTableColumn>
          </ElTable>
          <div
            v-if="historyData.length === 0"
            style="text-align: center; padding: 20px; color: #909399"
          >
            暫無歷程記錄
          </div>
        </div>
      </div>

      <template #footer>
        <BaseButton @click="historyDialogVisible = false">{{ t('dialogDemo.close') }}</BaseButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.text-wrap-column {
  white-space: normal !important;
  word-wrap: break-word;
  line-height: 1.5;
}
</style>
