<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NEmpty, NList, NListItem, NThing, NSpin, NPopconfirm, NIcon, NTag } from 'naive-ui'
import { useFavoritesStore } from '../stores/favorites'
import { useFilesStore } from '../stores/files'
import { useProjectsStore } from '../stores/projects'
import { type FileItem } from '../api'

const favoritesStore = useFavoritesStore()
const filesStore = useFilesStore()
const projectsStore = useProjectsStore()

onMounted(async () => {
  await Promise.all([
    favoritesStore.fetchFavorites(),
    projectsStore.fetchProjects()
  ])
})

function handleRemoveFavorite(file: FileItem) {
  favoritesStore.removeFavorite(file.id)
}

function handleOpenFile(file: FileItem) {
  // 找到文件所属项目并导航
  // 由于favorites返回的文件没有projectId，需要通过path推断
  // 这里简化处理：分发事件让FileBrowser处理
  const event = new CustomEvent('navigate-to-file', {
    detail: { path: file.path, name: file.name }
  })
  window.dispatchEvent(event)
}

function formatSize(bytes: number) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="favorites-page">
    <div class="favorites-header">
      <h2>我的收藏</h2>
      <span class="count" v-if="favoritesStore.favorites.length > 0">
        共 {{ favoritesStore.favorites.length }} 个收藏
      </span>
    </div>

    <div class="favorites-content">
      <NSpin :show="favoritesStore.loading">
        <NEmpty v-if="favoritesStore.favorites.length === 0" description="暂无收藏文件">
          <template #extra>
            <p class="empty-hint">在文件浏览中点击收藏按钮添加文件到此处</p>
          </template>
        </NEmpty>
        <NList v-else hoverable>
          <NListItem
            v-for="file in favoritesStore.favorites"
            :key="file.id"
            class="favorite-item"
          >
            <NThing>
              <template #avatar>
                <div class="file-icon" @click="handleOpenFile(file)">
                  <svg v-if="file.isDirectory" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                </div>
              </template>
              <template #header>
                <div class="file-header">
                  <span class="file-name" @click="handleOpenFile(file)">{{ file.name }}</span>
                </div>
              </template>
              <template #description>
                <div class="file-meta">
                  <span v-if="!file.isDirectory">{{ formatSize(file.size) }}</span>
                  <span class="separator">·</span>
                  <span>{{ formatDate(file.modified) }}</span>
                  <span class="separator">·</span>
                  <span class="file-path">{{ file.path }}</span>
                </div>
              </template>
              <template #header-extra>
                <NPopconfirm @positive-click="handleRemoveFavorite(file)">
                  <template #trigger>
                    <NButton quaternary type="error" size="small">
                      <template #icon>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                      </template>
                    </NButton>
                  </template>
                  取消收藏 "{{ file.name }}"？
                </NPopconfirm>
              </template>
            </NThing>
          </NListItem>
        </NList>
      </NSpin>
    </div>
  </div>
</template>

<style scoped>
.favorites-page {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.favorites-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.favorites-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.count {
  font-size: 14px;
  color: #999;
}

.favorites-content {
  min-height: 300px;
}

.favorite-item {
  cursor: default;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #f5f5f5;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.file-icon:hover {
  background: #e6f4ff;
  color: #1890ff;
}

.file-name {
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.file-name:hover {
  color: #1890ff;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #999;
  flex-wrap: wrap;
}

.separator {
  color: #ddd;
}

.empty-hint {
  color: #999;
  font-size: 14px;
}
</style>
