import openai
import json
from typing import List, Dict, Optional, Any
from jinja2 import Template

from .prompt_templates import PromptTemplateManager
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ResponseGenerator:
    """AI 응답 생성기"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.template_manager = PromptTemplateManager()
        
        logger.info("Response generator initialized", model=model)
    
    async def generate_response(
        self,
        user_message: str,
        intent_result: Any,
        recommendations: List[Dict],
        user_profile: Optional[Dict] = None,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """
        사용자 메시지와 추천 결과를 바탕으로 AI 응답 생성
        
        Args:
            user_message: 사용자 메시지
            intent_result: 의도 분석 결과
            recommendations: 추천 상품 리스트
            user_profile: 사용자 프로필
            chat_history: 대화 히스토리
            
        Returns:
            str: 생성된 AI 응답
        """
        try:
            logger.info("Generating AI response", 
                       intent=intent_result.intent.value,
                       recommendations_count=len(recommendations))
            
            # 1. 적절한 프롬프트 템플릿 선택
            template_name = self._select_template(intent_result, recommendations)
            
            # 2. 프롬프트 컨텍스트 구성
            context = self._build_context(
                user_message=user_message,
                intent_result=intent_result,
                recommendations=recommendations,
                user_profile=user_profile,
                chat_history=chat_history
            )
            
            # 3. 프롬프트 생성
            prompt = self.template_manager.render_template(template_name, context)
            
            # 4. GPT API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.template_manager.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=settings.MAX_RESPONSE_LENGTH
            )
            
            ai_response = response.choices[0].message.content
            
            # 5. 후처리
            final_response = self._post_process_response(ai_response, intent_result)
            
            logger.info("AI response generated", 
                       response_length=len(final_response))
            
            return final_response
            
        except Exception as e:
            logger.error("Error generating AI response", 
                        intent=getattr(intent_result, 'intent', 'unknown'),
                        error=str(e))
            
            # 에러 시 기본 응답
            return self._get_fallback_response(intent_result, recommendations)
    
    def _select_template(self, intent_result: Any, recommendations: List[Dict]) -> str:
        """의도와 추천 결과에 따라 적절한 템플릿 선택"""
        
        if not recommendations:
            return "no_recommendations"
        
        intent_value = intent_result.intent.value
        exploration_intent = getattr(intent_result, 'exploration_intent', False)
        
        # 탐색 의도가 강한 경우
        if exploration_intent:
            return f"{intent_value}_exploration"
        
        # 기본 의도별 템플릿
        template_mapping = {
            "가격·가성비": "price_value",
            "감성·스타일": "style_mood", 
            "시즌·날씨": "season_weather",
            "체형·핏": "fit_body",
            "코디·상황": "coordination_situation"
        }
        
        return template_mapping.get(intent_value, "default")
    
    def _build_context(
        self,
        user_message: str,
        intent_result: Any,
        recommendations: List[Dict],
        user_profile: Optional[Dict] = None,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """프롬프트 템플릿을 위한 컨텍스트 구성"""
        
        # 추천 상품을 새로운 발견과 기존 취향으로 분류
        new_discoveries = []
        existing_preferences = []
        
        for rec in recommendations:
            if rec.get("recommendation_type") in ["exploration", "bridge"]:
                new_discoveries.append(rec)
            else:
                existing_preferences.append(rec)
        
        context = {
            "user_message": user_message,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "exploration_intent": getattr(intent_result, 'exploration_intent', False),
            "keywords": getattr(intent_result, 'keywords', []),
            "new_discoveries": new_discoveries,
            "existing_preferences": existing_preferences,
            "total_recommendations": len(recommendations),
            "use_emojis": settings.USE_EMOJIS
        }
        
        # 사용자 프로필 정보 추가
        if user_profile:
            context.update({
                "user_style": user_profile.get("style_distribution", {}),
                "preferred_categories": user_profile.get("preferred_categories", []),
                "price_range": user_profile.get("price_range", {})
            })
        
        # 대화 히스토리 정보 추가
        if chat_history:
            context["previous_interactions"] = len(chat_history)
            context["recent_topics"] = self._extract_recent_topics(chat_history)
        
        return context
    
    def _extract_recent_topics(self, chat_history: List[Dict]) -> List[str]:
        """최근 대화 주제 추출"""
        topics = []
        
        for msg in chat_history[-3:]:  # 최근 3개 메시지
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # 간단한 키워드 추출 (실제로는 더 정교한 방법 필요)
                if len(content) > 10:
                    topics.append(content[:50])
        
        return topics
    
    def _post_process_response(self, response: str, intent_result: Any) -> str:
        """응답 후처리"""
        
        # 이모지 사용 설정에 따른 처리
        if not settings.USE_EMOJIS:
            response = self._remove_emojis(response)
        
        # 길이 제한
        if len(response) > settings.MAX_RESPONSE_LENGTH:
            response = response[:settings.MAX_RESPONSE_LENGTH-3] + "..."
        
        # 추가 안전성 검사
        response = self._apply_safety_filters(response)
        
        return response.strip()
    
    def _remove_emojis(self, text: str) -> str:
        """텍스트에서 이모지 제거"""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)
    
    def _apply_safety_filters(self, response: str) -> str:
        """안전성 필터 적용"""
        # 부적절한 내용 필터링 (기본적인 예시)
        inappropriate_words = ["문제", "오류", "실패"]
        
        for word in inappropriate_words:
            if word in response:
                logger.warning("Potentially inappropriate content detected", 
                              word=word)
        
        return response
    
    def _get_fallback_response(
        self, 
        intent_result: Any, 
        recommendations: List[Dict]
    ) -> str:
        """에러 시 폴백 응답"""
        
        if not recommendations:
            return (
                "죄송합니다. 현재 조건에 맞는 상품을 찾지 못했어요. 😅\n"
                "다른 스타일이나 조건으로 다시 검색해보시겠어요?"
            )
        
        intent_value = getattr(intent_result, 'intent', None)
        if intent_value:
            return f"{intent_value.value} 관련 추천을 준비했어요! 확인해보시겠어요?"
        
        return (
            "추천 상품을 준비했어요! 어떤 스타일이 마음에 드시나요? 😊\n"
            "더 자세한 정보가 필요하시면 언제든 말씀해주세요."
        )