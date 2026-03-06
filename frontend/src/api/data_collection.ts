import axios from '@/api'
import type { UUID } from '@/types'

// ============ 类型定义 ============

export interface Scene {
  id: string
  project_id: string
  species_id?: string
  scene_name: string
  scene_description?: string
  research_output_type?: string
  data_output_type?: string
  data_total_tb?: number
  file_size_description?: string
  data_output_description?: string
  created_at: string
}

export interface Equipment {
  id: string
  project_id: string
  scene_ids: string[]
  equipment_name: string
  equipment_type: string
  key_level: number
  procurement_method?: string
  usage_plan?: string
  unit_price?: number
  total_price: number
  supplier?: string
  is_imported: boolean
  origin_country?: string
  necessity_description?: string
  plan_usage_value?: number
  plan_usage_unit?: string
  plan_usage_description?: string
  created_at: string
}

export interface Dataset {
  id: string
  project_id: string
  data_name: string
  data_type: string
  other_data_type?: string
  data_total_tb?: number
  access_permission: string
  is_shared_with_lab: boolean
  source_equipment_ids: string[]
  scene_ids: string[]
  data_description?: string
  processing_fee: number
  compute_cycle_value?: number
  compute_cycle_unit?: string
  compute_cycle_total_days?: number
  source_cycle_months?: number
  cycle_data_gb?: number
  need_purchase: boolean
  purchase_fee: number
  created_at: string
}

export interface AIModel {
  id: string
  project_id: string
  model_name: string
  model_description?: string
  model_type: string
  model_scale?: string
  parameter_count?: string
  function_type?: string
  related_data_ids: string[]
  scene_ids: string[]
  estimated_total_fee: number
  created_at: string
}

export interface RDProject {
  id: string
  project_id: string
  rd_name: string
  rd_direction?: string
  rd_content?: string
  expected_output?: string
  estimated_fee: number
  scene_ids: string[]
  created_at: string
}

export interface Species {
  id: string
  species_code: string
  species_name: string
  category: string
  description?: string
}

export interface Dictionary {
  id: string
  dict_type: string
  dict_code: string
  dict_label: string
  dict_value?: string
}

// ============ API 函数 ============

// 场景
export const sceneApi = {
  list: (projectId: string) =>
    axios.get<Scene[]>(`/projects/${projectId}/scenes`),

  get: (id: string) =>
    axios.get<Scene>(`/scenes/${id}`),

  create: (projectId: string, data: Partial<Scene>) =>
    axios.post<Scene>(`/projects/${projectId}/scenes`, data),

  update: (id: string, data: Partial<Scene>) =>
    axios.patch<Scene>(`/scenes/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/scenes/${id}`)
}

// 设备
export const equipmentApi = {
  list: (projectId: string) =>
    axios.get<Equipment[]>(`/projects/${projectId}/equipments`),

  get: (id: string) =>
    axios.get<Equipment>(`/equipments/${id}`),

  create: (projectId: string, data: Partial<Equipment>) =>
    axios.post<Equipment>(`/projects/${projectId}/equipments`, data),

  update: (id: string, data: Partial<Equipment>) =>
    axios.patch<Equipment>(`/equipments/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/equipments/${id}`)
}

// 数据集
export const datasetApi = {
  list: (projectId: string) =>
    axios.get<Dataset[]>(`/projects/${projectId}/datasets`),

  get: (id: string) =>
    axios.get<Dataset>(`/datasets/${id}`),

  create: (projectId: string, data: Partial<Dataset>) =>
    axios.post<Dataset>(`/projects/${projectId}/datasets`, data),

  update: (id: string, data: Partial<Dataset>) =>
    axios.patch<Dataset>(`/datasets/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/datasets/${id}`)
}

// AI模型
export const aiModelApi = {
  list: (projectId: string) =>
    axios.get<AIModel[]>(`/projects/${projectId}/ai-models`),

  get: (id: string) =>
    axios.get<AIModel>(`/ai-models/${id}`),

  create: (projectId: string, data: Partial<AIModel>) =>
    axios.post<AIModel>(`/projects/${projectId}/ai-models`, data),

  update: (id: string, data: Partial<AIModel>) =>
    axios.patch<AIModel>(`/ai-models/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/ai-models/${id}`)
}

// 研发项目
export const rdProjectApi = {
  list: (projectId: string) =>
    axios.get<RDProject[]>(`/projects/${projectId}/rd-projects`),

  get: (id: string) =>
    axios.get<RDProject>(`/rd-projects/${id}`),

  create: (projectId: string, data: Partial<RDProject>) =>
    axios.post<RDProject>(`/projects/${projectId}/rd-projects`, data),

  update: (id: string, data: Partial<RDProject>) =>
    axios.patch<RDProject>(`/rd-projects/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/rd-projects/${id}`)
}

// 字典
export const dictionaryApi = {
  list: (dictType?: string) =>
    axios.get<Dictionary[]>('/dictionaries', { params: { dict_type: dictType } }),

  create: (data: Partial<Dictionary>) =>
    axios.post<Dictionary>('/dictionaries', data),

  update: (id: string, data: Partial<Dictionary>) =>
    axios.patch<Dictionary>(`/dictionaries/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/dictionaries/${id}`)
}

// 物种
export const speciesApi = {
  list: () =>
    axios.get<Species[]>('/species'),

  create: (data: Partial<Species>) =>
    axios.post<Species>('/species', data),

  update: (id: string, data: Partial<Species>) =>
    axios.patch<Species>(`/species/${id}`, data),

  delete: (id: string) =>
    axios.delete(`/species/${id}`)
}
