<template>
  <view class="container">
    <!-- 顯示掃描或輸入 -->
    <view v-if="!orderInfo">
      <u-button v-if="!isH5" type="primary" @click="scanOrderQRCode" size="large">
        掃描工單 QRCode
      </u-button>
      <view v-else class="input-mode">
        <u-input v-model="manualOrderNo" placeholder="請輸入工單號" />
        <u-button @click="submitManualOrder">提交</u-button>
      </view>
    </view>

    <!-- 顯示工單資訊與機號列表 -->
    <view v-else>
      <view class="order-info">
        <text>工單號：{{ orderInfo.order_no }}</text>
        <text>品號：{{ orderInfo.item_code }}</text>
        <text>品名：{{ orderInfo.item_name }}</text>
      </view>

      <view class="machine-list">
        <view v-for="(sn, index) in snList" :key="index" class="sn-item">
          <text>{{ index + 1 }}. {{ sn }}</text>
        </view>
      </view>

      <u-button type="success" @click="generateNewSN" size="medium" :loading="loading">
        來一台
      </u-button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isH5: false,
      manualOrderNo: "",
      orderInfo: null,
      snList: [],
      loading: false,
    };
  },
  onLoad() {
    this.isH5 = process.env.UNI_PLATFORM === 'h5';
  },
  methods: {
    // 真實掃碼
    scanOrderQRCode() {
      uni.scanCode({
        onlyFromCamera: true,
        scanType: ['qrCode'],
        success: (res) => {
          const orderNo = res.result.trim();
          this.fakeFetchOrderInfo(orderNo);
        },
        fail: () => {
          uni.showToast({ title: "掃描失敗", icon: "none" });
        },
      });
    },

    // 提交手動輸入（H5 模擬用）
    submitManualOrder() {
      const orderNo = this.manualOrderNo.trim();
      if (!orderNo) {
        uni.showToast({ title: "請輸入工單號", icon: "none" });
        return;
      }
      this.fakeFetchOrderInfo(orderNo);
    },

    // 模擬後端資料
    fakeFetchOrderInfo(orderNo) {
      setTimeout(() => {
        this.orderInfo = {
          order_no: orderNo,
          item_code: "ITEM-ABC123",
          item_name: "冷氣主機",
        };
        this.snList = ["BD20250430001", "BD20250430002"];
      }, 500);
    },

    // 模擬產生機號
    generateNewSN() {
      this.loading = true;
      setTimeout(() => {
        const newSn = `BD20250430${String(this.snList.length + 1).padStart(3, '0')}`;
        this.snList.push(newSn);
        this.loading = false;
      }, 800);
    },
  },
};
</script>

<style scoped>
.container {
  padding: 20px;
}
.order-info text {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
}
.machine-list {
  margin-top: 15px;
  margin-bottom: 10px;
}
.sn-item {
  padding: 6px;
  background: #eee;
  border-radius: 4px;
  margin-bottom: 5px;
  font-size: 14px;
}
.input-mode {
  display: flex;
  flex-direction: row;
  gap: 10px;
  margin-top: 10px;
}
</style>
