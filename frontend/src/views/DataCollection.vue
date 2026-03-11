<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Files, Monitor, Folder, Cpu, Calendar } from '@element-plus/icons-vue'
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
    // Initialize with empty arrays for relation fields
    if (type === 'equipment') {
      form.value = { scene_ids: [] }
    } else if (type === 'dataset') {
      form.value = { scene_ids: [], source_equipment_ids: [] }
    } else if (type === 'aiModel') {
      form.value = { scene_ids: [], related_data_ids: [], source_equipment_ids: [] }
    } else if (type === 'rdProject') {
      form.value = { scene_ids: [] }
    } else {
      form.value = {}
    }
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
  else if (tab === 'datasets') {
    // Make sure scenes and equipments are loaded for name resolution
    if (scenes.value.length === 0) fetchScenes()
    if (equipments.value.length === 0) fetchEquipments()
    fetchDatasets()
  }
  else if (tab === 'aiModels') {
    // Make sure scenes and datasets are loaded for name resolution
    if (scenes.value.length === 0) fetchScenes()
    if (datasets.value.length === 0) fetchDatasets()
    fetchAIModels()
  }
  else if (tab === 'rdProjects') {
    // Make sure scenes are loaded for name resolution
    if (scenes.value.length === 0) fetchScenes()
    fetchRDProjects()
  }
}

// 格式化金额
function formatMoney(value: number | undefined) {
  if (!value) return '-'
  return `¥${value.toLocaleString()}`
}

// 获取关联场景名称
function getSceneNames(sceneIds: string[] | undefined) {
  if (!sceneIds || sceneIds.length === 0) return '-'
  const names = sceneIds.map(id => {
    const scene = scenes.value.find(s => s.id === id)
    return scene ? scene.scene_name : id.slice(0, 8)
  })
  return names.join(', ')
}

// 获取关联设备名称
function getEquipmentNames(equipmentIds: string[] | undefined) {
  if (!equipmentIds || equipmentIds.length === 0) return '-'
  const names = equipmentIds.map(id => {
    const equip = equipments.value.find(e => e.id === id)
    return equip ? equip.equipment_name : id.slice(0, 8)
  })
  return names.join(', ')
}

// 获取关联数据名称
function getDataNames(dataIds: string[] | undefined) {
  if (!dataIds || dataIds.length === 0) return '-'
  const names = dataIds.map(id => {
    const data = datasets.value.find(d => d.id === id)
    return data ? data.data_name : id.slice(0, 8)
  })
  return names.join(', ')
}

