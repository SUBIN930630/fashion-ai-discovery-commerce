"""
Few-shot learning을 위한 프롬프트와 예시들
기획서의 프롬프트 규칙을 기반으로 작성
"""

SYSTEM_PROMPT = """
당신은 패션 이커머스 플랫폼의 AI 스타일리스트입니다. 
사용자의 질문을 분석하여 다음 5가지 Intent로 분류하고, 
필터버블 해소를 위한 추천 전략을 제시해야 합니다.

### Intent 분류:
1. 가격·가성비: 가격, 가성비, 저렴, 부담 없는, 학생, 예산 관련
2. 감성·스타일: 미니멀, 스트릿, 무드, 감성, 트렌디, 깔끔, 29CM, 무신사 관련
3. 시즌·날씨: 봄, 여름, 가을, 겨울, 장마, 더위, 추위 관련
4. 체형·핏: 키, 체형, 핏, 마른, 배, 어깨, 다리, cm 관련
5. 코디·상황: 출근, 데이트, 소개팅, 여행, 회식, 면접 관련

### 분석 요소:
- exploration_intent: 탐색 의도 (새로운 것을 찾는지)
- category_shift: 카테고리 전환 (평소와 다른 카테고리 요청)
- recommendation_strategy: 추천 비율 (exploitation/exploration/bridge)

응답은 반드시 JSON 형식으로 해주세요.
"""

FEW_SHOT_EXAMPLES = [
    {
        "question": "10만 원대 자켓 추천해줘",
        "analysis": {
            "intent": "가격·가성비",
            "confidence": 0.95,
            "exploration_intent": False,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.7,
                "exploration": 0.3
            },
            "keywords": ["10만원대", "자켓", "추천"],
            "reasoning": "명확한 가격대 언급으로 가격·가성비 의도. 특별한 탐색 신호 없음."
        }
    },
    {
        "question": "새로운 스타일 보여줘",
        "analysis": {
            "intent": "감성·스타일",
            "confidence": 0.9,
            "exploration_intent": True,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.3,
                "exploration": 0.7
            },
            "keywords": ["새로운", "스타일"],
            "reasoning": "'새로운'이라는 명시적 탐색 신호. 높은 탐색 비율 필요."
        }
    },
    {
        "question": "29CM 감성의 미니멀 셔츠 추천해줘",
        "analysis": {
            "intent": "감성·스타일",
            "confidence": 0.95,
            "exploration_intent": False,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.7,
                "exploration": 0.3
            },
            "keywords": ["29CM", "감성", "미니멀", "셔츠"],
            "reasoning": "29CM 감성과 미니멀이라는 구체적 스타일 언급. 명확한 취향 표현."
        }
    },
    {
        "question": "재킷 추천해줘",
        "analysis": {
            "intent": "감성·스타일",
            "confidence": 0.7,
            "exploration_intent": False,
            "category_shift": True,
            "recommendation_strategy": {
                "exploitation": 0.3,
                "bridge": 0.5,
                "exploration": 0.2
            },
            "keywords": ["재킷", "추천"],
            "reasoning": "평소 후드티 위주였는데 재킷 요청 → 카테고리 전환. 브릿지 스타일 강화 필요."
        }
    },
    {
        "question": "키 175cm인데 오버핏으로 입기 좋은 봄 자켓 추천해줘",
        "analysis": {
            "intent": "체형·핏",
            "confidence": 0.9,
            "exploration_intent": False,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.6,
                "exploration": 0.4
            },
            "keywords": ["키", "175cm", "오버핏", "봄", "자켓"],
            "reasoning": "구체적인 키와 핏 언급으로 체형·핏 의도가 주. 시즌(봄) 요소도 포함."
        }
    },
    {
        "question": "출근할 때 입기 좋은 코디",
        "analysis": {
            "intent": "코디·상황",
            "confidence": 0.95,
            "exploration_intent": False,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.7,
                "exploration": 0.3
            },
            "keywords": ["출근", "코디"],
            "reasoning": "명확한 상황(출근) 언급. TPO에 맞는 추천 필요."
        }
    },
    {
        "question": "스트릿 느낌 나는 아우터 뭐가 좋아?",
        "analysis": {
            "intent": "감성·스타일",
            "confidence": 0.85,
            "exploration_intent": True,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.4,
                "exploration": 0.6
            },
            "keywords": ["스트릿", "느낌", "아우터", "뭐가 좋아"],
            "reasoning": "'뭐가 좋아?'라는 표현에서 탐색 의도 감지. 스트릿 스타일 중심으로 다양한 옵션 제시 필요."
        }
    },
    {
        "question": "봄에 입기 좋은 자켓 뭐야?",
        "analysis": {
            "intent": "시즌·날씨",
            "confidence": 0.9,
            "exploration_intent": True,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.4,
                "exploration": 0.6
            },
            "keywords": ["봄", "자켓", "뭐야"],
            "reasoning": "시즌 중심 질문이지만 '뭐야?'에서 탐색 의도 엿보임. 봄 시즌에 맞는 다양한 자켓 제시."
        }
    },
    {
        "question": "학생한테 부담 없는 코디",
        "analysis": {
            "intent": "가격·가성비",
            "confidence": 0.9,
            "exploration_intent": False,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.7,
                "exploration": 0.3
            },
            "keywords": ["학생", "부담 없는", "코디"],
            "reasoning": "'학생', '부담 없는'에서 가격 고려사항 명확. 가성비 중심 추천."
        }
    },
    {
        "question": "다른 거 없어?",
        "analysis": {
            "intent": "감성·스타일",
            "confidence": 0.8,
            "exploration_intent": True,
            "category_shift": False,
            "recommendation_strategy": {
                "exploitation": 0.2,
                "exploration": 0.8
            },
            "keywords": ["다른", "없어"],
            "reasoning": "'다른 거'라는 명시적 탐색 요청. 기존 추천과 다른 스타일 높은 비율로 제시."
        }
    }
]

