import axios from '@/api'

export interface GenerationResult {
  content: string
  node_id: string
  generation_id: string
}

export interface OptimizeResult {
  content: string
  node_id: string
  generation_id: string
  optimize_type: string
}

export interface SetCurrentVersionResult {
  success: boolean
  generation_id: string
  content: string
}

export const docAgentApi = {
  // 流式生成 (SSE)
  generateStream: (nodeId: string) => {
    return new EventSource(`/api/outline/${nodeId}/generate-stream`)
  },

  // 异步生成
  generate: (nodeId: string) =>
    axios.post<GenerationResult>(`/outline/${nodeId}/generate`),

  // 内容优化
  optimize: (nodeId: string, content: string, optimizeType: string = 'polish') =>
    axios.post<OptimizeResult>(`/outline/${nodeId}/optimize`, {
      content,
      optimize_type: optimizeType
    }),

  // 设置当前版本
  setCurrentVersion: (nodeId: string, generationId: string) =>
    axios.post<SetCurrentVersionResult>(`/outline/${nodeId}/generations/${generationId}/set-current`),

  // 获取 Prompt 模板
  getTemplates: () =>
    axios.get<any[]>('/prompt-templates'),

  // 创建 Prompt 模板
  createTemplate: (data: any) =>
    axios.post('/prompt-templates', data)
}
