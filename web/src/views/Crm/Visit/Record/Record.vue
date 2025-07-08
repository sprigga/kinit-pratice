<script setup lang="tsx">
import { reactive, ref, unref } from 'vue'
import {
  getCrmVisitRecordListApi,
  addCrmVisitRecordApi,
  delCrmVisitRecordApi,
  putCrmVisitRecordApi,
  getCrmVisitRecordApi
} from '@/api/crm/visit/record'

import { useTable } from '@/hooks/web/useTable'
import { useI18n } from '@/hooks/web/useI18n'
import { Table, TableColumn } from '@/components/Table'
import { ElRow, ElCol, ElSwitch } from 'element-plus'
import { Search } from '@/components/Search'
import { FormSchema } from '@/components/Form'
import { ContentWrap } from '@/components/ContentWrap'
import Write from './components/Write.vue'
import { Dialog } from '@/components/Dialog'
import { useDictStore } from '@/store/modules/dict'
import { DictDetail, selectDictLabel } from '@/utils/dict'
import { BaseButton } from '@/components/Button'

defineOptions({
  name: 'CrmVisitRecord'
})

const { t } = useI18n()

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const { pageSize, currentPage } = tableState
    const res = await getCrmVisitRecordListApi({
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
    const res = await delCrmVisitRecordApi(value)
    return res.code === 200
  }
})

const { dataList, loading, total, pageSize, currentPage } = tableState
const { getList, delList } = tableMethods

const platformOptions = ref<DictDetail[]>([])
const issue_typeOptions = ref<DictDetail[]>([])
const assigned_userOptions = ref<DictDetail[]>([])

const getOptions = async () => {
  const dictStore = useDictStore()
  const dictOptions = await dictStore.getDictObj([
    'sys_vadmin_platform',
    'crm_record_issue_type',
    'crm_record_assigned_user'
  ])
  platformOptions.value = dictOptions.sys_vadmin_platform
  issue_typeOptions.value = dictOptions.crm_record_issue_type
  assigned_userOptions.value = dictOptions.crm_record_assigned_user
}

getOptions()

const tableColumns = reactive<TableColumn[]>([
  {
    field: 'name',
    label: '業務姓名',
    width: '100px',
    show: true,
    disabled: true
  },
  {
    field: 'customer_type',
    label: '拜訪店類型',
    width: '120px',
    show: true,
    disabled: true
  },
  {
    field: 'customer_name',
    label: '客戶名稱',
    width: '150px',
    show: true,
    disabled: true
  },
  {
    field: 'visit_period',
    label: '拜訪時間',
    width: '180px',
    show: true,
    disabled: true
  },
  {
    field: 'purpose',
    label: '拜訪目的',
    width: '150px',
    show: true,
    disabled: true
  },
  {
    field: 'content',
    label: '拜訪內容',
    width: '300px',
    show: true,
    showOverflowTooltip: false,
    slots: {
      default: ({ row }) => {
        return (
          <div style="white-space: normal; word-break: break-word; line-height: 1.5; font-size: 14px;">
            {row.content}
          </div>
        )
      }
    }
  },
  {
    field: 'issue_type',
    label: '問題類型',
    show: false,
    slots: {
      default: (data: any) => {
        const row = data.row
        return (
          <>
            <div>{selectDictLabel(unref(issue_typeOptions), row.issue_type)}</div>
          </>
        )
      }
    }
  },
  {
    field: 'assigned_user',
    label: '指派人員',
    width: '100px',
    show: true,
    disabled: true
  },
  {
    field: 'visit_period',
    label: '預計回覆日期',
    width: '180px',
    show: true,
    disabled: true
  },
  {
    field: 'is_closed',
    label: '是否結案',
    show: true,
    slots: {
      default: (data: any) => {
        const row = data.row
        return (
          <>
            <ElSwitch modelValue={row.is_closed} disabled />
          </>
        )
      }
    }
  },
  {
    field: 'action',
    label: '操作',
    width: '200px',
    show: true,
    slots: {
      default: (data: any) => {
        const row = data.row
        const update = ['crm.visit.record.update']
        const del = ['crm.visit.record.delete']
        return (
          <>
            <BaseButton
              type="primary"
              v-hasPermi={update}
              link
              size="small"
              onClick={() => editAction(row)}
            >
              回覆
            </BaseButton>
            <BaseButton
              type="primary"
              v-hasPermi={update}
              link
              size="small"
              onClick={() => editAction(row)}
            >
              編輯
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
    field: 'name',
    label: '業務姓名',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
    }
  },
  {
    field: 'visit_type',
    label: '拜訪店類型',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
    }
  },
  {
    field: 'purpose',
    label: '拜訪目的',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
    }
  },
  {
    field: 'create_datetime',
    label: '建立時間',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
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

const writeRef = ref<ComponentRef<typeof Write>>()

const saveLoading = ref(false)

const editAction = async (row: any) => {
  const res = await getCrmVisitRecordApi(row.id)
  if (res) {
    dialogTitle.value = '編輯資料'
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

const add = ['crm.visit.record.create']

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    try {
      const res = ref({})
      if (actionType.value === 'add') {
        res.value = await addCrmVisitRecordApi(formData)
        if (res.value) {
          dialogVisible.value = false
          getList()
        }
      } else if (actionType.value === 'edit') {
        res.value = await putCrmVisitRecordApi(formData)
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
  <ContentWrap>
    <Search :schema="searchSchema" @reset="setSearchParams" @search="setSearchParams" />
    <Table
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      showAction
      :columns="tableColumns"
      default-expand-all
      table-layout="auto"
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
            <BaseButton type="primary" v-hasPermi="{ add }" @click="addAction">新增資料</BaseButton>
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
</template>
