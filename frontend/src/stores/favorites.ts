import { defineStore } from 'pinia'
import { ref } from 'vue'
import { favoritesApi, type FileItem } from '../api'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<FileItem[]>([])
  const loading = ref(false)

  const fetchFavorites = async () => {
    loading.value = true
    try {
      favorites.value = await favoritesApi.getList()
    } finally {
      loading.value = false
    }
  }

  const addFavorite = async (fileId: number) => {
    await favoritesApi.add(fileId)
    await fetchFavorites()
  }

  const removeFavorite = async (fileId: number) => {
    await favoritesApi.remove(fileId)
    favorites.value = favorites.value.filter(f => f.id !== fileId)
  }

  const checkFavorite = async (fileId: number): Promise<boolean> => {
    return await favoritesApi.check(fileId)
  }

  return {
    favorites,
    loading,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    checkFavorite
  }
})
