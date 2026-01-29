<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

const props = defineProps<{
  loading: boolean
  formattedTime: string
  modelValue: {
    mc_resolution: number
    foreground_ratio: number
    do_remove_background: boolean
  }
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
  (e: 'generate'): void
  (e: 'update:imageUrl', value: string): void
}>()

const imageUrl = ref('')

const handleFileChange = (file: UploadFile) => {
  if (!file.raw) return
  emit('update:imageUrl', file.raw) // Actually we need to emit the file object to parent, but for preview we need URL
  imageUrl.value = URL.createObjectURL(file.raw)
  // We need to pass the file up to the parent
  emit('file-selected', file)
}

// Proxy params to support v-model
const params = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const emitGenerate = () => {
  emit('generate')
}
</script>

<template>
  <div class="input-section">
    <el-card class="box-card full-height-card">
      <template #header>
        <div class="card-header">
          <h3>TripoSR 3D Generator</h3>
          <p class="subtitle">Fast 3D Object Reconstruction</p>
        </div>
      </template>
      
      <div class="card-content-wrapper">
        <!-- Image Upload -->
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="false"
        >
          <div v-if="imageUrl" class="image-preview">
            <img :src="imageUrl" />
          </div>
          <template v-else>
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
          </template>
        </el-upload>

        <!-- Parameters Form -->
        <div class="params-form">
          <el-form label-position="top">
            <el-form-item>
              <template #label>
                <div class="param-label">
                  <span>Marching Cubes Resolution: {{ params.mc_resolution }}</span>
                </div>
              </template>
              <div class="slider-container">
                <el-slider v-model="params.mc_resolution" :min="32" :max="320" :step="32" :show-input="false" />
              </div>
            </el-form-item>
            
            <el-form-item>
              <template #label>
                <div class="param-label">
                  <span>Foreground Ratio: {{ params.foreground_ratio }}</span>
                </div>
              </template>
              <div class="slider-container">
                <el-slider v-model="params.foreground_ratio" :min="0.5" :max="1.0" :step="0.05" :show-input="false" />
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-checkbox v-model="params.do_remove_background" label="Remove Background" border />
            </el-form-item>

            <el-button type="primary" size="large" @click="emitGenerate" :loading="loading" style="width: 100%">
              {{ loading ? `Generating... (${formattedTime})` : 'Generate 3D Model' }}
            </el-button>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}
.card-header .subtitle {
  margin: 5px 0 0;
  font-size: 0.8rem;
  color: #666;
}

.input-section {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
}

.input-section .full-height-card :deep(.el-card__body) {
  padding: 20px;
  overflow-y: auto;
}

.card-content-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.image-preview {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.params-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.param-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.slider-container {
  width: 100%;
  padding: 0 10px;
  box-sizing: border-box;
}

:deep(.el-upload-dragger) {
  padding: 20px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .input-section {
    width: 100%;
    height: auto;
    flex-shrink: 1;
  }
}
</style>
