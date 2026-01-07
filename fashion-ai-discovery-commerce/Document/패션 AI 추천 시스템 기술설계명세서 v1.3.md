- **버전**: 1.3
- **목적**: 필터버블 해소형 패션 추천 AI 챗봇 개발
- **변경사항 (v1.3)**:
   - 실제 구현된 코드 기준으로 기술 스택 및 아키텍처 반영
   - SQL 기반 벡터 스토어 사용 (Pinecone/Weaviate 대체)
   - React.js 기반 프론트엔드 (Next.js 아님)
   - LocalStorage 기반 인증 (JWT 미구현)
   - Docker Compose 기반 로컬 개발 환경
   - 관리자 대시보드 UX/UI 개선 및 상품 수정 기능 추가
   - 사용자 취향 기반 맞춤 검색 기능 구현
   - 챗봇 입력창 자동 높이 조절 기능
- **변경사항 (v1.2)**:
   - 쇼핑몰 웹사이트 + 챗봇 위젯 통합 구조로 재설계
   - 더미 쇼핑몰 데이터 구축 전략 추가
   - 사용자 인증 시스템 (관리자/일반 사용자) 추가
   - 권한별 기능 차등화 설계
   - 프론트엔드 구조 전면 개편 (쇼핑몰 + 챗봇 위젯)
- **변경사항 (v1.1)**:
   - AWS 기반 인프라 구축 상세화
   - Docker 컨테이너 기반 배포 전략 수립
   - DBeaver를 활용한 채팅 로그 분석 및 고도화 전략 추가

---

## 1. 시스템 개요

### 1.1 프로젝트 목표

패션 쇼핑몰에 임베디드되는 AI 스타일리스트 챗봇을 구축하여, 사용자가 "매번 비슷한 상품만 보여요"라는 불만을 해소하고 개인화된 추천과 새로운 발견의 균형을 제공

### 1.2 핵심 기능

#### 1.2.1 쇼핑몰 기본 기능

- 상품 목록 조회 및 검색
- 상품 상세 정보 조회
- 카테고리별 필터링
- 장바구니 기능
- 주문/결제 (간소화)
- 주문 내역 조회
- 사용자 취향 기반 맞춤 검색 (로그인 사용자)

#### 1.2.2 챗봇 기능

- 우측 하단 플로팅 챗봇 아이콘
- 대화형 상품 추천 (Intent 기반)
- 필터버블 해소 알고리즘 (신규 70% + 기존 30%)
- 재추천 방지 시스템
- 추천 상품 클릭 시 상품 상세 페이지 연동
- 챗봇 입력창 자동 높이 조절

#### 1.2.3 사용자 인증 및 권한 관리

- 회원가입 / 로그인 / 로그아웃 (LocalStorage 기반)
- 역할 기반 접근 제어 (RBAC):
   - **관리자(Admin)**: 전체 관리 기능
   - **일반 사용자(User)**: 쇼핑 및 챗봇 이용

#### 1.2.4 관리자 전용 기능

- 상품 관리 (CRUD)
   - 상품 목록 조회 (카테고리/성별 필터)
   - 상품 정보 수정 (이름, 브랜드, 카테고리, 가격, 이미지, 설명, 스타일 태그, 계절, 상황 등)
   - 상품 삭제
   - 상품 임베딩 자동 재생성
- 사용자 관리
   - 사용자 목록 조회 (역할 필터)
   - 계정 추가 (ID, 이름, 비밀번호, 역할)
   - 계정 편집 (이름, 역할)
   - 계정 삭제
- 주문 관리
   - 주문 목록 조회 (상태 필터)
   - 주문 상태 업데이트
- 챗봇 대화 로그 분석 대시보드
   - 전체 대화 내역 조회
   - 사용자별 대화 내역 조회
   - 세션별 대화 내역 조회
- 좋아요 목록 관리 (일반 사용자만)
- 장바구니 관리 (일반 사용자만)
- 추천 성과 모니터링 (CTR, 전환율)
- Intent 분류 통계

#### 1.2.5 일반 사용자 기능

- 쇼핑몰 브라우징
- 상품 검색 및 구매
- 챗봇을 통한 상품 추천
- 마이페이지 (주문 내역, 찜 목록)
- 프로필 관리

### 1.3 기술 스택 (실제 구현 기준)

