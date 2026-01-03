# 패션 AI 추천 시스템 - AI 기능 정리

## 📋 목차
1. [전체 구조 개요](#전체-구조-개요)
2. [핵심 AI 모듈](#핵심-ai-모듈)
3. [서비스 레이어](#서비스-레이어)
4. [API 엔드포인트](#api-엔드포인트)
5. [실행 흐름](#실행-흐름)

---

## 전체 구조 개요

### AI 기능 아키텍처
```
사용자 메시지 입력
    ↓
[Intent Analyzer] - 의도 분석 (5가지 Intent 분류)
    ↓
[Vector Search] - 벡터 기반 상품 검색
    ↓
[MMR Algorithm] - 다양성 있는 추천 선택
    ↓
[Response Generator] - 자연어 응답 생성
    ↓
최종 추천 결과 + AI 응답
```

### 기술 스택
- **LLM**: GPT-4o-mini (OpenAI)
- **Embedding**: text-embedding-3-large (OpenAI)
- **Vector Store**: SQL 기반 (PostgreSQL/SQLite)
- **알고리즘**: MMR (Maximal Marginal Relevance)

---

## 핵심 AI 모듈

### 1. Intent Analyzer (의도 분석)
**위치**: `ml/intent_analyzer/`

#### 주요 파일
- `intent_classifier.py` - 의도 분류 클래스
- `few_shot_prompts.py` - Few-shot 학습 프롬프트

#### 기능
1. **5가지 Intent 분류**
   - 가격·가성비
   - 감성·스타일
   - 시즌·날씨
   - 체형·핏
   - 코디·상황

2. **탐색 의도 감지**
   - "새로운 스타일 보여줘" → exploration_intent: True
   - "다른 거 없어?" → exploration_intent: True

3. **카테고리 전환 감지**
   - 평소 후드티 → 재킷 요청 시 category_shift: True

4. **추천 전략 비율 결정**
   - 탐색 모드: exploitation 30% / exploration 70%
   - 활용 모드: exploitation 70% / exploration 30%
   - 카테고리 전환: exploitation 30% / bridge 50% / exploration 20%

#### 사용 예시
```python
from ml.intent_analyzer import IntentClassifier

classifier = IntentClassifier(api_key="your-key")
result = await classifier.classify_intent(
    user_message="새로운 스타일 보여줘",
    chat_history=[],
    user_profile={}
)

# 결과: IntentResult
# - intent: "감성·스타일"
# - exploration_intent: True
# - recommendation_strategy: {"exploitation": 0.3, "exploration": 0.7}
```

---

### 2. Vector Search (벡터 검색)
**위치**: `ml/vector_search/`

#### 주요 파일
- `embedding_service.py` - 임베딩 생성 서비스
- `search_engine.py` - 검색 엔진
- `sql_vector_store.py` - SQL 기반 벡터 스토어
- `vector_store.py` - 벡터 스토어 추상 클래스 (Pinecone/Weaviate 지원)

#### 기능
1. **임베딩 생성**
   - 상품 정보 → 벡터 변환 (3072차원)
   - 사용자 쿼리 → 벡터 변환
   - 캐싱 지원 (중복 호출 방지)

2. **유사도 검색**
   - 코사인 유사도 기반 검색
   - SQL 기반 벡터 검색 (Pinecone 대체)
   - 필터링 지원 (카테고리, 브랜드, 가격 등)

3. **유사도 범위별 검색**
   - High Similarity (>0.8): 기존 취향
   - Mid Similarity (0.5~0.8): 브릿지 스타일
   - Low Similarity (0.3~0.5): 새로운 발견

#### 사용 예시
```python
from ml.vector_search import SearchEngine

search_engine = SearchEngine(db=db_session)
candidates = await search_engine.search_products(
    query="미니멀 셔츠",
    user_profile={"preferred_styles": ["미니멀"]},
    limit=50
)

# 결과: List[ProductCandidate]
# - similarity_score: 유사도 점수
# - recommendation_type: EXPLOITATION/EXPLORATION/BRIDGE
```

---

### 3. MMR Algorithm (다양성 추천)
**위치**: `ml/mmr_algorithm/`

#### 주요 파일
- `mmr_scorer.py` - MMR 알고리즘 구현
- `diversity_calculator.py` - 다양성 점수 계산

#### 기능
1. **MMR 점수 계산**
   ```
   MMR = λ × Similarity(q, d) - (1-λ) × max Similarity(d, d')
   ```
   - λ (lambda): 0.7 (기본값)
   - 유사도와 다양성의 균형

2. **다양성 보장**
   - 스타일 다양성 (3개 이상 다른 스타일 필수)
   - 카테고리 다양성
   - 컬러 다양성
   - 가격 다양성
   - 브랜드 다양성 (동일 브랜드 최대 2개)

3. **추천 전략 반영**
   - exploitation/exploration/bridge 비율에 따라 선택
   - 유형별 목표 개수 자동 계산

#### 사용 예시
```python
from ml.mmr_algorithm import MMRScorer

mmr_scorer = MMRScorer(lambda_param=0.7)
result = await mmr_scorer.select_recommendations(
    query_embedding=query_vector,
    candidates=product_candidates,
    target_count=10,
    strategy={"exploitation": 0.7, "exploration": 0.3}
)

# 결과: MMRResult
# - selected_products: 선택된 상품 리스트
# - total_diversity_score: 전체 다양성 점수
# - type_distribution: 유형별 분포
```

---

### 4. Response Generator (응답 생성)
**위치**: `ml/response_generator/`

#### 주요 파일
- `response_generator.py` - 응답 생성 클래스
- `prompt_templates.py` - 프롬프트 템플릿 관리

#### 기능
1. **의도별 템플릿 선택**
   - 가격·가성비 → price_value 템플릿
   - 감성·스타일 → style_mood 템플릿
   - 시즌·날씨 → season_weather 템플릿
   - 체형·핏 → fit_body 템플릿
   - 코디·상황 → coordination_situation 템플릿

2. **응답 구조 (4단계)**
   - 공감 + 의도 확인
   - 새로운 발견 추천 (70%)
   - 기존 취향 추천 (30%)
   - 꼬리질문 or 대안 제시 (최대 2개)

3. **후처리 규칙**
   - 질문 개수 제한 (최대 2개)
   - 이모지 사용 제어
   - 길이 제한 (1000자)
   - 안전성 필터

#### 사용 예시
```python
from ml.response_generator import ResponseGenerator

generator = ResponseGenerator(api_key="your-key")
response = await generator.generate_response(
    user_message="미니멀 셔츠 추천해줘",
    intent_result=intent_result,
    recommendations=recommendations,
    user_profile=user_profile,
    chat_history=chat_history
)

# 결과: 자연어 응답 문자열
```

---

## 서비스 레이어

### 5. Chat Service (통합 서비스)
**위치**: `backend/app/services/chat_service.py`

#### 기능
1. **전체 프로세스 통합**
   - 의도 분석 → 상품 검색 → MMR 선택 → 응답 생성

2. **사용자 프로필 관리**
   - 좋아요 목록 조회
   - 장바구니 정보 조회
   - 사용자 취향 분석

3. **재추천 방지**
   - 최근 5회 대화에서 추천한 상품 제외
   - 클릭하지 않은 상품 우선 제외

4. **스타일 다양성 강제**
   - 최소 3개 이상 다른 스타일 포함
   - 부족 시 자동으로 추가 상품 선택

#### 주요 메서드
```python
class ChatService:
    async def process_message(
        self, 
        user_message: str, 
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        1. 대화 히스토리 조회
        2. 사용자 프로필 조회
        3. 의도 분석
        4. 상품 검색 및 추천
        5. AI 응답 생성
        6. 메시지 저장
        """
```

---

### 6. Recommendation Service (추천 서비스)
**위치**: `backend/app/services/recommendation_service.py`

#### 기능
1. **사용자 취향 분석**
   - 좋아요/장바구니 기반 스타일 분포 계산
   - 선호 카테고리/브랜드 추출
   - 가격 범위 분석

2. **추천 히스토리 관리**
   - 추천 내역 저장
   - 피드백 기록 (클릭, 좋아요, 구매 등)

3. **사용자 분석**
   - 추천 패턴 분석
   - 탐색률 계산
   - 피드백 분석

#### 주요 메서드
```python
class RecommendationService:
    async def analyze_user_preferences_from_db(
        self, user_id: str
    ) -> Dict[str, Any]:
        """
        DB에서 사용자 취향 분석
        - style_distribution: 스타일 분포
        - preferred_categories: 선호 카테고리
        - preferred_brands: 선호 브랜드
        - price_range: 가격 범위
        """
```

---

## API 엔드포인트

### 7. Chat API
**위치**: `backend/app/api/api_v1/endpoints/chat.py`

#### 엔드포인트
1. **POST /api/v1/chat/message**
   - 사용자 메시지 처리
   - AI 응답 및 추천 반환

2. **GET /api/v1/chat/history/{session_id}**
   - 대화 히스토리 조회

3. **GET /api/v1/chat/sessions/{user_id}**
   - 사용자 세션 목록 조회

4. **WebSocket /api/v1/chat/ws/{user_id}**
   - 실시간 채팅 지원

#### 요청/응답 예시
```json
// 요청
{
  "message": "미니멀 셔츠 추천해줘",
  "user_id": "user123",
  "session_id": "session456"
}

// 응답
{
  "response": "미니멀 스타일의 셔츠를 추천해드릴게요! ...",
  "session_id": "session456",
  "recommendations": [
    {
      "id": "prod001",
      "name": "미니멀 코튼 셔츠",
      "brand": "브랜드A",
      "price": 59000,
      "similarity_score": 0.92,
      "recommendation_type": "exploitation"
    }
  ],
  "intent": "감성·스타일",
  "confidence": 0.95
}
```

---

## 실행 흐름

### 전체 프로세스
```
1. 사용자 메시지 입력
   "미니멀 셔츠 추천해줘"
   ↓
2. ChatService.process_message()
   ↓
3. IntentClassifier.classify_intent()
   → IntentResult {
       intent: "감성·스타일",
       exploration_intent: False,
       recommendation_strategy: {exploitation: 0.7, exploration: 0.3}
     }
   ↓
4. SearchEngine.search_products()
   → 임베딩 생성 → 벡터 검색 → 50개 후보 선정
   ↓
5. MMRScorer.select_recommendations()
   → MMR 알고리즘 → 10개 선택 (다양성 보장)
   ↓
6. 스타일 다양성 강제 검증
   → 3개 이상 다른 스타일 확인 → 부족 시 추가 선택
   ↓
7. ResponseGenerator.generate_response()
   → 프롬프트 생성 → GPT API 호출 → 후처리
   ↓
8. 최종 응답 반환
   {
     response: "미니멀 스타일의 셔츠를 추천해드릴게요! ...",
     recommendations: [...],
     intent: "감성·스타일"
   }
```

---

## 주요 규칙 및 제약사항

### 필터버블 해소 규칙
1. **추천 비율**
   - 새로운 발견: 70%
   - 기존 취향: 30%

2. **스타일 다양성**
   - 최소 3개 이상 다른 스타일 포함

3. **브랜드 제한**
   - 동일 브랜드 최대 2개

4. **재추천 방지**
   - 최근 5회 대화에서 추천한 상품 제외
   - 클릭하지 않은 상품 우선 제외

### 응답 생성 규칙
1. **질문 개수 제한**
   - 최대 2개 질문

2. **응답 구조**
   - 공감 → 새로운 발견 (70%) → 기존 취향 (30%) → 꼬리질문

3. **톤앤매너**
   - 친근한 대화체
   - 이모지 적절히 사용
   - 존댓말 사용

---

## 설정 파일

### 환경 변수 (backend/app/core/config.py)
```python
# OpenAI
OPENAI_API_KEY: str
OPENAI_MODEL: str = "gpt-4o-mini"
EMBEDDING_MODEL: str = "text-embedding-3-large"
EMBEDDING_DIMENSIONS: int = 3072

# MMR Algorithm
MMR_LAMBDA: float = 0.7

# Recommendation
MAX_RECOMMENDATIONS: int = 10
MIN_SIMILARITY_THRESHOLD: float = 0.3
MAX_SIMILARITY_THRESHOLD: float = 0.9

# Response
MAX_RESPONSE_LENGTH: int = 1000
USE_EMOJIS: bool = True
MAX_FOLLOW_UP_QUESTIONS: int = 2
```

---

## 파일 구조 요약

```
ml/
├── intent_analyzer/
│   ├── intent_classifier.py      # 의도 분류 클래스
│   └── few_shot_prompts.py       # Few-shot 프롬프트
├── vector_search/
│   ├── embedding_service.py      # 임베딩 생성
│   ├── search_engine.py          # 검색 엔진
│   ├── sql_vector_store.py       # SQL 벡터 스토어
│   └── vector_store.py          # 벡터 스토어 추상 클래스
├── mmr_algorithm/
│   ├── mmr_scorer.py            # MMR 알고리즘
│   └── diversity_calculator.py  # 다양성 계산
└── response_generator/
    ├── response_generator.py     # 응답 생성
    └── prompt_templates.py       # 프롬프트 템플릿

backend/app/
├── services/
│   ├── chat_service.py           # 통합 채팅 서비스
│   └── recommendation_service.py # 추천 서비스
└── api/api_v1/endpoints/
    └── chat.py                   # 채팅 API 엔드포인트
```

---

## 요약

### 구현된 AI 기능
1. ✅ **의도 분석** - 5가지 Intent 분류, 탐색 의도 감지
2. ✅ **벡터 검색** - 임베딩 기반 유사도 검색
3. ✅ **다양성 추천** - MMR 알고리즘으로 필터버블 해소
4. ✅ **자연어 응답** - GPT 기반 맥락 맞춤 응답 생성
5. ✅ **사용자 프로필** - 좋아요/장바구니 기반 취향 분석
6. ✅ **재추천 방지** - 최근 추천 상품 제외 로직

### 핵심 특징
- **필터버블 해소**: 새로운 발견 70% / 기존 취향 30%
- **다양성 보장**: 최소 3개 이상 다른 스타일, 동일 브랜드 최대 2개
- **맥락 이해**: 대화 히스토리 및 사용자 프로필 활용
- **자연스러운 대화**: 친근한 톤앤매너, 최대 2개 질문

---

*최종 업데이트: 2025-01-02*

