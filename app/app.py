from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.core.database import SessionLocal
from app.routers import admin, user
from app.tasks.cleanup import run_user_cleanup

app = FastAPI(title="FlowChunk API", version="0.0.1")

app.include_router(user.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"])
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the FlowChunk API!"}


# -- Background cron jobs setup --

scheduler = BackgroundScheduler()


def cleanup_job():
    db = SessionLocal()

    try:
        run_user_cleanup(db)
    finally:
        db.close()


scheduler.add_job(
    cleanup_job,
    trigger="cron",
    hour=0,
    minute=0,
)

scheduler.start()