```
┌─────────────────────────────────────┐
│  Frontend (쇼핑몰 웹사이트)         │
│  - React.js 18                      │
│  - JavaScript (ES6+)                │
│  - React Router DOM v7              │
│  - CSS3 (컴포넌트별 CSS 파일)       │
│  - Axios (HTTP 클라이언트)          │
│  - Context API (상태 관리)          │
│  - LocalStorage (데이터 영속성)     │
├─────────────────────────────────────┤
│  Frontend (챗봇 위젯)               │
│  - React.js 18 (통합)               │
│  - JavaScript (ES6+)                │
│  - CSS3 (모달 스타일)               │
│  - 자동 높이 조절 Textarea           │
├─────────────────────────────────────┤
│  Backend Container                  │
│  - FastAPI (Python 3.9+)            │
│  - Uvicorn (ASGI Server)            │
│  - SQLAlchemy (ORM)                 │
│  - Pydantic (데이터 검증)           │
│  - Python-dotenv (환경 변수)        │
├─────────────────────────────────────┤
│  Database Services                  │
│  - SQLite (로컬 개발)               │
│  - PostgreSQL 15+ (Docker)          │
│  - SQL 기반 벡터 스토어              │
│    (JSONB 컬럼에 임베딩 저장)        │
├─────────────────────────────────────┤
│  Cache Layer                        │
│  - Redis 7.x (Docker Compose)       │
│  - 세션 관리                        │
│  - 챗봇 대화 컨텍스트 캐싱          │
├─────────────────────────────────────┤
│  AI/ML Services                     │
│  - OpenAI GPT-4o-mini API           │
│  - text-embedding-3-large           │
│  - SQL 기반 벡터 검색                │
│  - MMR 알고리즘 (NumPy/SciPy)        │
│  - Intent 분류 (Few-shot learning)  │
├─────────────────────────────────────┤
│  Authentication                     │
│  - LocalStorage 기반 세션            │
│  - Context API (프론트엔드)         │
│  - 역할 기반 접근 제어 (RBAC)       │
├─────────────────────────────────────┤
│  Infrastructure (로컬 개발)         │
│  - Docker Compose                   │
│  - Docker Desktop                   │
│  - Nginx (리버스 프록시)            │
│  - Prometheus (모니터링)            │
│  - Grafana (대시보드)               │
├─────────────────────────────────────┤
│  Development Tools                  │
│  - React Scripts (CRA)              │
│  - Docker Desktop                   │
│  - Docker Compose (로컬 개발)       │
│  - Git (버전 관리)                  │
└─────────────────────────────────────┘
```

---

## 2. 시스템 아키텍처

### 2.1 전체 구조도 (실제 구현 기준)

```
[사용자 브라우저]
   │
   ├─ 쇼핑몰 웹사이트 (React.js)
   │  - 상품 목록/상세
   │  - 장바구니
   │  - 주문/결제
   │  - 마이페이지
   │  - 관리자 대시보드
   │
   └─ 우측 하단 플로팅 챗봇 아이콘
      └─ 클릭 시 챗봇 위젯 오픈
         └─ AI 추천 대화
   ↓
[Docker Compose Network]
   ↓
┌─────────────────────────────────────────────────────┐
│  Docker Compose Services                            │
│                                                      │
│  ┌───────────────────┐    ┌───────────────────┐    │
│  │ Frontend          │    │ Backend API       │    │
│  │ (React.js)        │    │ (FastAPI)         │    │
│  │                   │    │                   │    │
│  │ - 상품 페이지     │◄───│ - 인증/인가       │    │
│  │ - 장바구니        │    │ - 상품 API        │    │
│  │ - 챗봇 위젯 임베드│    │ - 주문 API        │    │
│  │ - 관리자 대시보드 │    │ - 챗봇 API        │    │
│  └───────────────────┘    │ - 관리자 API      │    │
│                           │ - 추천 API        │    │
│                           └───────────────────┘    │
│                                  ↓                 │
│                           ┌───────────────────┐    │
│                           │ AI Services       │    │
│                           │ - Intent 분류     │    │
│                           │ - 필터버블 해소   │    │
│                           │ - GPT-4o-mini 호출│    │
│                           │ - SQL 벡터 검색   │    │
│                           └───────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
                  ↓
    ┌─────────────┴─────────────┐
    ↓                           ↓
┌─────────────────┐    ┌─────────────────┐
│ PostgreSQL      │    │ Redis           │
│ (Docker)        │    │ (Docker)        │
│                 │    │                 │
│ - users         │    │ - JWT 세션      │
│ - products      │    │ - 챗봇 컨텍스트 │
│ - orders        │    │ - 캐시          │
│ - chat_sessions │    └─────────────────┘
│ - chat_history  │
│ - user_favorites│
│ - user_cart     │
│ - recommendation│
│   _history      │
│ - recommendation│
│   _feedback     │
│                 │
│ 벡터 임베딩     │
│ (JSONB 컬럼)    │
└─────────────────┘
    ↓
┌─────────────────┐
│ External APIs   │
│ - OpenAI GPT-4  │
│   o-mini        │
│ - OpenAI        │
│   Embedding API │
└─────────────────┘
```

