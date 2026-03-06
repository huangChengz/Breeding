<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { outlineApi } from '@/api/outline'
import { sceneApi, equipmentApi, aiModelApi } from '@/api/data_collection'
import { docAgentApi } from '@/api/doc_agent'
import type { OutlineNode, NodeReference, ReferenceType, DocGeneration } from '@/api/outline'
import type { Scene, Equipment, AIModel } from '@/api/data_collection'
import OutlineTreeNode from '@/components/OutlineTreeNode.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)

// ============ 状态 ============
const outlineTree = ref<OutlineNode[]>([])
const selectedNode = ref<OutlineNode | null>(null)
const loading = ref(false)
const drawerVisible = ref(false)
const activeDrawerTab = ref('scenes')

// AI 生成状态
const isGenerating = ref(false)
const generatingNodeId = ref<string | null>(null)

// 引用相关
const references = ref<NodeReference[]>([])
const referenceTypes = ref<ReferenceType[]>([])
const scenes = ref<Scene[]>([])
const equipments = ref<Equipment[]>([])
const aiModels = ref<AIModel[]>([])
const selectedRefType = ref<string>('core')

// 生成历史
const generations = ref<DocGeneration[]>([])
const currentContent = ref('')

// ============ 获取大纲树 ============
async function fetchOutlineTree() {
  loading.value = true
  try {
    const { data } = await outlineApi.getTree(projectId.value)
    outlineTree.value = data
  } catch (error) {
    try {
      await outlineApi.initializeOutline(projectId.value)
      const { data } = await outlineApi.getTree(projectId.value)
      outlineTree.value = data
    } catch (e) {
      ElMessage.error('获取大纲失败')
    }
  } finally {
    loading.value = false
  }
}

// ============ 选择节点 ============
async function handleSelectNode(node: OutlineNode) {
  selectedNode.value = node

  if (node.id) {
    try {
      const [refsRes, gensRes, typesRes] = await Promise.all([
        outlineApi.getReferences(node.id),
        outlineApi.getGenerations(node.id),
        outlineApi.getReferenceTypes()
      ])
      references.value = refsRes.data
      generations.value = gensRes.data
      referenceTypes.value = typesRes.data

      const currentGen = gensRes.data.find((g: DocGeneration) => g.is_current_version)
      if (currentGen) {
        currentContent.value = currentGen.generation_content
      } else {
        currentContent.value = node.content || ''
      }
    } catch (error) {
      console.error('获取节点数据失败', error)
    }
  }
}

// ============ 引用侧边栏 ============
async function openReferenceDrawer() {
  drawerVisible.value = true
  activeDrawerTab.value = 'scenes'

  try {
    const [scenesRes, eqRes, modelsRes, typesRes] = await Promise.all([
      sceneApi.list(projectId.value),
      equipmentApi.list(projectId.value),
      aiModelApi.list(projectId.value),
      outlineApi.getReferenceTypes()
    ])
    scenes.value = scenesRes.data
    equipments.value = eqRes.data
    aiModels.value = modelsRes.data
    referenceTypes.value = typesRes.data
  } catch (error) {
    console.error('获取引用数据失败', error)
  }
}

// ============ 添加引用 ============
async function addReference(entityType: string, entityId: string, entityName: string) {
  if (!selectedNode.value) return

  const refType = referenceTypes.value.find(t => t.type_code === selectedRefType.value)
  if (!refType) return

  try {
    await outlineApi.createReference(selectedNode.value.id, {
      ref_entity_type: entityType,
      ref_entity_id: entityId,
      ref_type_id: refType.id
    })

    ElMessage.success(`已添加引用: ${entityName}`)

    const { data } = await outlineApi.getReferences(selectedNode.value.id)
    references.value = data
  } catch (error) {
    ElMessage.error('添加引用失败')
  }
}

