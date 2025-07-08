<template>
  <view class="container">
    <u-list>
      <u-list-item v-for="(order, index) in orders" :key="index" :title="order.name">
        <view>工單號: {{ order.code }}</view>
        <view>物料數量: {{ order.materialCount }}</view>
      </u-list-item>
    </u-list>
    <u-list>
      <u-list-item v-for="(material, index) in materials" :key="index" :title="material.name">
        <view>物料編號: {{ material.code }}</view>
        <view>領料數量: {{ material.quantity }}</view>
      </u-list-item>
    </u-list>
    <u-button @click="submit">提交領料</u-button>
  </view>
</template>

<script>
export default {
  props: {
    orders: {
      type: Array,
      default: () => []
    },
    materials: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    submit() {
      // 提交領料資料的處理
      console.log('提交領料資料', this.orders, this.materials)
      // 在這裡發送 API 請求到後端
    }
  }
}
</script>

<style scoped>
/* 添加一些樣式 */
</style>