### 2.2 사용자 플로우

#### 2.2.1 일반 사용자 플로우

```
1. 쇼핑몰 메인 페이지 접속
   ↓
2. (선택) 회원가입 또는 로그인
   ├─ 비로그인: 쇼핑 가능, 챗봇 이용 제한적
   └─ 로그인: 전체 기능 이용 가능, 맞춤 검색 활성화
   ↓
3. 상품 브라우징
   ├─ 카테고리별 탐색
   ├─ 검색 (로그인 시 사용자 취향 반영)
   └─ 챗봇 아이콘 클릭 → 대화형 추천
   ↓
4. 챗봇 대화
   ├─ "10만 원대 자켓 추천해줘"
   ├─ AI가 Intent 분석
   ├─ 상품 추천 (신규 70% + 기존 30%)
   └─ 추천 상품 클릭 → 상품 상세 페이지
   ↓
5. 장바구니 추가 → 주문/결제
   ↓
6. 주문 완료 → 마이페이지에서 확인
```

#### 2.2.2 관리자 플로우

```
1. 관리자 계정으로 로그인
   ↓
2. 관리자 대시보드 접근 (/admin)
   ├─ 상품 관리
   │  ├─ 상품 목록 조회 (카드 그리드)
   │  ├─ 카테고리/성별 필터
   │  ├─ 상품 수정 (모달)
   │  │  ├─ 기본 정보 수정
   │  │  ├─ 임베딩 자동 재생성
   │  │  └─ 데이터베이스 반영
   │  └─ 상품 삭제
   │
   ├─ 사용자 관리
   │  ├─ 사용자 목록 조회 (카드 그리드)
   │  ├─ 역할 필터 (전체/관리자/일반 사용자)
   │  ├─ 계정 추가 (ID, 이름, 비밀번호, 역할)
   │  ├─ 계정 편집 (이름, 역할)
   │  └─ 계정 삭제
   │
   ├─ 주문 관리
   │  ├─ 주문 목록 조회 (카드 그리드)
   │  ├─ 상태 필터 (전체/주문완료/결제완료/배송준비중/배송중/배송완료)
   │  └─ 주문 상태 업데이트
   │
   ├─ 좋아요 목록 (일반 사용자만)
   │  └─ 사용자별 좋아요 상품 조회
   │
   ├─ 장바구니 (일반 사용자만)
   │  └─ 사용자별 장바구니 조회
   │
   ├─ 챗봇 대화 내역
   │  ├─ 전체 대화 내역 조회
   │  ├─ 사용자별 대화 내역 조회
   │  └─ 세션별 대화 내역 조회
   │
   └─ 챗봇 분석 대시보드
      ├─ 전체 통계
      ├─ Intent 분포
      └─ 추천 성과 (CTR, 전환율)
```

### 2.3 챗봇 위젯 임베디드 구조

```html
<!-- 쇼핑몰 페이지 (React.js) -->
<div className="app">
  <Header />
  <main className="app-main">
    <Routes>
      <Route path="/" element={<AppContent />} />
      <Route path="/product/:productId" element={<ProductDetailPage />} />
      <Route path="/checkout" element={<CheckoutPage />} />
      <Route path="/mypage" element={<MyPage />} />
      <Route path="/admin" element={<AdminDashboard />} />
    </Routes>
  </main>
  
  <!-- 우측 하단 플로팅 챗봇 -->
  <FloatingChatButton onClick={toggleChat} isOpen={isChatOpen} />
  <ChatModal isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
</div>
```

#### 챗봇 UI 스펙 (실제 구현)

```
크기: 400px (width) × 600px (height)
위치: 우측 하단 (bottom: 80px, right: 20px)
애니메이션: Slide up (열릴 때), Slide down (닫힐 때)

구성:
┌─────────────────────────┐
│ 헤더                    │
│ AI 스타일리스트 💬      │
│              [□] [X]   │
├─────────────────────────┤
│ 대화 영역               │
│                         │
│ 👤 10만 원대 자켓       │
│    추천해줘             │
│                         │
│ 🤖 가성비 좋은 자켓을   │
│    찾고 계시는군요!     │
│                         │
│    💡 새로운 발견       │
│    [상품카드1]          │
│    [상품카드2]          │
│                         │
│    🏠 내 취향           │
│    [상품카드3]          │
│                         │
├─────────────────────────┤
│ 입력창 (자동 높이 조절) │
│ [메시지 입력...] [전송] │
│ (최소 1줄, 최대 6줄)    │
└─────────────────────────┘
```

