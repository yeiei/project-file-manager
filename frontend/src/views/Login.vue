<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import { authApi } from '../api'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const formRef = ref()
const formValue = ref({
  username: '',
  password: ''
})

const rules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur'
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: 'blur'
  }
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const { token, user } = await authApi.login(formValue.value.username, formValue.value.password)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    message.success('登录成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <NCard class="login-card" title="登录">
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        size="large"
      >
        <NFormItem path="username" label="用户名">
          <NInput
            v-model:value="formValue.username"
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </NFormItem>
        <NFormItem path="password" label="密码">
          <NInput
            v-model:value="formValue.password"
            type="password"
            placeholder="请输入密码"
            show-password-on="click"
            @keyup.enter="handleLogin"
          />
        </NFormItem>
        <NFormItem>
          <NButton
            type="primary"
            :loading="loading"
            block
            @click="handleLogin"
          >
            登录
          </NButton>
        </NFormItem>
        <div class="register-link">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.register-link {
  text-align: center;
  margin-top: 16px;
  color: #666;
}

.register-link a {
  color: #18a058;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