// ============ 删除引用 ============
async function deleteReference(refId: string) {
  try {
    await outlineApi.deleteReference(refId)
    ElMessage.success('删除成功')

    if (selectedNode.value) {
      const { data } = await outlineApi.getReferences(selectedNode.value.id)
      references.value = data
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// ============ 保存内容 ============
async function saveContent() {
  if (!selectedNode.value) return

  try {
    await outlineApi.updateNode(selectedNode.value.id, {
      content: currentContent.value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// ============ AI 生成 ============
async function generateContent() {
  if (!selectedNode.value || !selectedNode.value.id) return

  if (references.value.length === 0) {
    ElMessage.warning('请先添加引用数据后再生成内容')
    return
  }

  isGenerating.value = true
  generatingNodeId.value = selectedNode.value.id
  currentContent.value = ''

  try {
    const response = await fetch(`/api/outline/${selectedNode.value.id}/generate-stream`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`生成失败: ${response.status} - ${errorText}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应')
    }

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      const text = decoder.decode(value)
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.error) {
              ElMessage.error(data.error)
              break
            }

            if (data.content) {
              currentContent.value += data.content
              // 强制触发 Vue 更新
              await nextTick()
            }

            if (data.done) {
              ElMessage.success('内容生成完成')
              await outlineApi.updateNode(selectedNode.value!.id, {
                content: currentContent.value
              })
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }
  } catch (error: any) {
    console.error('AI生成错误:', error)
    ElMessage.error(error.message || '生成失败，请重试')
  } finally {
    isGenerating.value = false
    generatingNodeId.value = null
  }
}

// ============ 初始化 ============
onMounted(() => {
  fetchOutlineTree()
})

// ============ 格式化引用实体名称 ============
function getEntityName(ref: NodeReference): string {
  if (ref.ref_entity_type === 'scene') {
    const scene = scenes.value.find(s => s.id === ref.ref_entity_id)
    return scene?.scene_name || '未知场景'
  } else if (ref.ref_entity_type === 'equipment') {
    const eq = equipments.value.find(e => e.id === ref.ref_entity_id)
    return eq?.equipment_name || '未知设备'
  } else if (ref.ref_entity_type === 'ai_model') {
    const model = aiModels.value.find(m => m.id === ref.ref_entity_id)
    return model?.model_name || '未知模型'
  }
  return '未知'
}

function getRefTypeName(typeId: string): string {
  const type = referenceTypes.value.find(t => t.id === typeId)
  return type?.type_name || '未知'
}

function getRefTypeTag(typeCode: string): string {
  const map: Record<string, string> = {
    core: 'danger',
    background: 'warning',
    budget: 'success'
  }
  return map[typeCode] || 'info'
}
</script>

<template>
  <div class="outline-page">
    <!-- 页面标题 -->
    <div class="page-hero">
      <div class="hero-content">
        <h1 class="hero-title">项目大纲</h1>
        <p class="hero-subtitle">构建智能育种申报书体系</p>
      </div>
      <div class="hero-decoration">
        <div class="deco-line"></div>
        <div class="deco-circle"></div>
      </div>
    </div>

    <!-- 工作区 -->
    <div class="workspace">
      <!-- 左侧：大纲树 -->
      <aside class="outline-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">目录结构</span>
          <el-button text @click="fetchOutlineTree" class="refresh-btn">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>

        <div class="tree-wrapper" v-loading="loading">
          <div class="outline-tree">
            <template v-for="node in outlineTree" :key="node.id">
              <OutlineTreeNode
                :node="node"
                :selected-id="selectedNode?.id"
                :level="1"
                @select="handleSelectNode"
              />
            </template>
          </div>

          <el-empty v-if="!loading && outlineTree.length === 0" description="暂无大纲数据" :image-size="80" />
        </div>
      </aside>

      <!-- 中间：编辑面板 -->
      <main class="editor-main">
        <template v-if="selectedNode">
          <!-- 节点信息头部 -->
          <header class="editor-header">
            <div class="node-meta">
              <span class="node-code">{{ selectedNode.node_code }}</span>
              <h2 class="node-title">{{ selectedNode.node_title }}</h2>
            </div>
            <div class="header-actions">
              <el-button @click="openReferenceDrawer">
                <el-icon><Link /></el-icon>
                引用管理
              </el-button>
              <el-button type="primary" :disabled="isGenerating" :loading="isGenerating" @click="generateContent">
                <el-icon><MagicStick /></el-icon>
                {{ isGenerating ? '生成中' : 'AI生成' }}
              </el-button>
            </div>
          </header>

          <!-- 引用展示 -->
          <div class="references-bar" v-if="references.length">
            <span class="ref-label">当前引用</span>
            <div class="ref-tags">
              <el-tag
                v-for="ref in references"
                :key="ref.id"
                :type="getRefTypeTag(referenceTypes.find(t => t.id === ref.ref_type_id)?.type_code || '')"
                closable
                @close="deleteReference(ref.id)"
                class="ref-tag"
              >
                {{ getEntityName(ref) }}
              </el-tag>
            </div>
          </div>

          <!-- 内容编辑区 -->
          <div class="editor-body">
            <div v-if="isGenerating" class="generating-indicator">
              <span class="generating-dot"></span>
              <span class="generating-dot"></span>
              <span class="generating-dot"></span>
              <span>AI 正在生成内容...</span>
            </div>
            <textarea
              v-model="currentContent"
              class="content-editor"
              :class="{ 'streaming': isGenerating }"
              placeholder="请输入内容，或点击「AI生成」使用AI辅助编写..."
            ></textarea>
          </div>

          <!-- 底部操作栏 -->
          <footer class="editor-footer">
            <div class="footer-info">
              <span class="word-count">{{ currentContent.length }} 字</span>
            </div>
            <el-button type="primary" @click="saveContent">
              保存内容
            </el-button>
          </footer>
        </template>

        <!-- 空状态 -->
        <div class="empty-workspace" v-else>
          <div class="empty-illustration">
            <svg viewBox="0 0 200 200" class="empty-svg">
              <rect x="40" y="20" width="120" height="160" rx="4" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
              <rect x="50" y="40" width="100" height="12" rx="2" fill="currentColor" opacity="0.1"/>
              <rect x="50" y="60" width="80" height="8" rx="2" fill="currentColor" opacity="0.1"/>
              <rect x="50" y="76" width="60" height="8" rx="2" fill="currentColor" opacity="0.1"/>
              <rect x="50" y="100" width="100" height="12" rx="2" fill="currentColor" opacity="0.1"/>
              <rect x="50" y="120" width="70" height="8" rx="2" fill="currentColor" opacity="0.1"/>
              <circle cx="160" cy="160" r="30" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.2"/>
              <path d="M150 160 L158 168 L172 152" fill="none" stroke="currentColor" stroke-width="2" opacity="0.4"/>
            </svg>
          </div>
          <p class="empty-text">从左侧选择一个大纲节点开始编辑</p>
        </div>
      </main>
    </div>

    <!-- 引用抽屉 -->
    <el-drawer v-model="drawerVisible" title="引用库" direction="rtl" size="420px">
      <div class="drawer-body">
        <div class="ref-type-bar">
          <span class="bar-label">引用类型</span>
          <el-radio-group v-model="selectedRefType" size="small">
            <el-radio-button value="core">核心引用</el-radio-button>
            <el-radio-button value="background">参考背景</el-radio-button>
            <el-radio-button value="budget">预算关联</el-radio-button>
          </el-radio-group>
        </div>

        <el-tabs v-model="activeDrawerTab" class="ref-tabs">
          <el-tab-pane label="场景" name="scenes">
            <div class="ref-items">
              <div v-for="scene in scenes" :key="scene.id" class="ref-card" @click="addReference('scene', scene.id, scene.scene_name)">
                <div class="ref-card-icon">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="ref-card-content">
                  <h4>{{ scene.scene_name }}</h4>
                  <p>{{ scene.scene_description || '暂无描述' }}</p>
                </div>
                <el-icon class="ref-card-add"><Plus /></el-icon>
              </div>
              <el-empty v-if="!scenes.length" description="暂无场景" :image-size="60" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="设备" name="equipments">
            <div class="ref-items">
              <div v-for="eq in equipments" :key="eq.id" class="ref-card" @click="addReference('equipment', eq.id, eq.equipment_name)">
                <div class="ref-card-icon">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="ref-card-content">
                  <h4>{{ eq.equipment_name }}</h4>
                  <p>{{ eq.equipment_type }} · ¥{{ eq.total_price?.toLocaleString() }}</p>
                </div>
                <el-icon class="ref-card-add"><Plus /></el-icon>
              </div>
              <el-empty v-if="!equipments.length" description="暂无设备" :image-size="60" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="AI模型" name="aiModels">
            <div class="ref-items">
              <div v-for="model in aiModels" :key="model.id" class="ref-card" @click="addReference('ai_model', model.id, model.model_name)">
                <div class="ref-card-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="ref-card-content">
                  <h4>{{ model.model_name }}</h4>
                  <p>{{ model.model_type }} · {{ model.parameter_count }}</p>
                </div>
                <el-icon class="ref-card-add"><Plus /></el-icon>
              </div>
              <el-empty v-if="!aiModels.length" description="暂无AI模型" :image-size="60" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
/* ========== 页面布局 ========== */
.outline-page {
  min-height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

/* 页面英雄区 */
.page-hero {
  position: relative;
  padding: var(--space-2xl) var(--space-3xl);
  background: var(--color-bg);
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.hero-decoration {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
}

.deco-line {
  width: 120px;
  height: 1px;
  background: linear-gradient(90deg, var(--color-accent), transparent);
  margin-bottom: 8px;
}

.deco-circle {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
}

/* 工作区 */
.workspace {
  flex: 1;
  display: flex;
  gap: 0;
  background: var(--color-bg);
  padding: 0 var(--space-3xl) var(--space-3xl);
}

/* 左侧边栏 */
.outline-sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.refresh-btn {
  color: var(--color-text-tertiary);
}

.refresh-btn:hover {
  color: var(--color-accent);
}

.tree-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-sm);
}

.outline-tree {
  font-family: var(--font-body);
}

/* 主编辑区 */
.editor-main {
  flex: 1;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-left: var(--space-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 编辑头部 */
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.node-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.node-code {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-accent);
  letter-spacing: 0.5px;
}

.node-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

/* 引用栏 */
.references-bar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-xl);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-light);
}

.ref-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.ref-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.ref-tag {
  font-size: 12px;
}

/* 编辑器主体 */
.editor-body {
  flex: 1;
  padding: var(--space-xl);
  overflow: hidden;
}

.content-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-display);
  font-size: 15px;
  line-height: 1.9;
  color: var(--color-text-primary);
  background: transparent;
}

.content-editor::placeholder {
  color: var(--color-text-tertiary);
}

/* 生成中指示器 */
.generating-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: var(--space-md);
  background: var(--color-accent-subtle);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
  color: var(--color-accent);
  font-size: 14px;
  font-weight: 500;
}

.generating-dot {
  width: 8px;
  height: 8px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.generating-dot:nth-child(1) { animation-delay: -0.32s; }
.generating-dot:nth-child(2) { animation-delay: -0.16s; }
.generating-dot:nth-child(3) { animation-delay: 0s; }

@keyframes pulse {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 流光光标效果 */
.content-editor.streaming {
  caret-color: var(--color-accent);
}

/* 编辑器底部 */
.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-xl);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-secondary);
}

.footer-info {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

/* 空状态 */
.empty-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl);
}

.empty-illustration {
  width: 160px;
  height: 160px;
  margin-bottom: var(--space-lg);
  color: var(--color-text-tertiary);
}

.empty-svg {
  width: 100%;
  height: 100%;
}

.empty-text {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

/* 抽屉 */
.drawer-body {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--space-lg);
}

.ref-type-bar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--color-border-light);
}

.bar-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.ref-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ref-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

.ref-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.ref-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.ref-card:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-card);
  transform: translateX(4px);
}

.ref-card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent-subtle);
  border-radius: var(--radius-md);
  color: var(--color-accent);
  font-size: 16px;
}

.ref-card-content {
  flex: 1;
  min-width: 0;
}

.ref-card-content h4 {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.ref-card-content p {
  font-size: 12px;
  color: var(--color-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ref-card-add {
  color: var(--color-text-tertiary);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.ref-card:hover .ref-card-add {
  opacity: 1;
  color: var(--color-accent);
}
</style>