### 2.4 Docker 컨테이너 구조 (실제 구현)

```
프로젝트 루트/
├── docker-compose.yml           # 로컬 개발 환경
│
├── frontend/                    # React.js 프론트엔드
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   └── scripts/
│
└── ml/                          # AI/ML 모듈
    ├── intent_analyzer/
    ├── vector_search/
    ├── mmr_algorithm/
    └── response_generator/
```

### 2.5 데이터 흐름 (상세)

```
1. 사용자가 쇼핑몰 접속
   ↓ [HTTP]
2. React.js 앱 로드
   ↓
3. 상품 데이터 요청
   ↓ [REST API]
4. Backend FastAPI → PostgreSQL/SQLite
   ↓
5. 상품 목록 반환 → 화면 렌더링
   ↓
6. 사용자가 챗봇 아이콘 클릭
   ↓
7. 챗봇 모달 오픈
   ↓
8. "10만 원대 자켓 추천해줘" 입력
   ↓ [REST API]
9. Backend: Intent 분류 (GPT-4o-mini)
   ↓
10. Redis에서 세션 확인 (사용자 로그인 여부)
   ↓
11. PostgreSQL/SQLite에서 사용자 히스토리 조회
    ├─ 최근 추천 이력 (최근 5회)
    ├─ 좋아요/장바구니 이력
    └─ 선호도 프로필
   ↓
12. 필터버블 해소 로직 실행
    ├─ SQL 벡터 검색 (임베딩 유사도)
    ├─ 재추천 방지 필터링
    ├─ 브랜드 다양성 체크 (최대 2개)
    ├─ 스타일 다양성 강제 (최소 3개)
    └─ 신규 70% + 기존 30% 선정
   ↓
13. GPT-4o-mini 프롬프트 생성 및 호출
   ↓
14. 추천 결과 반환
    ├─ 챗봇 UI에 표시
    └─ PostgreSQL/SQLite에 추천 이력 저장
   ↓
15. 사용자가 추천 상품 클릭
    ↓
16. 상품 상세 페이지로 이동 (/product/{product_id})
    └─ 클릭 이벤트 기록 (PostgreSQL/SQLite)
```

---

## 3. 데이터베이스 설계

### 3.1 ERD (실제 구현 기준)

```
┌─────────────────┐       ┌─────────────────┐
│  chat_sessions  │       │    products     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ session_id (UK) │       │ product_id (UK)│
│ user_id          │       │ name            │
│ is_active       │       │ brand           │
│ created_at      │       │ category        │
│ updated_at      │       │ gender          │
└─────────────────┘       │ style_tags      │
        │                 │ color           │
        │                 │ price           │
        │                 │ popularity_score│
        │                 │ image_url       │
        │                 │ description     │
        │                 │ embedding (JSONB)│
        │                 │ metadata (JSONB) │
        │                 │ created_at      │
        │                 │ updated_at      │
        │                 └─────────────────┘
        │                         │
        │                 ┌───────▼─────────┐
        │                 │ user_favorites  │
        │                 ├─────────────────┤
        │                 │ id (PK)         │
        │                 │ user_id         │
        │                 │ product_id       │
        │                 │ created_at      │
        │                 └─────────────────┘
        │
┌───────▼─────────┐       ┌─────────────────┐
│  chat_history   │       │   user_cart     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ session_id (FK) │       │ user_id         │
│ user_id         │       │ product_id      │
│ role            │       │ quantity        │
│ content         │       │ product_data    │
│ metadata (JSONB)│       │ created_at      │
│ created_at      │       │ updated_at      │
└─────────────────┘       └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ recommendation  │       │ recommendation  │
│   _history      │       │   _feedback     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id         │       │ user_id         │
│ query           │       │ product_id      │
│ recommendations │       │ feedback_type   │
│ total_count     │       │ created_at      │
│ diversity_score │       └─────────────────┘
│ strategy_used   │
│ created_at      │
└─────────────────┘
```

### 3.2 주요 테이블 상세 (실제 구현)

