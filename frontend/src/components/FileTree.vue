<script setup lang="ts">
import { computed } from 'vue'
import { NTree } from 'naive-ui'
import type { TreeOption } from 'naive-ui'
import type { FileItem } from '../api'

const props = defineProps<{
  files: FileItem[]
  currentPath: string
}>()

const emit = defineEmits<{
  (e: 'select', file: FileItem): void
  (e: 'navigate', path: string): void
}>()

const treeData = computed<TreeOption[]>(() => {
  return props.files
    .filter(f => f.isDirectory)
    .map(file => ({
      label: file.name,
      key: file.path,
      children: file.children ? convertToTreeOptions(file.children) : undefined,
      isLeaf: !file.children?.length
    }))
})

function convertToTreeOptions(files: FileItem[]): TreeOption[] {
  return files
    .filter(f => f.isDirectory)
    .map(file => ({
      label: file.name,
      key: file.path,
      children: file.children ? convertToTreeOptions(file.children) : undefined,
      isLeaf: !file.children?.length
    }))
}

function handleSelect(keys: string[], option: TreeOption[]) {
  if (option.length > 0) {
    emit('navigate', option[0].key as string)
  }
}
</script>

<template>
  <div class="file-tree">
    <NTree
      :data="treeData"
      :default-expand-all="false"
      selectable
      block-line
      @update:selected-keys="handleSelect"
    />
  </div>
</template>

<style scoped>
.file-tree {
  padding: 8px;
  height: 100%;
  overflow: auto;
}
</style>
