<script setup lang="ts">
import { ElTable, ElTableColumn, ElPopconfirm, ElMessage, ElTag } from 'element-plus'
import { postUsersInitPasswordSendEmailApi } from '@/api/vadmin/auth/user'
import { ref, PropType } from 'vue'

const props = defineProps({
  selections: {
    type: Object as PropType<Recordable[]>
  }
})

const tableData = ref(JSON.parse(JSON.stringify(props.selections)))
const loading = ref(false)

const handleDelete = (index: number) => {
  tableData.value.splice(index, 1)
}

const initPassword = async () => {
  loading.value = true
  const ids = tableData.value
    .filter((item) => item.reset_password_status !== true)
    .map((item) => item.id)
  if (ids.length <= 0) {
    return ElMessage.warning('已全部重置完成，無需重複操作')
  }
  try {
    const res = await postUsersInitPasswordSendEmailApi(ids)
    if (res) {
      tableData.value = res.data
      ElMessage.success('重置成功')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between">
      <span>已選用户列表</span>
      <BaseButton
        type="primary"
        :disabled="tableData?.length === 0"
        :loading="loading"
        @click="initPassword"
        >確認重置並發送郵件通知</BaseButton
      >
    </div>
    <ElTable
      :data="tableData"
      :stripe="true"
      :border="true"
      style="width: 100%"
      class="mt-10px"
      max-height="500px"
    >
      <ElTableColumn prop="id" label="用户編號" width="100" align="center" />
      <ElTableColumn prop="name" label="姓名" width="120" align="center" />
      <ElTableColumn prop="email" label="郵箱" width="200" align="center" />
      <ElTableColumn prop="reset_password_status" label="重置狀態" width="100" align="center">
        <template #default="scope">
          <ElTag v-if="scope.row.reset_password_status === true" type="success" effect="dark">
            重置成功
          </ElTag>
          <ElTag v-else-if="scope.row.reset_password_status === false" type="danger" effect="dark">
            重置失敗
          </ElTag>
          <ElTag v-else type="warning" effect="dark"> 待重置 </ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="send_sms_status" label="發送狀態" width="100" align="center">
        <template #default="scope">
          <ElTag v-if="scope.row.send_sms_status === true" type="success" effect="dark">
            發送成功
          </ElTag>
          <ElTag v-else-if="scope.row.send_sms_status === false" type="danger" effect="dark">
            發送失敗
          </ElTag>
          <ElTag v-else type="warning" effect="dark"> 待發送 </ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="send_sms_msg" label="描述" align="center" />
      <ElTableColumn fixed="right" label="操作" width="100" align="center">
        <template #default="scope">
          <ElPopconfirm title="確認移除嗎?" @confirm="handleDelete(scope.$index)">
            <template #reference>
              <BaseButton v-if="scope.row.send_sms_status !== true" link type="primary" size="small"
                >移除</BaseButton
              >
            </template>
          </ElPopconfirm>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
</template>
