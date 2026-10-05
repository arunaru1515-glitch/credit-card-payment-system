from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import router as auth_router
from routers.card_router import router as card_router
from routers.payment_router import router as payment_router


# ==================================================
# SWAGGER TAGS
# ==================================================

tags_metadata = [

    {
        "name": "Auth",
        "description": "User authentication and protected user operations",
    },

    {
        "name": "Cards",
        "description": "Credit and debit card management",
    },

    {
        "name": "Payments",
        "description": "Payment processing",
    },

]


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Credit Card Payment System",
    description="Credit Card Payment System API",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

allowed_origins = [
    # Local Vite frontend
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Docker React frontend
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# HOME
# ==================================================

@app.get("/", include_in_schema=False)
def home():
    return {
        "message": "Credit Card Payment System API is running"
    }


# ==================================================
# ROUTERS
# ==================================================

app.include_router(auth_router)
app.include_router(card_router)
app.include_router(payment_router)