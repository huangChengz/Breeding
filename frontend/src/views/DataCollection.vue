<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  sceneApi, equipmentApi, datasetApi, aiModelApi, rdProjectApi, dictionaryApi
} from '@/api/data_collection'
import type { Scene, Equipment, Dataset, AIModel, RDProject, Dictionary } from '@/api/data_collection'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const error = ref('')

if (!projectId.value) {
  error.value = '项目ID不存在'
}

console.log('DataCollection mounted, projectId:', projectId.value)

const activeTab = ref('scenes')
const loading = ref(false)

// 数据列表
const scenes = ref<Scene[]>([])
const equipments = ref<Equipment[]>([])
const datasets = ref<Dataset[]>([])
const aiModels = ref<AIModel[]>([])
const rdProjects = ref<RDProject[]>([])

// 字典数据
const equipmentTypes = ref<Dictionary[]>([])
const dataTypes = ref<Dictionary[]>([])
const modelTypes = ref<Dictionary[]>([])

// 对话框
const dialogVisible = ref(false)
const dialogType = ref('')

// 对话框标题
const dialogTitle = computed(() => {
  const titles: Record<string, string> = {
    scene: form.value.id ? '编辑场景' : '添加场景',
    equipment: form.value.id ? '编辑设备' : '添加设备',
    dataset: form.value.id ? '编辑数据' : '添加数据',
    aiModel: form.value.id ? '编辑AI模型' : '添加AI模型',
    rdProject: form.value.id ? '编辑研发项目' : '添加研发项目'
  }
  return titles[dialogType.value] || '添加'
})

// 表单数据
const form = ref<any>({})

// ============ 获取字典数据 ============
async function fetchDictionaries() {
  try {
    console.log('DataCollection: Fetching dictionaries')
    const [eqTypes, dTypes, mTypes] = await Promise.all([
      dictionaryApi.list('equipment_type'),
      dictionaryApi.list('data_type'),
      dictionaryApi.list('model_type')
    ])
    equipmentTypes.value = eqTypes.data
    dataTypes.value = dTypes.data
    modelTypes.value = mTypes.data
    console.log('DataCollection: Dictionaries fetched')
  } catch (error: any) {
    console.error('DataCollection: Error fetching dictionaries:', error)
  }
}