#### chat_sessions

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
```

#### chat_history

```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
```

#### products

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(50),
    gender VARCHAR(20),  -- '남성', '여성', '공용'
    style_tags JSONB,
    color VARCHAR(50),
    price INTEGER,
    popularity_score FLOAT DEFAULT 0.0,
    image_url TEXT,
    description TEXT,
    embedding JSONB,  -- 벡터 임베딩 배열 [0.12, 0.45, ...]
    metadata JSONB,   -- season, situation 등 추가 정보
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_products_product_id ON products(product_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_gender ON products(gender);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_embedding ON products USING GIN (embedding);
```

#### user_favorites

```sql
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_product_id ON user_favorites(product_id);
```

#### user_cart

```sql
CREATE TABLE user_cart (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1 NOT NULL,
    product_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_user_cart_user_id ON user_cart(user_id);
CREATE INDEX idx_user_cart_product_id ON user_cart(product_id);
```

#### recommendation_history

```sql
CREATE TABLE recommendation_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    recommendations JSONB,
    total_count INTEGER NOT NULL,
    diversity_score FLOAT NOT NULL,
    strategy_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_recommendation_history_user_id ON recommendation_history(user_id);
CREATE INDEX idx_recommendation_history_created_at ON recommendation_history(created_at);
```

#### recommendation_feedback

```sql
CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_recommendation_feedback_user_id ON recommendation_feedback(user_id);
CREATE INDEX idx_recommendation_feedback_product_id ON recommendation_feedback(product_id);
```

---

## 4. API 설계

### 4.1 엔드포인트 목록 (실제 구현)

```
# 헬스 체크 (Health)
GET    /api/v1/health/              # 기본 헬스 체크
GET    /api/v1/health/detailed       # 상세 헬스 체크

# 챗봇 (Chat)
POST   /api/v1/chat/message         # 메시지 전송
GET    /api/v1/chat/history/{session_id}  # 대화 이력
GET    /api/v1/chat/sessions/{user_id}    # 사용자 세션 목록
DELETE /api/v1/chat/session/{session_id}  # 세션 삭제

# 추천 (Recommendations)
POST   /api/v1/recommendations/search      # 추천 검색
GET    /api/v1/recommendations/history/{user_id}  # 추천 이력
POST   /api/v1/recommendations/feedback   # 피드백 제출
GET    /api/v1/recommendations/analytics/{user_id}  # 추천 분석
GET    /api/v1/recommendations/products/search  # 상품 검색 (맞춤 검색)

# 사용자 (Users)
GET    /api/v1/users/profile/{user_id}    # 프로필 조회
PUT    /api/v1/users/profile/{user_id}    # 프로필 수정
POST   /api/v1/users/profile/{user_id}/initialize  # 프로필 초기화
GET    /api/v1/users/preferences/{user_id}  # 선호도 조회
GET    /api/v1/users/behavior/{user_id}   # 행동 분석

# 좋아요 (Favorites)
POST   /api/v1/favorites/add             # 좋아요 추가
DELETE /api/v1/favorites/remove           # 좋아요 삭제
POST   /api/v1/favorites/toggle           # 좋아요 토글
GET    /api/v1/favorites/user/{user_id}   # 사용자 좋아요 목록
GET    /api/v1/favorites/user/{user_id}/product-ids  # 상품 ID 목록
GET    /api/v1/favorites/check/{user_id}/{product_id}  # 좋아요 확인

# 장바구니 (Cart)
POST   /api/v1/cart/add                  # 장바구니 추가
PUT    /api/v1/cart/update                # 장바구니 수정
DELETE /api/v1/cart/remove                 # 장바구니 삭제
DELETE /api/v1/cart/clear/{user_id}       # 장바구니 비우기
GET    /api/v1/cart/user/{user_id}        # 사용자 장바구니 조회

# 관리자 (Admin)
GET    /api/v1/admin/chat-history/all     # 전체 대화 내역
GET    /api/v1/admin/chat-history/user/{user_id}  # 사용자별 대화 내역
GET    /api/v1/admin/chat-history/session/{session_id}  # 세션별 대화 내역
GET    /api/v1/admin/favorites/all        # 전체 좋아요 목록
GET    /api/v1/admin/cart/all              # 전체 장바구니 목록
POST   /api/v1/admin/products/init         # 상품 초기화
PUT    /api/v1/admin/products/{product_id} # 상품 수정
```

### 4.2 주요 API 상세

#### POST /api/v1/chat/message

