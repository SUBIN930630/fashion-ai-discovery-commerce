# 패션 AI 추천 시스템 - AI 기능 문서

> **필터버블 해소를 위한 대화형 AI 스타일리스트**  
> "매번 비슷한 상품만 보여요" 문제를 해결하는 지능형 추천 시스템

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [핵심 AI 기능](#핵심-ai-기능)
3. [기술 아키텍처](#기술-아키텍처)
4. [상세 기능 설명](#상세-기능-설명)
5. [서비스 레이어](#서비스-레이어)
6. [API 엔드포인트](#api-엔드포인트)
7. [실행 흐름](#실행-흐름)
8. [사용자 경험 기능](#사용자-경험-기능)
9. [최근 개선 사항](#최근-개선-사항)
10. [비즈니스 가치](#비즈니스-가치)

---

## 📌 프로젝트 개요

**Fashion AI Discovery Commerce**는 사용자의 패션 스타일을 이해하고, 새로운 발견과 기존 취향의 균형을 맞춘 맞춤형 상품을 추천하는 AI 기반 이커머스 플랫폼입니다.

### 핵심 가치 제안

- 🎯 **필터버블 해소**: 새로운 발견 70% + 기존 취향 30%의 균형잡힌 추천
- 💬 **자연스러운 대화**: GPT-4 기반 대화형 인터페이스로 편안한 쇼핑 경험
- 🔍 **맥락 이해**: 대화 히스토리와 사용자 프로필을 활용한 지능형 추천
- 🎨 **다양성 보장**: MMR 알고리즘으로 매번 다른 스타일의 상품 추천

### 핵심 목표

- 추천 다양성 **0.5 이상** 달성 (기존 0.2~0.3)
- 탐색적 추천 CTR **5% 이상**
- 부정 피드백 **10% 이하**로 감소 (기존 18%)

---

## 🤖 핵심 AI 기능

### 전체 AI 파이프라인

```
사용자 메시지 입력
    ↓
[Intent Analyzer] - 의도 분석 (GPT-4o-mini)
    ↓
[Vector Search] - 벡터 기반 상품 검색 (text-embedding-3-large)
    ↓
[MMR Algorithm] - 다양성 있는 추천 선택 (NumPy/SciPy)
    ↓
[Response Generator] - 자연어 응답 생성 (GPT-4o-mini)
    ↓
[Hybrid Matching] - GPT 응답에서 상품명 추출 및 매칭
    ↓
최종 추천 결과 + AI 응답
```

### 기술 스택

| 계층 | 기술 |
|---|---|
| **LLM** | GPT-4o-mini (OpenAI) |
| **Embedding** | text-embedding-3-large (OpenAI) |
| **Vector Store** | SQL 기반 (PostgreSQL/SQLite) |
| **알고리즘** | MMR (Maximal Marginal Relevance) |
| **프레임워크** | FastAPI (Python) |
| **프론트엔드** | React.js |

---

## 🔧 기술 아키텍처

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

### 파일 구조

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

## 📖 상세 기능 설명

### 1. Intent Analyzer (의도 분석)

**위치**: `ml/intent_analyzer/`

#### 주요 파일
- `intent_classifier.py` - 의도 분류 클래스
- `few_shot_prompts.py` - Few-shot 학습 프롬프트

#### 기능 개요

사용자의 자연어 메시지를 분석하여 5가지 의도로 분류합니다:

| Intent 카테고리 | 설명 | 예시 질문 |
|---|---|---|
| **가격·가성비** | 예산과 가성비 중심 | "10만 원대 자켓 추천해줘" |
| **감성·스타일** | 스타일과 무드 중심 | "29CM 감성 미니멀 셔츠" |
| **시즌·날씨** | 계절과 날씨 고려 | "봄에 입기 좋은 자켓" |
| **체형·핏** | 체형과 핏 중심 | "키 작은 남자 자켓" |
| **코디·상황** | 상황별 코디 | "출근할 때 코디" |

#### 상세 기능

1. **5가지 Intent 분류**
   - GPT-4o-mini + Few-shot Learning 기반
   - Confidence 점수 제공 (0.0~1.0)

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

#### 기능 개요

상품 정보와 사용자 쿼리를 벡터로 변환하여 의미 기반 유사도 검색을 수행합니다.

#### 상세 기능

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

#### 작동 원리

1. **임베딩 생성**: 상품명, 브랜드, 카테고리, 스타일 태그 등을 벡터로 변환
2. **유사도 계산**: 코사인 유사도로 사용자 요청과 가장 관련성 높은 상품 검색
3. **캐싱 최적화**: 중복 임베딩 호출 방지로 API 비용 절감

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

**예시 시나리오**:
```
사용자: "따뜻한 상의 추천"
→ "따뜻한", "상의" 키워드 임베딩 생성
→ 유사도 높은 상품 50개 검색
→ MMR 알고리즘으로 최종 10개 선택
```

---

### 3. MMR Algorithm (다양성 추천)

**위치**: `ml/mmr_algorithm/`

#### 주요 파일
- `mmr_scorer.py` - MMR 알고리즘 구현
- `diversity_calculator.py` - 다양성 점수 계산

#### 기능 개요

유사도와 다양성의 균형을 맞춰 매번 다른 스타일의 상품을 추천합니다.

#### 핵심 원칙

- **새로운 발견 70%**: 기존에 추천하지 않았던 상품, 새로운 스타일
- **기존 취향 30%**: 사용자가 좋아했던 스타일 기반
- **재추천 방지**: 최근 5회 대화에서 추천한 상품 자동 제외
- **브랜드 다양성**: 동일 브랜드 최대 2개까지만 추천
- **스타일 다양성**: 한 번에 최소 3개 이상의 다른 스타일 포함

#### 알고리즘 수식

```
MMR = λ × Similarity(query, item) - (1-λ) × max(Similarity(item, selected))
```

- λ = 0.7 (유사도 70%, 다양성 30% 가중치)

#### 상세 기능

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

#### 기능 개요

사용자에게 친근하고 자연스러운 대화로 추천 상품을 소개합니다.

#### 상세 기능

1. **의도별 템플릿 선택**
   - 가격·가성비 → price_value 템플릿
   - 감성·스타일 → style_mood 템플릿
   - 시즌·날씨 → season_weather 템플릿
   - 체형·핏 → fit_body 템플릿
   - 코디·상황 → coordination_situation 템플릿

2. **상황별 응답 최적화**

   **명확한 요청인 경우** (confidence ≥ 0.7, 키워드 2개 이상):
   - 공감 멘트 생략, 바로 추천 시작
   - 예: "따뜻한 상의 추천해드릴게요!"

   **불명확한 요청인 경우** (confidence < 0.7):
   - 공감 + 의도 확인 후 추천
   - 예: "어떤 스타일을 찾고 계신가요? 좀 더 구체적으로 알려주시면..."

3. **대화 히스토리 활용**
   - 최근 10개 메시지를 GPT API에 전달하여 맥락 유지
   - 이전 대화에서 언급한 스타일, 카테고리 자동 기억
   - 반복적인 멘트 방지 (동문서답 금지)

4. **응답 다양성 보장**
   - 매번 다른 표현과 문장 구조 사용
   - 고정된 멘트 반복 금지 ("괜찮아요! 스타일을 찾는 게..." 등)
   - 이모지 적절히 사용 (과하지 않게)

5. **후처리 규칙**
   - 질문 개수 제한 (최대 2개)
   - 이모지 사용 제어
   - 길이 제한 (1000자)
   - 안전성 필터
   - 비율 정보 제거 (70%, 30% 등)

#### 응답 구조 (상황에 따라 다름)

**명확한 요청인 경우**:
1. 간단한 인사 또는 바로 추천 시작 (공감 멘트 생략)
2. 새로운 발견 추천 (비율 표시 금지)
3. 기존 취향 추천 (비율 표시 금지)
4. 꼬리질문 or 대안 제시

**불명확한 요청인 경우**:
1. 공감 + 의도 확인
2. 새로운 발견 추천 (비율 표시 금지)
3. 기존 취향 추천 (비율 표시 금지)
4. 꼬리질문 or 대안 제시

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

### 5. Hybrid Product Matching (하이브리드 상품 매칭)

**기술**: 키워드 추출 + 벡터 검색 + MMR 알고리즘

#### 기능 개요

GPT가 자연어로 상품을 언급했지만 DB 매칭이 안 된 경우, 자동으로 상품을 찾아 추천합니다.

#### 작동 흐름

1. **키워드 추출**: GPT 응답에서 상품 관련 키워드 추출
   - 예: "블레이저", "화이트 셔츠", "슬랙스" 등
   - 패션 상품 키워드 사전 기반 매칭

2. **유연한 매칭**: 공백 차이 무시 ("오피스룩" = "오피스 룩")
   - 정규표현식 기반 패턴 매칭
   - 상품명 정규화 (공백 제거)

3. **DB 검색**: 추출된 키워드로 벡터 검색 수행
   - 키워드를 조합하여 검색 쿼리 생성 (상위 3개 키워드)

4. **MMR 선택**: 다양성 있는 최종 추천 10개 선택

#### 예시 시나리오

```
사용자: "오피스룩 추천해줘"
GPT 응답: "클래식한 블레이저와 화이트 셔츠, 슬랙스를 추천해드릴게요!"
→ 시스템이 "블레이저", "셔츠", "슬랙스" 키워드 추출
→ DB에서 매칭하여 실제 상품 링크 제공
```

#### 구현 위치

- `backend/app/services/chat_service.py`
  - `_extract_product_keywords_from_response()`: 키워드 추출
  - `_is_product_recommendation_response()`: 추천 완료 신호 감지
  - `_match_products_from_response()`: DB 매칭

---

### 6. 사용자 프로필 기반 맞춤 추천

#### 데이터 소스

- 좋아요 목록 (사용자가 관심 있는 스타일)
- 장바구니 (구매 의향이 있는 상품)
- 최근 조회 내역
- 과거 추천 피드백 (클릭/미클릭)

#### 활용 방식

- 좋아요한 상품과 유사하거나 대조되는 상품 추천
- 장바구니 상품과 코디 가능한 아이템 제안
- 이미 좋아요/장바구니에 담은 상품은 중복 추천 방지

#### 구현 위치

- `backend/app/services/recommendation_service.py`
  - `analyze_user_preferences_from_db()`: 사용자 취향 분석

---

## 🏗 서비스 레이어

### Chat Service (통합 서비스)

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

5. **추천 타이밍 제어**
   - Confidence 기반 스마트 추천 (0.6 이상일 때만)
   - 질문 단계(정보 수집)에서는 추천하지 않음

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
        6. GPT 응답에서 상품명 추출 및 DB 매칭 (하이브리드)
        7. 메시지 저장
        """
```

---

### Recommendation Service (추천 서비스)

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

## 🌐 API 엔드포인트

### Chat API

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

## 🔄 실행 흐름

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
8. Hybrid Matching (선택적)
   → GPT 응답에서 상품명 추출 → DB 매칭 → 추천 추가
   ↓
9. 최종 응답 반환
   {
     response: "미니멀 스타일의 셔츠를 추천해드릴게요! ...",
     recommendations: [...],
     intent: "감성·스타일"
   }
```

---

## 🎨 사용자 경험 (UX) 기능

### 1. 대화형 인터페이스

- **플로팅 챗봇**: 우측 하단에 항상 접근 가능한 채팅 창
- **마크다운 렌더링**: 볼드, 헤딩, 리스트 등 자연스러운 텍스트 포맷
- **인라인 하이퍼링크**: AI 응답 텍스트 내 상품명 클릭 시 바로 상품 페이지 이동
- **추천 상품 버튼**: 하단에 추천 상품 목록을 버튼 형태로 제공

### 2. 스마트 스크롤

- 새 메시지 도착 시 자동 스크롤
- 사용자가 수동 스크롤 중이면 강제 스크롤하지 않음
- 답변 시작 부분이 보이도록 90% 지점으로 스크롤

**구현 위치**: `frontend/src/components/ChatModal.js` (54-80번째 줄)

### 3. 상품 링크 통합

- 추천 상품 클릭 시 채팅 창 유지 (닫히지 않음)
- 상품 페이지에서도 계속 대화 가능
- 클릭 로그 자동 수집 (추천 성과 분석용)

---

## 🚀 최근 개선 사항 (커밋 히스토리 기반)

### 최근 개선 내역

1. **명확한 요청 시 공감 멘트 생략** (2026-01-03)
   - 사용자가 구체적인 요구사항을 명시한 경우 불필요한 공감 표현 제거
   - 예: "33세 남자 상의 따뜻한걸로 추천" → 바로 추천 시작

2. **AI 응답 다양성 개선** (2026-01-03)
   - 반복적인 멘트 방지 및 대화 히스토리 활용 강화
   - 동문서답(같은 말 반복) 방지

3. **GPT 응답에서 상품명 추출 및 DB 매칭** (2026-01-03)
   - GPT가 자연어로 상품을 언급한 경우 자동으로 DB에서 매칭
   - 하이브리드 추천 시스템 완성

4. **공백 차이 무시하여 상품명 하이퍼링크 매칭** (2026-01-03)
   - "오피스룩" = "오피스 룩" 자동 인식
   - 유연한 패턴 매칭으로 사용자 경험 개선

5. **대화 히스토리 전달** (2026-01-03)
   - GPT API에 최근 10개 메시지 전달
   - 맥락 유지로 자연스러운 대화 가능

6. **질문 단계에서 추천 상품 표시하지 않기** (2026-01-03)
   - 정보 수집 단계에서는 추천하지 않음
   - Confidence 기반 스마트 추천 타이밍

7. **AI 응답 텍스트에 상품명 하이퍼링크 추가** (2026-01-03)
   - 응답 내 상품명 클릭 시 바로 상품 페이지 이동
   - 자연스러운 사용자 경험

---

## 📊 주요 규칙 및 제약사항

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
   - 상황에 따라 다름 (명확한 요청 vs 불명확한 요청)

3. **톤앤매너**
   - 친근한 대화체
   - 이모지 적절히 사용
   - 존댓말 사용

---

## ⚙️ 설정 파일

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

## 📈 AI 성능 지표

### 추천 다양성
- **목표**: 0.5 이상 (기존 시스템: 0.2~0.3)
- **측정 방법**: 추천 상품 간 스타일/브랜드 다양성 점수

### 탐색적 추천 CTR
- **목표**: 5% 이상
- **측정 방법**: 새로운 발견 카테고리 상품 클릭률

### 부정 피드백 감소
- **목표**: 10% 이하 (기존: 18%)
- **측정 방법**: "비슷한 상품만 보여요" 피드백 비율

---

## 💡 핵심 차별화 포인트

### 1. 필터버블 해소
기존 협업 필터링의 "비슷한 상품만 추천" 문제를 MMR 알고리즘과 70/30 비율로 해결

### 2. 자연스러운 대화
GPT 기반 대화형 인터페이스로 쇼핑몰이 아닌 스타일리스트와 대화하는 느낌

### 3. 맥락 이해
대화 히스토리와 사용자 프로필을 활용한 지능형 추천

### 4. 설명 가능한 AI
모든 추천에 자연어로 이유를 제공하여 사용자 신뢰도 향상

### 5. 실시간 적응
사용자의 피드백(클릭/미클릭)을 즉시 반영하여 다음 추천 개선

---

## 📈 비즈니스 가치

### 사용자 측면
- **새로운 발견 경험**: 평소 보지 못했던 스타일과 브랜드 발견
- **시간 절약**: 대화형 인터페이스로 빠른 상품 탐색
- **맞춤형 추천**: 개인 취향을 이해한 정확한 추천

### 비즈니스 측면
- **전환율 향상**: 다양성 있는 추천으로 구매 기회 확대
- **장기 고객 유지**: 새로운 발견 경험으로 재방문 증가
- **데이터 수집**: 대화 로그를 통한 사용자 인사이트 확보

---

## 🎯 향후 개선 계획

1. **멀티모달 추천**: 이미지 기반 스타일 분석 추가
2. **감정 분석**: 사용자 메시지의 감정을 파악하여 톤 조절
3. **A/B 테스트**: 다양한 추천 전략 실험 및 최적화
4. **실시간 학습**: 사용자 피드백을 즉시 모델에 반영

---

## 📞 기술 문의

프로젝트 저장소: [GitHub Repository]  
기술 문서: `Document/` 디렉토리 참조  
API 문서: `/api/docs` (Swagger UI)

---

*최종 업데이트: 2026-01-03*

