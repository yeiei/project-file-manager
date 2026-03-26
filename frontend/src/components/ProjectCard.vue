<script setup lang="ts">
import { NCard, NTag, NButton, NSpace, NDivider } from 'naive-ui'
import { computed } from 'vue'
import type { Project } from '../api'

const props = defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()

// 将逗号分隔的字符串转换为标签数组
const ownerTags = computed(() => {
  if (!props.project.owner) return []
  return props.project.owner.split(',').map(s => s.trim()).filter(s => s)
})

const debuggerTags = computed(() => {
  if (!props.project.debugger) return []
  return props.project.debugger.split(',').map(s => s.trim()).filter(s => s)
})

// 自定义字段
const customFields = computed(() => {
  if (!props.project.custom_fields) return []
  return Object.entries(props.project.custom_fields)
})
</script>

<template>
  <NCard hoverable>
    <template #header>
      <div class="card-header">
        <span class="project-name">{{ project.name }}</span>
        <NSpace>
          <NTag :bordered="false" type="info">{{ project.year }}</NTag>
        </NSpace>
      </div>
    </template>
    
    <div class="card-content">
      <p class="category">
        <strong>分类：</strong>{{ project.category }}
      </p>
      <p class="path">
        <strong>路径：</strong>{{ project.path }}
      </p>
      <template v-if="ownerTags.length > 0 || debuggerTags.length > 0">
        <NDivider style="margin: 8px 0" />
        <p class="owner" v-if="ownerTags.length > 0">
          <strong>负责人：</strong>
          <NTag v-for="tag in ownerTags" :key="tag" size="small" type="success" style="margin-right: 4px">{{ tag }}</NTag>
        </p>
        <p class="debugger" v-if="debuggerTags.length > 0">
          <strong>调试人：</strong>
          <NTag v-for="tag in debuggerTags" :key="tag" size="small" type="warning" style="margin-right: 4px">{{ tag }}</NTag>
        </p>
      </template>
      <template v-if="customFields.length > 0">
        <NDivider style="margin: 8px 0" />
        <div class="custom-fields">
          <p v-for="[key, value] in customFields" :key="key" class="custom-field">
            <strong>{{ key }}：</strong>{{ value }}
          </p>
        </div>
      </template>
      <p class="improvement" v-if="project.improvements">
        <strong>改进内容：</strong>{{ project.improvements }}
      </p>
      <p class="description" v-if="project.description">
        {{ project.description }}
      </p>
    </div>

    <template #footer>
      <NSpace justify="end">
        <NButton size="small" type="error" quaternary @click="emit('delete', project.id)">
          删除
        </NButton>
      </NSpace>
    </template>
  </NCard>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
}

.card-content p {
  margin-bottom: 8px;
  color: #666;
}

.category, .path, .owner, .debugger {
  font-size: 14px;
}

.improvement {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.description {
  font-size: 13px;
  color: #999;
  margin-top: 12px;
}

.custom-fields {
  margin-top: 4px;
}

.custom-field {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}
</style>
