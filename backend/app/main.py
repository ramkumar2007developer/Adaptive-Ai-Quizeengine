import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.routers import quiz_routes, document_routes, analytics_routes, user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[main] Starting up... initializing database tables")
    await init_db()
    from app.rag.vector_store import get_vector_store
    get_vector_store()
    print("[main] Startup complete. Server is ready.")
    yield
    print("[main] Shutting down... cleaning up")
    await close_db()


settings = get_settings()

app = FastAPI(
    title="AI Assessment Engine API",
    description="Production-grade adaptive quiz backend with RAG pipeline",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health Check"])
async def health_check():
    return {
        "status": "ok",
        "provider": settings.LLM_PROVIDER,
        "model": settings.GROQ_MODEL,
        "version": "2.0.0",
    }


# Mount all routers
app.include_router(quiz_routes.router)
app.include_router(document_routes.router)
app.include_router(analytics_routes.router)
app.include_router(user_routes.router)


if __name__ == "__main__":
    import uvicorn
    print(f"[AI Assessment Engine] Starting server on http://localhost:{settings.PORT}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