```python
# Request
{
    "message": "10만 원대 자켓 추천해줘",
    "session_id": "uuid-string",  # optional
    "user_id": "user123"
}

# Response (200 OK)
{
    "response": "가성비 좋은 자켓을 찾고 계시는군요! 👔\n\n💡 새로운 발견...",
    "session_id": "uuid-string",
    "recommendations": [
        {
            "product_id": "prod_001",
            "name": "오버핏 후드티",
            "brand": "무신사 스탠다드",
            "price": 89000,
            "image_url": "https://...",
            "product_url": "/product/prod_001",
            "recommendation_type": "new_discovery"
        }
    ],
    "intent": "가격·가성비",
    "confidence": 0.92
}
```

#### GET /api/v1/recommendations/products/search

```python
# Request Query Parameters
{
    "query": "미니멀한 셔츠",
    "user_id": "user123",  # optional
    "limit": 10
}

# Response (200 OK)
{
    "recommendations": [
        {
            "id": "prod_001",
            "name": "미니멀 셔츠",
            "brand": "29CM Studio",
            "price": 89000,
            "image_url": "https://...",
            "similarity_score": 0.85,
            "recommendation_type": "exploration",
            "reasoning": "사용자 취향을 반영한 검색 결과입니다."
        }
    ],
    "total_count": 10,
    "diversity_score": 0.65,
    "strategy_used": {"personalized_search": 1.0}
}
```

#### PUT /api/v1/admin/products/{product_id}

```python
# Request Header
Authorization: Bearer <admin_access_token>

# Request Body
{
    "name": "수정된 상품명",
    "brand": "수정된 브랜드",
    "category": "상의",
    "gender": "남성",
    "style_tags": ["미니멀", "29CM 감성"],
    "color": "화이트",
    "price": 150000,
    "popularity_score": 0.8,
    "image_url": "https://...",
    "description": "수정된 설명",
    "season": "사계절",
    "situation": "데일리"
}

# Response (200 OK)
{
    "message": "상품 정보가 수정되었습니다.",
    "product_id": "prod_001",
    "success": true
}
```

---

## 5. 핵심 알고리즘

### 5.1 Intent 분류 시스템

```python
# ml/intent_analyzer/intent_classifier.py

class IntentType(Enum):
    PRICE_VALUE = "가격·가성비"
    STYLE_MOOD = "감성·스타일"
    SEASON_WEATHER = "시즌·날씨"
    BODY_FIT = "체형·핏"
    SITUATION_COORD = "코디·상황"
    UNKNOWN = "unknown"

class IntentClassifier:
    """의도 분류기 - GPT-4o-mini + Few-shot learning"""
    
    def classify_intent(
        self,
        user_message: str,
        chat_history: List[Dict],
        user_profile: Optional[Dict] = None
    ) -> IntentResult:
        """
        사용자 메시지의 의도를 분류
        - Few-shot learning 기반
        - GPT-4o-mini API 사용
        """
        # 프롬프트 생성 및 GPT-4o-mini 호출
        # ...
```

### 5.2 필터버블 해소 엔진

```python
# ml/mmr_algorithm/mmr_scorer.py

class MMRScorer:
    """
    MMR (Maximal Marginal Relevance) 알고리즘
    - 유사도와 다양성의 균형
    - 브랜드 다양성 보장 (최대 2개)
    - 스타일 다양성 강제 (최소 3개)
    """
    
    def select_recommendations(
        self,
        candidates: List[ProductCandidate],
        strategy: Dict[str, float],  # {"exploitation": 0.3, "exploration": 0.7}
        total_count: int = 5
    ) -> List[ProductCandidate]:
        """
        필터버블을 해소한 추천 상품 리스트 생성
        - 신규 발견 70% + 기존 취향 30%
        - 재추천 방지 (최근 5회 대화 제외)
        - 브랜드 다양성 (동일 브랜드 최대 2개)
        - 스타일 다양성 (최소 3개 다른 스타일)
        """
        # ...
```

### 5.3 SQL 기반 벡터 검색

```python
# ml/vector_search/sql_vector_store.py

class SQLVectorStore:
    """
    SQL 기반 벡터 스토어
    - PostgreSQL/SQLite JSONB 컬럼에 임베딩 저장
    - 코사인 유사도 계산 (NumPy)
    - 인덱스 최적화 (GIN 인덱스)
    """
    
    async def search_similar(
        self,
        query_embedding: np.ndarray,
        limit: int = 50,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        유사 상품 검색
        - SQL 쿼리로 임베딩 조회
        - NumPy로 코사인 유사도 계산
        - 필터 적용 (카테고리, 성별 등)
        """
        # ...
```

### 5.4 사용자 취향 분석

