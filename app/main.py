from fastapi import FastAPI

app = FastAPI(
    title="FlowChunk API",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FlowChunk API!"
    }