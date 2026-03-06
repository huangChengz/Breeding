<script setup lang="ts">
import { RouterView, useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const userName = computed(() => userStore.user?.real_name || userStore.user?.username || '用户')

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

const menuItems = [
  { path: '/', icon: 'House', label: '首页' },
  { path: '/projects', icon: 'Folder', label: '项目管理' }
]

// 判断是否需要显示导航栏（排除登录和注册页面）
const showNav = computed(() => {
  return route.path !== '/login' && route.path !== '/register'
})
</script>

<template>
  <div class="app-layout" v-if="showNav">
    <!-- 顶部导航 -->
    <header class="app-header">
      <div class="header-left">
        <div class="logo">
          <svg viewBox="0 0 40 40" class="logo-svg">
            <g transform="translate(20, 20)">
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(0)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(30)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(60)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(90)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(120)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(150)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(180)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(210)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(240)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(270)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(300)"/>
              <ellipse cx="0" cy="-12" rx="2.5" ry="7" fill="currentColor" opacity="0.8" transform="rotate(330)"/>
            </g>
            <rect x="16" y="16" width="8" height="8" rx="1.5" fill="currentColor" opacity="0.9"/>
          </svg>
        </div>
        <span class="brand-name">AI育种</span>
      </div>

      <nav class="header-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path)) }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          {{ item.label }}
        </router-link>
      </nav>

      <div class="header-right">
        <div class="user-info">
          <el-icon><User /></el-icon>
          <span>{{ userName }}</span>
        </div>
        <el-button text @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <RouterView />
    </main>
  </div>

  <!-- 登录注册页面不需要导航 -->
  <RouterView v-else />
</template>

<style>
/* ========== 全局样式 - 现代极简风格 ========== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  /* 主色调 - 温暖米白 */
  --color-bg: #FAFAF9;
  --color-bg-secondary: #F5F5F4;
  --color-bg-card: #FFFFFF;

  /* 文字颜色 */
  --color-text-primary: #1C1917;
  --color-text-secondary: #57534E;
  --color-text-tertiary: #A8A29E;

  /* 强调色 - 科技蓝 */
  --color-accent: #2563EB;
  --color-accent-light: #3B82F6;
  --color-accent-subtle: #DBEAFE;

  /* 功能色 */
  --color-success: #059669;
  --color-warning: #F59E0B;
  --color-error: #DC2626;
  --color-info: #2563EB;

  /* 边框 */
  --color-border: #E7E5E4;
  --color-border-light: #F5F5F4;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.03);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 12px 40px rgba(0, 0, 0, 0.06);
  --shadow-xl: 0 24px 60px rgba(0, 0, 0, 0.08);

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-xl: 24px;

  /* 字体 */
  --font-display: 'Noto Serif SC', 'Songti SC', serif;
  --font-body: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;

  /* 间距 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* 过渡 */
  --transition-fast: 0.15s ease;
  --transition-base: 0.25s ease;
  --transition-slow: 0.4s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text-primary);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100vw;
  min-height: 100vh;
  background: var(--color-bg);
}

/* 加载动画 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: var(--color-bg);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-text-tertiary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* Element Plus 自定义覆盖 */
.el-button--primary {
  --el-button-bg-color: var(--color-accent);
  --el-button-border-color: var(--color-accent);
  --el-button-hover-bg-color: var(--color-accent-light);
  --el-button-hover-border-color: var(--color-accent-light);
  --el-button-active-bg-color: #B45309;
  --el-button-active-border-color: #B45309;
}

.el-button--success {
  --el-button-bg-color: var(--color-success);
  --el-button-border-color: var(--color-success);
}

.el-button--danger {
  --el-button-bg-color: var(--color-error);
  --el-button-border-color: var(--color-error);
}

.el-input__wrapper {
  box-shadow: none !important;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.el-input__wrapper:hover,
.el-input__wrapper:focus-within {
  border-color: var(--color-accent);
}

.el-input__wrapper.is-focus {
  border-color: var(--color-accent) !important;
}

.el-textarea__inner {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.el-textarea__inner:focus {
  border-color: var(--color-accent);
}

.el-select .el-input__wrapper {
  border: 1px solid var(--color-border);
}

.el-table {
  --el-table-border-color: var(--color-border-light);
  --el-table-header-bg-color: var(--color-bg-secondary);
  font-family: var(--font-body);
}

.el-table th.el-table__cell {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.el-dialog {
  --el-dialog-border-radius: var(--radius-lg);
}

.el-dialog__header {
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: var(--space-md);
}

.el-dialog__title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 18px;
  color: var(--color-text-primary);
}

.el-tabs__item {
  font-family: var(--font-body);
  font-weight: 500;
}

.el-tabs__item.is-active {
  color: var(--color-accent);
}

.el-tabs__active-bar {
  background-color: var(--color-accent);
}

.el-message-box {
  --el-messagebox-border-radius: var(--radius-lg);
}

.el-drawer {
  --el-drawer-padding-primary: 0;
}

.el-card {
  --el-card-border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: none;
}

.el-card:hover {
  box-shadow: var(--shadow-md);
  transition: box-shadow var(--transition-base);
}

.el-tag {
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.el-dropdown-menu__item {
  font-family: var(--font-body);
}

.el-message {
  --el-message-border-radius: var(--radius-md);
}

.el-empty__description {
  color: var(--color-text-tertiary);
}

.el-form-item__label {
  font-family: var(--font-body);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.el-input-number {
  width: 100%;
}
</style>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

/* 顶部导航 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 var(--space-3xl);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.logo {
  width: 32px;
  height: 32px;
  color: var(--color-accent);
}

.logo-svg {
  width: 100%;
  height: 100%;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* 导航链接 */
.header-nav {
  display: flex;
  gap: var(--space-sm);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
}

.nav-link.active {
  color: var(--color-accent);
  background: var(--color-accent-subtle);
}

/* 右侧 */
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.logout-btn:hover {
  color: var(--color-error);
}

/* 主内容区 */
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