// ============ 数据获取函数 ============
async function fetchScenes() {
  loading.value = true
  try {
    console.log('DataCollection: Fetching scenes for project:', projectId.value)
    const { data } = await sceneApi.list(projectId.value)
    console.log('DataCollection: Scenes fetched:', data)
    scenes.value = data
  } catch (error: any) {
    console.error('DataCollection: Error fetching scenes:', error)
    ElMessage.error(error.response?.data?.detail || '获取场景列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchEquipments() {
  loading.value = true
  try {
    const { data } = await equipmentApi.list(projectId.value)
    equipments.value = data
  } catch (error) {
    ElMessage.error('获取设备列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchDatasets() {
  loading.value = true
  try {
    const { data } = await datasetApi.list(projectId.value)
    datasets.value = data
  } catch (error) {
    ElMessage.error('获取数据集列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchAIModels() {
  loading.value = true
  try {
    const { data } = await aiModelApi.list(projectId.value)
    aiModels.value = data
  } catch (error) {
    ElMessage.error('获取AI模型列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchRDProjects() {
  loading.value = true
  try {
    const { data } = await rdProjectApi.list(projectId.value)
    rdProjects.value = data
  } catch (error) {
    ElMessage.error('获取研发项目列表失败')
  } finally {
    loading.value = false
  }
}

// ============ CRUD 操作 ============
function openDialog(type: string, row?: any) {
  dialogType.value = type
  if (row) {
    form.value = { ...row }
  } else {
    form.value = {}
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (dialogType.value === 'scene') {
      if (form.value.id) {
        await sceneApi.update(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await sceneApi.create(projectId.value, form.value)
        ElMessage.success('创建成功')
      }
      fetchScenes()
    } else if (dialogType.value === 'equipment') {
      if (form.value.id) {
        await equipmentApi.update(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await equipmentApi.create(projectId.value, form.value)
        ElMessage.success('创建成功')
      }
      fetchEquipments()
    } else if (dialogType.value === 'dataset') {
      if (form.value.id) {
        await datasetApi.update(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await datasetApi.create(projectId.value, form.value)
        ElMessage.success('创建成功')
      }
      fetchDatasets()
    } else if (dialogType.value === 'aiModel') {
      if (form.value.id) {
        await aiModelApi.update(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await aiModelApi.create(projectId.value, form.value)
        ElMessage.success('创建成功')
      }
      fetchAIModels()
    } else if (dialogType.value === 'rdProject') {
      if (form.value.id) {
        await rdProjectApi.update(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await rdProjectApi.create(projectId.value, form.value)
        ElMessage.success('创建成功')
      }
      fetchRDProjects()
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(type: string, id: string) {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', {
      type: 'warning'
    })

    if (type === 'scene') {
      await sceneApi.delete(id)
      fetchScenes()
    } else if (type === 'equipment') {
      await equipmentApi.delete(id)
      fetchEquipments()
    } else if (type === 'dataset') {
      await datasetApi.delete(id)
      fetchDatasets()
    } else if (type === 'aiModel') {
      await aiModelApi.delete(id)
      fetchAIModels()
    } else if (type === 'rdProject') {
      await rdProjectApi.delete(id)
      fetchRDProjects()
    }
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消
  }
}

// ============ 切换标签页 ============
function handleTabChange(tab: string) {
  loading.value = true
  if (tab === 'scenes') fetchScenes()
  else if (tab === 'equipments') fetchEquipments()
  else if (tab === 'datasets') fetchDatasets()
  else if (tab === 'aiModels') fetchAIModels()
  else if (tab === 'rdProjects') fetchRDProjects()
}

// 格式化金额
function formatMoney(value: number | undefined) {
  if (!value) return '-'
  return `¥${value.toLocaleString()}`
}

// 初始化
onMounted(async () => {
  console.log('DataCollection: Starting initialization')
  try {
    await fetchDictionaries()
    await fetchScenes()
    console.log('DataCollection: Initialization complete')
  } catch (error) {
    console.error('DataCollection: Initialization error', error)
  }
})
</script>

<template>
  <div class="data-collection">
    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon style="margin-bottom: 20px" />

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" v-else>
      <!-- 场景管理 -->
      <el-tab-pane label="场景管理" name="scenes">
        <div class="toolbar">
          <el-button type="primary" @click="openDialog('scene')">
            <el-icon><Plus /></el-icon>添加场景
          </el-button>
        </div>
        <el-table :data="scenes" v-loading="loading" stripe>
          <el-table-column prop="scene_name" label="场景名称" min-width="150" />
          <el-table-column prop="scene_description" label="场景描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="research_output_type" label="科研产出类型" width="120" />
          <el-table-column prop="data_output_type" label="数据产出类型" width="120" />
          <el-table-column prop="data_total_tb" label="数据总量(TB)" width="100" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog('scene', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('scene', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 设备管理 -->
      <el-tab-pane label="设备管理" name="equipments">
        <div class="toolbar">
          <el-button type="primary" @click="openDialog('equipment')">
            <el-icon><Plus /></el-icon>添加设备
          </el-button>
        </div>
        <el-table :data="equipments" v-loading="loading" stripe>
          <el-table-column prop="equipment_name" label="设备名称" min-width="150" />
          <el-table-column prop="equipment_type" label="设备类型" width="100" />
          <el-table-column prop="key_level" label="关键星级" width="90">
            <template #default="{ row }">
              <el-rate v-model="row.key_level" disabled />
            </template>
          </el-table-column>
          <el-table-column prop="total_price" label="总价(元)" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.total_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="supplier" label="供应商" min-width="120" show-overflow-tooltip />
          <el-table-column prop="is_imported" label="是否进口" width="80">
            <template #default="{ row }">
              {{ row.is_imported ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog('equipment', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('equipment', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 数据管理 -->
      <el-tab-pane label="数据管理" name="datasets">
        <div class="toolbar">
          <el-button type="primary" @click="openDialog('dataset')">
            <el-icon><Plus /></el-icon>添加数据
          </el-button>
        </div>
        <el-table :data="datasets" v-loading="loading" stripe>
          <el-table-column prop="data_name" label="数据名称" min-width="150" />
          <el-table-column prop="data_type" label="数据类型" width="100" />
          <el-table-column prop="data_total_tb" label="数据总量(TB)" width="100" />
          <el-table-column prop="processing_fee" label="处理费(万元)" width="110">
            <template #default="{ row }">
              {{ formatMoney(row.processing_fee) }}
            </template>
          </el-table-column>
          <el-table-column prop="purchase_fee" label="购买费(万元)" width="110">
            <template #default="{ row }">
              {{ formatMoney(row.purchase_fee) }}
            </template>
          </el-table-column>
          <el-table-column prop="access_permission" label="访问权限" width="90" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog('dataset', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('dataset', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- AI模型管理 -->
      <el-tab-pane label="AI模型管理" name="aiModels">
        <div class="toolbar">
          <el-button type="primary" @click="openDialog('aiModel')">
            <el-icon><Plus /></el-icon>添加AI模型
          </el-button>
        </div>
        <el-table :data="aiModels" v-loading="loading" stripe>
          <el-table-column prop="model_name" label="模型名称" min-width="150" />
          <el-table-column prop="model_type" label="模型类型" width="100" />
          <el-table-column prop="model_scale" label="模型规模" width="100" />
          <el-table-column prop="parameter_count" label="参数量" width="80" />
          <el-table-column prop="function_type" label="功能类型" width="80" />
          <el-table-column prop="estimated_total_fee" label="预计费用(万元)" width="130">
            <template #default="{ row }">
              {{ formatMoney(row.estimated_total_fee) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog('aiModel', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('aiModel', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 研发项目管理 -->
      <el-tab-pane label="研发项目管理" name="rdProjects">
        <div class="toolbar">
          <el-button type="primary" @click="openDialog('rdProject')">
            <el-icon><Plus /></el-icon>添加研发项目
          </el-button>
        </div>
        <el-table :data="rdProjects" v-loading="loading" stripe>
          <el-table-column prop="rd_name" label="项目名称" min-width="150" />
          <el-table-column prop="rd_direction" label="研发方向" width="120" />
          <el-table-column prop="rd_content" label="研发内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="expected_output" label="预期成果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="estimated_fee" label="预估费用(万元)" width="130">
            <template #default="{ row }">
              {{ formatMoney(row.estimated_fee) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog('rdProject', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('rdProject', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="120px">
        <!-- 场景表单 -->
        <template v-if="dialogType === 'scene'">
          <el-form-item label="场景名称" required>
            <el-input v-model="form.scene_name" />
          </el-form-item>
          <el-form-item label="场景描述">
            <el-input v-model="form.scene_description" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="科研产出类型">
            <el-input v-model="form.research_output_type" />
          </el-form-item>
          <el-form-item label="数据产出类型">
            <el-input v-model="form.data_output_type" />
          </el-form-item>
          <el-form-item label="数据总量(TB)">
            <el-input-number v-model="form.data_total_tb" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="数据产出说明">
            <el-input v-model="form.data_output_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- 设备表单 -->
        <template v-else-if="dialogType === 'equipment'">
          <el-form-item label="设备名称" required>
            <el-input v-model="form.equipment_name" />
          </el-form-item>
          <el-form-item label="设备类型" required>
            <el-select v-model="form.equipment_type" placeholder="请选择">
              <el-option
                v-for="item in equipmentTypes"
                :key="item.dict_code"
                :label="item.dict_label"
                :value="item.dict_code"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="关键星级">
            <el-rate v-model="form.key_level" />
          </el-form-item>
          <el-form-item label="总价(元)" required>
            <el-input-number v-model="form.total_price" :min="0" />
          </el-form-item>
          <el-form-item label="单价(元)">
            <el-input-number v-model="form.unit_price" :min="0" />
          </el-form-item>
          <el-form-item label="采购方式">
            <el-input v-model="form.procurement_method" />
          </el-form-item>
          <el-form-item label="供应商">
            <el-input v-model="form.supplier" />
          </el-form-item>
          <el-form-item label="是否进口">
            <el-switch v-model="form.is_imported" />
          </el-form-item>
          <el-form-item label="必要性与匹配性">
            <el-input v-model="form.necessity_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- 数据集表单 -->
        <template v-else-if="dialogType === 'dataset'">
          <el-form-item label="数据名称" required>
            <el-input v-model="form.data_name" />
          </el-form-item>
          <el-form-item label="数据类型" required>
            <el-select v-model="form.data_type" placeholder="请选择">
              <el-option
                v-for="item in dataTypes"
                :key="item.dict_code"
                :label="item.dict_label"
                :value="item.dict_code"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数据总量(TB)">
            <el-input-number v-model="form.data_total_tb" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="处理费(万元)">
            <el-input-number v-model="form.processing_fee" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="购买费(万元)">
            <el-input-number v-model="form.purchase_fee" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="是否需要购买">
            <el-switch v-model="form.need_purchase" />
          </el-form-item>
          <el-form-item label="数据描述">
            <el-input v-model="form.data_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- AI模型表单 -->
        <template v-else-if="dialogType === 'aiModel'">
          <el-form-item label="模型名称" required>
            <el-input v-model="form.model_name" />
          </el-form-item>
          <el-form-item label="模型类型" required>
            <el-select v-model="form.model_type" placeholder="请选择">
              <el-option
                v-for="item in modelTypes"
                :key="item.dict_code"
                :label="item.dict_label"
                :value="item.dict_code"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="模型规模">
            <el-input v-model="form.model_scale" />
          </el-form-item>
          <el-form-item label="参数量">
            <el-input v-model="form.parameter_count" placeholder="如: 7B, 70B" />
          </el-form-item>
          <el-form-item label="功能类型">
            <el-select v-model="form.function_type" placeholder="请选择">
              <el-option label="训练" value="training" />
              <el-option label="推理" value="inference" />
            </el-select>
          </el-form-item>
          <el-form-item label="预计费用(万元)" required>
            <el-input-number v-model="form.estimated_total_fee" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="模型描述">
            <el-input v-model="form.model_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- 研发项目表单 -->
        <template v-else-if="dialogType === 'rdProject'">
          <el-form-item label="项目名称" required>
            <el-input v-model="form.rd_name" />
          </el-form-item>
          <el-form-item label="研发方向">
            <el-input v-model="form.rd_direction" />
          </el-form-item>
          <el-form-item label="研发内容">
            <el-input v-model="form.rd_content" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="预期成果">
            <el-input v-model="form.expected_output" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="预估费用(万元)" required>
            <el-input-number v-model="form.estimated_fee" :min="0" :precision="2" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.data-collection {
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
