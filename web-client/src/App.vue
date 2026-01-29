<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import axios from 'axios'
import type { UploadFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import InputPanel from './components/InputPanel.vue'
import ResultViewer from './components/ResultViewer.vue'

const modelUrl = ref('')
const loading = ref(false)
const error = ref('')

// Timer
const timer = ref(0)
const formattedTime = ref('00:00')
let timerInterval: any = null

const startTimer = () => {
  timer.value = 0
  formattedTime.value = '00:00'
  timerInterval = setInterval(() => {
    timer.value++
    const m = Math.floor(timer.value / 60).toString().padStart(2, '0')
    const s = (timer.value % 60).toString().padStart(2, '0')
    formattedTime.value = `${m}:${s}`
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
}

// Parameters
const params = reactive({
  mc_resolution: 256,
  foreground_ratio: 0.85,
  do_remove_background: true
})

// Add custom type for model-viewer element
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'model-viewer': any
    }
  }
}

const currentFileRaw = ref<File | null>(null)

const handleFileSelected = (file: UploadFile) => {
  if (!file.raw) return
  currentFileRaw.value = file.raw
}

const generateModel = async () => {
  if (!currentFileRaw.value) return
  
  loading.value = true
  error.value = ''
  modelUrl.value = ''
  startTimer()
  
  const formData = new FormData()
  formData.append('image', currentFileRaw.value)
  formData.append('mc_resolution', params.mc_resolution.toString())
  formData.append('foreground_ratio', params.foreground_ratio.toString())
  formData.append('do_remove_background', params.do_remove_background.toString())

  try {
    // Call Node.js backend
    const response = await axios.post('http://localhost:3000/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      modelUrl.value = response.data.modelUrl
    } else {
      const errorData = response.data || {}
      ElMessage.error(errorData.detail || 'Failed to generate model')
    }
  } catch (err: any) {
    console.error('Error:', err)
    error.value = err instanceof Error ? err.message : 'An error occurred'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
    stopTimer()
  }
}

onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <div class="container">
    <div class="main-layout">
      <!-- Left Column: Input & Settings -->
      <InputPanel 
        v-model="params"
        :loading="loading"
        :formatted-time="formattedTime"
        @generate="generateModel"
        @file-selected="handleFileSelected"
      />

      <!-- Right Column: Result -->
      <ResultViewer
        :model-url="modelUrl"
        :loading="loading"
        :formatted-time="formattedTime"
        :error="error"
      />
    </div>
  </div>
</template>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
  padding: 10px;
  box-sizing: border-box;
  background-color: #121212;
  overflow: hidden; /* Prevent scrollbar */
}

.main-layout {
  display: flex;
  gap: 10px;
  height: 100%;
  width: 100%;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
}
</style>
