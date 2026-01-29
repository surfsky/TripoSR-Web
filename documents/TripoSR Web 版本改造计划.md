这是一个涉及跨语言协作的全栈开发任务。为了保证性能和用户体验，我建议采用 **Python 后端 (计算服务)** + **Node.js 全栈 (业务服务 + 前端)** 的架构。

## 架构设计

1.  **AI 计算服务 (Python)**
    *   **角色**: 核心计算引擎，常驻运行。
    *   **技术**: FastAPI。
    *   **原因**: TripoSR 模型加载耗时且占用显存，必须作为常驻服务运行，不能通过命令行频繁启动。
    *   **功能**: 提供 HTTP 接口，接收图片，返回 3D 模型文件 (GLB/OBJ)。

2.  **Web 业务服务 (Node.js)**
    *   **角色**: 业务后端，处理用户请求、文件存储。
    *   **技术**: Express + TypeScript。
    *   **功能**:
        *   提供文件上传接口。
        *   调用 Python 计算服务。
        *   管理静态资源（图片和生成的模型）。

3.  **前端应用 (Browser)**
    *   **角色**: 用户交互界面。
    *   **技术**: Vue 3 + TypeScript + Vite + Element Plus。
    *   **功能**:
        *   响应式布局。
        *   图片上传与预览。
        *   使用 `<model-viewer>` 或 Three.js 进行 3D 模型在线展示。

---

## 实施步骤

### 第一步：Python 服务化 (AI Engine)
1.  创建`tripo-server'目录，将原有项目文件移动到该目录；
2.  在`tripo-server`目录下创建`service.py`。
3.  引入 `FastAPI` 和现有 `tsr` 包。
4.  实现模型预加载（启动时加载一次）。
5.  开发 `/generate` 接口：接收 `UploadFile`，返回生成的 `.glb` 模型文件流。
6.  实现 access key 逻辑，用于验证请求来源是否授权。

### 第二步：Node.js 后端搭建 (Backend)
1.  初始化 `web-server` 目录。
2.  配置 Express 服务器与 Multer (文件上传)。
3.  开发 `/api/upload` 接口：
    *   接收前端上传的图片。
    *   转发请求给 Python 服务 (`localhost:8000/generate`)。
    *   接收 Python 返回的 GLB 文件并保存到本地 `public/models` 目录。
    *   返回模型访问 URL 给前端。

### 第三步：前端开发 (Frontend)
1.  初始化 `web-client` 目录 (Vite + Vue 3 + TS)。
2.  安装 `element-plus` 和 `@google/model-viewer`。
3.  开发主页面：
    *   **Header**: 简单的导航栏。
    *   **Main**: 左侧上传区域 (Element Plus Upload)，右侧/下方 3D 展示区域。
    *   **逻辑**: 上传成功后，自动在 `<model-viewer>` 中加载返回的模型 URL。

### 第四步：联调与测试
1.  启动 Python FastAPI 服务。
2.  启动 Node.js Express 服务。
3.  启动 Vite 前端开发服务器。
4.  测试完整流程：上传 -> 生成 -> 展示。
