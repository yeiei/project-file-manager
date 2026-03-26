<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NInput, NButton, NList, NListItem, NThing, NEmpty, NSpin, NIcon } from 'naive-ui'
import { useFilesStore } from '../stores/files'
import { useProjectsStore } from '../stores/projects'
import { filesApi, type SearchResult } from '../api'

const filesStore = useFilesStore()
const projectsStore = useProjectsStore()

const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const searching = ref(false)
const hasSearched = ref(false)

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  
  searching.value = true
  hasSearched.value = true
  try {
    searchResults.value = await filesApi.search(searchQuery.value)
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

function handleResultClick(result: SearchResult) {
  // 切换到文件浏览并导航到对应文件
  // 通过事件或者路由来触发
  const event = new CustomEvent('navigate-to-file', {
    detail: { projectId: result.projectId, path: result.path }
  })
  window.dispatchEvent(event)
}

function formatPath(path: string) {
  return path || '/'
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
})
</script>

<template>
  <div class="search-page">
    <div class="search-header">
      <h2>搜索文件</h2>
      <div class="search-form">
        <NInput
          v-model:value="searchQuery"
          placeholder="输入文件名或内容关键词..."
          clearable
          size="large"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </template>
        </NInput>
        <NButton type="primary" size="large" @click="handleSearch" :loading="searching">
          搜索
        </NButton>
      </div>
    </div>

    <div class="search-results">
      <NSpin :show="searching">
        <NEmpty v-if="hasSearched && searchResults.length === 0 && !searching" description="未找到相关文件" />
        <NList v-else-if="searchResults.length > 0" hoverable clickable>
          <NListItem
            v-for="result in searchResults"
            :key="result.id"
            @click="handleResultClick(result)"
          >
            <NThing>
              <template #avatar>
                <div class="file-icon">
                  <svg v-if="result.isDirectory" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                </div>
              </template>
              <template #header>
                <span class="file-name">{{ result.name }}</span>
              </template>
              <template #description>
                <div class="file-meta">
                  <span class="project-name">{{ result.projectName }}</span>
                  <span class="separator">/</span>
                  <span class="file-path">{{ formatPath(result.path) }}</span>
                </div>
              </template>
            </NThing>
          </NListItem>
        </NList>
        <div v-else-if="!hasSearched" class="empty-hint">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <p>输入关键词搜索项目中的文件</p>
        </div>
      </NSpin>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.search-header {
  margin-bottom: 24px;
}

.search-header h2 {
  margin-bottom: 16px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.search-form {
  display: flex;
  gap: 12px;
}

.search-form :deep(.n-input) {
  flex: 1;
}

.search-results {
  min-height: 300px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f5f5f5;
  border-radius: 8px;
  color: #666;
}

.file-name {
  font-weight: 500;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #999;
}

.project-name {
  color: #1890ff;
}

.separator {
  color: #ddd;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-hint svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-hint p {
  font-size: 14px;
}
</style>
