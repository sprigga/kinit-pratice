<script setup lang="tsx">
import { reactive, ref, unref } from 'vue'
import {
  getCrmVisitReplyListApi,
  addCrmVisitReplyApi,
  delCrmVisitReplyApi,
  putCrmVisitReplyApi,
  getCrmVisitReplyApi
} from '@/api/crm/visit/reply'

import { useTable } from '@/hooks/web/useTable'
import { useI18n } from '@/hooks/web/useI18n'
import { Table, TableColumn } from '@/components/Table'
import { ElRow, ElCol } from 'element-plus'
import { Search } from '@/components/Search'
import { FormSchema } from '@/components/Form'
import { ContentWrap } from '@/components/ContentWrap'
import Write from './components/Write.vue'
import { Dialog } from '@/components/Dialog'
import { useDictStore } from '@/store/modules/dict'
import { DictDetail } from '@/utils/dict'
import { BaseButton } from '@/components/Button'

defineOptions({
  name: 'CrmVisitReply'
})

const { t } = useI18n()

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const { pageSize, currentPage } = tableState
    const res = await getCrmVisitReplyListApi({
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
    const res = await delCrmVisitReplyApi(value)
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

const tableColumns = reactive<TableColumn[]>([
  {
    field: 'action',
    label: '操作',
    width: '200px',
    show: true,
    slots: {
      default: (data: any) => {
        const row = data.row
        const update = ['crm.visit.reply.update']
        const del = ['crm.visit.reply.delete']
        return (
          <>
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
    field: 'id',
    label: '流水號',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
    }
  },
  {
    field: 'record_id',
    label: '對應主檔',
    component: 'Input',
    componentProps: {
      clearable: true,
      style: { width: '214px' }
    }
  },
  {
    field: 'record',
    label: '回覆內容',
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
  const res = await getCrmVisitReplyApi(row.id)
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

const add = ['crm.visit.reply.create']

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    try {
      const res = ref({})
      if (actionType.value === 'add') {
        res.value = await addCrmVisitReplyApi(formData)
        if (res.value) {
          dialogVisible.value = false
          getList()
        }
      } else if (actionType.value === 'edit') {
        res.value = await putCrmVisitReplyApi(formData)
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
