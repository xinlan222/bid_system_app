"""API v1 router aggregation."""
# ruff: noqa: I001 - Imports structured for Jinja2 template conditionals

from fastapi import APIRouter

from app.api.routes.v1 import health
from app.api.routes.v1 import auth, users
from app.api.routes.v1 import items
from app.api.routes.v1 import agent
from app.api.routes.v1 import bid_documents

v1_router = APIRouter()

# Health check routes (no auth required)
v1_router.include_router(health.router, tags=["health"])

# Authentication routes
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# User routes
v1_router.include_router(users.router, prefix="/users", tags=["users"])

# Example CRUD routes (items)
v1_router.include_router(items.router, prefix="/items", tags=["items"])

# AI Agent routes
v1_router.include_router(agent.router, tags=["agent"])

# Bid documents routes
v1_router.include_router(bid_documents.router, prefix="/bid-documents", tags=["bid_documents"])
