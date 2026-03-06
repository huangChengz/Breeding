import axios from '@/api'

// ============ 类型定义 ============

export interface OutlineNode {
  id: string
  project_id: string
  parent_id?: string
  node_code: string
  node_title: string
  node_level: number
  species_ids: string[]
  content?: string
  is_leaf: boolean
  sort_order: number
  is_locked: boolean
  is_expanded: boolean
  created_at: string
  updated_at: string
  children: OutlineNode[]
}

export interface NodeReference {
  id: string
  project_id: string
  node_id: string
  ref_type_id: string
  ref_entity_type: string
  ref_entity_id: string
  reference_note?: string
  is_active: boolean
  created_at: string
}

export interface ReferenceType {
  id: string
  type_code: string
  type_name: string
  description?: string
  sort_order: number
}

export interface DocGeneration {
  id: string
  project_id: string
  node_id: string
  generation_content: string
  prompt_template_id?: string
  prompt_version?: string
  input_tokens?: number
  output_tokens?: number
  model_used?: string
  generation_source: string
  is_current_version: boolean
  parent_generation_id?: string
  entity_snapshot?: Record<string, any>
  generation_time_ms?: number
  cost_usd?: number
  created_by?: string
  created_at: string
}

// ============ API 函数 ============

export const outlineApi = {
  // 获取大纲树
  getTree: (projectId: string) =>
    axios.get<OutlineNode[]>(`/projects/${projectId}/outline`),

  // 创建节点
  createNode: (projectId: string, data: Partial<OutlineNode>) =>
    axios.post<OutlineNode>(`/projects/${projectId}/outline`, data),

  // 获取节点详情
  getNode: (nodeId: string) =>
    axios.get<OutlineNode>(`/outline/${nodeId}`),

  // 更新节点
  updateNode: (nodeId: string, data: Partial<OutlineNode>) =>
    axios.patch<OutlineNode>(`/outline/${nodeId}`, data),

  // 初始化大纲
  initializeOutline: (projectId: string) =>
    axios.post(`/projects/${projectId}/outline/initialize`),

  // 获取节点引用
  getReferences: (nodeId: string) =>
    axios.get<NodeReference[]>(`/outline/${nodeId}/references`),

  // 创建节点引用
  createReference: (nodeId: string, data: Partial<NodeReference>) =>
    axios.post<NodeReference>(`/outline/${nodeId}/references`, data),

  // 删除节点引用
  deleteReference: (referenceId: string) =>
    axios.delete(`/references/${referenceId}`),

  // 获取引用类型
  getReferenceTypes: () =>
    axios.get<ReferenceType[]>('/reference-types'),

  // 获取节点生成历史
  getGenerations: (nodeId: string) =>
    axios.get<DocGeneration[]>(`/outline/${nodeId}/generations`),

  // 创建生成记录
  createGeneration: (nodeId: string, data: Partial<DocGeneration>) =>
    axios.post<DocGeneration>(`/outline/${nodeId}/generations`, data)
}
