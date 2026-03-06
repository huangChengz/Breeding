<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { budgetApi } from '@/api/budget'
import type {
  BudgetSummary,
  EquipmentBudget,
  DatasetBudget,
  AIModelBudget,
  RDProjectBudget
} from '@/api/budget'

const route = useRoute()
const projectId = computed(() => route.params.id as string)

// 状态
const loading = ref(false)
const activeTab = ref('summary')

// 预算数据
const summary = ref<BudgetSummary | null>(null)
const equipments = ref<EquipmentBudget[]>([])
const datasets = ref<DatasetBudget[]>([])
const aiModels = ref<AIModelBudget[]>([])
const rdProjects = ref<RDProjectBudget[]>([])

// 格式化金额
function formatMoney(value: number | undefined): string {
  if (value === undefined || value === null) return '¥0'
  return '¥' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 获取预算汇总
async function fetchSummary() {
  loading.value = true
  try {
    const { data } = await budgetApi.getSummary(projectId.value)
    summary.value = data
  } catch (error) {
    console.error('获取预算汇总失败', error)
  } finally {
    loading.value = false
  }
}

// 获取所有明细数据
async function fetchDetails() {
  loading.value = true
  try {
    const [eqRes, dsRes, aiRes, rdRes] = await Promise.all([
      budgetApi.getEquipments(projectId.value),
      budgetApi.getDatasets(projectId.value),
      budgetApi.getAIModels(projectId.value),
      budgetApi.getRDProjects(projectId.value)
    ])
    equipments.value = eqRes.data
    datasets.value = dsRes.data
    aiModels.value = aiRes.data
    rdProjects.value = rdRes.data
  } catch (error) {
    console.error('获取预算明细失败', error)
  } finally {
    loading.value = false
  }
}

// 导出预算报表
async function exportBudget() {
  try {
    const { data } = await budgetApi.export(projectId.value)

    // 创建下载
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `项目预算报表_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 计算各类占比
const equipmentPercent = computed(() => {
  if (!summary.value || summary.value.total_budget === 0) return 0
  return (summary.value.equipment_budget / summary.value.total_budget * 100).toFixed(1)
})

const dataPercent = computed(() => {
  if (!summary.value || summary.value.total_budget === 0) return 0
  return ((summary.value.data_processing_budget + summary.value.data_purchase_budget) / summary.value.total_budget * 100).toFixed(1)
})

const aiModelPercent = computed(() => {
  if (!summary.value || summary.value.total_budget === 0) return 0
  return (summary.value.ai_model_budget / summary.value.total_budget * 100).toFixed(1)
})

const rdPercent = computed(() => {
  if (!summary.value || summary.value.total_budget === 0) return 0
  return (summary.value.rd_budget / summary.value.total_budget * 100).toFixed(1)
})

// 切换标签页
function handleTabChange(tab: string) {
  if (tab === 'summary') {
    fetchSummary()
  } else {
    fetchDetails()
  }
}

// 初始化
onMounted(() => {
  fetchSummary()
})
</script>

<template>
  <div class="budget-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>项目预算汇总</h2>
        <p class="subtitle">全面掌握项目投资情况</p>
      </div>
      <el-button type="primary" size="large" @click="exportBudget">
        <el-icon><Download /></el-icon>
        导出预算报表
      </el-button>
    </div>

    <!-- 预算汇总卡片 -->
    <div class="summary-cards">
      <div class="summary-card total-card">
        <div class="card-icon">
          <el-icon><Wallet /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">项目总预算</div>
          <div class="card-value">{{ formatMoney(summary?.total_budget) }}</div>
          <div class="card-unit">人民币（元）</div>
        </div>
        <div class="card-decoration"></div>
      </div>

      <div class="summary-card">
        <div class="card-icon equipment">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">设备预算</div>
          <div class="card-value">{{ formatMoney(summary?.equipment_budget) }}</div>
          <div class="card-percent">{{ equipmentPercent }}%</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill equipment" :style="{ width: equipmentPercent + '%' }"></div>
        </div>
      </div>

      <div class="summary-card">
        <div class="card-icon data">
          <el-icon><Files /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">数据预算</div>
          <div class="card-value">{{ formatMoney((summary?.data_processing_budget || 0) + (summary?.data_purchase_budget || 0)) }}</div>
          <div class="card-percent">{{ dataPercent }}%</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill data" :style="{ width: dataPercent + '%' }"></div>
        </div>
      </div>

      <div class="summary-card">
        <div class="card-icon ai-model">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">AI模型预算</div>
          <div class="card-value">{{ formatMoney(summary?.ai_model_budget) }}</div>
          <div class="card-percent">{{ aiModelPercent }}%</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill ai-model" :style="{ width: aiModelPercent + '%' }"></div>
        </div>
      </div>

      <div class="summary-card">
        <div class="card-icon rd">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-label">研发预算</div>
          <div class="card-value">{{ formatMoney(summary?.rd_budget) }}</div>
          <div class="card-percent">{{ rdPercent }}%</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill rd" :style="{ width: rdPercent + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 明细表格 -->
    <el-tabs v-model="activeTab" class="detail-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="设备明细" name="equipments">
        <el-table :data="equipments" v-loading="loading" stripe>
          <el-table-column prop="equipment_name" label="设备名称" min-width="180" />
          <el-table-column prop="equipment_type" label="设备类型" width="100" />
          <el-table-column prop="key_level" label="关键星级" width="100">
            <template #default="{ row }">
              <el-rate v-model="row.key_level" disabled />
            </template>
          </el-table-column>
          <el-table-column prop="total_price" label="总价(元)" width="140">
            <template #default="{ row }">
              {{ formatMoney(row.total_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="supplier" label="供应商" min-width="150" show-overflow-tooltip />
          <el-table-column prop="is_imported" label="是否进口" width="80">
            <template #default="{ row }">
              {{ row.is_imported ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="necessity_description" label="必要性说明" min-width="200" show-overflow-tooltip />
        </el-table>
        <div class="table-footer">
          <span>设备总计：</span>
          <strong>{{ formatMoney(summary?.equipment_budget) }}</strong>
        </div>
      </el-tab-pane>

      <el-tab-pane label="数据明细" name="datasets">
        <el-table :data="datasets" v-loading="loading" stripe>
          <el-table-column prop="data_name" label="数据名称" min-width="180" />
          <el-table-column prop="data_type" label="数据类型" width="100" />
          <el-table-column prop="data_total_tb" label="数据总量(TB)" width="120" />
          <el-table-column prop="processing_fee" label="处理费(万元)" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.processing_fee * 10000) }}
            </template>
          </el-table-column>
          <el-table-column prop="purchase_fee" label="购买费(万元)" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.purchase_fee * 10000) }}
            </template>
          </el-table-column>
          <el-table-column prop="need_purchase" label="是否购买" width="80">
            <template #default="{ row }">
              {{ row.need_purchase ? '是' : '否' }}
            </template>
          </el-table-column>
        </el-table>
        <div class="table-footer">
          <span>数据总计：</span>
          <strong>{{ formatMoney(((summary?.data_processing_budget || 0) + (summary?.data_purchase_budget || 0)) * 10000) }}</strong>
        </div>
      </el-tab-pane>

      <el-tab-pane label="AI模型明细" name="aiModels">
        <el-table :data="aiModels" v-loading="loading" stripe>
          <el-table-column prop="model_name" label="模型名称" min-width="180" />
          <el-table-column prop="model_type" label="模型类型" width="100" />
          <el-table-column prop="model_scale" label="模型规模" width="100" />
          <el-table-column prop="parameter_count" label="参数量" width="80" />
          <el-table-column prop="function_type" label="功能类型" width="80">
            <template #default="{ row }">
              {{ row.function_type === 'training' ? '训练' : '推理' }}
            </template>
          </el-table-column>
          <el-table-column prop="estimated_total_fee" label="预计费用(万元)" width="140">
            <template #default="{ row }">
              {{ formatMoney(row.estimated_total_fee * 10000) }}
            </template>
          </el-table-column>
        </el-table>
        <div class="table-footer">
          <span>AI模型总计：</span>
          <strong>{{ formatMoney((summary?.ai_model_budget || 0) * 10000) }}</strong>
        </div>
      </el-tab-pane>

      <el-tab-pane label="研发项目明细" name="rdProjects">
        <el-table :data="rdProjects" v-loading="loading" stripe>
          <el-table-column prop="rd_name" label="项目名称" min-width="200" />
          <el-table-column prop="rd_direction" label="研发方向" width="120" />
          <el-table-column prop="rd_content" label="研发内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="expected_output" label="预期成果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="estimated_fee" label="预估费用(万元)" width="140">
            <template #default="{ row }">
              {{ formatMoney(row.estimated_fee * 10000) }}
            </template>
          </el-table-column>
        </el-table>
        <div class="table-footer">
          <span>研发项目总计：</span>
          <strong>{{ formatMoney((summary?.rd_budget || 0) * 10000) }}</strong>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.budget-page {
  background: #f5f7fa;
  min-height: calc(100vh - 140px);
  padding: 24px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 28px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 16px;
  color: white;
}

.header-content h2 {
  margin: 0 0 6px 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  opacity: 0.7;
}

/* 汇总卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: 2fr repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  position: relative;
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.summary-card.total-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  grid-row: span 2;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  font-size: 22px;
  color: #667eea;
}

.card-icon.equipment {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0284c7;
}

.card-icon.data {
  background: linear-gradient(135deg, #dcfce7 0%, #86efac 100%);
  color: #16a34a;
}

.card-icon.ai-model {
  background: linear-gradient(135deg, #f3e8ff 0%, #d8b4fe 100%);
  color: #9333ea;
}

.card-icon.rd {
  background: linear-gradient(135deg, #ffedd5 0%, #fdba74 100%);
  color: #ea580c;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 6px;
}

.summary-card.total-card .card-label {
  color: rgba(255, 255, 255, 0.8);
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.summary-card.total-card .card-value {
  font-size: 32px;
  color: white;
}

.card-unit, .card-percent {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.summary-card.total-card .card-unit {
  color: rgba(255, 255, 255, 0.7);
}

/* 进度条 */
.progress-bar {
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.progress-fill.equipment {
  background: linear-gradient(90deg, #0284c7, #38bdf8);
}

.progress-fill.data {
  background: linear-gradient(90deg, #16a34a, #4ade80);
}

.progress-fill.ai-model {
  background: linear-gradient(90deg, #9333ea, #c084fc);
}

.progress-fill.rd {
  background: linear-gradient(90deg, #ea580c, #fb923c);
}

.card-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  transform: translate(30%, -30%);
}

/* 标签页 */
.detail-tabs {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.detail-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.detail-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
}

.detail-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.detail-tabs :deep(.el-tabs__active-bar) {
  background: #667eea;
}

/* 表格底部 */
.table-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  font-size: 14px;
  color: #6b7280;
}

.table-footer strong {
  font-size: 18px;
  color: #667eea;
  font-family: 'JetBrains Mono', monospace;
}

/* 响应式 */
@media (max-width: 1400px) {
  .summary-cards {
    grid-template-columns: repeat(3, 1fr);
  }

  .summary-card.total-card {
    grid-column: span 3;
    grid-row: span 1;
  }
}

@media (max-width: 900px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-card.total-card {
    grid-column: span 2;
  }
}
</style>
