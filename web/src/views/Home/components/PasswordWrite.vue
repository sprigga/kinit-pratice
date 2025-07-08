<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { reactive, ref } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'
import { postCurrentUserResetPassword } from '@/api/vadmin/auth/user'
import { BaseButton } from '@/components/Button'

const { required } = useValidator()

const authStore = useAuthStore()

const formSchema = reactive<FormSchema[]>([
  {
    field: 'title',
    colProps: {
      span: 24
    }
  },
  {
    field: 'password',
    label: '新密碼',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '50%'
      },
      placeholder: '請輸入新密碼'
    }
  },
  {
    field: 'password_two',
    label: '確認密碼',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '50%'
      },
      placeholder: '請再次輸入新密碼'
    }
  },
  {
    field: 'save',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <>
              <div class="w-[50%]">
                <BaseButton loading={loading.value} type="primary" class="w-[100%]" onClick={save}>
                  保存
                </BaseButton>
              </div>
            </>
          )
        }
      }
    }
  }
])

const rules = {
  password: [
    required(),
    { min: 8, max: 16, message: '長度需為8-16个字符,請重新輸入。', trigger: 'blur' }
  ],
  password_two: [
    required(),
    { min: 8, max: 16, message: '長度需為8-16个字符,請重新輸入。', trigger: 'blur' }
  ]
}

const { formRegister, formMethods } = useForm()
const { setValues, getFormData, getElFormExpose } = formMethods

setValues(authStore.getUser)

const loading = ref(false)

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
        elForm?.resetFields()
        authStore.logout()
        ElMessage.warning('請重新登錄')
      }
    } finally {
      loading.value = false
    }
  }
}
</script>

<template>
  <Form
    @register="formRegister"
    :schema="formSchema"
    :rules="rules"
    hide-required-asterisk
    class="dark:(border-1 border-[var(--el-border-color)] border-solid)"
  />
</template>
