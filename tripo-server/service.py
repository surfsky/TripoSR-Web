
import logging
import os

# Set U2NET_HOME to the local .u2net directory
os.environ["U2NET_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".u2net")
logging.info(f"Set U2NET_HOME to: {os.environ['U2NET_HOME']}")

# Check if model exists
model_path = os.path.join(os.environ["U2NET_HOME"], "u2net.onnx")
if os.path.exists(model_path):
    logging.info(f"Found u2net model at: {model_path}")
else:
    logging.error(f"u2net model NOT found at: {model_path}")

import tempfile
import time
from contextlib import asynccontextmanager

import numpy as np
import rembg
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from PIL import Image

from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground

# Global model variables
model = None
rembg_session = None
device = "cuda:0" if torch.cuda.is_available() else "cpu"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, rembg_session
    # Load model on startup
    logging.info("Initializing model...")
    model = TSR.from_pretrained(
        "stabilityai/TripoSR",
        config_name="config.yaml",
        weight_name="model.ckpt",
    )
    model.renderer.set_chunk_size(8192)
    model.to(device)
    
    # Initialize background remover
    rembg_session = rembg.new_session()
    logging.info("Model initialized successfully")
    
    yield
    
    # Cleanup (if needed)
    pass

app = FastAPI(lifespan=lifespan)

def process_image(image_data: Image.Image, do_remove_background: bool, foreground_ratio: float):
    if do_remove_background:
        image = remove_background(image_data, rembg_session)
        image = resize_foreground(image, foreground_ratio)
        image = np.array(image).astype(np.float32) / 255.0
        image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
        image = Image.fromarray((image * 255.0).astype(np.uint8))
    else:
        image = image_data
        if image.mode == "RGBA":
            image = np.array(image).astype(np.float32) / 255.0
            image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
            image = Image.fromarray((image * 255.0).astype(np.uint8))
    return image

@app.post("/generate")
async def generate_model(
    file: UploadFile = File(...),
    mc_resolution: int = Form(256),
    foreground_ratio: float = Form(0.85),
    do_remove_background: bool = Form(True)
):
    if not model:
        raise HTTPException(status_code=500, detail="Model not initialized")
        
    try:
        # Read and process image
        input_image = Image.open(file.file).convert("RGB" if do_remove_background else "RGBA")
        processed_image = process_image(input_image, do_remove_background, foreground_ratio)
        
        # Run inference
        with torch.no_grad():
            scene_codes = model([processed_image], device=device)
            
        # Extract mesh
        meshes = model.extract_mesh(scene_codes, True, resolution=mc_resolution)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".glb", delete=False)
        meshes[0].export(temp_file.name)
        temp_file.close()
        
        return FileResponse(
            temp_file.name, 
            media_type="model/gltf-binary", 
            filename="model.glb"
        )
        
    except Exception as e:
        logging.error(f"Error generating model: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
