<script setup lang="ts">
import { NCard, NTag, NButton, NSpace, NDivider } from 'naive-ui'
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
      <template v-if="project.owner || project.debugger">
        <NDivider style="margin: 8px 0" />
        <p class="owner" v-if="project.owner">
          <strong>负责人：</strong>{{ project.owner }}
        </p>
        <p class="debugger" v-if="project.debugger">
          <strong>调试人：</strong>{{ project.debugger }}
        </p>
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
</style>
