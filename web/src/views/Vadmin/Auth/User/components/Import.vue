<script setup lang="ts">
import {
  ElLink,
  ElRow,
  ElCol,
  ElTable,
  ElTableColumn,
  ElUpload,
  ElTooltip,
  UploadProps,
  ElMessage,
  ElPopconfirm
} from 'element-plus'
import { getImportTemplateApi, postImportUserApi } from '@/api/vadmin/auth/user'
import { ref } from 'vue'

const emit = defineEmits(['getList'])

const beforeFileUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const isExcel = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(
    rawFile.type
  )
  const isLtSize = rawFile.size / 1024 / 1024 < 10

  if (!isExcel) {
    ElMessage.error('上傳文件必須是 XLSX 格式!')
  }
  if (!isLtSize) {
    ElMessage.error('上傳文件大小不能超過 10MB!')
  }
  return isExcel && isLtSize
}

const importFile = ref()
const tableData = ref([] as Recordable[])
const resultTableData = ref([] as Recordable[])

const handleUpload = async (file) => {
  tableData.value = []
  tableData.value.push({
    filename: file.file.name,
    filesize: (file.file.size / 1024).toFixed(1) + 'KB',
    status: '上傳成功'
  })
  importFile.value = file.file
}

const handleDelete = () => {
  tableData.value = []
  importFile.value = null
}

const importLoading = ref(false)
const successTotalNumber = ref(0)

const handleImport = async () => {
  importLoading.value = true
  const formData = new FormData()
  formData.append('file', importFile.value)
  try {
    const res = await postImportUserApi(formData)
    if (res) {
      resultTableData.value.push({
        filename: importFile.value.name,
        success_number: res.data.success_number,
        error_number: res.data.error_number,
        error_url: res.data.error_url
      })
      successTotalNumber.value += res.data.success_number
      handleDelete()
      emit('getList')
    }
  } finally {
    importLoading.value = false
  }
}

const downloadTemplate = async () => {
  ElMessage.info('正在下載請稍等！')
  const res = await getImportTemplateApi()
  if (res) {
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = res.data.url
    a.target = '_blank'
    a.download = res.data.filename
    const event = new MouseEvent('click')
    a.dispatchEvent(event)
  }
}

const downloadErrorFile = async (row: Recordable) => {
  ElMessage.info('正在下載請稍等！')
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = row.error_url
  a.target = '_blank'
  a.download = row.filename
  const event = new MouseEvent('click')
  a.dispatchEvent(event)
}
</script>

<template>
  <div>
    <span>導入步驟：</span>
    <ol>
      <li style="margin-top: 7px">
        <ElLink @click="downloadTemplate" target="_blank" type="primary">
          下載最新批量導入模板
        </ElLink>
      </li>
      <li style="margin-top: 7px">編輯模板文件，（將需要導入的數據按格式填寫進去）</li>
      <li style="margin-top: 7px">上傳模板文件，點擊確認導入</li>
      <li style="margin-top: 7px">查看導入结果，是否全部導入</li>
    </ol>
  </div>
  <div>
    <ElRow :gutter="10" class="!mt-0 !mr-0">
      <ElCol :span="1.5">
        <div>
          <ElUpload
            action=""
            :http-request="handleUpload"
            :data="{ path: 'users' }"
            :show-file-list="false"
            :before-upload="beforeFileUpload"
            accept=".xlsx"
            :disabled="tableData.length > 0"
          >
            <ElTooltip effect="dark" content="只支持上傳XLSX文件" placement="top">
              <BaseButton type="primary" size="small" :disabled="tableData.length > 0"
                >上傳文件</BaseButton
              >
            </ElTooltip>
          </ElUpload>
        </div>
      </ElCol>
      <ElCol :span="1.5">
        <BaseButton
          type="primary"
          size="small"
          :disabled="tableData.length === 0"
          :loading="importLoading"
          @click="handleImport"
          >確認導入</BaseButton
        >
      </ElCol>
    </ElRow>
    <ElTable :data="tableData" :border="true" style="width: 100%" class="mt-10px">
      <ElTableColumn prop="filename" label="文件名稱" align="left" />
      <ElTableColumn prop="filesize" label="文件大小" width="100" align="center" />
      <ElTableColumn prop="status" label="上傳狀態" width="100" align="center" />
      <ElTableColumn fixed="right" label="操作" width="130" align="center">
        <template #default>
          <ElPopconfirm title="確認刪除嗎?" @confirm="handleDelete">
            <template #reference>
              <BaseButton link type="primary" size="small">刪除</BaseButton>
            </template>
          </ElPopconfirm>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
  <div class="mt-10px">
    <div class="flex justify-between mr-10px">
      <span>導入结果</span>
      <span>成功導入總數：{{ successTotalNumber }}</span>
    </div>
    <ElTable :data="resultTableData" :border="true" style="width: 100%" class="mt-10px">
      <ElTableColumn prop="filename" label="文件名稱" align="left" />
      <ElTableColumn prop="success_number" label="成功數量" width="100" align="center" />
      <ElTableColumn prop="error_number" label="失敗數量" width="100" align="center">
        <template #default="scope">
          <span style="color: red">{{ scope.row.error_number }}</span>
        </template>
      </ElTableColumn>
      <ElTableColumn fixed="right" label="操作" width="130" align="center">
        <template #default="scope">
          <ElLink
            v-if="scope.row.error_number > 0"
            @click="downloadErrorFile(scope.row)"
            target="_blank"
            type="primary"
            >下載失敗數據</ElLink
          >
          <ElLink v-else type="success" :underline="false">成功全部導入</ElLink>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
</template>
