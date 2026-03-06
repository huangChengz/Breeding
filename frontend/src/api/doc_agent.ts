import axios from '@/api'

export interface GenerationResult {
  content: string
  node_id: string
  generation_id: string
}

export const docAgentApi = {
  // 流式生成 (SSE)
  generateStream: (nodeId: string) => {
    return new EventSource(`/api/outline/${nodeId}/generate-stream`)
  },

  // 异步生成
  generate: (nodeId: string) =>
    axios.post<GenerationResult>(`/outline/${nodeId}/generate`),

  // 获取 Prompt 模板
  getTemplates: () =>
    axios.get<any[]>('/prompt-templates'),

  // 创建 Prompt 模板
  createTemplate: (data: any) =>
    axios.post('/prompt-templates', data)
}
