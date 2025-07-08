<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { computed, reactive, ref, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'
import { postCurrentUserResetPassword } from '@/api/vadmin/auth/user'
import { getRoleMenusApi } from '@/api/login'
import { usePermissionStore } from '@/store/modules/permission'
import { RouteLocationNormalizedLoaded, RouteRecordRaw, useRouter } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import { Footer } from '@/components/Footer'

const { required } = useValidator()
const { addRoute, push, currentRoute } = useRouter()

const authStore = useAuthStore()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const footer = computed(() => appStore.getFooter)

const formSchema = reactive<FormSchema[]>([
  {
    field: 'password',
    label: '新密碼',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: '請輸入新密碼'
    }
  },
  {
    field: 'password_two',
    label: '再次輸入新密碼',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: '請再次輸入新密碼'
    }
  }
])

const rules = {
  password: [
    required(),
    { min: 8, max: 16, message: '長度需為8-16個字符,請重新輸入。', trigger: 'blur' }
  ],
  password_two: [
    required(),
    { min: 8, max: 16, message: '長度需為8-16個字符,請重新輸入。', trigger: 'blur' }
  ]
}

const { formRegister, formMethods } = useForm()
const { setValues, getFormData, getElFormExpose } = formMethods

setValues(authStore.getUser)

const loading = ref(false)
const redirect = ref<string>('')

watch(
  () => currentRoute.value,
  (route: RouteLocationNormalizedLoaded) => {
    redirect.value = route?.query?.redirect as string
  },
  {
    immediate: true
  }
)

// 提交
const save = async () => {
  if (authStore.getUser.id === 1) {
    return ElMessage.warning('編輯帳號為演示帳號，無權限操作！')
  }
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate()
  if (valid) {
    loading.value = true
    const formData = await getFormData()
    try {
      const res = await postCurrentUserResetPassword(formData)
      if (res) {
        // 是否使用動態路由
        getMenu()
      } else {
        loading.value = false
      }
    } catch (e: any) {
      loading.value = false
    }
  }
}

// 獲取用户選單信息
const getMenu = async () => {
  const res = await getRoleMenusApi()
  if (res) {
    const routers = res.data || []
    await permissionStore.generateRoutes(routers).catch(() => {})
    permissionStore.getAddRouters.forEach((route) => {
      addRoute(route as RouteRecordRaw) // 動態添加可訪問路由表
    })
    permissionStore.setIsAddRouters(true)
    push({ path: redirect.value || permissionStore.addRouters[0].path })
  }
}
</script>

<template>
  <div class="main-container">
    <div class="form-container">
      <div>
        <h2 class="text-2xl font-bold text-center w-[100%]">第一次登錄系统，需先重置密碼</h2>
      </div>
      <Form
        @register="formRegister"
        :schema="formSchema"
        :rules="rules"
        hide-required-asterisk
        class="dark:(border-1 border-[var(--el-border-color)] border-solid)"
      />
      <div class="w-[100%]">
        <BaseButton :loading="loading" type="primary" class="w-[100%]" @click="save">
          重置密碼
        </BaseButton>
      </div>
    </div>

    <div class="footer-container">
      <Footer v-if="footer" />
    </div>
  </div>
</template>

<style lang="less" scoped>
:deep(.anticon) {
  &:hover {
    color: var(--el-color-primary) !important;
  }
}

.main-container {
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  width: 100%;
  height: 100%;
  background-color: var(--app-content-bg-color);
  position: relative;
}

.main-container .form-container {
  width: 500px;
  align-self: center;
  padding: 30px;
  background-color: #fff;
  border-radius: 30px;
}

.footer-container {
  position: absolute;
  bottom: 0;
  margin-bottom: 20px;
  width: 100%;
}
</style>
