from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.routes import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(title="RAG Resume Matcher")

    # Enable CORS for the frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve static files (frontend) from project root under /static
    app.mount("/static", StaticFiles(directory="."), name="static")

    # Serve the SPA index at root
    @app.get("/")
    async def serve_index():
        return FileResponse("index.html")

    app.include_router(api_router, prefix="")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

