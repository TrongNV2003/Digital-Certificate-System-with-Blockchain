import asyncio
from loguru import logger
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.routes import router
from backend.event_listener.event_listener import listen_events

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(listen_events())
    logger.info("Bắt đầu lắng nghe sự kiện blockchain")
    try:
        yield
    finally:
        task.cancel()
        logger.info("Ngừng lắng nghe sự kiện blockchain")


app = FastAPI(title="Hệ thống Chứng chỉ Số", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:2206"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