```python
# backend/app/services/recommendation_service.py

class RecommendationService:
    """
    추천 서비스
    - 사용자 취향 분석 (좋아요/장바구니 기반)
    - 맞춤 검색 결과 생성
    """
    
    async def analyze_user_preferences_from_db(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        사용자 취향 분석
        - 좋아요/장바구니 데이터 기반
        - 스타일 분포, 카테고리, 브랜드, 가격 범위 계산
        """
        # ...
    
    async def get_personalized_search_results(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        사용자 취향을 반영한 맞춤 검색
        - 스타일 유사도 (가중치 0.4)
        - 카테고리 유사도 (가중치 0.3)
        - 브랜드 유사도 (가중치 0.2)
        - 가격 범위 유사도 (가중치 0.1)
        - 인기도 보너스 (최대 0.2)
        """
        # ...
```

---

## 6. 프론트엔드 구조

### 6.1 컴포넌트 구조

```
frontend/src/
├── components/
│   ├── Header.js              # 헤더 (로고, 검색바, 사용자 메뉴)
│   ├── SearchBar.js           # 검색바
│   ├── ProductList.js         # 상품 목록
│   ├── ProductCard.js         # 상품 카드
│   ├── ProductDetailPage.js  # 상품 상세 페이지
│   ├── CartModal.js          # 장바구니 모달
│   ├── FavoritesModal.js     # 좋아요 모달
│   ├── ChatModal.js          # 챗봇 모달
│   ├── FloatingChatButton.js # 플로팅 챗봇 버튼
│   ├── AuthModal.js          # 인증 모달
│   ├── CheckoutPage.js       # 결제 페이지
│   ├── OrderCompletePage.js  # 주문 완료 페이지
│   ├── MyPage.js             # 마이페이지
│   └── AdminDashboard.js     # 관리자 대시보드
├── contexts/
│   ├── AuthContext.js        # 인증 컨텍스트
│   ├── CartContext.js        # 장바구니 컨텍스트
│   └── FavoritesContext.js   # 좋아요 컨텍스트
├── services/
│   ├── chatService.js        # 챗봇 API
│   ├── cartService.js        # 장바구니 API
│   ├── favoriteService.js    # 좋아요 API
│   ├── adminService.js       # 관리자 API
│   ├── recommendationService.js  # 추천 API
│   └── searchService.js      # 검색 API
├── data/
│   └── dummyProducts.js      # 더미 상품 데이터
├── App.js                    # 메인 앱 컴포넌트
└── index.js                  # 진입점
```

### 6.2 라우팅 구조

```javascript
// App.js
<Router>
  <Routes>
    <Route path="/" element={<AppContent />} />
    <Route path="/product/:productId" element={<ProductDetailPage />} />
    <Route path="/checkout" element={<CheckoutPage />} />
    <Route path="/order-complete/:orderId" element={<OrderCompletePage />} />
    <Route path="/mypage" element={<MyPage />} />
    <Route path="/admin" element={<AdminDashboard />} />
  </Routes>
</Router>
```

### 6.3 상태 관리

- **Context API**: 인증, 장바구니, 좋아요 상태 관리
- **LocalStorage**: 사용자 데이터, 장바구니, 좋아요, 주문 내역 영속성
- **React State**: 컴포넌트별 로컬 상태

---

## 7. 백엔드 구조

### 7.1 디렉토리 구조

```
backend/
├── app/
│   ├── api/
│   │   └── api_v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── chat.py
│   │           ├── recommendations.py
│   │           ├── users.py
│   │           ├── favorites.py
│   │           ├── cart.py
│   │           ├── admin.py
│   │           └── health.py
│   ├── core/
│   │   ├── config.py          # 설정 관리
│   │   └── logging.py         # 로깅 설정
│   ├── models/
│   │   ├── db_models.py       # SQLAlchemy 모델
│   │   └── chat.py            # 챗봇 모델
│   ├── services/
│   │   ├── chat_service.py    # 챗봇 서비스
│   │   ├── chat_history_service.py
│   │   ├── session_service.py
│   │   ├── recommendation_service.py
│   │   ├── favorite_service.py
│   │   ├── cart_service.py
│   │   └── user_service.py
│   ├── database.py            # DB 연결
│   └── main.py                # FastAPI 앱
├── migrations/
│   └── init_db.sql            # 초기 스키마
├── scripts/
│   ├── init_products.py      # 상품 초기화
│   └── generate_products.py  # 더미 상품 생성
├── requirements.txt
└── Dockerfile
```

### 7.2 서비스 레이어

- **ChatService**: 챗봇 메시지 처리 및 AI 응답 생성
- **RecommendationService**: 추천 로직 및 사용자 취향 분석
- **SearchEngine**: 벡터 검색 엔진
- **MMRScorer**: MMR 알고리즘 구현
- **IntentClassifier**: 의도 분류
- **ResponseGenerator**: AI 응답 생성

