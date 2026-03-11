<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const { data } = await authApi.login({
      username: form.username,
      password: form.password
    })

    userStore.setToken(data.access_token)
    await userStore.fetchCurrentUser()

    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- 背景动画 -->
    <div class="bg-canvas">
      <div class="floating-shape shape-1">
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
          <circle cx="50" cy="50" r="25" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
          <circle cx="50" cy="50" r="10" fill="currentColor" opacity="0.1"/>
        </svg>
      </div>
      <div class="floating-shape shape-2">
        <svg viewBox="0 0 100 100">
          <path d="M50 10 L90 80 L10 80 Z" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
          <path d="M50 30 L70 65 L30 65 Z" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.15"/>
        </svg>
      </div>
      <div class="floating-shape shape-3">
        <svg viewBox="0 0 100 100">
          <rect x="15" y="15" width="70" height="70" rx="10" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
          <rect x="30" y="30" width="40" height="40" rx="5" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.15"/>
        </svg>
      </div>
    </div>

    <!-- 左侧品牌区 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="brand-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 64 64" class="logo-svg">
              <!-- 麦穗图形 -->
              <g transform="translate(32, 32)">
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(0)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(30)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(60)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(90)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(120)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(150)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(180)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(210)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(240)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(270)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(300)"/>
                <ellipse cx="0" cy="-20" rx="4" ry="12" fill="currentColor" opacity="0.8" transform="rotate(330)"/>
              </g>
              <!-- 中心AI芯片 -->
              <rect x="26" y="26" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
              <circle cx="32" cy="32" r="3" fill="white"/>
            </svg>
          </div>
          <h1 class="brand-name">AI育种</h1>
          <p class="brand-tagline">智能申报书生成系统</p>
        </div>

        <div class="feature-list">
          <div class="feature-item">
            <el-icon><Document /></el-icon>
            <span>智能本子生成</span>
          </div>
          <div class="feature-item">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据采集管理</span>
          </div>
          <div class="feature-item">
            <el-icon><Wallet /></el-icon>
            <span>预算自动汇总</span>
          </div>
        </div>
      </div>

      <div class="brand-footer">
        <p>© 2026 AI育种项目申报系统</p>
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-section">
      <div class="login-card">
        <div class="card-header">
          <h2>欢迎回来</h2>
          <p>登录您的账号继续使用</p>
        </div>

        <el-form :model="form" @submit.prevent="handleLogin" class="login-form">
          <el-form-item>
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
              />
            </div>
          </el-form-item>

          <el-form-item>
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <div class="form-options">
            <el-checkbox>记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="card-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: var(--color-bg);
  position: relative;
  overflow: hidden;
}

/* 背景动画 */
.bg-canvas {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-shape {
  position: absolute;
  color: var(--color-accent);
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: 20%;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: 10%;
  left: 10%;
  animation-delay: -5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 40%;
  right: 5%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(5deg); }
  50% { transform: translateY(0) rotate(0deg); }
  75% { transform: translateY(20px) rotate(-5deg); }
}

/* 左侧品牌区 */
.brand-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, var(--color-accent) 0%, #1D4ED8 100%);
  padding: var(--space-3xl);
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.brand-logo {
  margin-bottom: var(--space-3xl);
}

.logo-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto var(--space-lg);
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.logo-svg {
  width: 60px;
  height: 60px;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  margin-bottom: var(--space-sm);
  letter-spacing: 2px;
}

.brand-tagline {
  font-size: 16px;
  opacity: 0.9;
  font-weight: 300;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  font-size: 15px;
  opacity: 0.9;
}

.feature-item .el-icon {
  font-size: 20px;
}

.brand-footer {
  position: absolute;
  bottom: var(--space-xl);
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

/* 右侧登录区 */
.login-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl);
  background: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  box-shadow: var(--shadow-xl);
}

.card-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.card-header h2 {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.card-header p {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

/* 输入框 */
.input-wrapper {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  color: var(--color-text-tertiary);
  font-size: 18px;
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 42px;
}

.input-wrapper :deep(.el-input__inner) {
  height: 44px;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.forgot-link {
  font-size: 13px;
  color: var(--color-accent);
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-accent) 0%, #1D4ED8 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(217, 119, 6, 0.3);
}

/* 底部 */
.card-footer {
  text-align: center;
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border-light);
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.register-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.register-link:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 900px) {
  .login-page {
    flex-direction: column;
  }

  .brand-section {
    padding: var(--space-2xl);
    min-height: 200px;
  }

  .logo-icon {
    width: 60px;
    height: 60px;
    border-radius: 16px;
  }

  .logo-svg {
    width: 36px;
    height: 36px;
  }

  .brand-name {
    font-size: 24px;
  }

  .feature-list {
    display: none;
  }
}
</style>
