<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NCard, NModal, NForm, NFormItem, NInput, NGrid, NGridItem, useMessage, useDialog, NSpace, NInputGroup, NDynamicTags, NInputNumber } from 'naive-ui'
import { useProjectsStore } from '../stores/projects'
import ProjectCard from '../components/ProjectCard.vue'
import type { CreateProjectInput } from '../api'

const message = useMessage()
const dialog = useDialog()
const store = useProjectsStore()

const currentYear = new Date().getFullYear()

const showModal = ref(false)
const formValue = ref<CreateProjectInput & { ownerTags: string[], debuggerTags: string[] }>({
  name: '',
  path: '',
  year: currentYear,
  category: '',
  description: '',
  owner: '',
  debugger: '',
  improvements: '',
  ownerTags: [],
  debuggerTags: []
})

onMounted(() => {
  store.fetchProjects()
})

const openModal = () => {
  formValue.value = {
    name: '',
    path: '',
    year: currentYear,
    category: '',
    description: '',
    owner: '',
    debugger: '',
    improvements: '',
    ownerTags: [],
    debuggerTags: []
  }
  showModal.value = true
}

const selectDirectory = () => {
  // 触发文件选择器 - 使用 input type="file" 选择目录
  const input = document.createElement('input')
  input.type = 'file'
  input.webkitdirectory = true
  input.multiple = false
  input.onchange = (e) => {
    const files = (e.target as HTMLInputElement).files
    if (files && files.length > 0) {
      // 获取选中的目录路径
      const file = files[0] as any
      // @ts-ignore - webkitRelativePath 包含目录路径
      const path = file.webkitRelativePath || file.name
      // 由于浏览器安全限制，我们只能获取文件名，使用提示让用户手动补充完整路径
      formValue.value.path = path.split('/').slice(0, -1).join('/') + '/'
      if (!formValue.value.path || formValue.value.path === '/') {
        formValue.value.path = file.name + '/'
      }
    }
  }
  input.click()
}

const handleSubmit = async () => {
  if (!formValue.value.name || !formValue.value.path || !formValue.value.category) {
    message.warning('请填写必填项')
    return
  }
  
  // 将标签数组转换为逗号分隔的字符串
  const submitData = {
    ...formValue.value,
    owner: formValue.value.ownerTags.join(', '),
    debugger: formValue.value.debuggerTags.join(', ')
  }
  // 删除临时字段
  delete (submitData as any).ownerTags
  delete (submitData as any).debuggerTags
  
  try {
    await store.createProject(submitData)
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
          <NInputGroup>
            <NInput v-model:value="formValue.path" placeholder="请输入或选择项目路径" />
            <NButton @click="selectDirectory">选择目录</NButton>
          </NInputGroup>
        </NFormItem>

        <NFormItem label="年份">
          <NInputNumber v-model:value="formValue.year" :show-button="false" placeholder="请输入年份" style="width: 100%" />
        </NFormItem>

        <NFormItem label="分类" required>
          <NInput v-model:value="formValue.category" placeholder="请输入分类" />
        </NFormItem>

        <NFormItem label="负责人">
          <NDynamicTags v-model:value="formValue.ownerTags" />
        </NFormItem>

        <NFormItem label="调试人">
          <NDynamicTags v-model:value="formValue.debuggerTags" />
        </NFormItem>

        <NFormItem label="改进内容">
          <NInput
            v-model:value="formValue.improvements"
            type="textarea"
            placeholder="请输入改进内容"
            :rows="2"
          />
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
