<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NConfigProvider, NMessageProvider, NDialogProvider, NTabs, NTabPane, NLayout, NLayoutHeader, NLayoutContent, NButton, NSpace, NAvatar } from 'naive-ui'
import Projects from '../views/Projects.vue'
import FileBrowser from '../views/FileBrowser.vue'
import Search from '../views/Search.vue'
import Tags from '../views/Tags.vue'
import Favorites from '../views/Favorites.vue'
import type { User } from '../api'

const router = useRouter()
const activeTab = ref('projects')
const currentUser = ref<User | null>(null)

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    currentUser.value = JSON.parse(userStr)
  }
})

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<template>
  <NConfigProvider>
    <NMessageProvider>
      <NDialogProvider>
        <NLayout class="app-layout">
          <NLayoutHeader class="app-header" bordered>
            <div class="header-content">
              <div class="app-title">项目文件管理系统</div>
              <NSpace align="center" :size="12">
                <NAvatar round size="small">👤</NAvatar>
                <span class="username">{{ currentUser?.username }}</span>
                <NButton size="small" quaternary @click="handleLogout">退出</NButton>
              </NSpace>
            </div>
          </NLayoutHeader>
          <NLayoutContent>
            <NTabs v-model:value="activeTab" type="line" animated>
              <NTabPane name="projects" tab="项目管理">
                <Projects />
              </NTabPane>
              <NTabPane name="files" tab="文件浏览">
                <FileBrowser />
              </NTabPane>
              <NTabPane name="search" tab="搜索">
                <Search />
              </NTabPane>
              <NTabPane name="tags" tab="标签">
                <Tags />
              </NTabPane>
              <NTabPane name="favorites" tab="收藏">
                <Favorites />
              </NTabPane>
            </NTabs>
          </NLayoutContent>
        </NLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style scoped>
.app-layout {
  height: 100vh;
}

.app-header {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #fff;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.username {
  color: #666;
}
</style>
