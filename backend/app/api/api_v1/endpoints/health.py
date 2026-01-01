from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, str]:
    """기본 헬스 체크"""
    return {
        "status": "healthy",
        "service": "Fashion AI Discovery Commerce",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, any]:
    """상세 헬스 체크"""
    return {
        "status": "healthy",
        "service": "Fashion AI Discovery Commerce",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "database": "not_implemented",
            "redis": "not_implemented", 
            "vector_db": "not_implemented",
            "openai": "not_implemented"
        }
    }