// 初始化
onMounted(async () => {
  console.log('DataCollection: Starting initialization')
  try {
    await fetchDictionaries()
    await Promise.all([
      fetchScenes(),
      fetchEquipments(),
      fetchDatasets(),
      fetchAIModels(),
      fetchRDProjects()
    ])
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
          <el-table-column prop="research_output_data" label="科研产出数据" width="120" />
          <el-table-column prop="data_output_type" label="数据产出类型" width="120" />
          <el-table-column prop="data_total_tb" label="数据总量(TB)" width="100" />
          <el-table-column prop="file_size_description" label="文件大小描述" width="120" show-overflow-tooltip />
          <el-table-column prop="data_output_description" label="数据产出说明" width="150" show-overflow-tooltip />
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
          <el-table-column label="关联场景" min-width="150">
            <template #default="{ row }">
              {{ getSceneNames(row.scene_ids) }}
            </template>
          </el-table-column>
          <el-table-column prop="equipment_type" label="设备类型" width="100" />
          <el-table-column prop="key_level" label="关键星级" width="90">
            <template #default="{ row }">
              <el-rate v-model="row.key_level" disabled />
            </template>
          </el-table-column>
          <el-table-column prop="procurement_method" label="采购方式" width="90" />
          <el-table-column prop="unit_price" label="单价(元)" width="100">
            <template #default="{ row }">
              {{ formatMoney(row.unit_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_price" label="总价(元)" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.total_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="supplier" label="供应商" min-width="100" show-overflow-tooltip />
          <el-table-column prop="origin_country" label="国产/进口" width="80" />
          <el-table-column prop="is_imported" label="是否进口" width="80">
            <template #default="{ row }">
              {{ row.is_imported ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="need_quote_seal" label="需报价盖章" width="90">
            <template #default="{ row }">
              {{ row.need_quote_seal ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="purchase_time" label="计划购置时间" width="120">
            <template #default="{ row }">
              {{ row.purchase_time ? row.purchase_time.split('T')[0] : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="commissioning_time" label="计划投用时间" width="120">
            <template #default="{ row }">
              {{ row.commissioning_time ? row.commissioning_time.split('T')[0] : '-' }}
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
          <el-table-column label="关联场景" min-width="120">
            <template #default="{ row }">
              {{ getSceneNames(row.scene_ids) }}
            </template>
          </el-table-column>
          <el-table-column label="关联设备" min-width="120">
            <template #default="{ row }">
              {{ getEquipmentNames(row.source_equipment_ids) }}
            </template>
          </el-table-column>
          <el-table-column prop="data_type" label="数据类型" width="100" />
          <el-table-column prop="other_data_type" label="其他类型" width="100" show-overflow-tooltip />
          <el-table-column prop="data_total_tb" label="数据总量(TB)" width="100" />
          <el-table-column prop="cycle_data_gb" label="周期数据量(GB)" width="110" />
          <el-table-column prop="access_permission" label="访问权限" width="90" />
          <el-table-column prop="is_shared_with_lab" label="实验室共享" width="90">
            <template #default="{ row }">
              {{ row.is_shared_with_lab ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="need_purchase" label="需要购买" width="80">
            <template #default="{ row }">
              {{ row.need_purchase ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column prop="purchase_fee" label="购买费(万元)" width="100">
            <template #default="{ row }">
              {{ formatMoney(row.purchase_fee) }}
            </template>
          </el-table-column>
          <el-table-column prop="processing_fee" label="处理费(万元)" width="100">
            <template #default="{ row }">
              {{ formatMoney(row.processing_fee) }}
            </template>
          </el-table-column>
          <el-table-column prop="compute_cycle_total_days" label="计算周期(天)" width="100" />
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
          <el-table-column label="关联场景" min-width="120">
            <template #default="{ row }">
              {{ getSceneNames(row.scene_ids) }}
            </template>
          </el-table-column>
          <el-table-column label="关联数据" min-width="120">
            <template #default="{ row }">
              {{ getDataNames(row.related_data_ids) }}
            </template>
          </el-table-column>
          <el-table-column prop="model_description" label="模型描述" min-width="180" show-overflow-tooltip />
          <el-table-column prop="model_type" label="模型类型" width="100" />
          <el-table-column prop="model_scale" label="模型规模" width="80" />
          <el-table-column prop="parameter_count" label="参数量" width="80" />
          <el-table-column prop="function_type" label="功能类型" width="80">
            <template #default="{ row }">
              {{ row.function_type === 'training' ? '训练' : row.function_type === 'inference' ? '推理' : row.function_type }}
            </template>
          </el-table-column>
          <el-table-column prop="estimated_total_fee" label="预计费用(万元)" width="120">
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
          <el-table-column label="关联场景" min-width="120">
            <template #default="{ row }">
              {{ getSceneNames(row.scene_ids) }}
            </template>
          </el-table-column>
          <el-table-column prop="rd_direction" label="研发方向" width="100" />
          <el-table-column prop="rd_content" label="研发内容" min-width="180" show-overflow-tooltip />
          <el-table-column prop="expected_output" label="预期成果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="estimated_fee" label="预估费用(万元)" width="120">
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px" class="data-dialog" destroy-on-close>
      <div class="dialog-header-icon">
        <el-icon v-if="dialogType === 'scene'"><Files /></el-icon>
        <el-icon v-else-if="dialogType === 'equipment'"><Monitor /></el-icon>
        <el-icon v-else-if="dialogType === 'dataset'"><Folder /></el-icon>
        <el-icon v-else-if="dialogType === 'aiModel'"><Cpu /></el-icon>
        <el-icon v-else-if="dialogType === 'rdProject'"><Calendar /></el-icon>
      </div>
      <el-form :model="form" label-position="top" class="data-form">
        <!-- 场景表单 -->
        <template v-if="dialogType === 'scene'">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="场景名称" required>
                <el-input v-model="form.scene_name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="科研产出类型">
                <el-input v-model="form.research_output_type" placeholder="如：论文、专利、软件著作权" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="科研产出-数据产出">
            <el-input v-model="form.research_output_data" placeholder="科研产出相关的数据产出" />
          </el-form-item>
          <el-form-item label="场景描述">
            <el-input v-model="form.scene_description" type="textarea" :rows="3" placeholder="对于文本生成很重要，请详细描述" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="数据产出类型">
                <el-input v-model="form.data_output_type" placeholder="如：图像、文本、基因组" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="数据总量(TB)">
                <el-input-number v-model="form.data_total_tb" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="文件大小描述">
                <el-input v-model="form.file_size_description" placeholder="如：10mb-500mb/张" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="数据产出说明">
            <el-input v-model="form.data_output_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- 设备表单 -->
        <template v-else-if="dialogType === 'equipment'">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="设备名称" required>
                <el-input v-model="form.equipment_name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="设备类型" required>
                <el-select v-model="form.equipment_type" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="item in equipmentTypes"
                    :key="item.dict_code"
                    :label="item.dict_label"
                    :value="item.dict_code"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="关联场景">
            <el-select v-model="form.scene_ids" multiple placeholder="请选择关联场景" style="width: 100%">
              <el-option
                v-for="scene in scenes"
                :key="scene.id"
                :label="scene.scene_name"
                :value="scene.id"
              />
            </el-select>
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="关键星级">
                <el-rate v-model="form.key_level" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="采购方式">
                <el-input v-model="form.procurement_method" placeholder="如：公开招标" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="国产/进口">
                <el-select v-model="form.origin_country" placeholder="请选择" style="width: 100%">
                  <el-option label="国产" value="国产" />
                  <el-option label="进口" value="进口" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="单价(元)">
                <el-input-number v-model="form.unit_price" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="总价(元)" required>
                <el-input-number v-model="form.total_price" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="是否进口">
                <el-switch v-model="form.is_imported" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="需报价盖章">
                <el-switch v-model="form.need_quote_seal" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="计划购置时间">
                <el-date-picker v-model="form.purchase_time" type="date" placeholder="选择日期" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="计划投用时间">
                <el-date-picker v-model="form.commissioning_time" type="date" placeholder="选择日期" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="供应商">
            <el-input v-model="form.supplier" placeholder="主要供应商" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="供应商1">
                <el-input v-model="form.supplier_1" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="供应商2">
                <el-input v-model="form.supplier_2" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="供应商3">
                <el-input v-model="form.supplier_3" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="最终选择供应商">
            <el-input v-model="form.final_supplier" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="计划使用数值">
                <el-input-number v-model="form.plan_usage_value" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="计划使用单位">
                <el-input v-model="form.plan_usage_unit" placeholder="如：小时、天" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="计划使用说明">
            <el-input v-model="form.plan_usage_description" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="必要性与匹配性">
            <el-input v-model="form.necessity_description" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="数据输出类型">
            <el-input v-model="form.data_output_type" placeholder="如：CSV、JSON、图片" />
          </el-form-item>
        </template>

        <!-- 数据集表单 -->
        <template v-else-if="dialogType === 'dataset'">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="数据名称" required>
                <el-input v-model="form.data_name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="数据类型" required>
                <el-select v-model="form.data_type" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="item in dataTypes"
                    :key="item.dict_code"
                    :label="item.dict_label"
                    :value="item.dict_code"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="关联场景">
            <el-select v-model="form.scene_ids" multiple placeholder="请选择关联场景" style="width: 100%">
              <el-option
                v-for="scene in scenes"
                :key="scene.id"
                :label="scene.scene_name"
                :value="scene.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="关联设备">
            <el-select v-model="form.source_equipment_ids" multiple placeholder="请选择关联设备" style="width: 100%">
              <el-option
                v-for="equip in equipments"
                :key="equip.id"
                :label="equip.equipment_name"
                :value="equip.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="其他数据类型">
            <el-input v-model="form.other_data_type" placeholder="如以上没有，可填写其他类型" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="数据总量(TB)">
                <el-input-number v-model="form.data_total_tb" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="周期数据量(GB)">
                <el-input-number v-model="form.cycle_data_gb" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="访问权限">
                <el-select v-model="form.access_permission" placeholder="请选择" style="width: 100%">
                  <el-option label="公开(public)" value="public" />
                  <el-option label="授权(authorized)" value="authorized" />
                  <el-option label="私有(private)" value="private" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="与实验室共享">
                <el-switch v-model="form.is_shared_with_lab" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="需要购买">
                <el-switch v-model="form.need_purchase" />
              </el-form-item>
            </el-col>
            <el-col :span="8" v-if="form.need_purchase">
              <el-form-item label="购买费用(万元)">
                <el-input-number v-model="form.purchase_fee" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="计算周期数值">
                <el-input-number v-model="form.compute_cycle_value" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="计算周期单位">
                <el-select v-model="form.compute_cycle_unit" placeholder="请选择" style="width: 100%">
                  <el-option label="小时" value="小时" />
                  <el-option label="天" value="天" />
                  <el-option label="周" value="周" />
                  <el-option label="月" value="月" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="总计(天)">
                <el-input-number v-model="form.compute_cycle_total_days" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="来源周期(月)">
                <el-input-number v-model="form.source_cycle_months" :min="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="处理费(万元)">
                <el-input-number v-model="form.processing_fee" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="数据描述">
            <el-input v-model="form.data_description" type="textarea" :rows="2" />
          </el-form-item>
        </template>

        <!-- AI模型表单 -->
        <template v-else-if="dialogType === 'aiModel'">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="模型名称" required>
                <el-input v-model="form.model_name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模型类型" required>
                <el-select v-model="form.model_type" placeholder="请选择" style="width: 100%">
                  <el-option
                    v-for="item in modelTypes"
                    :key="item.dict_code"
                    :label="item.dict_label"
                    :value="item.dict_code"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="关联场景">
            <el-select v-model="form.scene_ids" multiple placeholder="请选择关联场景" style="width: 100%">
              <el-option
                v-for="scene in scenes"
                :key="scene.id"
                :label="scene.scene_name"
                :value="scene.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="关联数据">
            <el-select v-model="form.related_data_ids" multiple placeholder="请选择关联数据" style="width: 100%">
              <el-option
                v-for="data in datasets"
                :key="data.id"
                :label="data.data_name"
                :value="data.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="关联设备">
            <el-select v-model="form.source_equipment_ids" multiple placeholder="请选择关联设备" style="width: 100%">
              <el-option
                v-for="equip in equipments"
                :key="equip.id"
                :label="equip.equipment_name"
                :value="equip.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="模型描述">
            <el-input v-model="form.model_description" type="textarea" :rows="2" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="模型规模">
                <el-input v-model="form.model_scale" placeholder="如：大型、中型、小型" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="参数量">
                <el-input v-model="form.parameter_count" placeholder="如: 7B, 70B, 100亿" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="功能类型">
                <el-select v-model="form.function_type" placeholder="请选择" style="width: 100%">
                  <el-option label="模型训练" value="training" />
                  <el-option label="模型推理" value="inference" />
                  <el-option label="训练+推理" value="both" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="预计费用(万元)" required>
            <el-input-number v-model="form.estimated_total_fee" :min="0" :precision="2" style="width: 100%" />
          </el-form-item>
        </template>

        <!-- 研发项目表单 -->
        <template v-else-if="dialogType === 'rdProject'">
          <el-form-item label="项目名称" required>
            <el-input v-model="form.rd_name" />
          </el-form-item>
          <el-form-item label="关联场景">
            <el-select v-model="form.scene_ids" multiple placeholder="请选择关联场景" style="width: 100%">
              <el-option
                v-for="scene in scenes"
                :key="scene.id"
                :label="scene.scene_name"
                :value="scene.id"
              />
            </el-select>
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

/* 对话框样式 */
.data-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.data-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--color-border-light);
  margin-right: 0;
}

.data-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.data-dialog :deep(.el-dialog__body) {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.data-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--color-border-light);
}

.dialog-header-icon {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, var(--color-accent) 0%, #3b82f6 100%);
  border-radius: 10px;
  color: white;
}

.dialog-header-icon .el-icon {
  font-size: 24px;
}

/* 表单样式 */
.data-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.data-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--color-text-primary);
  padding-bottom: 6px;
  line-height: 1;
}

.data-form :deep(.el-input__wrapper),
.data-form :deep(.el-select),
.data-form :deep(.el-textarea__inner),
.data-form :deep(.el-date-editor) {
  border-radius: 8px;
}

.data-form :deep(.el-input-number) {
  width: 100%;
}

.data-form :deep(.el-rate) {
  height: 32px;
  line-height: 32px;
}

.data-form :deep(.el-switch) {
  margin-top: 6px;
}

/* 分组标题 */
.form-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 8px 0;
  margin: 16px 0 12px;
  border-bottom: 1px solid var(--color-border-light);
}

.form-section-title:first-child {
  margin-top: 0;
}
</style>
