<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { NCard, NButton, NModal, NInput, NColorPicker, NTag, NEmpty, NPopconfirm, NList, NListItem, NThing, NSpin } from 'naive-ui'
import { useTagsStore } from '../stores/tags'
import { tagsApi, type Tag } from '../api'

const tagsStore = useTagsStore()

const showModal = ref(false)
const editingTag = ref<Tag | null>(null)
const tagName = ref('')
const tagColor = ref('#1890ff')

const isEditing = computed(() => editingTag.value !== null)

onMounted(async () => {
  await tagsStore.fetchTags()
})

function openCreateModal() {
  editingTag.value = null
  tagName.value = ''
  tagColor.value = '#1890ff'
  showModal.value = true
}

function openEditModal(tag: Tag) {
  editingTag.value = tag
  tagName.value = tag.name
  tagColor.value = tag.color
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingTag.value = null
  tagName.value = ''
  tagColor.value = '#1890ff'
}

async function handleSave() {
  if (!tagName.value.trim()) return
  
  if (isEditing.value && editingTag.value) {
    await tagsStore.updateTag(editingTag.value.id, {
      name: tagName.value,
      color: tagColor.value
    })
  } else {
    await tagsStore.createTag({
      name: tagName.value,
      color: tagColor.value
    })
  }
  closeModal()
}

async function handleDelete(tag: Tag) {
  await tagsStore.deleteTag(tag.id)
}

const defaultColors = [
  '#ff4d4f', '#ff7a45', '#ffa940', '#ffc53d', '#d4f043',
  '#73d13d', '#36cfc9', '#40a9ff', '#597ef7', '#9254de',
  '#f759ab', '#ff85c0'
]

function selectColor(color: string) {
  tagColor.value = color
}
</script>

<template>
  <div class="tags-page">
    <div class="tags-header">
      <h2>标签管理</h2>
      <NButton type="primary" @click="openCreateModal">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        </template>
        新建标签
      </NButton>
    </div>

    <div class="tags-list" v-if="tagsStore.tags.length > 0">
      <NCard
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        class="tag-card"
        size="small"
      >
        <div class="tag-content">
          <NTag :bordered="false" :color="{ color: tag.color, textColor: '#fff' }">
            {{ tag.name }}
          </NTag>
          <div class="tag-actions">
            <NButton quaternary size="small" @click="openEditModal(tag)">
              <template #icon>
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              </template>
            </NButton>
            <NPopconfirm @positive-click="handleDelete(tag)">
              <template #trigger>
                <NButton quaternary size="small" type="error">
                  <template #icon>
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                  </template>
                </NButton>
              </template>
              确定删除标签 "{{ tag.name }}" 吗？
            </NPopconfirm>
          </div>
        </div>
      </NCard>
    </div>
    <NEmpty v-else description="暂无标签，点击新建按钮创建" />

    <!-- 创建/编辑弹窗 -->
    <NModal
      v-model:show="showModal"
      :title="isEditing ? '编辑标签' : '新建标签'"
      preset="card"
      style="width: 400px;"
      :mask-closable="!isEditing"
    >
      <div class="tag-form">
        <div class="form-item">
          <label>标签名称</label>
          <NInput v-model:value="tagName" placeholder="输入标签名称" />
        </div>
        <div class="form-item">
          <label>标签颜色</label>
          <div class="color-picker-row">
            <NColorPicker v-model:value="tagColor" :show-alpha="false" />
            <div class="quick-colors">
              <div
                v-for="color in defaultColors"
                :key="color"
                class="color-swatch"
                :style="{ backgroundColor: color }"
                :class="{ active: tagColor === color }"
                @click="selectColor(color)"
              />
            </div>
          </div>
        </div>
        <div class="form-preview">
          <label>预览</label>
          <NTag :color="{ color: tagColor, textColor: '#fff' }">
            {{ tagName || '标签名称' }}
          </NTag>
        </div>
      </div>
      <template #footer>
        <div class="modal-footer">
          <NButton @click="closeModal">取消</NButton>
          <NButton type="primary" @click="handleSave" :disabled="!tagName.trim()">保存</NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.tags-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.tags-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.tags-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-card {
  min-width: 180px;
}

.tag-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tag-actions {
  display: flex;
  gap: 4px;
}

.tag-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.color-picker-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.quick-colors {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.active {
  border-color: #333;
}

.form-preview label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
