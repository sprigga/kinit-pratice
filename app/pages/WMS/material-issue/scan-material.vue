<template>
  <view class="container">
    <u-button @click="scanQRCode">掃描物料 QRCode</u-button>
    <view v-if="scannedMaterial">
      <u-card :title="scannedMaterial.name">
        <view>物料編號: {{ scannedMaterial.code }}</view>
        <view>領料數量: {{ scannedMaterial.quantity }}</view>
      </u-card>
      <u-button @click="goBack">返回</u-button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      scannedMaterial: null // 存儲掃描的物料信息
    }
  },
  methods: {
    scanQRCode() {
      // 使用 uni-app 的 API 扫描二维码
      uni.scanCode({
        success: (res) => {
          // 假資料：根據掃描結果來設置物料資料
          this.scannedMaterial = {
            name: '物料名稱', // 假設掃描返回的是物料名稱
            code: res.result, // 掃描得到的物料 QRCode
            quantity: 5 // 假資料，這裡可以顯示領料數量
          }
          // 假設將物料信息儲存到父組件
          this.$emit('materialScanned', this.scannedMaterial)
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
