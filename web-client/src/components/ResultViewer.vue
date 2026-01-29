<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Refresh, ZoomIn, ZoomOut, Rank, Operation, Picture, Coordinate, Top, Right, View, Download } from '@element-plus/icons-vue'

const props = defineProps<{
  modelUrl: string
  loading: boolean
  formattedTime: string
  error: string
}>()

const viewerRef = ref<any>(null)
const isGreyMode = ref(false)
const isPanMode = ref(false)
const currentView = ref('default') // 'default' | 'xy' | 'yz' | 'xz'

// Axis rotation
const axisRotation = ref('rotate(0deg)')

// Viewer Controls
/** Reset view to default perspective */
const resetView = () => {
  if (viewerRef.value) {
    viewerRef.value.cameraOrbit = '0deg 75deg 105%'
    viewerRef.value.fieldOfView = 'auto'
    currentView.value = 'default'
  }
}

/** Zoom In (Decrease FOV) */
const zoomIn = () => {
  if (viewerRef.value) {
    const currentFov = parseFloat(viewerRef.value.getFieldOfView()) || 30
    viewerRef.value.fieldOfView = `${Math.max(10, currentFov - 5)}deg`
  }
}

/** Zoom Out (Increase FOV) */
const zoomOut = () => {
  if (viewerRef.value) {
    const currentFov = parseFloat(viewerRef.value.getFieldOfView()) || 30
    viewerRef.value.fieldOfView = `${Math.min(90, currentFov + 5)}deg`
  }
}

/** Toggle between texture and grey mode */
const toggleGrey = () => {
  isGreyMode.value = !isGreyMode.value
}

/** Cycle through standard views (Front, Side, Top) */
const cycleViewMode = () => {
  if (!viewerRef.value) return

  if (currentView.value === 'default') {
    // Front View (XY plane approx)
    viewerRef.value.cameraOrbit = '0deg 90deg 105%'
    currentView.value = 'xy'
  } else if (currentView.value === 'xy') {
    // Side View (YZ plane approx)
    viewerRef.value.cameraOrbit = '90deg 90deg 105%'
    currentView.value = 'yz'
  } else if (currentView.value === 'yz') {
    // Top View (XZ plane approx)
    viewerRef.value.cameraOrbit = '0deg 0deg 105%'
    currentView.value = 'xz'
  } else {
    // Reset
    viewerRef.value.cameraOrbit = '0deg 75deg 105%'
    currentView.value = 'default'
  }
}

/** Toggle Pan Mode (Right-click/2-finger drag) */
const togglePanMode = () => {
  isPanMode.value = !isPanMode.value
}

