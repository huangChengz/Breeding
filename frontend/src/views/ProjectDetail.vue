<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectApi } from '@/api'
import type { Project } from '@/types'
import DataCollection from './DataCollection.vue'

const route = useRoute()
const router = useRouter()
const project = ref<Project | null>(null)
const loading = ref(false)
const activeTab = ref('overview')
const error = ref('')

const projectId = computed(() => route.params.id as string)

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

async function fetchProject() {
  if (!projectId.value) {
    error.value = '项目ID不存在'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data } = await projectApi.get(projectId.value)
    project.value = data
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取项目详情失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

function goToDataCollection() {
  router.push(`/projects/${projectId.value}/data`)
}

function goToOutline() {
  router.push(`/projects/${projectId.value}/outline`)
}

function goToBudget() {
  router.push(`/projects/${projectId.value}/budget`)
}

onMounted(() => {
  fetchProject()
})
</script>

<template>
  <div class="project-detail">
    <!-- 页面头部 -->
    <header class="detail-header" v-if="project">
      <div class="header-main">
        <div class="header-content">
          <span class="project-code">{{ project.project_code || 'PROJECT' }}</span>
          <h1 class="project-title">{{ project.project_name }}</h1>
          <p class="project-desc">{{ project.description || '暂无描述' }}</p>
        </div>
        <el-tag :type="statusTypeMap[project.status] as any" size="large" class="status-tag">
          {{ statusMap[project.status] }}
        </el-tag>
      </div>
    </header>

    <!-- 导航标签 -->
    <nav class="detail-nav">
      <el-tabs v-model="activeTab" class="nav-tabs">
        <el-tab-pane label="项目概览" name="overview" />
        <el-tab-pane label="数据采集" name="data" />
      </el-tabs>
    </nav>

    <!-- 内容区域 -->
    <div class="detail-content" v-loading="loading">
      <!-- 错误提示 -->
      <el-alert v-if="error" :title="error" type="error" show-icon style="margin-bottom: 20px" />

      <!-- 项目概览 -->
      <div v-if="activeTab === 'overview'" class="overview-section">
        <el-card class="info-card">
          <template #header>
            <h3 class="card-title">项目信息</h3>
          </template>
          <el-descriptions :column="2" border class="info-descriptions">
            <el-descriptions-item label="项目编码">
              {{ project?.project_code || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="建设单位">
              {{ project?.owner_unit || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="建设周期">
              {{ project?.construction_period_months ? project.construction_period_months + '个月' : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="建设地点">
              {{ project?.location || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="项目描述" :span="2">
              {{ project?.description || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 快捷入口 -->
        <div class="quick-entry">
          <h3 class="section-title">快捷入口</h3>
          <div class="entry-grid">
            <div class="entry-card" @click="goToDataCollection">
              <div class="entry-icon">
                <el-icon><Folder /></el-icon>
              </div>
              <h4>数据采集</h4>
              <p>管理场景、设备、数据、AI模型</p>
            </div>
            <div class="entry-card" @click="goToOutline">
              <div class="entry-icon accent">
                <el-icon><Document /></el-icon>
              </div>
              <h4>本子编写</h4>
              <p>AI智能生成申报书内容</p>
            </div>
            <div class="entry-card" @click="goToBudget">
              <div class="entry-icon warning">
                <el-icon><Wallet /></el-icon>
              </div>
              <h4>预算汇总</h4>
              <p>查看项目预算明细</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据采集 -->
      <div v-if="activeTab === 'data'" class="data-section">
        <DataCollection />
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-detail {
  min-height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

/* 页面头部 */
.detail-header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-2xl) var(--space-3xl);
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content {
  flex: 1;
}

.project-code {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.project-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--space-sm) 0;
}

.project-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  max-width: 600px;
}

.status-tag {
  font-size: 13px;
  padding: 8px 16px;
}

/* 导航 */
.detail-nav {
  background: var(--color-bg-card);
  padding: 0 var(--space-3xl);
  border-bottom: 1px solid var(--color-border-light);
}

.nav-tabs :deep(.el-tabs__header) {
  margin: 0;
}

.nav-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
  padding: 0 20px;
  height: 50px;
  line-height: 50px;
}

/* 内容区域 */
.detail-content {
  flex: 1;
  padding: var(--space-xl) var(--space-3xl);
  background: var(--color-bg);
}

/* 概览部分 */
.overview-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.info-card {
  border-radius: var(--radius-lg);
}

.card-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.info-descriptions :deep(.el-descriptions__label) {
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
}

/* 快捷入口 */
.section-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.entry-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  cursor: pointer;
  transition: all 0.25s ease;
}

.entry-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.entry-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
  font-size: 22px;
  color: var(--color-info);
}

.entry-icon.accent {
  background: var(--color-accent-subtle);
  color: var(--color-accent);
}

.entry-icon.warning {
  background: #fef3c7;
  color: var(--color-warning);
}

.entry-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.entry-card p {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0;
}

/* 响应式 */
@media (max-width: 900px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
