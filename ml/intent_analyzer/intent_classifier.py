import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
import openai
from pydantic import BaseModel

from .few_shot_prompts import FEW_SHOT_EXAMPLES, SYSTEM_PROMPT


class Intent(str, Enum):
    """사용자 의도 분류"""
    PRICE_VALUE = "가격·가성비"
    STYLE_MOOD = "감성·스타일"  
    SEASON_WEATHER = "시즌·날씨"
    FIT_BODY = "체형·핏"
    COORDINATION_SITUATION = "코디·상황"


class IntentResult(BaseModel):
    """의도 분석 결과"""
    intent: Intent
    confidence: float
    exploration_intent: bool  # 탐색 의도 여부
    category_shift: bool  # 카테고리 전환 여부
    recommendation_strategy: Dict[str, float]  # 추천 전략 비율
    keywords: List[str]  # 추출된 키워드
    reasoning: str  # 분석 근거


class IntentClassifier:
    """사용자 의도 분석 클래스"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
    async def classify_intent(
        self, 
        user_message: str,
        chat_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None
    ) -> IntentResult:
        """
        사용자 메시지에서 의도를 분석합니다.
        
        Args:
            user_message: 사용자 메시지
            chat_history: 대화 히스토리
            user_profile: 사용자 프로필 (기존 취향 정보)
            
        Returns:
            IntentResult: 분석된 의도 정보
        """
        
        # 프롬프트 구성
        prompt = self._build_prompt(user_message, chat_history, user_profile)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 일관성을 위해 낮은 temperature
                max_tokens=800
            )
            
            # JSON 응답 파싱
            result_json = json.loads(response.choices[0].message.content)
            
            return IntentResult(
                intent=Intent(result_json["intent"]),
                confidence=result_json["confidence"],
                exploration_intent=result_json["exploration_intent"],
                category_shift=result_json["category_shift"],
                recommendation_strategy=result_json["recommendation_strategy"],
                keywords=result_json["keywords"],
                reasoning=result_json["reasoning"]
            )
            
        except Exception as e:
            # 기본값 반환
            return IntentResult(
                intent=Intent.STYLE_MOOD,
                confidence=0.5,
                exploration_intent=False,
                category_shift=False,
                recommendation_strategy={"exploitation": 0.7, "exploration": 0.3},
                keywords=[],
                reasoning=f"분석 중 오류 발생: {str(e)}"
            )
    
    def _build_prompt(
        self, 
        user_message: str,
        chat_history: Optional[List[Dict]] = None,
        user_profile: Optional[Dict] = None
    ) -> str:
        """분석을 위한 프롬프트를 구성합니다."""
        
        prompt_parts = []
        
        # Few-shot 예시 추가
        prompt_parts.append("=== 예시 ===")
        for example in FEW_SHOT_EXAMPLES:
            prompt_parts.append(f"질문: {example['question']}")
            prompt_parts.append(f"분석: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}")
            prompt_parts.append("")
        
        # 사용자 프로필 정보
        if user_profile:
            prompt_parts.append("=== 사용자 프로필 ===")
            prompt_parts.append(f"기존 취향: {user_profile.get('style_distribution', {})}")
            prompt_parts.append(f"선호 카테고리: {user_profile.get('preferred_categories', [])}")
            prompt_parts.append(f"탐색 점수: {user_profile.get('exploration_score', 0.3)}")
            prompt_parts.append("")
        
        # 대화 히스토리
        if chat_history and len(chat_history) > 0:
            prompt_parts.append("=== 대화 히스토리 ===")
            for msg in chat_history[-3:]:  # 최근 3개 메시지만
                prompt_parts.append(f"{msg['role']}: {msg['content']}")
            prompt_parts.append("")
        
        # 현재 사용자 질문
        prompt_parts.append("=== 분석할 질문 ===")
        prompt_parts.append(f"질문: {user_message}")
        prompt_parts.append("")
        prompt_parts.append("위 질문을 분석하여 JSON 형식으로 응답해주세요:")
        
        return "\n".join(prompt_parts)
    
    def detect_exploration_signals(self, message: str, user_profile: Optional[Dict] = None) -> bool:
        """탐색 의도 신호를 감지합니다."""
        
        explicit_signals = [
            "새로운", "다른", "새롭게", "처음", "변화", "도전",
            "추천", "뭐가 좋아", "어떤 게", "다양한", "여러", "색다른"
        ]
        
        # 명시적 탐색 신호
        for signal in explicit_signals:
            if signal in message:
                return True
        
        # 카테고리 전환 감지
        if user_profile and self._detect_category_shift(message, user_profile):
            return True
            
        return False
    
    def _detect_category_shift(self, message: str, user_profile: Dict) -> bool:
        """카테고리 전환을 감지합니다."""
        
        current_categories = set(user_profile.get('preferred_categories', []))
        
        # 메시지에서 언급된 카테고리 추출
        categories_mentioned = set()
        category_keywords = {
            "상의": ["티셔츠", "셔츠", "후드티", "맨투맨", "니트", "가디건"],
            "하의": ["바지", "팬츠", "슬랙스", "청바지", "조거팬츠", "치노"],
            "아우터": ["자켓", "코트", "패딩", "바람막이", "가디건", "블레이저"],
            "신발": ["운동화", "구두", "부츠", "슬리퍼", "샌들"],
            "악세서리": ["모자", "가방", "시계", "목걸이", "반지"]
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    categories_mentioned.add(category)
                    break
        
        # 기존 선호 카테고리와 다른 카테고리 언급시 전환으로 감지
        return len(categories_mentioned - current_categories) > 0
    
    def calculate_recommendation_strategy(
        self, 
        intent: Intent,
        exploration_intent: bool,
        category_shift: bool,
        user_exploration_score: float = 0.3
    ) -> Dict[str, float]:
        """추천 전략 비율을 계산합니다."""
        
        # 기본 비율
        base_exploitation = 0.7
        base_exploration = 0.3
        
        # 명시적 탐색 요청
        if exploration_intent:
            return {"exploitation": 0.3, "exploration": 0.7}
        
        # 카테고리 전환
        if category_shift:
            return {"exploitation": 0.3, "bridge": 0.5, "exploration": 0.2}
        
        # 사용자 탐색 성향에 따른 조정
        if user_exploration_score > 0.6:
            return {"exploitation": 0.5, "exploration": 0.5}
        elif user_exploration_score < 0.2:
            return {"exploitation": 0.8, "exploration": 0.2}
        
        # 기본값
        return {"exploitation": base_exploitation, "exploration": base_exploration}