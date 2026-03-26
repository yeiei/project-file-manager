<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NCard, NModal, NForm, NFormItem, NInput, NSelect, NGrid, NGridItem, useMessage, useDialog } from 'naive-ui'
import { useProjectsStore } from '../stores/projects'
import ProjectCard from '../components/ProjectCard.vue'
import type { CreateProjectInput } from '../api'

const message = useMessage()
const dialog = useDialog()
const store = useProjectsStore()

const showModal = ref(false)
const formValue = ref<CreateProjectInput>({
  name: '',
  path: '',
  year: 2026,
  category: '',
  description: ''
})

const yearOptions = Array.from({ length: 22 }, (_, i) => ({
  label: String(2005 + i),
  value: 2005 + i
}))

onMounted(() => {
  store.fetchProjects()
})

const openModal = () => {
  formValue.value = {
    name: '',
    path: '',
    year: 2026,
    category: '',
    description: ''
  }
  showModal.value = true
}

const handleSubmit = async () => {
  if (!formValue.value.name || !formValue.value.path || !formValue.value.category) {
    message.warning('请填写必填项')
    return
  }
  
  try {
    await store.createProject(formValue.value)
    message.success('创建成功')
    showModal.value = false
  } catch (e) {
    message.error('创建失败')
  }
}

const handleDelete = (id: number) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这个项目吗？',
    positiveText: '确认',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await store.deleteProject(id)
        message.success('删除成功')
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}
</script>

<template>
  <div class="projects-page">
    <header class="page-header">
      <h1>项目列表</h1>
      <NButton type="primary" @click="openModal">新建项目</NButton>
    </header>

    <div class="projects-grid" v-if="store.projects.length > 0">
      <ProjectCard
        v-for="project in store.projects"
        :key="project.id"
        :project="project"
        @delete="handleDelete"
      />
    </div>

    <NCard v-else class="empty-card">
      <div class="empty-state">
        <p>暂无项目</p>
        <NButton type="primary" @click="openModal">创建第一个项目</NButton>
      </div>
    </NCard>

    <NModal v-model:show="showModal" preset="card" title="新建项目" style="width: 600px">
      <NForm :model="formValue" label-placement="left" label-width="80">
        <NFormItem label="项目名称" required>
          <NInput v-model:value="formValue.name" placeholder="请输入项目名称" />
        </NFormItem>
        
        <NFormItem label="项目路径" required>
          <NInput v-model:value="formValue.path" placeholder="请输入项目路径" />
        </NFormItem>

        <NFormItem label="年份">
          <NSelect v-model:value="formValue.year" :options="yearOptions" />
        </NFormItem>

        <NFormItem label="分类" required>
          <NInput v-model:value="formValue.category" placeholder="请输入分类" />
        </NFormItem>

        <NFormItem label="描述">
          <NInput
            v-model:value="formValue.description"
            type="textarea"
            placeholder="请输入描述"
            :rows="3"
          />
        </NFormItem>
      </NForm>

      <template #footer>
        <div class="modal-footer">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" @click="handleSubmit">创建</NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.projects-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.empty-card {
  text-align: center;
  padding: 48px 0;
}

.empty-state p {
  color: #999;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
