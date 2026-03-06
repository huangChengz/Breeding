import axios from '@/api'

export interface BudgetSummary {
  equipment_budget: number
  data_processing_budget: number
  data_purchase_budget: number
  ai_model_budget: number
  rd_budget: number
  total_budget: number
}

export interface EquipmentBudget {
  id: string
  equipment_name: string
  equipment_type: string
  key_level: number
  unit_price: number
  total_price: number
  supplier?: string
  is_imported: boolean
  necessity_description?: string
  procurement_method?: string
}

export interface DatasetBudget {
  id: string
  data_name: string
  data_type: string
  data_total_tb: number
  processing_fee: number
  purchase_fee: number
  total_fee: number
  need_purchase: boolean
  data_description?: string
}

export interface AIModelBudget {
  id: string
  model_name: string
  model_type: string
  model_scale?: string
  parameter_count?: string
  function_type?: string
  estimated_total_fee: number
  model_description?: string
}

export interface RDProjectBudget {
  id: string
  rd_name: string
  rd_direction?: string
  rd_content?: string
  expected_output?: string
  estimated_fee: number
}

export const budgetApi = {
  // 获取预算汇总
  getSummary: (projectId: string) =>
    axios.get<BudgetSummary>(`/projects/${projectId}/budget-summary`),

  // 获取设备预算明细
  getEquipments: (projectId: string) =>
    axios.get<EquipmentBudget[]>(`/projects/${projectId}/budget-equipments`),

  // 获取数据预算明细
  getDatasets: (projectId: string) =>
    axios.get<DatasetBudget[]>(`/projects/${projectId}/budget-datasets`),

  // 获取AI模型预算明细
  getAIModels: (projectId: string) =>
    axios.get<AIModelBudget[]>(`/projects/${projectId}/budget-ai-models`),

  // 获取研发项目预算明细
  getRDProjects: (projectId: string) =>
    axios.get<RDProjectBudget[]>(`/projects/${projectId}/budget-rd-projects`),

  // 导出预算报表
  export: (projectId: string) =>
    axios.get(`/projects/${projectId}/budget-export`)
}
