from fastapi import FastAPI

from app.routes import user

app = FastAPI(title="FlowChunk API", version="1.0.0")
app.include_router(user.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the FlowChunk API!"}
