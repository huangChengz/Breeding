import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  User, LoginRequest, TokenResponse, CurrentUser,
  Project, Role, Permission
} from '@/types'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  register: (data: { username: string; password: string; real_name?: string; email?: string }) =>
    api.post<User>('/auth/register', data),

  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/auth/login', data),

  getCurrentUser: () =>
    api.get<CurrentUser>('/auth/me')
}

// 项目 API
export const projectApi = {
  create: (data: Partial<Project>) =>
    api.post<Project>('/projects', data),

  list: (params?: { skip?: number; limit?: number }) =>
    api.get<Project[]>('/projects', { params }),

  get: (id: string) =>
    api.get<Project>(`/projects/${id}`),

  update: (id: string, data: Partial<Project>) =>
    api.patch<Project>(`/projects/${id}`, data),

  delete: (id: string) =>
    api.delete(`/projects/${id}`)
}

// 角色 API
export const roleApi = {
  list: () =>
    api.get<Role[]>('/roles')
}

// 权限 API
export const permissionApi = {
  list: () =>
    api.get<Permission[]>('/permissions')
}

export default api
