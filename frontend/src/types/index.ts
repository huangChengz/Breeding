export type UUID = string

export interface User {
  id: string
  username: string
  real_name?: string
  email?: string
  phone?: string
  department?: string
  status: number
  created_at: string
}

export interface Role {
  id: string
  role_code: string
  role_name: string
  description?: string
  is_system: boolean
}

export interface Permission {
  id: string
  perm_code: string
  perm_name: string
  module?: string
  description?: string
}

export interface Project {
  id: string
  project_name: string
  project_code?: string
  description?: string
  construction_period_months?: number
  location?: string
  owner_unit?: string
  status: number
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface CurrentUser {
  id: string
  username: string
  real_name?: string
  email?: string
  roles: string[]
}
