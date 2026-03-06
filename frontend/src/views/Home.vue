<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { projectApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const projects = ref<any[]>([])

const userName = computed(() => userStore.user?.real_name || userStore.user?.username || '用户')

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const menuItems = [
  {
    path: '/projects',
    icon: 'Folder',
    title: '项目管理',
    desc: '创建和管理申报项目',
    color: '#2563EB'
  },
  {
    path: '/projects',
    icon: 'Document',
    title: '本子编写',
    desc: 'AI智能生成申报书',
    color: '#059669'
  },
  {
    path: '/projects',
    icon: 'DataAnalysis',
    title: '数据采集',
    desc: '管理场景和设备数据',
    color: '#2563EB'
  },
  {
    path: '/projects',
    icon: 'Wallet',
    title: '预算汇总',
    desc: '查看项目预算明细',
    color: '#7C3AED'
  }
]

const stats = [
  { label: '项目总数', value: 0, icon: 'Folder', color: '#2563EB' },
  { label: '进行中', value: 0, icon: 'Loading', color: '#2563EB' },
  { label: '已完成', value: 0, icon: 'CircleCheck', color: '#059669' },
  { label: '待审核', value: 0, icon: 'Warning', color: '#F59E0B' }
]

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

async function fetchProjects() {
  try {
    const { data } = await projectApi.list()
    projects.value = data
    stats[0].value = data.length
    stats[1].value = data.filter((p: any) => p.status === 1).length
    stats[2].value = data.filter((p: any) => p.status === 3).length
    stats[3].value = data.filter((p: any) => p.status === 2).length
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<template>
  <div class="home-page">
    <!-- 欢迎区域 -->
    <section class="hero-section">
      <div class="hero-bg">
        <div class="bg-gradient"></div>
        <div class="bg-pattern"></div>
      </div>
      <div class="hero-content">
        <div class="hero-text">
          <p class="greeting">{{ greeting }}，<span class="username">{{ userName }}</span></p>
          <h1 class="hero-title">欢迎使用 AI育种智能申报系统</h1>
          <p class="hero-desc">高效、智能、一站式完成项目申报书编写与预算管理</p>
        </div>
        <div class="hero-illustration">
          <svg viewBox="0 0 300 200" class="hero-svg">
            <!-- 文档图形 -->
            <rect x="40" y="30" width="120" height="150" rx="8" fill="white" opacity="0.9" stroke="#E7E5E4"/>
            <rect x="55" y="50" width="90" height="8" rx="2" fill="#2563EB" opacity="0.3"/>
            <rect x="55" y="66" width="70" height="6" rx="2" fill="#E7E5E4"/>
            <rect x="55" y="80" width="50" height="6" rx="2" fill="#E7E5E4"/>
            <rect x="55" y="100" width="90" height="8" rx="2" fill="#059669" opacity="0.3"/>
            <rect x="55" y="116" width="60" height="6" rx="2" fill="#E7E5E4"/>
            <rect x="55" y="130" width="80" height="6" rx="2" fill="#E7E5E4"/>
            <rect x="55" y="150" width="40" height="20" rx="4" fill="#2563EB" opacity="0.8"/>
            <!-- AI图标 -->
            <circle cx="200" cy="80" r="40" fill="#2563EB" opacity="0.1"/>
            <circle cx="200" cy="80" r="25" fill="#2563EB" opacity="0.2"/>
            <circle cx="200" cy="80" r="10" fill="#2563EB"/>
            <!-- 预算图表 -->
            <rect x="170" y="140" width="80" height="50" rx="6" fill="white" opacity="0.9" stroke="#E7E5E4"/>
            <rect x="180" y="165" width="12" height="20" rx="2" fill="#2563EB" opacity="0.6"/>
            <rect x="198" y="155" width="12" height="30" rx="2" fill="#059669" opacity="0.6"/>
            <rect x="216" y="145" width="12" height="40" rx="2" fill="#2563EB" opacity="0.6"/>
          </svg>
        </div>
      </div>
    </section>

    <!-- 快捷入口 -->
    <section class="quick-section">
      <h2 class="section-title">快捷入口</h2>
      <div class="quick-grid">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="quick-card"
          @click="router.push(item.path)"
        >
          <div class="card-icon" :style="{ background: item.color + '15', color: item.color }">
            <el-icon :size="28"><component :is="item.icon" /></el-icon>
          </div>
          <div class="card-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
          <el-icon class="card-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-card">
          <div class="stat-icon" :style="{ background: stat.color + '15', color: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 最近项目 -->
    <section class="recent-section" v-if="projects.length > 0">
      <div class="section-header">
        <h2 class="section-title">最近项目</h2>
        <router-link to="/projects" class="view-all">查看全部 <el-icon><ArrowRight /></el-icon></router-link>
      </div>
      <div class="recent-list">
        <div
          v-for="project in projects.slice(0, 3)"
          :key="project.id"
          class="project-item"
          @click="router.push(`/projects/${project.id}`)"
        >
          <div class="project-icon">
            <el-icon :size="20"><Folder /></el-icon>
          </div>
          <div class="project-info">
            <h4>{{ project.project_name }}</h4>
            <p>{{ project.owner_unit || '未设置单位' }}</p>
          </div>
          <el-tag size="small" :type="project.status === 3 ? 'success' : project.status === 2 ? 'warning' : 'info'">
            {{ project.status === 0 ? '草稿' : project.status === 1 ? '填报中' : project.status === 2 ? '审核中' : project.status === 3 ? '已完成' : '已归档' }}
          </el-tag>
        </div>
      </div>
    </section>

    <!-- 空白状态 -->
    <section class="empty-section" v-else>
      <div class="empty-illustration">
        <svg viewBox="0 0 200 200" class="empty-svg">
          <rect x="30" y="40" width="140" height="120" rx="8" fill="none" stroke="#E7E5E4" stroke-width="2"/>
          <path d="M70 80 L100 110 L140 70" fill="none" stroke="#2563EB" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="100" cy="150" r="20" fill="#F5F5F4"/>
          <line x1="90" y1="150" x2="110" y2="150" stroke="#A8A29E" stroke-width="2"/>
        </svg>
      </div>
      <h3>还没有任何项目</h3>
      <p>点击下方按钮创建您的第一个AI育种项目</p>
      <el-button type="primary" size="large" @click="router.push('/projects')">
        <el-icon><Plus /></el-icon>
        创建项目
      </el-button>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  padding: var(--space-xl) var(--space-3xl);
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎区域 */
.hero-section {
  position: relative;
  margin-bottom: var(--space-2xl);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--color-accent) 0%, #1D4ED8 100%);
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.hero-content {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3xl);
  min-height: 220px;
}

.hero-text {
  color: white;
}

.greeting {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: var(--space-sm);
}

.username {
  font-weight: 600;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

.hero-desc {
  font-size: 15px;
  opacity: 0.9;
}

.hero-illustration {
  width: 280px;
  height: 180px;
}

.hero-svg {
  width: 100%;
  height: 100%;
}

/* 快捷入口 */
.quick-section {
  margin-bottom: var(--space-2xl);
}

.section-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
}

.quick-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.25s ease;
}

.quick-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.card-content p {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.card-arrow {
  color: var(--color-text-tertiary);
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.25s ease;
}

.quick-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* 统计卡片 */
.stats-section {
  margin-bottom: var(--space-2xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

/* 最近项目 */
.recent-section {
  margin-bottom: var(--space-2xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.section-header .section-title {
  margin-bottom: 0;
}

.view-all {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-accent);
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.project-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-item:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-secondary);
}

.project-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border-radius: var(--radius-md);
}

.project-info {
  flex: 1;
}

.project-info h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.project-info p {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

/* 空白状态 */
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl);
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-xl);
  text-align: center;
}

.empty-illustration {
  width: 160px;
  height: 160px;
  margin-bottom: var(--space-lg);
}

.empty-svg {
  width: 100%;
  height: 100%;
}

.empty-section h3 {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.empty-section p {
  font-size: 14px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-lg);
}

/* 响应式 */
@media (max-width: 900px) {
  .quick-grid,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-illustration {
    display: none;
  }

  .hero-content {
    justify-content: center;
    text-align: center;
  }
}

@media (max-width: 600px) {
  .quick-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .home-page {
    padding: var(--space-md);
  }
}
</style>
