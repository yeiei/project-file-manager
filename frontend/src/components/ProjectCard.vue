<script setup lang="ts">
import { NCard, NTag, NButton, NSpace } from 'naive-ui'
import type { Project } from '../api'

defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()
</script>

<template>
  <NCard hoverable>
    <template #header>
      <div class="card-header">
        <span class="project-name">{{ project.name }}</span>
        <NTag :bordered="false" type="info">{{ project.year }}</NTag>
      </div>
    </template>
    
    <div class="card-content">
      <p class="category">
        <strong>分类：</strong>{{ project.category }}
      </p>
      <p class="path">
        <strong>路径：</strong>{{ project.path }}
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

.category, .path {
  font-size: 14px;
}

.description {
  font-size: 13px;
  color: #999;
  margin-top: 12px;
}
</style>
