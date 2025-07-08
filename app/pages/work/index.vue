<template>
  <view class="work-container">
    <!-- 轮播图 -->
    <u-swiper
      :list="images"
      indicator
      indicator-mode="line"
      circular
      :height="`${windowWidth / 2.5}px`"
    ></u-swiper>

    <!-- 宫格组件 -->
    <view class="grid-body">
      <u-grid :border="false" col="3">
        <u-grid-item v-for="(item, index) in baseList" :key="index" @click="changeGrid(item)">
          <view class="grid-item">
            <view :class="'iconfont ' + item.icon + ' grid-icon'"></view>
            <u--text :text="item.title" align="center" line-height="32px"></u--text>
          </view>
        </u-grid-item>
      </u-grid>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      windowWidth: uni.getSystemInfoSync().windowWidth,
      images: [
        'https://i.imgur.com/FUWEnuV.png',
        '/static/images/banner/banner03.jpg',
        '/static/images/banner/banner03.jpg'
      ],
      baseList: [
        {
          icon: 'icon-user1',
          title: '來一台',
          path: '/pages/mes/production/index'  // 只有生產領料頁面設計好，其他顯示設計中
        },
        {
          icon: 'icon-user2',
          title: '列印保證書/外箱'
        },
        {
          icon: 'icon-user3',
          title: '入庫管理'
        },
        {
          icon: 'icon-caidan2',
          title: '生產領料',
          path: '/pages/WMS/material-issue/index'  // 只有生產領料頁面設計好，其他顯示設計中
        }
      ]
    }
  },
  methods: {
    changeGrid(item) {
      if (item.path) {
        // 跳轉到指定頁面
        uni.navigateTo({
          url: item.path
        });
      } else {
        // 顯示模塊建設中的提示
        this.$modal.showToast('模塊建設中~');
      }
    }
  }
}
</script>

<style lang="scss">
page {
  background-color: #fff;
  min-height: 100%;
  height: auto;
}
</style>

<style lang="scss" scoped>
.grid-body {
  margin-top: 60rpx;

  .grid-item {
    margin-bottom: 30rpx;
    text-align: center;
  }

  .grid-icon {
    font-size: 40rpx;
  }
}
</style>
