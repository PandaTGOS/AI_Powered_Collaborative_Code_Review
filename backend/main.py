import os
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import subprocess
from pathlib import Path

app = FastAPI()

# Local Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "deepseek-coder"

# Serve frontend files from the parent directory
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path / "static"), name="static")

@app.get("/")
async def get_frontend():
    return FileResponse(frontend_path / "static" / "index.html")

@app.websocket("/ws/{repo_id}")
async def websocket_endpoint(websocket: WebSocket, repo_id: str):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            # Echo back for demo purposes
            await websocket.send_json(data)
        except Exception as e:
            print(f"WebSocket error: {e}")
            break

async def query_ollama(prompt: str) -> str:
    """Send a prompt to the local Ollama model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30.0
            )
            return response.json()["response"]
    except Exception as e:
        return f"AI Error: {str(e)}"

@app.post("/analyze")
async def analyze_code(request: dict):
    """Analyze code using local LLM"""
    code = request.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    
    prompt = f"""
    Analyze this code and provide specific suggestions:
    - Identify potential bugs
    - Suggest optimizations
    - Point out style issues
    - Recommend security improvements
    
    Code:
    ```python
    {code}
    ```
    
    Respond in markdown format with clear sections.
    """
    
    suggestions = await query_ollama(prompt)
    return {"suggestions": suggestions}

def ensure_ollama_running():
    """Check if Ollama is running"""
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
        print(f"Model {MODEL_NAME} is ready")
    except subprocess.CalledProcessError as e:
        print(f"Ollama error: {e.stderr.decode()}")
        raise RuntimeError("Ollama not running. Please start Ollama first.")

if __name__ == "__main__":
    import uvicorn
    
    # Verify Ollama is ready
    ensure_ollama_running()
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)