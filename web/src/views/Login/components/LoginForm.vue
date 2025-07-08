<script setup lang="tsx">
import { reactive, ref, watch } from 'vue'
import { Form } from '@/components/Form'
import { useI18n } from '@/hooks/web/useI18n'
import { ElCheckbox, ElLink } from 'element-plus'
import { useForm } from '@/hooks/web/useForm'
import { getRoleMenusApi } from '@/api/login'
import { useAuthStore } from '@/store/modules/auth'
import { usePermissionStore } from '@/store/modules/permission'
import { useRouter } from 'vue-router'
import type { RouteLocationNormalizedLoaded, RouteRecordRaw } from 'vue-router'
import { UserLoginType } from '@/api/login/types'
import { useValidator } from '@/hooks/web/useValidator'
import { FormSchema } from '@/components/Form'
import { Icon } from '@/components/Icon'
import { BaseButton } from '@/components/Button'

const emit = defineEmits(['to-telephone'])

const { required } = useValidator()

const permissionStore = usePermissionStore()

const authStore = useAuthStore()

const { currentRoute, addRoute, push } = useRouter()

const { t } = useI18n()

const remember = ref(false)
const hoverColor = 'var(--el-color-primary)'

const rules = {
  telephone: [required()],
  method: [required()],
  password: [required()]
}

const schema = reactive<FormSchema[]>([
  {
    field: 'title',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return <h2 class="text-2xl font-bold text-center w-[100%]">{t('login.login')}</h2>
        }
      }
    }
  },
  {
    field: 'telephone',
    label: t('login.telephone'),
    value: '',
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: t('login.telephonePlaceholder'),
      maxlength: 11
    }
  },
  {
    field: 'password',
    label: t('login.password'),
    value: '',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: t('login.passwordPlaceholder')
    }
  },
  {
    field: 'method',
    label: '登錄類型',
    value: '0',
    component: 'Input',
    hidden: true
  },
  {
    field: 'login',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <>
              <div class="w-[100%]">
                <BaseButton
                  loading={loading.value}
                  type="primary"
                  class="w-[100%]"
                  onClick={signIn}
                >
                  {t('login.login')}
                </BaseButton>
              </div>
            </>
          )
        }
      }
    }
  }
])

const iconSize = 30
const { formRegister, formMethods } = useForm()
const { getFormData, getElFormExpose } = formMethods
const loading = ref(false)
const iconColor = '#999'
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

// 登錄
const signIn = async () => {
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate()
  if (valid) {
    loading.value = true
    const formData: UserLoginType = await getFormData()
    try {
      const res = await authStore.login(formData)
      if (res) {
        if (!res.data.is_reset_password) {
          // 重置密碼
          push({ path: '/reset/password' })
        } else {
          // 獲取動態路由
          getMenu()
        }
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

// 手機驗證碼登錄
const toTelephoneLogin = () => {
  emit('to-telephone')
}
</script>

<template>
  <Form
    :schema="schema"
    :rules="rules"
    label-position="top"
    hide-required-asterisk
    size="large"
    class="dark:(border-1 border-[var(--el-border-color)] border-solid)"
    @register="formRegister"
  />
</template>
