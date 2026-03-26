import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})

// 请求拦截器：添加 token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：处理错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface Project {
  id: number
  name: string
  path: string
  year: number
  category: string
  description: string
  owner: string
  debugger: string
  improvements: string
  custom_fields: Record<string, string>
}

export interface CreateProjectInput {
  name: string
  path: string
  year: number
  category: string
  description: string
  owner: string
  debugger: string
  improvements: string
  custom_fields: Record<string, string>
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

export interface Tag {
  id: number
  name: string
  color: string
}

export interface CreateTagInput {
  name: string
  color: string
}

export interface SearchResult {
  id: number
  name: string
  path: string
  isDirectory: boolean
  projectId: number
  projectName: string
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
  preview: (fileId: number) => api.get(`/api/files/preview/${fileId}`, { responseType: 'blob' }),
  search: (query: string) => api.get<SearchResult[]>('/api/files/search', { params: { q: query } })
}

export const tagsApi = {
  getList: () => api.get<Tag[]>('/api/tags').then(res => res.data),
  create: (data: CreateTagInput) => api.post<Tag>('/api/tags', data).then(res => res.data),
  update: (id: number, data: Partial<CreateTagInput>) => api.put<Tag>(`/api/tags/${id}`, data).then(res => res.data),
  delete: (id: number) => api.delete(`/api/tags/${id}`),
  getFileTags: (fileId: number) => api.get<Tag[]>(`/api/files/${fileId}/tags`).then(res => res.data),
  addTagToFile: (fileId: number, tagId: number) => api.post(`/api/files/${fileId}/tags`, { tagId }),
  removeTagFromFile: (fileId: number, tagId: number) => api.delete(`/api/files/${fileId}/tags/${tagId}`)
}

export const favoritesApi = {
  getList: () => api.get<FileItem[]>('/api/favorites').then(res => res.data),
  add: (fileId: number) => api.post(`/api/favorites/${fileId}`),
  remove: (fileId: number) => api.delete(`/api/favorites/${fileId}`),
  check: (fileId: number) => api.get<boolean>(`/api/favorites/check/${fileId}`).then(res => res.data)
}

export interface User {
  id: number
  username: string
}

export const authApi = {
  login: (username: string, password: string) => 
    api.post<{ token: string; user: User }>('/api/auth/login', { username, password })
      .then(res => res.data),
  register: (username: string, password: string) => 
    api.post<{ message: string }>('/api/auth/register', { username, password })
      .then(res => res.data),
  getCurrentUser: () => 
    api.get<User>('/api/auth/me').then(res => res.data)
}

export default api
