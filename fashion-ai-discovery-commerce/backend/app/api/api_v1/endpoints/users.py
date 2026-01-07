from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


class UserProfile(BaseModel):
    """사용자 프로필 모델"""
    user_id: str
    style_distribution: Dict[str, float]
    preferred_categories: List[str]
    preferred_colors: List[str]
    price_range: Dict[str, int]
    exploration_score: float


class UserProfileUpdate(BaseModel):
    """사용자 프로필 업데이트 모델"""
    style_distribution: Optional[Dict[str, float]] = None
    preferred_categories: Optional[List[str]] = None
    preferred_colors: Optional[List[str]] = None
    price_range: Optional[Dict[str, int]] = None
    exploration_score: Optional[float] = None


def get_user_service() -> UserService:
    """사용자 서비스 의존성"""
    return UserService()


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 프로필 조회"""
    try:
        profile = await user_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=404, 
                detail="사용자 프로필을 찾을 수 없습니다."
            )
        
        return UserProfile(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving user profile",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="프로필 조회 중 오류가 발생했습니다."
        )


@router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 프로필 업데이트"""
    try:
        result = await user_service.update_user_profile(
            user_id=user_id,
            profile_data=profile_update.dict(exclude_none=True)
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return {"message": "프로필이 업데이트되었습니다.", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating user profile",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="프로필 업데이트 중 오류가 발생했습니다."
        )


@router.post("/profile/{user_id}/initialize")
async def initialize_user_profile(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 프로필 초기화"""
    try:
        profile = await user_service.initialize_user_profile(user_id)
        
        return {
            "message": "프로필이 초기화되었습니다.",
            "profile": profile
        }
        
    except Exception as e:
        logger.error("Error initializing user profile",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="프로필 초기화 중 오류가 발생했습니다."
        )


@router.get("/preferences/{user_id}")
async def get_user_preferences(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 선호도 분석"""
    try:
        preferences = await user_service.analyze_user_preferences(user_id)
        
        return {
            "user_id": user_id,
            "preferences": preferences
        }
        
    except Exception as e:
        logger.error("Error analyzing user preferences",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="선호도 분석 중 오류가 발생했습니다."
        )


@router.get("/behavior/{user_id}")
async def get_user_behavior(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 행동 분석"""
    try:
        behavior = await user_service.get_user_behavior_analysis(user_id)
        
        return {
            "user_id": user_id,
            "behavior": behavior
        }
        
    except Exception as e:
        logger.error("Error analyzing user behavior",
                    user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="행동 분석 중 오류가 발생했습니다."
        )