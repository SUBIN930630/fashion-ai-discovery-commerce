from fastapi import APIRouter

from app.api.api_v1.endpoints import chat, recommendations, users, health, admin, favorites, cart, orders

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])