import openai
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Any
from jinja2 import Template

from .prompt_templates import PromptTemplateManager
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ResponseGenerator:
    """AI 응답 생성기"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.template_manager = PromptTemplateManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
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
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()

            response = await loop.run_in_executor(
                self.executor,
                self._create_completion_sync,
                prompt,
                chat_history,
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

    def _create_completion_sync(self, prompt: str, chat_history: Optional[List[Dict]] = None):
        """
        동기 호출을 스레드에서 실행하기 위한 래퍼
        
        Args:
            prompt: 현재 사용자 프롬프트
            chat_history: 대화 히스토리 (이전 메시지들)
        """
        messages = []
        
        # 1. 시스템 프롬프트 추가
        messages.append({
            "role": "system",
            "content": self.template_manager.get_system_prompt()
        })
        
        # 2. 대화 히스토리 추가 (최근 10개 메시지만, 토큰 제한 고려)
        if chat_history:
            # 최근 10개 메시지만 포함 (user와 assistant 쌍으로 최대 5쌍)
            recent_history = chat_history[-10:]
            
            for msg in recent_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                # role이 user 또는 assistant인 경우만 추가
                if role in ["user", "assistant"] and content:
                    messages.append({
                        "role": role,
                        "content": content
                    })
        
        # 3. 현재 사용자 프롬프트 추가
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=settings.MAX_RESPONSE_LENGTH,
        )
    
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
        
        # 문서 규칙: 새로운 발견 70%, 기존 취향 30% 비율 계산
        total_count = len(recommendations)
        new_discoveries_target = max(1, int(total_count * 0.7))  # 최소 1개
        existing_preferences_target = max(1, total_count - new_discoveries_target)  # 최소 1개
        
        # 실제 개수와 목표 개수 중 작은 값 사용
        new_discoveries_display = new_discoveries[:new_discoveries_target]
        existing_preferences_display = existing_preferences[:existing_preferences_target]
        
        context = {
            "user_message": user_message,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "exploration_intent": getattr(intent_result, 'exploration_intent', False),
            "keywords": getattr(intent_result, 'keywords', []),
            "new_discoveries": new_discoveries_display,  # 70% 비율로 제한된 리스트
            "existing_preferences": existing_preferences_display,  # 30% 비율로 제한된 리스트
            "new_discoveries_all": new_discoveries,  # 전체 리스트 (필요시 사용)
            "existing_preferences_all": existing_preferences,  # 전체 리스트 (필요시 사용)
            "total_recommendations": len(recommendations),
            "new_discoveries_count": len(new_discoveries_display),
            "existing_preferences_count": len(existing_preferences_display),
            "use_emojis": settings.USE_EMOJIS
        }
        
        # 사용자 프로필 정보 추가 (좋아요, 장바구니 정보 포함)
        if user_profile:
            context.update({
                "user_style": user_profile.get("style_distribution", {}),
                "preferred_categories": user_profile.get("preferred_categories", []),
                "price_range": user_profile.get("price_range", {}),
                # 좋아요 정보
                "user_favorites": user_profile.get("favorites", []),
                "user_favorite_product_ids": user_profile.get("favorite_product_ids", []),
                "user_favorites_count": user_profile.get("stats", {}).get("favorites_count", 0),
                # 장바구니 정보
                "user_cart_items": user_profile.get("cart_items", []),
                "user_cart_product_ids": user_profile.get("cart_product_ids", []),
                "user_cart_count": user_profile.get("stats", {}).get("cart_items_count", 0),
                "user_cart_total_price": user_profile.get("stats", {}).get("cart_total_price", 0),
                # 전체 사용자 통계 (인기 상품 등)
                "popular_products": user_profile.get("popular_products", []),
                "global_stats": user_profile.get("global_stats", {})
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
        """
        응답 후처리
        문서 규칙: 최대 2개 질문 (3개 이상 연속 질문 금지)
        """
        import re
        
        # 문서 규칙: 꼬리질문 개수 제한 (최대 2개)
        response = self._limit_question_count(response)
        
        # 비율 정보 제거 (70%, 30% 등)
        response = self._remove_percentage_info(response)
        
        # 이모지 사용 설정에 따른 처리
        if not settings.USE_EMOJIS:
            response = self._remove_emojis(response)
        
        # 길이 제한
        if len(response) > settings.MAX_RESPONSE_LENGTH:
            response = response[:settings.MAX_RESPONSE_LENGTH-3] + "..."
        
        # 추가 안전성 검사
        response = self._apply_safety_filters(response)
        
        return response.strip()
    
    def _limit_question_count(self, response: str) -> str:
        """
        질문 개수 제한 (문서 규칙: 최대 2개)
        
        Args:
            response: 원본 응답 텍스트
            
        Returns:
            질문 개수가 2개 이하로 제한된 응답
        """
        import re
        
        # 질문 마커 찾기 (?, ?!, ?? 등)
        question_pattern = r'[?？][!！]*'
        question_matches = list(re.finditer(question_pattern, response))
        
        question_count = len(question_matches)
        
        # 문서 규칙: 최대 2개 질문
        if question_count <= 2:
            logger.debug("Question count within limit", count=question_count)
            return response
        
        logger.warning("Question count exceeds limit, limiting to 2",
                      original_count=question_count,
                      limit=2)
        
        # 2개 초과 시 마지막 2개 질문만 유지
        # 문장 단위로 분리하여 처리
        # 문장 구분자: . ! ? (한글/영문 모두)
        sentence_endings = r'([.!?。！？]\s*)'
        parts = re.split(sentence_endings, response)
        
        # 질문이 포함된 문장 인덱스 찾기
        question_sentence_indices = []
        current_text = ""
        
        for i, part in enumerate(parts):
            current_text += part
            # 문장 끝을 만나면 확인
            if re.search(r'[.!?。！？]', part):
                if re.search(question_pattern, current_text):
                    question_sentence_indices.append(i)
                current_text = ""
        
        # 마지막 부분도 확인
        if current_text and re.search(question_pattern, current_text):
            question_sentence_indices.append(len(parts) - 1)
        
        # 마지막 2개 질문 문장만 유지
        if len(question_sentence_indices) > 2:
            # 마지막 2개 질문 문장의 인덱스
            last_two_indices = question_sentence_indices[-2:]
            first_question_idx = last_two_indices[0]
            
            # 첫 번째 질문 문장 이전의 모든 문장은 유지
            # 첫 번째 질문 문장부터 마지막 질문 문장까지 유지
            result_parts = []
            for i, part in enumerate(parts):
                if i <= last_two_indices[-1]:
                    result_parts.append(part)
                else:
                    break
            
            response = ''.join(result_parts).strip()
        else:
            # 질문이 2개 이하면 그대로 유지 (이미 위에서 처리됨)
            pass
        
        # 최종 검증
        final_questions = list(re.finditer(question_pattern, response))
        final_count = len(final_questions)
        
        if final_count > 2:
            # 여전히 2개 초과면 가장 간단한 방법: 마지막 질문만 유지
            if final_questions:
                last_question_end = final_questions[-1].end()
                # 마지막 질문 이전의 텍스트도 유지하되, 중간 질문은 제거
                # 간단하게: 마지막 질문이 포함된 문장만 유지
                response = response[:last_question_end]
                logger.info("Applied strict question limit", final_count=1)
        else:
            logger.info("Question count limited successfully",
                       original_count=question_count,
                       final_count=final_count)
        
        return response
    
    def _remove_percentage_info(self, text: str) -> str:
        """
        응답에서 비율 정보 제거 (70%, 30% 등)
        예: "새로운 발견 추천 (70%)" -> "새로운 발견 추천"
        """
        import re
        
        # (70%), (30%), (50%) 등의 패턴 제거
        text = re.sub(r'\s*\(\d+%\)\s*', '', text)
        
        # "새로운 발견 추천 70%" -> "새로운 발견 추천"
        text = re.sub(r'\s*\d+%\s*', '', text)
        
        # "70%", "30%" 같은 단독 비율 텍스트 제거
        text = re.sub(r'\b\d+%\b', '', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
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
