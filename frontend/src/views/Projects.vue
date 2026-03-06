<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi } from '@/api'
import type { Project } from '@/types'

const router = useRouter()

const projects = ref<Project[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({
  project_name: '',
  project_code: '',
  description: '',
  construction_period_months: undefined as number | undefined,
  location: '',
  owner_unit: ''
})

const statusMap: Record<number, string> = {
  0: '草稿',
  1: '填报中',
  2: '审核中',
  3: '已完成',
  4: '已归档'
}

const statusTypeMap: Record<number, string> = {
  0: 'info',
  1: 'warning',
  2: 'primary',
  3: 'success',
  4: 'info'
}

async function fetchProjects() {
  loading.value = true
  try {
    const { data } = await projectApi.list()
    projects.value = data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取项目列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  try {
    await projectApi.create(form.value)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchProjects()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

function handleView(id: string) {
  router.push(`/projects/${id}`)
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除此项目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await projectApi.delete(id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<template>
  <div class="projects-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">项目管理</h1>
        <p class="page-subtitle">管理您的AI育种项目申报书</p>
      </div>
      <el-button type="primary" size="large" @click="dialogVisible = true">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </header>

    <!-- 项目列表 -->
    <div class="projects-grid" v-loading="loading">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="handleView(project.id)"
      >
        <div class="card-header">
          <span class="project-code">{{ project.project_code || 'PROJECT' }}</span>
          <el-tag :type="statusTypeMap[project.status] as any" size="small">
            {{ statusMap[project.status] }}
          </el-tag>
        </div>
        <h3 class="project-name">{{ project.project_name }}</h3>
        <p class="project-desc">{{ project.description || '暂无描述' }}</p>
        <div class="card-meta">
          <span class="meta-item" v-if="project.owner_unit">
            <el-icon><OfficeBuilding /></el-icon>
            {{ project.owner_unit }}
          </span>
          <span class="meta-item" v-if="project.construction_period_months">
            <el-icon><Calendar /></el-icon>
            {{ project.construction_period_months }}个月
          </span>
        </div>
        <div class="card-actions" @click.stop>
          <el-button text type="danger" @click="handleDelete(project.id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && projects.length === 0" class="empty-state">
        <div class="empty-illustration">
          <svg viewBox="0 0 200 200" class="empty-svg">
            <rect x="30" y="50" width="140" height="100" rx="4" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.2"/>
            <rect x="40" y="70" width="50" height="6" rx="2" fill="currentColor" opacity="0.1"/>
            <rect x="40" y="84" width="80" height="4" rx="2" fill="currentColor" opacity="0.1"/>
            <rect x="40" y="96" width="60" height="4" rx="2" fill="currentColor" opacity="0.1"/>
            <circle cx="160" cy="160" r="30" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.15"/>
            <path d="M150 160 L158 168 L172 152" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          </svg>
        </div>
        <p>暂无项目，点击上方按钮创建</p>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="dialogVisible" title="新建项目" width="520px" :close-on-click-modal="false">
      <el-form :model="form" label-position="top" class="project-form">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.project_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目编码">
          <el-input v-model="form.project_code" placeholder="请输入项目编码" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="建设单位">
              <el-input v-model="form.owner_unit" placeholder="请输入建设单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="建设周期(月)">
              <el-input-number v-model="form.construction_period_months" :min="1" :max="120" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="建设地点">
          <el-input v-model="form.location" placeholder="请输入建设地点" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.projects-page {
  padding: var(--space-2xl) var(--space-3xl);
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--space-2xl);
  padding-bottom: var(--space-xl);
  border-bottom: 1px solid var(--color-border);
}

.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

/* 项目卡片网格 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
}

.project-card {
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  cursor: pointer;
  transition: all 0.25s ease;
}

.project-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.project-code {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.project-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
  line-height: 1.4;
}

.project-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-md);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.card-actions {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  opacity: 0;
  transition: opacity 0.2s;
}

.project-card:hover .card-actions {
  opacity: 1;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl);
  color: var(--color-text-tertiary);
}

.empty-illustration {
  width: 140px;
  height: 140px;
  margin-bottom: var(--space-lg);
}

.empty-svg {
  width: 100%;
  height: 100%;
}

/* 表单样式 */
.project-form :deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
