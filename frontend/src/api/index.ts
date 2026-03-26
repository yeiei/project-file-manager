import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
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

export const projectsApi = {
  getList: () => api.get<Project[]>('/api/projects').then(res => res.data),
  create: (data: CreateProjectInput) => api.post<Project>('/api/projects', data).then(res => res.data),
  delete: (id: number) => api.delete(`/api/projects/${id}`)
}

export default api
