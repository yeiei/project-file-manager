<script setup lang="ts">
import { h } from 'vue'
import { NDataTable, NEmpty, NSpin, NButton } from 'naive-ui'
import type { FileItem } from '../api'

const props = defineProps<{
  files: FileItem[]
  loading: boolean
  viewMode: 'list' | 'grid'
  currentPath: string
}>()

const emit = defineEmits<{
  (e: 'enter', file: FileItem): void
  (e: 'preview', file: FileItem): void
  (e: 'back'): void
}>()

function formatSize(bytes: number): string {
  if (bytes === 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i]
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const columns = [
  {
    title: 'Name',
    key: 'name',
    width: 300,
    render: (row: FileItem) => {
      const iconSvg = row.isDirectory 
        ? '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>'
        : '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>'
      return h('div', { class: 'file-name-cell' }, [
        h('span', { class: 'file-icon', innerHTML: iconSvg }),
        h('span', { class: 'file-name' }, row.name)
      ])
    }
  },
  {
    title: 'Size',
    key: 'size',
    width: 100,
    render: (row: FileItem) => row.isDirectory ? '-' : formatSize(row.size)
  },
  {
    title: 'Modified',
    key: 'modifiedTime',
    render: (row: FileItem) => formatDate(row.modifiedTime)
  }
]

function handleRowClick(row: FileItem) {
  if (row.isDirectory) {
    emit('enter', row)
  } else {
    emit('preview', row)
  }
}
</script>

<template>
  <div class="file-list">
    <NSpin :show="loading">
      <div v-if="currentPath" class="back-bar">
        <NButton quaternary @click="emit('back')">
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          </template>
          Go Back
        </NButton>
      </div>
      
      <NEmpty v-if="!loading && files.length === 0" description="Directory is empty" />
      
      <template v-else>
        <!-- List View -->
        <NDataTable
          v-if="viewMode === 'list'"
          :columns="columns"
          :data="files"
          :row-class-name="() => 'file-row'"
          @click-row="handleRowClick"
          :single-line="false"
        />
        
        <!-- Grid View -->
        <div v-else class="grid-view">
          <div
            v-for="file in files"
            :key="file.id"
            class="grid-item"
            :class="{ 'is-directory': file.isDirectory }"
            @click="handleRowClick(file)"
          >
            <div class="grid-icon">
              <svg v-if="file.isDirectory" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f0a020" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="1.5"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
            </div>
            <div class="grid-name">{{ file.name }}</div>
            <div class="grid-size">{{ file.isDirectory ? '-' : formatSize(file.size) }}</div>
          </div>
        </div>
      </template>
    </NSpin>
  </div>
</template>

<style scoped>
.file-list {
  height: 100%;
  overflow: auto;
  padding: 16px;
}

.back-bar {
  margin-bottom: 12px;
}

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.grid-item:hover {
  background: #f5f5f5;
}

.grid-icon {
  margin-bottom: 8px;
}

.grid-name {
  font-size: 13px;
  text-align: center;
  word-break: break-all;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.grid-size {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.file-row) {
  cursor: pointer;
}

:deep(.file-row:hover) {
  background: #f5f5f5 !important;
}
</style>
