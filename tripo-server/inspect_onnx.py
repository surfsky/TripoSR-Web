import onnxruntime as ort
import os

model_path = os.path.join(os.getcwd(), ".u2net", "u2net.onnx")

if not os.path.exists(model_path):
    print(f"Error: File not found at {model_path}")
    exit(1)

print(f"Loading model from: {model_path}")

try:
    session = ort.InferenceSession(model_path)
    
    print("\n=== Model Inputs ===")
    for i in session.get_inputs():
        print(f"Name: {i.name}, Shape: {i.shape}, Type: {i.type}")

    print("\n=== Model Outputs ===")
    for o in session.get_outputs():
        print(f"Name: {o.name}, Shape: {o.shape}, Type: {o.type}")

    print("\nModel loaded successfully with ONNX Runtime.")

except Exception as e:
    print(f"Error loading model: {e}")
