from fastapi import FastAPI, Request
from inference import run_inference  # Importing from your root inference.py
import uvicorn

app = FastAPI()

# Health Check Endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "Ecommerce Bot API is live"}

# Prediction Endpoint
@app.post("/predict")
async def predict(request: Request):
    data = await request.json()
    # Assuming your inference.py has a function called run_inference
    result = run_inference(data) 
    return {"prediction": result}

# The Reset Endpoint (which your logs show is already working)
@app.post("/reset")
async def reset():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
