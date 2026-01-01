# Fashion AI Discovery Commerce

패션 이커머스 플랫폼의 **필터버블 해소**를 위한 대화형 탐색적 추천 시스템

## 프로젝트 개요

기존 협업 필터링 기반 추천 시스템의 한계를 극복하고, 사용자에게 **새로운 발견 경험**을 제공하는 AI 챗봇 기반 추천 시스템입니다.

### 핵심 목표
- 추천 다양성 **0.5 이상** 달성 (기존 0.2~0.3)
- 탐색적 추천 CTR **5% 이상**
- 부정 피드백 **10% 이하**로 감소 (기존 18%)

### 주요 특징
- 🤖 **RAG 기반 대화형 추천**: 사용자 의도에 따른 동적 추천 비율 조정
- 🔍 **MMR 알고리즘**: 유사도와 다양성의 균형 보장
- 💡 **새로운 발견**: 기존 취향(30%) + 새로운 발견(70%) 구성
- 🎯 **설명 가능한 AI**: 추천 이유를 자연어로 제공

## 시스템 아키텍처

```
사용자 앱/웹
    ↓
Chat Interface Layer (React.js + WebSocket)
    ↓
Intent Analysis Module (GPT-4 + Few-shot learning)
    ↓
Vector DB Search (Pinecone + text-embedding-3-large)
    ↓
MMR Algorithm (유사도 + 다양성 균형)
    ↓
LLM Response Generator (GPT-4 Turbo)
    ↓
대화형 추천 결과
```

## 기술 스택

### Frontend
- **React.js**: 사용자 인터페이스
- **WebSocket**: 실시간 대화 통신
- **Redis**: 세션 관리

### Backend
- **FastAPI**: API 서버
- **Python**: 핵심 로직
- **NumPy/SciPy**: MMR 알고리즘

### AI/ML
- **OpenAI GPT-4**: 의도 분석 및 응답 생성
- **text-embedding-3-large**: 상품 임베딩
- **Pinecone/Weaviate**: 벡터 데이터베이스

## 디렉토리 구조

```
fashion-ai-discovery-commerce/
├── frontend/                 # React.js 프론트엔드
│   ├── src/
│   │   ├── components/       # UI 컴포넌트
│   │   ├── services/         # API 통신
│   │   └── utils/           # 유틸리티 함수
│   └── package.json
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/             # API 라우터
│   │   ├── core/            # 핵심 설정
│   │   ├── models/          # 데이터 모델
│   │   └── services/        # 비즈니스 로직
│   └── requirements.txt
├── ml/                      # AI/ML 모듈
│   ├── intent_analyzer/     # 의도 분석
│   ├── vector_search/       # 벡터 검색
│   ├── mmr_algorithm/       # MMR 알고리즘
│   └── response_generator/  # 응답 생성
├── data/                    # 데이터 관리
│   ├── product_data/        # 상품 데이터
│   ├── user_profiles/       # 사용자 프로필
│   └── embeddings/          # 임베딩 데이터
├── docs/                    # 문서화
│   ├── api/                 # API 문서
│   ├── architecture/        # 아키텍처 문서
│   └── planning/            # 기획 문서
├── docker-compose.yml       # 개발 환경 설정
└── .env.example            # 환경 변수 템플릿
```

## 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd fashion-ai-discovery-commerce

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 OpenAI API Key, Pinecone API Key 등 설정
```

### 2. 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm start
```

### 4. Docker로 실행 (권장)
```bash
docker-compose up -d
```

## 핵심 기능

### 1. 의도 분석 (Intent Analysis)
사용자 질문을 5가지 Intent로 분류:
- **가격·가성비**: "10만원대 자켓", "학생한테 부담 없는"
- **감성·스타일**: "29CM 감성", "스트릿 느낌"
- **시즌·날씨**: "봄에 입기 좋은", "장마철"
- **체형·핏**: "키 작은 남자", "배 안 보이는"
- **코디·상황**: "출근룩", "데이트"

### 2. 필터버블 해소 로직
```python
# 추천 구성 비율
새로운 발견: 70%  # 기존에 추천하지 않았던 상품
기존 취향: 30%    # 사용자가 좋아했던 스타일

# 재추천 방지
- 최근 5회 대화에서 추천한 상품 제외
- 클릭하지 않은 상품 우선 제외
- 동일 브랜드 최대 2개로 제한
```

### 3. MMR 알고리즘
```python
MMR = λ × Similarity(q, d) - (1-λ) × max Similarity(d, d')

# q: 사용자 취향 쿼리
# d: 후보 상품
# λ: 유사도/다양성 가중치 (기본 0.7)
```

## API 엔드포인트

### 채팅 API
```
POST /api/chat/message
GET  /api/chat/history/{session_id}
```

### 추천 API
```
POST /api/recommend/products
GET  /api/recommend/history/{user_id}
```

### 사용자 프로필 API
```
GET  /api/user/profile/{user_id}
PUT  /api/user/profile/{user_id}
```

## 데이터 구조

### 사용자 취향 프로필
```json
{
  "user_id": "user_12345",
  "preference_vector": [0.12, 0.45, 0.78, ...],
  "style_distribution": {
    "스트릿": 0.45,
    "캐주얼": 0.30,
    "미니멀": 0.15
  },
  "exploration_score": 0.3
}
```

### 상품 메타데이터
```json
{
  "product_id": "prod_67890",
  "name": "오버핏 후드티",
  "embedding_vector": [0.23, 0.56, 0.89, ...],
  "style_tags": ["스트릿", "캐주얼"],
  "popularity_score": 0.85
}
```

## 개발 로드맵

### Phase 1: MVP (1~2개월)
- [x] 텍스트 기반 챗봇 인터페이스
- [x] 의도 분석 기능
- [x] 벡터 DB 기반 검색
- [x] 간단한 MMR 알고리즘

### Phase 2: 고도화 (2~3개월)
- [ ] 사용자 취향 프로필 학습
- [ ] 다양성 점수 고도화
- [ ] A/B 테스트 인프라
- [ ] 응답 속도 최적화

### Phase 3: 확장 (3~4개월)
- [ ] 이미지 기반 검색 통합
- [ ] 멀티모달 추천
- [ ] 실시간 트렌드 반영

## 성능 지표

### 목표 KPI
- 대화형 추천 사용률: **30% 이상**
- 대화 완료율: **70% 이상**
- 추천 상품 구매 전환율: **8% 이상**
- 사용자 만족도(CSAT): **4.2점 이상** (5점 만점)

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성하거나 이메일로 연락주세요.