---

## 8. AI/ML 모듈

### 8.1 모듈 구조

```
ml/
├── intent_analyzer/
│   ├── intent_classifier.py      # 의도 분류기
│   └── few_shot_prompts.py       # Few-shot 프롬프트
├── vector_search/
│   ├── embedding_service.py      # 임베딩 생성
│   ├── search_engine.py          # 검색 엔진
│   ├── sql_vector_store.py       # SQL 벡터 스토어
│   └── vector_store.py           # 벡터 스토어 인터페이스
├── mmr_algorithm/
│   ├── mmr_scorer.py             # MMR 알고리즘
│   └── diversity_calculator.py   # 다양성 계산
└── response_generator/
    ├── response_generator.py      # 응답 생성기
    └── prompt_templates.py       # 프롬프트 템플릿
```

### 8.2 주요 기능

#### 8.2.1 의도 분류

- **모델**: GPT-4o-mini
- **방법**: Few-shot learning
- **의도 타입**: 가격·가성비, 감성·스타일, 시즌·날씨, 체형·핏, 코디·상황

#### 8.2.2 벡터 검색

- **임베딩 모델**: text-embedding-3-large (3072 차원)
- **저장소**: PostgreSQL/SQLite JSONB 컬럼
- **검색 방법**: 코사인 유사도 (NumPy)

#### 8.2.3 MMR 알고리즘

- **목표**: 유사도와 다양성의 균형
- **비율**: 신규 발견 70% + 기존 취향 30%
- **제약 조건**:
  - 재추천 방지 (최근 5회 대화 제외)
  - 브랜드 다양성 (동일 브랜드 최대 2개)
  - 스타일 다양성 (최소 3개 다른 스타일)

#### 8.2.4 응답 생성

- **모델**: GPT-4o-mini
- **템플릿**: Jinja2 기반
- **구조**: 4단계 (공감 → 신규 발견 → 기존 취향 → 꼬리질문)
- **제약**: 꼬리질문 최대 2개

---

## 9. 배포 및 인프라

### 9.1 로컬 개발 환경 (Docker Compose)

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/fashion_ai_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./ml:/ml

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 9.2 실행 방법

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 로컬 환경에서 실행 (개발용)
# 백엔드
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드
cd frontend
npm start
```

---

## 10. 주요 개선사항 (v1.2 → v1.3)

### 10.1 기술 스택 변경

- **프론트엔드**: Next.js → React.js (CRA)
- **TypeScript**: 미사용 (JavaScript)
- **벡터 DB**: Pinecone/Weaviate → SQL 기반 (PostgreSQL/SQLite)
- **인증**: JWT → LocalStorage 기반
- **배포**: AWS ECS → Docker Compose (로컬 개발)

### 10.2 기능 추가

- **관리자 대시보드 UX/UI 개선**
  - 카드 그리드 레이아웃
  - 필터 기능 (역할, 상태, 카테고리, 성별)
  - 통계 정보 표시

- **상품 수정 기능**
  - 상품 정보 수정 모달
  - 임베딩 자동 재생성
  - 데이터베이스 반영

- **사용자 취향 기반 맞춤 검색**
  - 좋아요/장바구니 데이터 분석
  - 유사도 기반 재정렬
  - 로그인 사용자만 적용

- **챗봇 입력창 개선**
  - 자동 높이 조절 (최소 1줄, 최대 6줄)
  - 부드러운 애니메이션

### 10.3 알고리즘 개선

- **재추천 방지**: 최근 10회 → 최근 5회 대화
- **브랜드 다양성**: 동일 브랜드 최대 2개 제한
- **스타일 다양성**: 최소 3개 다른 스타일 강제
- **템플릿 비율**: 동적 계산 (70/30)
- **꼬리질문 제한**: 최대 2개

---

## 11. 향후 계획 (v1.4)

### 11.1 인증 시스템 개선

- JWT 기반 인증 구현
- Refresh Token 지원
- 소셜 로그인 (Google, Kakao)

### 11.2 배포 인프라

- AWS ECS 배포
- RDS PostgreSQL
- ElastiCache Redis
- CloudFront CDN

### 11.3 기능 추가

- 실시간 채팅 (WebSocket)
- 이미지 검색
- 상품 리뷰 시스템
- 모바일 앱 (React Native)

---

**문서 버전**: 1.3  
**최종 수정일**: 2026-01-02  
**기준**: 실제 구현된 코드 전수 조사 결과