/** Download the current model as GLB */
const downloadModel = () => {
  if (props.modelUrl) {
    const link = document.createElement('a')
    link.href = props.modelUrl
    link.download = `triposr-model-${Date.now()}.glb`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

/** Update the 3D Axis Gizmo based on camera orbit */
const updateAxis = (event: any) => {
  if (!viewerRef.value) return
  const orbit = viewerRef.value.getCameraOrbit()
  // orbit.theta is in radians. 
  const thetaDeg = (orbit.theta * 180) / Math.PI
  const phiDeg = (orbit.phi * 180) / Math.PI
  
  // Apply rotation to the axis container
  axisRotation.value = `rotateY(${-thetaDeg}deg) rotateX(${phiDeg - 90}deg)`
}

const getViewIcon = computed(() => {
  if (currentView.value === 'default') return View
  if (currentView.value === 'xy') return Coordinate // Front
  if (currentView.value === 'yz') return Right // Side
  if (currentView.value === 'xz') return Top // Top
  return View
})

const getViewTooltip = computed(() => {
  if (currentView.value === 'default') return 'Switch View (Current: Default)'
  if (currentView.value === 'xy') return 'Switch View (Current: Front XY)'
  if (currentView.value === 'yz') return 'Switch View (Current: Side YZ)'
  if (currentView.value === 'xz') return 'Switch View (Current: Top XZ)'
  return 'Switch View'
})

onMounted(() => {
  const viewer = viewerRef.value
  if (viewer) {
    viewer.addEventListener('camera-change', updateAxis)
  }
})

onUnmounted(() => {
  const viewer = viewerRef.value
  if (viewer) {
    viewer.removeEventListener('camera-change', updateAxis)
  }
})
</script>

<template>
  <div class="result-section">
    <el-card class="box-card result-card full-height-card">
      <div class="viewer-wrapper" v-loading="loading" :element-loading-text="`Generating... ${formattedTime}`">
        <div class="viewer-container" :class="{ 'grey-mode': isGreyMode, 'pan-mode': isPanMode }">
          <model-viewer
            ref="viewerRef"
            v-if="modelUrl"
            :src="modelUrl"
            camera-controls
            :auto-rotate="false"
            interaction-prompt="none"
            ar
            shadow-intensity="1"
            background-color="#f5f5f5"
            :disable-pan="!isPanMode"
            interpolation-decay="200"
            min-camera-orbit="auto auto auto"
            max-camera-orbit="auto auto auto"
            @camera-change="updateAxis"
            style="width: 100%; height: 100%;"
          >
          </model-viewer>
          
          <div v-else-if="!loading" class="placeholder">
            <el-empty description="Upload an image and click Generate" />
          </div>
          
          <!-- Mode Indicator Overlay -->
          <div class="mode-indicator" v-if="modelUrl">
            <span class="mode-text">{{ isPanMode ? 'Pan Mode: Right-Click / 2-Finger Drag' : 'Rotate Mode: Left-Click Drag' }}</span>
          </div>
          
          <!-- 3D Axis Gizmo -->
          <div class="axis-gizmo-container">
             <div class="axis-gizmo" :style="{ transform: axisRotation }">
                <!-- X Axis -->
                <div class="axis-arrow x-axis">
                    <div class="arrow-shaft"></div>
                    <div class="arrow-head"></div>
                    <span class="axis-label">X</span>
                </div>
                <!-- Y Axis -->
                <div class="axis-arrow y-axis">
                    <div class="arrow-shaft"></div>
                    <div class="arrow-head"></div>
                    <span class="axis-label">Y</span>
                </div>
                <!-- Z Axis -->
                <div class="axis-arrow z-axis">
                    <div class="arrow-shaft"></div>
                    <div class="arrow-head"></div>
                    <span class="axis-label">Z</span>
                </div>
                <!-- Origin -->
                <div class="axis-origin"></div>
             </div>
          </div>
        </div>

        <!-- Toolbar -->
        <div class="viewer-toolbar" v-if="modelUrl">
          <el-tooltip content="Reset View" placement="top">
            <el-button circle :icon="Refresh" @click="resetView" size="small" />
          </el-tooltip>
          
          <el-tooltip content="Pan Mode (Left-click drag)" placement="top">
            <el-button circle :icon="Rank" @click="togglePanMode" :type="isPanMode ? 'primary' : 'default'" size="small" />
          </el-tooltip>
          
          <el-tooltip :content="getViewTooltip" placement="top">
            <el-button circle :icon="getViewIcon" @click="cycleViewMode" :type="currentView !== 'default' ? 'primary' : 'default'" size="small" />
          </el-tooltip>

          <el-tooltip content="Zoom In" placement="top">
            <el-button circle :icon="ZoomIn" @click="zoomIn" size="small" />
          </el-tooltip>
          <el-tooltip content="Zoom Out" placement="top">
            <el-button circle :icon="ZoomOut" @click="zoomOut" size="small" />
          </el-tooltip>
          <el-tooltip :content="isGreyMode ? 'Show Texture' : 'Show Wireframe/Grey'" placement="top">
            <el-button circle :icon="isGreyMode ? Picture : Operation" @click="toggleGrey" size="small" />
          </el-tooltip>
          <el-tooltip content="Download Model" placement="top">
            <el-button circle :icon="Download" @click="downloadModel" size="small" type="success" />
          </el-tooltip>
        </div>
      </div>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        style="margin-top: 10px"
      />
    </el-card>
  </div>
</template>

<style scoped>
.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
}

.result-section .full-height-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.viewer-wrapper {
  position: relative;
  flex: 1;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  overflow: hidden;
}

.viewer-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.viewer-container.grey-mode model-viewer {
  filter: grayscale(100%) contrast(1.1);
}

.viewer-container.pan-mode {
  cursor: grab;
}

.viewer-toolbar {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 4px 8px;
  border-radius: 24px;
  display: flex;
  gap: 2px;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
  z-index: 100;
  white-space: nowrap;
}

/* Axis Gizmo Styles */
.axis-gizmo-container {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  perspective: 600px;
  pointer-events: none;
  z-index: 10;
}

.axis-gizmo {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}

.axis-arrow {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 4px;
    transform-origin: 0 50%;
    display: flex;
    align-items: center;
}

.arrow-shaft {
    flex: 1;
    height: 100%;
    border-radius: 2px;
}

.arrow-head {
    width: 0; 
    height: 0; 
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left-width: 8px;
    border-left-style: solid;
}

.axis-label {
    margin-left: 4px;
    font-size: 14px;
    font-weight: 900;
    text-shadow: 0 0 2px rgba(255, 255, 255, 0.8);
}

.axis-origin {
    position: absolute;
    bottom: -3px;
    left: -3px;
    width: 6px;
    height: 6px;
    background: #333;
    border-radius: 50%;
}

/* X Axis - Red */
.x-axis {
    transform: rotateY(0deg);
}
.x-axis .arrow-shaft { background-color: #ff3b30; box-shadow: 0 0 4px rgba(255, 59, 48, 0.4); }
.x-axis .arrow-head { border-left-color: #ff3b30; }
.x-axis .axis-label { color: #ff3b30; }

/* Y Axis - Green */
.y-axis {
    transform: rotateZ(-90deg); /* Points Up */
}
.y-axis .arrow-shaft { background-color: #4cd964; box-shadow: 0 0 4px rgba(76, 217, 100, 0.4); }
.y-axis .arrow-head { border-left-color: #4cd964; }
.y-axis .axis-label { color: #4cd964; transform: rotate(90deg); }

/* Z Axis - Blue */
.z-axis {
    transform: rotateY(90deg); /* Points Forward/Back */
}
.z-axis .arrow-shaft { background-color: #007aff; box-shadow: 0 0 4px rgba(0, 122, 255, 0.4); }
.z-axis .arrow-head { border-left-color: #007aff; }
.z-axis .axis-label { color: #007aff; transform: rotateY(-90deg); }


.mode-indicator {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  padding: 6px 12px;
  border-radius: 4px;
  pointer-events: none;
  z-index: 10;
}

.mode-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .result-section {
    height: 60vh;
  }
}
</style>
