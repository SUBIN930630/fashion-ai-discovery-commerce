#!/usr/bin/env python3
"""
통합 테스트 스크립트
전체 시스템의 주요 컴포넌트들이 올바르게 작동하는지 검증
"""

import sys
import os
import asyncio
from typing import Dict, Any

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """필수 모듈 import 테스트"""
    print("🔍 Testing imports...")
    
    try:
        # Backend imports
        from backend.app.core.config import settings
        from backend.app.core.logging import get_logger
        from backend.app.models.chat import ChatSession, ChatMessage
        from backend.app.services.chat_service import ChatService
        from backend.app.services.session_service import SessionService
        from backend.app.services.user_service import UserService
        from backend.app.services.recommendation_service import RecommendationService
        print("  ✅ Backend modules imported successfully")
        
        # ML imports
        from ml.intent_analyzer import IntentClassifier, FEW_SHOT_EXAMPLES
        from ml.vector_search import VectorStore, SearchEngine, EmbeddingService
        from ml.mmr_algorithm import MMRScorer, DiversityCalculator
        from ml.response_generator import ResponseGenerator, PromptTemplateManager
        print("  ✅ ML modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_configuration():
    """설정 로딩 테스트"""
    print("🔍 Testing configuration...")
    
    try:
        from backend.app.core.config import settings
        
        # 기본 설정 확인
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'VERSION')
        assert hasattr(settings, 'MMR_LAMBDA')
        assert hasattr(settings, 'MAX_RECOMMENDATIONS')
        
        print(f"  ✅ App Name: {settings.APP_NAME}")
        print(f"  ✅ Version: {settings.VERSION}")
        print(f"  ✅ MMR Lambda: {settings.MMR_LAMBDA}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_intent_analysis():
    """의도 분석 모듈 테스트"""
    print("🔍 Testing intent analysis...")
    
    try:
        from ml.intent_analyzer import IntentClassifier, Intent, FEW_SHOT_EXAMPLES
        
        # Few-shot 예시 확인
        assert len(FEW_SHOT_EXAMPLES) > 0
        assert all('question' in ex and 'analysis' in ex for ex in FEW_SHOT_EXAMPLES)
        print(f"  ✅ Few-shot examples loaded: {len(FEW_SHOT_EXAMPLES)} examples")
        
        # Intent enum 확인
        intents = list(Intent)
        assert len(intents) == 5
        print(f"  ✅ Intent categories: {[intent.value for intent in intents]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Intent analysis error: {e}")
        return False

def test_vector_search():
    """벡터 검색 모듈 테스트"""
    print("🔍 Testing vector search...")
    
    try:
        from ml.vector_search import EmbeddingService, VectorStore, SearchEngine
        
        # 임베딩 서비스 초기화 테스트 (API 키 없이)
        # embedding_service = EmbeddingService("test_key")
        print("  ✅ EmbeddingService class available")
        
        # 벡터 스토어 클래스 확인
        print("  ✅ VectorStore class available")
        
        # 검색 엔진 클래스 확인
        print("  ✅ SearchEngine class available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vector search error: {e}")
        return False

def test_mmr_algorithm():
    """MMR 알고리즘 테스트"""
    print("🔍 Testing MMR algorithm...")
    
    try:
        from ml.mmr_algorithm import MMRScorer, DiversityCalculator, ProductCandidate, RecommendationType
        import numpy as np
        
        # MMR 스코어러 초기화
        mmr_scorer = MMRScorer(lambda_param=0.7)
        assert mmr_scorer.lambda_param == 0.7
        print("  ✅ MMRScorer initialized")
        
        # 다양성 계산기 초기화
        diversity_calc = DiversityCalculator()
        print("  ✅ DiversityCalculator initialized")
        
        # 추천 유형 확인
        rec_types = list(RecommendationType)
        assert len(rec_types) == 3
        print(f"  ✅ Recommendation types: {[rt.value for rt in rec_types]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MMR algorithm error: {e}")
        return False

def test_response_generation():
    """응답 생성 모듈 테스트"""
    print("🔍 Testing response generation...")
    
    try:
        from ml.response_generator import ResponseGenerator, PromptTemplateManager
        
        # 템플릿 매니저 초기화
        template_manager = PromptTemplateManager()
        assert hasattr(template_manager, 'templates')
        print(f"  ✅ Templates loaded: {len(template_manager.templates)} templates")
        
        # 시스템 프롬프트 확인
        system_prompt = template_manager.get_system_prompt()
        assert len(system_prompt) > 100
        assert "스타일리스트" in system_prompt
        print("  ✅ System prompt loaded")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Response generation error: {e}")
        return False

async def test_services():
    """서비스 클래스들 테스트"""
    print("🔍 Testing services...")
    
    try:
        from backend.app.services.chat_service import ChatService
        from backend.app.services.session_service import SessionService
        from backend.app.services.user_service import UserService
        from backend.app.services.recommendation_service import RecommendationService
        from backend.app.models.chat import ChatSession
        from datetime import datetime
        
        # 세션 서비스 테스트
        session_service = SessionService()
        test_session = await session_service.create_session("test_user_123")
        assert isinstance(test_session, ChatSession)
        assert test_session.user_id == "test_user_123"
        print("  ✅ SessionService working")
        
        # 사용자 서비스 테스트
        user_service = UserService()
        profile = await user_service.initialize_user_profile("test_user_123")
        assert profile["user_id"] == "test_user_123"
        assert "style_distribution" in profile
        print("  ✅ UserService working")
        
        # 추천 서비스 테스트
        rec_service = RecommendationService()
        recommendations = await rec_service.get_recommendations(
            query="테스트 쿼리",
            user_id="test_user_123",
            limit=5
        )
        assert "recommendations" in recommendations
        assert "diversity_score" in recommendations
        print("  ✅ RecommendationService working")
        
        print("  ⚠️  ChatService requires API keys - skipping detailed test")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Services error: {e}")
        return False

def test_api_structure():
    """API 구조 테스트"""
    print("🔍 Testing API structure...")
    
    try:
        from backend.app.api.api_v1.api import api_router
        from backend.app.api.api_v1.endpoints import chat, recommendations, users, health
        
        # 라우터 확인
        assert api_router is not None
        print("  ✅ API router configured")
        
        # 엔드포인트 모듈 확인
        assert hasattr(chat, 'router')
        assert hasattr(recommendations, 'router')
        assert hasattr(users, 'router')
        assert hasattr(health, 'router')
        print("  ✅ All endpoint routers available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API structure error: {e}")
        return False

async def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 Starting Fashion AI Discovery Commerce Integration Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration), 
        ("Intent Analysis Tests", test_intent_analysis),
        ("Vector Search Tests", test_vector_search),
        ("MMR Algorithm Tests", test_mmr_algorithm),
        ("Response Generation Tests", test_response_generation),
        ("API Structure Tests", test_api_structure),
        ("Services Tests", test_services),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("TEST RESULTS SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review and fix issues before deployment.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        exit_code = 0 if result else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Tests failed with unexpected error: {e}")
        sys.exit(1)