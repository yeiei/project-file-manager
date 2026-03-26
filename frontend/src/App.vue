<script setup lang="ts">
import { ref } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, NTabs, NTabPane, NLayout, NLayoutContent } from 'naive-ui'
import Projects from './views/Projects.vue'
import FileBrowser from './views/FileBrowser.vue'

const activeTab = ref('projects')
</script>

<template>
  <NConfigProvider>
    <NMessageProvider>
      <NDialogProvider>
        <NLayout class="app-layout">
          <NLayoutContent>
            <NTabs v-model:value="activeTab" type="line" animated>
              <NTabPane name="projects" tab="项目管理">
                <Projects />
              </NTabPane>
              <NTabPane name="files" tab="文件浏览">
                <FileBrowser />
              </NTabPane>
            </NTabs>
          </NLayoutContent>
        </NLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f5f5;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-layout {
  height: 100vh;
}
</style>
