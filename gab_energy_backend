from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, sales, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GAB Energy API",
    description="Fuel Sales Management System API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(sales.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "message": "GAB Energy API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


