# TripoSR Web Application

[中文文档](README_CN.md) | [TripoSR Original Project](https://github.com/VAST-AI-Research/TripoSR)

This project is a web-based interface for **TripoSR**, a state-of-the-art 3D object reconstruction model. It allows users to upload a single image and generate a high-quality 3D model in seconds.

## Screenshot

![Screenshot](documents/ScreenShot.png)

## Architecture

The application consists of three main components:

1.  **Tripo Server (`tripo-server`)**: A Python FastAPI service that hosts the TripoSR model and handles the core 3D generation logic.
2.  **Web Server (`web-server`)**: A Node.js Express server acting as a middleware to handle file uploads, storage, and communication with the Python service.
3.  **Web Client (`web-client`)**: A Vue 3 + Vite frontend application providing the user interface.

## Prerequisites

-   **Python 3.8+** (with CUDA support if using GPU)
-   **Node.js 16+**
-   **npm** or **yarn**

## Deployment Instructions

### 1. Setup Tripo Server (Python)

Navigate to the `tripo-server` directory and install dependencies:

```bash
cd tripo-server
pip install -r requirements.txt
```

**Download Models:**

Before starting, download the required background removal model:

```bash
python download_models.py
```

Start the Python service:

```bash
# Set U2NET_HOME if needed, though the code handles it automatically
python service.py
```

The service will start on `http://localhost:8000`.

### 2. Setup Web Server (Node.js)

Navigate to the `web-server` directory and install dependencies:

```bash
cd web-server
npm install
```

Start the middleware server:

```bash
npm run dev
```

The server will start on `http://localhost:3000`.

### 3. Setup Web Client (Vue)

Navigate to the `web-client` directory and install dependencies:

```bash
cd web-client
npm install
```

Start the frontend development server:

```bash
npm run dev
```

The client will be available at `http://localhost:5173`.

## Usage

1.  Open the web client in your browser (`http://localhost:5173`).
2.  Upload an image of an object (preferably with a clean background, though background removal is included).
3.  Adjust parameters if needed (Resolution, Foreground Ratio).
4.  Click "Generate 3D Model".
5.  View, rotate, and interact with the generated 3D model in real-time.
6.  Download the model as a `.glb` file.

## Features

-   **Fast Reconstruction**: Generates 3D models in seconds.
-   **Interactive Viewer**: Rotate, zoom, and pan the 3D model.
-   **View Modes**: Switch between default, front, side, and top views.
-   **Visual Helpers**: 3D Axis gizmo and wireframe/texture toggle.
-   **Download**: Export generated models for use in other 3D software.
