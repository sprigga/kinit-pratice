<script setup>
import { ElDescriptions, ElDescriptionsItem } from 'element-plus'
import { ref } from 'vue'

const cronExample = ref([
  {
    value: '0 0 10,15,16 * * ?',
    label: '每天上午10點，下午3點，4點'
  },
  {
    value: '0 0/30 9-17 * * ?',
    label: '朝九晚五工作時間内每半小時'
  },
  {
    value: '0 0 12 ? * WED	',
    label: '表示每個星期三中午12點'
  },
  {
    value: '0 0 12 * * ?',
    label: '每天中午12點觸發'
  },
  {
    value: '0 15 10 ? * *',
    label: '每天上午10:15觸發'
  },
  {
    value: '0 15 10 * * ?',
    label: '每天上午10:15觸發 （跟上面的一樣）'
  },
  {
    value: '0 15 10 * * ? 2005',
    label: '2005年的每天上午10:15觸發'
  },
  {
    value: '0 * 14 * * ?',
    label: '在每天下午2點到下午2:59期間的每1分鐘觸發'
  },
  {
    value: '0 0/5 14 * * ?',
    label: '在每天下午2點到下午2:55期間的每5分鐘觸發'
  },
  {
    value: '0 0/5 14,18 * * ?',
    label: '在每天下午2點到2:55期間和下午6點到6:55期間的每5分鐘觸發'
  },
  {
    value: '0 0-5 14 * * ?',
    label: '在每天下午2點到下午2:05期間的每1分鐘觸發'
  },
  {
    value: '0 10,44 14 ? 3 WED',
    label: '每年三月的星期三的下午2:10和2:44觸發'
  },
  {
    value: '0 15 10 ? * MON-FRI',
    label: '周一至周五的上午10:15觸發'
  },
  {
    value: '0 15 10 15 * ?',
    label: '每月15日上午10:15觸發'
  },
  {
    value: '0 15 10 L * ?',
    label: '每月最後一日的上午10:15觸發'
  }
])
</script>

<template>
  <ElDescriptions :column="1" :border="true">
    <ElDescriptionsItem v-for="(item, index) in cronExample" :key="index" :label="item.value">{{
      item.label
    }}</ElDescriptionsItem>
  </ElDescriptions>
</template>

<style lang="scss" scoped></style>
