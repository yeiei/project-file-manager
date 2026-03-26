<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import { authApi } from '../api'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const formRef = ref()
const formValue = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: 'blur'
    },
    {
      min: 3,
      max: 20,
      message: '用户名长度为3-20个字符',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      message: '密码至少6位',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    {
      required: true,
      message: '请确认密码',
      trigger: 'blur'
    },
    {
      validator: (_: any, value: string) => {
        if (value !== formValue.value.password) {
          return new Error('两次输入的密码不一致')
        }
        return true
      },
      trigger: 'blur'
    }
  ]
}

const canSubmit = computed(() => {
  return formValue.value.username && 
         formValue.value.password && 
         formValue.value.confirmPassword &&
         formValue.value.password === formValue.value.confirmPassword
})

async function handleRegister() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authApi.register(
      formValue.value.username,
      formValue.value.password
    )
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    message.error(error.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-container">
    <NCard class="register-card" title="注册">
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        size="large"
      >
        <NFormItem path="username" label="用户名">
          <NInput
            v-model:value="formValue.username"
            placeholder="请输入用户名（3-20个字符）"
            @keyup.enter="handleRegister"
          />
        </NFormItem>
        <NFormItem path="password" label="密码">
          <NInput
            v-model:value="formValue.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            show-password-on="click"
            @keyup.enter="handleRegister"
          />
        </NFormItem>
        <NFormItem path="confirmPassword" label="确认密码">
          <NInput
            v-model:value="formValue.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password-on="click"
            @keyup.enter="handleRegister"
          />
        </NFormItem>
        <NFormItem>
          <NButton
            type="primary"
            :loading="loading"
            :disabled="!canSubmit"
            block
            @click="handleRegister"
          >
            注册
          </NButton>
        </NFormItem>
        <div class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 400px;
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: #666;
}

.login-link a {
  color: #18a058;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