# 키워드 매핑
INTENT_KEYWORDS = {
    "가격·가성비": [
        "가격", "가성비", "저렴", "부담 없는", "학생", "예산", "만원", "원",
        "싸게", "합리적", "경제적", "할인", "세일", "특가"
    ],
    "감성·스타일": [
        "미니멀", "스트릿", "무드", "감성", "트렌디", "깔끔", "29CM", "무신사",
        "스타일", "느낌", "분위기", "룩", "패션", "세련", "모던", "클래식",
        "캐주얼", "포멀", "시크"
    ],
    "시즌·날씨": [
        "봄", "여름", "가을", "겨울", "장마", "더위", "추위", "날씨",
        "시즌", "계절", "온도", "햇빛", "비", "눈", "바람", "습도"
    ],
    "체형·핏": [
        "키", "체형", "핏", "마른", "배", "어깨", "다리", "cm", "몸매",
        "비율", "실루엣", "사이즈", "오버핏", "레귤러핏", "슬림핏",
        "루즈핏", "타이트", "와이드"
    ],
    "코디·상황": [
        "출근", "데이트", "소개팅", "여행", "회식", "면접", "결혼식",
        "파티", "모임", "학교", "캠퍼스", "일상", "데일리", "주말",
        "휴가", "외출"
    ]
}

# 탐색 신호 키워드
EXPLORATION_SIGNALS = [
    "새로운", "새롭게", "다른", "다양한", "여러", "색다른", "신선한",
    "처음", "변화", "도전", "시도", "추천", "뭐가 좋아", "어떤 게",
    "없어?", "뭐야?", "어때?", "괜찮은", "좋은"
]

# 카테고리 키워드
CATEGORY_KEYWORDS = {
    "상의": ["티셔츠", "셔츠", "후드티", "맨투맨", "니트", "가디건", "블라우스", "탱크톱"],
    "하의": ["바지", "팬츠", "슬랙스", "청바지", "조거팬츠", "치노", "와이드팬츠", "스키니"],
    "아우터": ["자켓", "코트", "패딩", "바람막이", "가디건", "블레이저", "트러커", "MA-1"],
    "신발": ["운동화", "구두", "부츠", "슬리퍼", "샌들", "로퍼", "스니커즈", "하이탑"],
    "악세서리": ["모자", "가방", "시계", "목걸이", "반지", "귀걸이", "팔찌", "벨트"]
}