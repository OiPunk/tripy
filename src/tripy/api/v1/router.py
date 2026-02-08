from __future__ import annotations

from fastapi import APIRouter

from tripy.api.v1.endpoints import admin, auth, graph, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(graph.router)
api_router.include_router(admin.router)
