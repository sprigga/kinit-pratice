<template>
  <view class="container">
    <!-- 輸入工單號 -->
    <view class="input-container">
      <u-input
        ref="manualOrderInput"
        v-model="manualOrderNumber"
        placeholder="請輸入工單號"
        class="order-input"
        :clearable="true"
        size="mini"
        :focus.sync="inputFocus"
      />
      <u-button @click="scanCode" class="submit-button" size="mini">掃描</u-button>
      <u-button @click="handleSubmitOrder" class="submit-button" size="mini">提交</u-button>
    </view>

    <!-- 顯示工單列表 -->
    <view v-if="orders.length > 0" class="order-list">
      <u-list>
        <u-list-item
          v-for="(order, index) in orders"
          :key="index"
          class="order-list-item"
        >
          <view class="order-actions">
            <view class="move-btns">
              <u-button @click="moveUp(index)" class="move-btn" type="primary" size="mini">︿</u-button>
              <u-button @click="moveDown(index)" class="move-btn" type="primary" size="mini">﹀</u-button>
            </view>
            <view class="order-info">
              <text class="order-text">工單號: {{ order.number }}</text>
              <text class="order-text">數量: {{ order.quantity }}</text>
            </view>
            <u-button @click="deleteOrder(index)" type="error" size="mini" class="delete-btn">刪除</u-button>
          </view>
        </u-list-item>
        <u-button
          :disabled="orders.length === 0"
          @click="handleSubmitOrders"
          class="submit-orders-button"
          size="mini"
        >
          送出
        </u-button>
      </u-list>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      manualOrderNumber: "", // 輸入框的工單號
      orders: [], // 工單列表
      inputFocus: true, // 控制焦點
    };
  },
  methods: {
    // 掃碼
    scanCode() {
      uni.scanCode({
        success: (res) => {
          const scanned = res.result.trim();
          console.log("掃描結果:", scanned);
          this.manualOrderNumber = scanned;

          // ⚠️ 等待欄位更新後再提交
          setTimeout(() => {
            this.handleSubmitOrder();
          }, 50);
        },
        fail: (err) => {
          console.log("掃描錯誤:", err);
          this.$u.toast("掃描失敗，請重試");
        },
      });
    },

    // 提交單筆工單
    handleSubmitOrder() {
      const number = this.manualOrderNumber.trim();

      if (!number) {
        this.$u.toast("請輸入或掃描工單號");
        return;
      }

      // 防重複
      const exists = this.orders.some(order => order.number === number);
      if (exists) {
        this.$u.toast("此工單號已存在，請勿重複掃描");
        this.manualOrderNumber = "";
        this.focusInput();
        return;
      }

      const orderData = {
        number,
        quantity: this.getOrderQuantity(number),
      };

      this.orders.push(orderData);
      console.log("✅ 加入工單:", orderData);

      this.manualOrderNumber = "";
      this.focusInput();
    },

    // 模擬取得數量
    getOrderQuantity(orderNumber) {
      return 70;
    },

    // 重新聚焦
    focusInput() {
      this.inputFocus = false;
      this.$nextTick(() => {
        this.inputFocus = true;
      });
    },

    // 刪除工單
    deleteOrder(index) {
      uni.showModal({
        title: "確認刪除",
        content: "您確定要刪除這個工單嗎？",
        success: (res) => {
          if (res.confirm) {
            this.orders.splice(index, 1);
          }
        },
      });
    },

    // 工單上移
    moveUp(index) {
      if (index > 0) {
        const temp = this.orders[index];
        this.orders.splice(index, 1);
        this.orders.splice(index - 1, 0, temp);
      }
    },

    // 工單下移
    moveDown(index) {
      if (index < this.orders.length - 1) {
        const temp = this.orders[index];
        this.orders.splice(index, 1);
        this.orders.splice(index + 1, 0, temp);
      }
    },

    // 批次送出工單
    handleSubmitOrders() {
      uni.showModal({
        title: "確認送出",
        content: "您確定要送出這些工單嗎？",
        success: (res) => {
          if (res.confirm) {
            console.log("📦 提交資料: ", this.orders);
            this.clearOrders();
          }
        },
      });
    },

    // 清空所有工單
    clearOrders() {
      this.orders = [];
    },
  },
};
</script>

<style scoped>
.container {
  padding: 10px;
  background-color: #f7f7f7;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.input-container {
  display: flex;
  margin-bottom: 15px;
  align-items: center;
}

.order-input {
  flex: 1;
  height: 35px;
  padding: 0 10px;
  margin-right: 10px;
  font-size: 14px;
}

.submit-button {
  height: 35px;
  width: 70px;
  font-size: 14px;
}

.order-list {
  margin-top: 15px;
  flex-grow: 1;
}

.order-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 10px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
}

.order-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.move-btns {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.move-btn {
  margin-right: 5px;
}

.order-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-text {
  font-size: 12px;
  margin-right: 10px;
}

.delete-btn {
  font-size: 12px;
  background-color: #f44;
  color: #fff;
  width: 60px;
}

.submit-orders-button {
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  font-size: 14px;
}

.submit-orders-button:disabled {
  background-color: #dcdcdc;
}
</style>
