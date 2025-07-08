<template>
  <view class="container">
    <u-button @click="scanQRCode">掃描工單 QRCode</u-button>
    <view v-if="scannedOrder">
      <u-card :title="scannedOrder.name">
        <view>工單號: {{ scannedOrder.code }}</view>
        <view>物料數量: {{ scannedOrder.materialCount }}</view>
      </u-card>
      <u-button @click="goBack">返回</u-button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      scannedOrder: null // 存儲掃描的工單信息
    }
  },
  methods: {
    scanQRCode() {
      // 使用 uni-app 的 API 扫描二维码
      uni.scanCode({
        success: (res) => {
          // 假資料：根據掃描結果來設置工單資料
          this.scannedOrder = {
            name: '工單名稱', // 假設掃描返回的是工單名稱
            code: res.result, // 掃描得到的工單 QRCode
            materialCount: 10 // 假資料，這裡可以顯示物料數量
          }
          // 假設將工單信息儲存到父組件
          this.$emit('orderScanned', this.scannedOrder)
        }
      })
    },
    goBack() {
      uni.navigateBack() // 返回上一頁
    }
  }
}
</script>

<style scoped>
/* 添加一些樣式 */
</style>
