import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

export interface Project {
  id: number
  name: string
  path: string
  year: number
  category: string
  description: string
}

export interface CreateProjectInput {
  name: string
  path: string
  year: number
  category: string
  description: string
}

export interface FileItem {
  id: number
  name: string
  path: string
  isDirectory: boolean
  size: number
  modified: string
  children?: FileItem[]
}

export interface BrowseParams {
  project_id: number
  path?: string
}

export const projectsApi = {
  getList: () => api.get<Project[]>('/api/projects').then(res => res.data),
  create: (data: CreateProjectInput) => api.post<Project>('/api/projects', data).then(res => res.data),
  delete: (id: number) => api.delete(`/api/projects/${id}`)
}

export const filesApi = {
  browse: (params: BrowseParams) => api.get<{path: string, items: FileItem[]}>('/api/files/browse', { params }).then(res => res.data.items),
  preview: (fileId: number) => api.get(`/api/files/preview/${fileId}`, { responseType: 'blob' })
}

export default api
