<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  email: ''
})

async function handleRegister() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      password: form.password,
      real_name: form.real_name || undefined,
      email: form.email || undefined
    })

    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <!-- 背景动画 -->
    <div class="bg-canvas">
      <div class="floating-shape shape-1">
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
        </svg>
      </div>
      <div class="floating-shape shape-2">
        <svg viewBox="0 0 100 100">
          <path d="M50 10 L90 80 L10 80 Z" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.15"/>
        </svg>
      </div>
    </div>

    <!-- 左侧品牌区 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="brand-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 64 64" class="logo-svg">
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
              <rect x="26" y="26" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
              <circle cx="32" cy="32" r="3" fill="white"/>
            </svg>
          </div>
          <h1 class="brand-name">AI育种</h1>
          <p class="brand-tagline">智能申报书生成系统</p>
        </div>

        <div class="benefit-list">
          <h3>加入我们，开启智能育种新篇章</h3>
          <ul>
            <li>
              <el-icon><Check /></el-icon>
              <span>AI智能生成申报材料</span>
            </li>
            <li>
              <el-icon><Check /></el-icon>
              <span>一站式数据采集管理</span>
            </li>
            <li>
              <el-icon><Check /></el-icon>
              <span>精准预算自动汇总</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 右侧注册区 -->
    <div class="register-section">
      <div class="register-card">
        <div class="card-header">
          <router-link to="/login" class="back-link">
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </router-link>
          <h2>创建账号</h2>
          <p>填写以下信息完成注册</p>
        </div>

        <el-form :model="form" label-position="top" class="register-form">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="用户名" required>
                <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名">
                <el-input v-model="form.real_name" placeholder="请输入姓名" size="large" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="密码" required>
                <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="确认密码" required>
                <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" size="large" show-password />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="邮箱">
            <el-input v-model="form.email" placeholder="请输入邮箱（选填）" size="large" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="register-btn" @click="handleRegister">
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="card-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
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
  width: 250px;
  height: 250px;
  bottom: -50px;
  left: 30%;
}

.shape-2 {
  width: 180px;
  height: 180px;
  top: 20%;
  right: 10%;
  animation-delay: -8s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(10deg); }
}

/* 左侧品牌区 */
.brand-section {
  width: 45%;
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
  background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M20 20.5V18H0v-2h20v-2.5l5 4-5 4z' fill='%23ffffff' fill-opacity='0.05'/%3E%3C/svg%3E");
}

.brand-content {
  position: relative;
  z-index: 1;
  color: white;
}

.brand-logo {
  text-align: center;
  margin-bottom: var(--space-3xl);
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-lg);
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-svg {
  width: 48px;
  height: 48px;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  margin-bottom: var(--space-xs);
}

.brand-tagline {
  font-size: 15px;
  opacity: 0.9;
}

.benefit-list {
  text-align: left;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
}

.benefit-list h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-lg);
}

.benefit-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.benefit-list li {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
  font-size: 14px;
}

.benefit-list li:last-child {
  margin-bottom: 0;
}

.benefit-list .el-icon {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px;
  border-radius: 50%;
  font-size: 12px;
}

/* 右侧注册区 */
.register-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  box-shadow: var(--shadow-xl);
}

.card-header {
  margin-bottom: var(--space-xl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-tertiary);
  text-decoration: none;
  margin-bottom: var(--space-md);
}

.back-link:hover {
  color: var(--color-accent);
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

/* 表单 */
.register-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-accent) 0%, #1D4ED8 100%);
  border: none;
  margin-top: var(--space-md);
  transition: all 0.3s ease;
}

.register-btn:hover {
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

.login-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.login-link:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 900px) {
  .register-page {
    flex-direction: column;
  }

  .brand-section {
    width: 100%;
    padding: var(--space-xl);
    min-height: auto;
  }

  .benefit-list {
    display: none;
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
}
</style>
