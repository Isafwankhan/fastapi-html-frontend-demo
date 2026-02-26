from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from pathlib import Path

app = FastAPI()

# Create 'uploads' directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 1. Endpoint to upload a file
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Sanitize filename to prevent directory traversal
    safe_filename = Path(file.filename).name
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        # Save the file to the local folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save file")
        
    return {"message": f"File '{safe_filename}' uploaded successfully!"}

# 2. Endpoint to fetch and read the file
@app.get("/files/{filename}")
async def get_file(filename: str):
    # Sanitize filename to prevent directory traversal
    safe_filename = Path(filename).name
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read file")

# Serve the HTML UI
@app.get("/", response_class=HTMLResponse)
async def main():
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")
