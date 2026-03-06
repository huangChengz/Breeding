<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElIcon } from 'element-plus'
import { EditPen, ArrowRight } from '@element-plus/icons-vue'

interface OutlineNode {
  id: string
  node_code: string
  node_title: string
  is_leaf: boolean
  children?: OutlineNode[]
}

const props = defineProps<{
  node: OutlineNode
  selectedId?: string
  level: number
}>()

const emit = defineEmits<{
  select: [node: OutlineNode]
}>()

const expanded = ref(true)

const isSelected = computed(() => props.selectedId === props.node.id)
const hasChildren = computed(() => props.node.children && props.node.children.length > 0)
const levelClass = computed(() => `level-${props.level}`)

function toggleExpand() {
  if (hasChildren.value) {
    expanded.value = !expanded.value
  }
}

function handleSelect() {
  emit('select', props.node)
}
</script>

<template>
  <div class="tree-node-wrapper">
    <div
      class="tree-node"
      :class="[levelClass, { 'is-selected': isSelected, 'is-leaf': node.is_leaf }]"
      @click="handleSelect"
    >
      <!-- 展开/收起 -->
      <span class="expand-icon" :class="{ 'has-children': hasChildren }" @click.stop="toggleExpand">
        <el-icon v-if="hasChildren" :size="12">
          <ArrowRight :class="{ rotated: expanded }" />
        </el-icon>
      </span>

      <!-- 节点内容 -->
      <span class="node-code">{{ node.node_code }}</span>
      <span class="node-title">{{ node.node_title }}</span>

      <!-- 叶子标识 -->
      <span v-if="node.is_leaf && level <= 3" class="leaf-badge">
        <el-icon :size="10"><EditPen /></el-icon>
      </span>
    </div>

    <!-- 子节点 -->
    <div v-if="hasChildren && expanded" class="children">
      <template v-for="child in node.children" :key="child.id">
        <OutlineTreeNode
          :node="child"
          :selected-id="selectedId"
          :level="level + 1"
          @select="(n) => emit('select', n)"
        />
      </template>
    </div>
  </div>
</template>

<style scoped>
.tree-node-wrapper {
  user-select: none;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  margin: 1px 0;
}

.tree-node:hover {
  background: var(--color-bg-secondary);
}

.tree-node.is-selected {
  background: var(--color-accent-subtle);
}

.tree-node.is-selected .node-code,
.tree-node.is-selected .node-title {
  color: var(--color-accent);
  font-weight: 500;
}

.expand-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  transition: transform 0.2s ease;
}

.expand-icon.has-children {
  cursor: pointer;
}

.expand-icon.has-children:hover {
  color: var(--color-accent);
}

.expand-icon :deep(.rotated) {
  transform: rotate(90deg);
}

.node-code {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  min-width: 45px;
}

.node-title {
  flex: 1;
  font-size: 13px;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.leaf-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border-radius: 50%;
  margin-left: 4px;
}

/* 层级缩进 */
.level-1 { padding-left: 8px; }
.level-2 { padding-left: 24px; }
.level-3 { padding-left: 40px; }
.level-4 { padding-left: 56px; }
.level-5 { padding-left: 72px; }
.level-6 { padding-left: 88px; }
.level-7 { padding-left: 104px; }
.level-8 { padding-left: 120px; }

.children {
  margin-left: 0;
}
</style>
