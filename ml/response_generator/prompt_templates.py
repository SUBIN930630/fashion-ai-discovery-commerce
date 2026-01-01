"""
프롬프트 템플릿 관리 모듈
기획서의 프롬프트 규칙을 기반으로 작성
"""

from jinja2 import Template
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class PromptTemplateManager:
    """프롬프트 템플릿 관리자"""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.templates = self._load_templates()
        logger.info("Prompt template manager initialized")
    
    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환"""
        return self.system_prompt
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """템플릿 렌더링"""
        try:
            if template_name not in self.templates:
                logger.warning("Template not found, using default", 
                              template_name=template_name)
                template_name = "default"
            
            template = Template(self.templates[template_name])
            rendered = template.render(**context)
            
            logger.debug("Template rendered", template_name=template_name)
            return rendered
            
        except Exception as e:
            logger.error("Error rendering template", 
                        template_name=template_name, 
                        error=str(e))
            return self._get_fallback_template(context)
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 정의"""
        return """
당신은 패션 이커머스 플랫폼의 AI 스타일리스트입니다. 
사용자의 질문 의도를 파악하고, 새로운 발견이 있는 맥락 맞춤 상품을 추천합니다.

## 핵심 원칙: 필터버블 해소
"매번 비슷한 상품만 보여요" 문제를 해결하는 것이 최우선 목표입니다.

### 추천 구성 비율
- 새로운 발견: 70% (기존에 추천하지 않았던 상품, 새로운 스타일)
- 기존 취향: 30% (사용자가 좋아했던 스타일 기반)

### 사용자 정보 활용
- 사용자의 좋아요 목록을 참고하여 이미 좋아한 상품과 유사하거나 대조되는 상품 추천
- 장바구니에 담은 상품 정보를 활용하여 코디 추천이나 추가 아이템 제안
- 전체 사용자들의 인기 상품 데이터를 참고하여 트렌드 반영
- 사용자가 이미 좋아요/장바구니에 담은 상품은 중복 추천하지 않음

### 응답 구조 (4단계)
1. 공감 + 의도 확인
2. 새로운 발견 추천 (70%)
3. 기존 취향 추천 (30%)
4. 꼬리질문 or 대안 제시

### 톤앤매너
- 친근하고 자연스러운 대화체
- 이모지 적절히 사용 (과하지 않게)
- 존댓말 사용
- 추천 이유 필수 포함
- 새로운 스타일 추천 시 "새로운 발견"으로 프레이밍

### 금지사항
- 같은 상품 반복 추천
- 같은 브랜드만 추천 (최대 2개)
- 비슷한 스타일만 추천
- 모호한 답변
- 3개 이상 연속 질문
"""
    
    def _load_templates(self) -> Dict[str, str]:
        """모든 템플릿 로드"""
        return {
            "price_value": self._price_value_template(),
            "price_value_exploration": self._price_value_exploration_template(),
            "style_mood": self._style_mood_template(),
            "style_mood_exploration": self._style_mood_exploration_template(),
            "season_weather": self._season_weather_template(),
            "season_weather_exploration": self._season_weather_exploration_template(),
            "fit_body": self._fit_body_template(),
            "fit_body_exploration": self._fit_body_exploration_template(),
            "coordination_situation": self._coordination_situation_template(),
            "coordination_situation_exploration": self._coordination_situation_exploration_template(),
            "default": self._default_template(),
            "no_recommendations": self._no_recommendations_template()
        }
    
    def _price_value_template(self) -> str:
        """가격·가성비 기반 템플릿"""
        return """
사용자 질문: {{ user_message }}
의도: {{ intent }} (신뢰도: {{ confidence }})

가성비 좋은 {% if keywords %}{{ keywords | join(", ") }}{% endif %}을/를 찾고 계시는군요! 👔

{% if new_discoveries %}
💡 **새로운 발견**

이번에는 평소 스타일과 조금 다른 아이템도 함께 추천드릴게요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}** - {{ "{:,}".format(item.price) }}원
   - {{ item.brand }}
   - {% if item.recommendation_type == "exploration" %}평소와 다른 새로운 스타일이에요!{% elif item.recommendation_type == "bridge" %}기존 취향과 비슷하지만 새로운 무드를 더했어요!{% endif %}
   - 비슷한 취향 고객들의 만족도가 높아요
{% endfor %}
{% endif %}

{% if existing_preferences %}
🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) + 1 }}. **{{ item.name }}** - {{ "{:,}".format(item.price) }}원
   - 평소 좋아하시는 스타일과 비슷해요
{% endfor %}
{% endif %}

혹시 선호하시는 컬러나 입으실 상황이 있으세요?
"""

    def _price_value_exploration_template(self) -> str:
        """가격·가성비 탐색 템플릿"""
        return """
가성비 좋은 새로운 스타일을 찾고 계시는군요! 🔍

💡 **새로운 발견**

예산 내에서 새로운 스타일도 도전해보세요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}** - {{ "{:,}".format(item.price) }}원
   - {{ item.brand }}
   - 새로운 스타일이지만 활용도가 높아요!
   - 가격 대비 만족도: ⭐⭐⭐⭐⭐
{% endfor %}

{% if existing_preferences %}
🏠 **안전한 선택**

물론 평소 스타일도 준비했어요 😊
{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}** - {{ "{:,}".format(item.price) }}원
{% endfor %}
{% endif %}

캐주얼 vs 깔끔한 느낌 중 어떤 쪽이 더 끌리세요?
"""

    def _style_mood_template(self) -> str:
        """감성·스타일 기반 템플릿"""
        return """
{% if "29CM" in user_message %}29CM 감성의{% elif "무신사" in user_message %}무신사 스타일의{% elif "미니멀" in user_message %}미니멀한{% elif "스트릿" in user_message %}스트릿{% endif %} 
{% if keywords %}{{ keywords | join(", ") }}{% endif %}을/를 찾고 계시는군요! ✨

{% if new_discoveries %}
💡 **새로운 발견**

평소 보시던 스타일 + 새로운 브랜드도 함께 추천드려요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }} (새로운 브랜드)
   - {% if item.recommendation_type == "exploration" %}평소 스타일과는 살짝 다르지만, 요즘 트렌드예요!{% elif item.recommendation_type == "bridge" %}기존 취향 + 새로운 무드를 더해봤어요!{% endif %}
   - 비슷한 취향 고객 {{ 30 + (loop.index * 15) }}%가 만족한 제품!
{% endfor %}
{% endif %}

{% if existing_preferences %}
🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
   - 이전에 좋아하셨던 스타일과 비슷해요
{% endfor %}
{% endif %}

출근용인가요, 데일리인가요?
"""

    def _style_mood_exploration_template(self) -> str:
        """감성·스타일 탐색 템플릿"""
        return """
새로운 스타일을 찾고 계시는군요! 🌟

💡 **새로운 발견**

평소와 다른 무드로 시도해볼 만한 스타일들이에요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - {% if "미니멀" in (user_style.keys() | list) %}미니멀 좋아하시는 분들이 새로 시도하는 스타일!{% else %}요즘 {{ (user_style.keys() | list)[0] if user_style else "스타일리시한" }} 좋아하시는 분들 사이에서 인기!{% endif %}
   - 의외로 잘 어울릴 수 있어요!
{% endfor %}

{% if existing_preferences %}
🏠 **기존 스타일**

물론 안전한 스타일도 준비했어요
{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
{% endfor %}
{% endif %}

가벼운 느낌 vs 묵직한 느낌 중 선호하시는 쪽이 있으세요?
"""

    def _season_weather_template(self) -> str:
        """시즌·날씨 기반 템플릿"""
        return """
{% if "봄" in user_message %}봄에{% elif "여름" in user_message %}여름에{% elif "가을" in user_message %}가을에{% elif "겨울" in user_message %}겨울에{% endif %}
활용하기 좋은 {% if keywords %}{{ keywords[-1] }}{% endif %}을/를 찾으시는군요! 🌸

💡 **새로운 발견**

올 시즌에는 새로운 스타일도 도전해보세요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - {% if "봄" in user_message %}봄에 딱 맞는 가벼운 소재예요{% elif "여름" in user_message %}시원하고 통기성이 좋아요{% elif "가을" in user_message %}적당한 보온성으로 가을에 완벽해요{% elif "겨울" in user_message %}따뜻하면서도 스타일리시해요{% endif %}
   - 작년에 안 보셨던 새로운 실루엣!
{% endfor %}

🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
   - 평소 좋아하시는 스타일과 비슷해요
{% endfor %}

캐주얼 vs 깔끔한 스타일 중 선호하시는 쪽이 있으세요?
"""

    def _season_weather_exploration_template(self) -> str:
        """시즌·날씨 탐색 템플릿"""
        return """
시즌에 맞는 새로운 스타일을 찾고 계시는군요! 🔍

💡 **새로운 발견**

이번 시즌 트렌드를 미리 만나보세요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - 새로운 시즌 트렌드 아이템
   - 기능성 + 스타일 두 마리 토끼!
{% endfor %}

🏠 **클래식한 선택**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
{% endfor %}

실내외 온도차를 고려하신 건가요?
"""

    def _fit_body_template(self) -> str:
        """체형·핏 기반 템플릿"""
        return """
{% if "키" in user_message %}키{% endif %} {% if keywords %}{{ keywords | join(", ") }}{% endif %}에 맞는 핏을 찾아볼게요! 👕

💡 **새로운 발견**

체형에 맞으면서도 새로운 스타일로 시도해볼 만한 아이템들이에요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - {% if "키" in user_message %}비율이 깔끔해 보이는 핏이에요{% else %}체형 커버에 좋은 디자인{% endif %}
   - 이전에 추천 안 드렸던 새로운 스타일!
{% endfor %}

🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
   - 평소 좋아하시는 핏과 비슷해요
{% endfor %}

평소 상의 사이즈는 어떻게 되세요? 캐주얼 vs 미니멀 중 선호는요?
"""

    def _fit_body_exploration_template(self) -> str:
        """체형·핏 탐색 템플릿"""
        return """
체형에 맞는 새로운 핏을 찾고 계시는군요! 💪

💡 **새로운 발견**

체형 보완 + 새로운 스타일을 동시에!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - 체형 보완 효과가 있으면서도 트렌디해요
   - 새로운 핏이지만 착용감이 편안해요
{% endfor %}

🏠 **안전한 핏**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
{% endfor %}

편안한 핏 vs 딱 맞는 핏 중 어떤 걸 선호하세요?
"""

    def _coordination_situation_template(self) -> str:
        """코디·상황 기반 템플릿"""
        return """
{% if "출근" in user_message %}출근룩{% elif "데이트" in user_message %}데이트룩{% elif "소개팅" in user_message %}소개팅룩{% elif "여행" in user_message %}여행룩{% elif "회식" in user_message %}회식룩{% endif %}을 찾고 계시는군요! 💼

{% if "출근" in user_message and new_discoveries %}
💡 **새로운 발견**

매일 비슷한 출근룩이 지겹다면, 이런 변화는 어떠세요?

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - {% if "셔츠" in item.name %}셔츠 대신 이런 스타일로 편안하면서 깔끔해요{% else %}출근룩에 새로운 무드를 줄 수 있어요!{% endif %}
   - 비슷한 직장인 고객 {{ 30 + (loop.index * 8) }}%가 시도한 스타일!
{% endfor %}
{% elif new_discoveries %}
💡 **새로운 발견**

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - 상황에 적합하면서도 새로운 스타일이에요
{% endfor %}
{% endif %}

🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
   - 무난하고 안전한 조합이에요
{% endfor %}

{% if "출근" in user_message %}회사 분위기가 캐주얼한 편인가요, 포멀한 편인가요?{% else %}어떤 분위기를 연출하고 싶으세요?{% endif %}
"""

    def _coordination_situation_exploration_template(self) -> str:
        """코디·상황 탐색 템플릿"""
        return """
상황에 맞는 새로운 스타일을 찾고 계시는군요! ✨

💡 **새로운 발견**

상황은 고려하되, 새로운 무드도 시도해보세요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - 상황에 적절하면서도 개성 있는 스타일
   - 주변 사람들에게 좋은 인상을 줄 수 있어요!
{% endfor %}

🏠 **안전한 선택**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
{% endfor %}

편안한 느낌 vs 세련된 느낌 중 어떤 쪽을 원하시나요?
"""

    def _default_template(self) -> str:
        """기본 템플릿"""
        return """
추천을 요청해주셔서 감사해요! {{ "😊" if use_emojis else "" }}

{% if new_discoveries %}
💡 **새로운 발견**

이번에는 새로운 스타일도 추천드릴게요!

{% for item in new_discoveries %}
{{ loop.index }}. **{{ item.name }}**
   - {{ item.brand }}
   - 평소와 다른 새로운 시도!
{% endfor %}
{% endif %}

{% if existing_preferences %}
🏠 **내 취향**

{% for item in existing_preferences %}
{{ loop.index + (new_discoveries|length) }}. **{{ item.name }}**
   - 평소 좋아하시는 스타일과 비슷해요
{% endfor %}
{% endif %}

어떤 상황에서 착용하실 건가요?
"""

    def _no_recommendations_template(self) -> str:
        """추천 없음 템플릿"""
        return """
죄송해요. 현재 조건에 맞는 상품을 찾지 못했어요. {{ "😅" if use_emojis else "" }}

다음과 같은 방법으로 다시 검색해보시면 어떨까요?

• 다른 스타일 키워드로 시도
• 가격대나 브랜드 조건 조정  
• 카테고리를 바꿔서 검색

혹시 구체적으로 어떤 스타일을 원하시나요?
"""

    def _get_fallback_template(self, context: Dict[str, Any]) -> str:
        """폴백 템플릿"""
        return f"""
안녕하세요! 패션 추천을 도와드릴게요.

현재 {context.get('total_recommendations', 0)}개의 상품을 추천드릴 수 있어요.
어떤 스타일이나 상황에 맞는 옷을 찾고 계신가요?

더 구체적으로 알려주시면 더 정확한 추천을 드릴 수 있어요!
"""