import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { filesApi, type FileItem } from '../api'

export const useFilesStore = defineStore('files', () => {
  const currentProjectId = ref<number | null>(null)
  const currentPath = ref<string>('')
  const files = ref<FileItem[]>([])
  const loading = ref(false)
  const viewMode = ref<'list' | 'grid'>('list')
  const searchQuery = ref('')
  const pathStack = ref<string[]>([])

  const breadcrumbs = computed(() => {
    if (!currentPath.value) return []
    const parts = currentPath.value.split('/').filter(Boolean)
    const crumbs: { name: string; path: string }[] = []
    let accumPath = ''
    for (const part of parts) {
      accumPath += '/' + part
      crumbs.push({ name: part, path: accumPath })
    }
    return crumbs
  })

  const filteredFiles = computed(() => {
    if (!searchQuery.value) return files.value
    const query = searchQuery.value.toLowerCase()
    return files.value.filter(f => f.name.toLowerCase().includes(query))
  })

  async function browse(projectId: number, path: string = '') {
    loading.value = true
    try {
      currentProjectId.value = projectId
      currentPath.value = path
      files.value = await filesApi.browse({ projectId, path })
    } finally {
      loading.value = false
    }
  }

  function enterDirectory(dir: FileItem) {
    if (!dir.isDirectory) return
    pathStack.value.push(currentPath.value)
    currentPath.value = dir.path
    if (currentProjectId.value) {
      browse(currentProjectId.value, dir.path)
    }
  }

  function goBack() {
    const prevPath = pathStack.value.pop() || ''
    currentPath.value = prevPath
    if (currentProjectId.value) {
      browse(currentProjectId.value, prevPath)
    }
  }

  function goToPath(path: string) {
    currentPath.value = path
    if (currentProjectId.value) {
      browse(currentProjectId.value, path)
    }
  }

  function setViewMode(mode: 'list' | 'grid') {
    viewMode.value = mode
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  function refresh() {
    if (currentProjectId.value) {
      browse(currentProjectId.value, currentPath.value)
    }
  }

  return {
    currentProjectId,
    currentPath,
    files,
    loading,
    viewMode,
    searchQuery,
    breadcrumbs,
    filteredFiles,
    browse,
    enterDirectory,
    goBack,
    goToPath,
    setViewMode,
    setSearchQuery,
    refresh
  }
})
