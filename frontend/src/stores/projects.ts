import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectsApi, type Project, type CreateProjectInput } from '../api'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const loading = ref(false)

  const fetchProjects = async () => {
    loading.value = true
    try {
      projects.value = await projectsApi.getList()
    } finally {
      loading.value = false
    }
  }

  const createProject = async (input: CreateProjectInput) => {
    const newProject = await projectsApi.create(input)
    projects.value.push(newProject)
  }

  const deleteProject = async (id: number) => {
    await projectsApi.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  return {
    projects,
    loading,
    fetchProjects,
    createProject,
    deleteProject
  }
})
