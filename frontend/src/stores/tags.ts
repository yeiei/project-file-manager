import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi, type Tag, type CreateTagInput } from '../api'

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  const fetchTags = async () => {
    loading.value = true
    try {
      tags.value = await tagsApi.getList()
    } finally {
      loading.value = false
    }
  }

  const createTag = async (input: CreateTagInput) => {
    const newTag = await tagsApi.create(input)
    tags.value.push(newTag)
    return newTag
  }

  const updateTag = async (id: number, input: Partial<CreateTagInput>) => {
    const updated = await tagsApi.update(id, input)
    const index = tags.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tags.value[index] = updated
    }
    return updated
  }

  const deleteTag = async (id: number) => {
    await tagsApi.delete(id)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  const getFileTags = async (fileId: number): Promise<Tag[]> => {
    return await tagsApi.getFileTags(fileId)
  }

  const addTagToFile = async (fileId: number, tagId: number) => {
    await tagsApi.addTagToFile(fileId, tagId)
  }

  const removeTagFromFile = async (fileId: number, tagId: number) => {
    await tagsApi.removeTagFromFile(fileId, tagId)
  }

  return {
    tags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    getFileTags,
    addTagToFile,
    removeTagFromFile
  }
})
