<template>
  <view class="container">
    <view style="padding: 20px">
      <u--form ref="formRef" label-position="left" label-width="100px" :model="form" :rules="rules">
        <u-form-item label="用戶姓名" prop="name" border-bottom :required="true">
          <u--input v-model="form.name" placeholder="請輸入用戶姓名" border="none"></u--input>
        </u-form-item>
        <u-form-item label="用戶簡稱" prop="nickname" border-bottom :required="false">
          <u--input v-model="form.nickname" placeholder="請輸入用戶簡稱" border="none"></u--input>
        </u-form-item>
        <u-form-item label="工號" prop="telephone" border-bottom :required="true">
          <u--input v-model="form.telephone" placeholder="請輸入工號" border="none"></u--input>
        </u-form-item>
        <u-form-item label="用户性别" prop="gender" border-bottom :required="false">
          <u-radio-group v-model="form.gender">
            <u-radio
              v-for="(item, index) in genderOptions"
              :key="index"
              :custom-style="{ marginRight: '16px' }"
              :label="item.label"
              :name="item.value"
            >
            </u-radio>
          </u-radio-group>
        </u-form-item>
      </u--form>
      <view style="margin-top: 20px">
        <u-button :loading="btnLoading" type="primary" text="提交" @click="submit"> </u-button>
      </view>
    </view>
  </view>
</template>

<script>
import { getInfo } from '@/common/request/api/login'
import { updateCurrentUser } from '@/common/request/api/vadmin/auth/user.js'

export default {
  data() {
    return {
      btnLoading: false,
      form: {
        name: '',
        nickname: '',
        telephone: '',
        gender: ''
      },
      rules: {
        name: {
          type: 'string',
          required: true,
          message: '請填寫姓名',
          trigger: ['blur', 'change']
        },
        telephone: [
          {
            type: 'string',
            required: true,
            message: '請填寫正確工號',
            trigger: ['blur', 'change']
          },
          {
            validator: (rule, value, callback) => {
              // 上面有说，返回true表示校验通过，返回false表示不通过
              // uni.$u.test.mobile()就是返回true或者false的
              return uni.$u.test.mobile(value)
            },
            message: '工號不正確',
            // 触发器可以同时用blur和change
            trigger: ['change', 'blur']
          }
        ]
      },
      genderOptions: []
    }
  },
  onLoad() {
    this.$store.dispatch('dict/getDicts', ['sys_vadmin_gender']).then((result) => {
      this.genderOptions = result.sys_vadmin_gender
    })
    // this.resetForm()
    this.getUser()
  },
  onReady() {
    //onReady 为uni-app支持的生命周期之一
    this.$refs.formRef.setRules(this.rules)
  },
  methods: {
    resetForm() {
      this.form = {
        name: '',
        nickname: '',
        telephone: '',
        gender: ''
      }
    },
    getUser() {
      this.$modal.loading('載入中')
      getInfo()
        .then((res) => {
          this.form = res.data
        })
        .finally(() => {
          this.$modal.closeLoading()
        })
    },
    submit(ref) {
      this.$refs.formRef.validate().then((res) => {
        this.btnLoading = true
        updateCurrentUser(this.form)
          .then((res) => {
            this.$store.dispatch('auth/UpdateInfo', res.data)
            this.$modal.msgSuccess('更新成功')
          })
          .finally(() => {
            this.btnLoading = false
          })
      })
    }
  }
}
</script>

<style lang="scss">
page {
  background-color: #ffffff;
}
</style>
