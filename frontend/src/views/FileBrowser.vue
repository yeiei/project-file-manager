<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { NLayout, NLayoutSider, NLayoutContent, NInput, NButton, NIcon, NBreadcrumb, NBreadcrumbItem, NDropdown, NModal, NImage, NSpin } from 'naive-ui'
import { useProjectsStore } from '../stores/projects'
import { useFilesStore } from '../stores/files'
import FileTree from '../components/FileTree.vue'
import FileList from '../components/FileList.vue'
import type { Project, FileItem } from '../api'

const projectsStore = useProjectsStore()
const filesStore = useFilesStore()

const searchQuery = ref('')
const previewVisible = ref(false)
const previewUrl = ref<string | null>(null)
const previewLoading = ref(false)
const selectedProject = ref<Project | null>(null)

onMounted(async () => {
  await projectsStore.fetchProjects()
  if (projectsStore.projects.length > 0) {
    selectProject(projectsStore.projects[0])
  }
})

function selectProject(project: Project) {
  selectedProject.value = project
  filesStore.browse(project.id)
}

function handleNavigate(path: string) {
  if (selectedProject.value) {
    filesStore.goToPath(path)
  }
}

function handleEnter(file: FileItem) {
  filesStore.enterDirectory(file)
}

async function handlePreview(file: FileItem) {
  if (!file.isDirectory) {
    previewLoading.value = true
    previewVisible.value = true
    try {
      const response = await fetch(`/api/files/preview/${file.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })
      const blob = await response.blob()
      previewUrl.value = URL.createObjectURL(blob)
    } catch (error) {
      console.error('Preview failed:', error)
      previewVisible.value = false
    } finally {
      previewLoading.value = false
    }
  }
}

function handleBack() {
  filesStore.goBack()
}

function handleRefresh() {
  filesStore.refresh()
}

function handleSearch() {
  filesStore.setSearchQuery(searchQuery.value)
}

function toggleView() {
  filesStore.setViewMode(filesStore.viewMode === 'list' ? 'grid' : 'list')
}

const viewModeOptions = [
  { label: '列表视图', key: 'list' },
  { label: '网格视图', key: 'grid' }
]

function handleViewModeSelect(key: string) {
  filesStore.setViewMode(key as 'list' | 'grid')
}
</script>

<template>
  <NLayout class="file-browser" has-sider>
    <!-- 左侧项目列表 -->
    <NLayoutSider
      bordered
      :width="240"
      :collapsed-width="64"
      collapse-mode="width"
      :native-scrollbar="true"
      content-style="padding: 12px;"
    >
      <div class="project-sidebar">
        <h3 class="sidebar-title">项目列表</h3>
        <div class="project-list">
          <div
            v-for="project in projectsStore.projects"
            :key="project.id"
            class="project-item"
            :class="{ active: selectedProject?.id === project.id }"
            @click="selectProject(project)"
          >
            <div class="project-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            </div>
            <div class="project-info">
              <div class="project-name">{{ project.name }}</div>
              <div class="project-meta">{{ project.year }} · {{ project.category }}</div>
            </div>
          </div>
        </div>
      </div>
    </NLayoutSider>

    <!-- 右侧文件浏览区 -->
    <NLayout>
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <NBreadcrumb>
            <NBreadcrumbItem>
              <span class="breadcrumb-root" @click="filesStore.goToPath('')">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                {{ selectedProject?.name || '选择项目' }}
              </span>
            </NBreadcrumbItem>
            <NBreadcrumbItem v-for="crumb in filesStore.breadcrumbs" :key="crumb.path">
              <span @click="filesStore.goToPath(crumb.path)">{{ crumb.name }}</span>
            </NBreadcrumbItem>
          </NBreadcrumb>
        </div>
        
        <div class="toolbar-right">
          <NInput
            v-model:value="searchQuery"
            placeholder="搜索文件..."
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </template>
          </NInput>
          
          <NButton quaternary @click="handleRefresh" title="刷新">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
            </template>
          </NButton>
          
          <NDropdown
            :options="viewModeOptions"
            @select="handleViewModeSelect"
            trigger="click"
          >
            <NButton quaternary title="切换视图">
              <template #icon>
                <svg v-if="filesStore.viewMode === 'list'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
              </template>
            </NButton>
          </NDropdown>
        </div>
      </div>

      <!-- 文件列表区域 -->
      <NLayoutContent content-style="padding: 0;">
        <div class="content-area">
          <FileTree
            v-if="filesStore.files.length > 0"
            :files="filesStore.files"
            :current-path="filesStore.currentPath"
            @navigate="handleNavigate"
          />
          <FileList
            :files="filesStore.filteredFiles"
            :loading="filesStore.loading"
            :view-mode="filesStore.viewMode"
            :current-path="filesStore.currentPath"
            @enter="handleEnter"
            @preview="handlePreview"
            @back="handleBack"
          />
        </div>
      </NLayoutContent>
    </NLayout>

    <!-- 预览弹窗 -->
    <NModal
      v-model:show="previewVisible"
      preset="card"
      title="文件预览"
      style="width: 80%; max-width: 900px;"
      :mask-closable="true"
    >
      <NSpin :show="previewLoading">
        <NImage
          v-if="previewUrl"
          :src="previewUrl"
          object-fit="contain"
          style="width: 100%; max-height: 70vh;"
        />
        <div v-else-if="!previewLoading" style="text-align: center; padding: 40px; color: #999;">
          预览不可用
        </div>
      </NSpin>
    </NModal>
  </NLayout>
</template>

<style scoped>
.file-browser {
  height: 100vh;
}

.project-sidebar {
  height: 100%;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  padding: 0 8px;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.project-item:hover {
  background: #f5f5f5;
}

.project-item.active {
  background: #e6f4ff;
}

.project-icon {
  flex-shrink: 0;
  color: #666;
}

.project-info {
  flex: 1;
  overflow: hidden;
}

.project-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-meta {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.breadcrumb-root {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #666;
}

.breadcrumb-root:hover {
  color: #1890ff;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-area {
  display: flex;
  height: calc(100vh - 56px);
  background: #fff;
}
</style>
