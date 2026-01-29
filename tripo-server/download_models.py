import os
import urllib.request
import sys

def download_file(url, path):
    if os.path.exists(path):
        print(f"File already exists: {path}")
        return

    print(f"Downloading {url} to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading... {percent}%")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, path, reporthook=progress)
        print("\nDownload complete.")
    except Exception as e:
        print(f"\nError downloading file: {e}")
        if os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    # U2NET for background removal (used by rembg)
    # Mirror link can be replaced if slow
    u2net_url = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
    
    # Path relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    u2net_path = os.path.join(base_dir, ".u2net", "u2net.onnx")
    
    print(f"Checking model at: {u2net_path}")
    download_file(u2net_url, u2net_path)
