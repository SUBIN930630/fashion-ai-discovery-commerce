


- **버전**: 1.2
- **목적**: 필터버블 해소형 패션 추천 AI 챗봇 개발
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

#### 1.2.2 챗봇 기능

- 우측 하단 플로팅 챗봇 아이콘
- 대화형 상품 추천 (Intent 기반)
- 필터버블 해소 알고리즘 (신규 70% + 기존 30%)
- 재추천 방지 시스템
- 추천 상품 클릭 시 상품 상세 페이지 연동

#### 1.2.3 사용자 인증 및 권한 관리

- 회원가입 / 로그인 / 로그아웃
- 소셜 로그인 (Google, Kakao - 선택사항)
- JWT 기반 인증
- 역할 기반 접근 제어 (RBAC):
    - **관리자(Admin)**: 전체 관리 기능
    - **일반 사용자(User)**: 쇼핑 및 챗봇 이용

#### 1.2.4 관리자 전용 기능

- 상품 관리 (CRUD)
- 사용자 관리
- 주문 관리
- 챗봇 대화 로그 분석 대시보드
- 추천 성과 모니터링 (CTR, 전환율)
- Intent 분류 통계
- 시스템 설정 관리

#### 1.2.5 일반 사용자 기능

- 쇼핑몰 브라우징
- 상품 검색 및 구매
- 챗봇을 통한 상품 추천
- 마이페이지 (주문 내역, 찜 목록)
- 프로필 관리

### 1.3 기술 스택

```
┌─────────────────────────────────────┐
│  Frontend (쇼핑몰 웹사이트)         │
│  - Next.js 14 (App Router)          │
│  - TypeScript                       │
│  - Tailwind CSS                     │
│  - Zustand (상태 관리)              │
│  - React Query (서버 상태)          │
│  - Nginx (정적 파일 서빙)           │
├─────────────────────────────────────┤
│  Frontend (챗봇 위젯)               │
│  - React 18                         │
│  - TypeScript                       │
│  - Styled Components                │
│  - Zustand (챗봇 상태)              │
│  - Socket.io Client (실시간 통신)   │
├─────────────────────────────────────┤
│  Backend Container                  │
│  - FastAPI (Python 3.11+)           │
│  - Uvicorn (ASGI Server)            │
│  - SQLAlchemy (ORM)                 │
│  - Alembic (마이그레이션)           │
│  - Poetry (의존성 관리)             │
│  - Pydantic (데이터 검증)           │
├─────────────────────────────────────┤
│  Database Services (AWS RDS)        │
│  - PostgreSQL 15+                   │
│  - Multi-AZ 배포                    │
│  - 자동 백업 활성화                 │
├─────────────────────────────────────┤
│  Cache Layer (AWS ElastiCache)      │
│  - Redis 7.x                        │
│  - 세션 관리                        │
│  - 챗봇 대화 컨텍스트 캐싱          │
├─────────────────────────────────────┤
│  AI/ML Services                     │
│  - OpenAI GPT-4 API                 │
│  - LangChain                        │
│  - Vector DB (Pinecone)             │
├─────────────────────────────────────┤
│  Authentication                     │
│  - JWT (Access Token + Refresh)     │
│  - bcrypt (비밀번호 해싱)           │
│  - OAuth 2.0 (소셜 로그인)          │
├─────────────────────────────────────┤
│  Infrastructure (AWS)               │
│  - ECS Fargate (컨테이너 오케스트레이션) │
│  - ECR (컨테이너 레지스트리)        │
│  - ALB (로드 밸런서)                │
│  - S3 (상품 이미지, 로그)           │
│  - CloudWatch (모니터링/로깅)       │
│  - Route 53 (DNS)                   │
│  - CloudFront (CDN)                 │
├─────────────────────────────────────┤
│  Development Tools                  │
│  - DBeaver (DB 관리/분석)           │
│  - Docker Desktop                   │
│  - Docker Compose (로컬 개발)       │
│  - GitHub Actions (CI/CD)           │
│  - Figma (UI/UX 디자인)             │
└─────────────────────────────────────┘
```

---

## 2. 시스템 아키텍처

### 2.1 전체 구조도 (쇼핑몰 + 챗봇 통합)

```
[사용자 브라우저]
   │
   ├─ 쇼핑몰 웹사이트
   │  - 상품 목록/상세
   │  - 장바구니
   │  - 주문/결제
   │
   └─ 우측 하단 플로팅 챗봇 아이콘
      └─ 클릭 시 챗봇 위젯 오픈
         └─ AI 추천 대화
   ↓
[CloudFront CDN]
   ↓
[Route 53 DNS]
   ↓
[Application Load Balancer]
   ↓
┌─────────────────────────────────────────────────────┐
│  AWS ECS Fargate Cluster                            │
│                                                      │
│  ┌───────────────────┐    ┌───────────────────┐    │
│  │ Shop Frontend     │    │ Backend API       │    │
│  │ Task (Next.js)    │    │ Task (FastAPI)    │    │
│  │                   │    │                   │    │
│  │ - 상품 페이지     │◄───│ - 인증/인가       │    │
│  │ - 장바구니        │    │ - 상품 API        │    │
│  │ - 챗봇 위젯 임베드│    │ - 주문 API        │    │
│  └───────────────────┘    │ - 챗봇 API        │    │
│                           │ - 관리자 API      │    │
│  ┌───────────────────┐    └───────────────────┘    │
│  │ Chatbot Widget    │           ↓                 │
│  │ Task (React)      │    ┌───────────────────┐    │
│  │                   │    │ AI Services       │    │
│  │ - 대화 UI         │◄───│ - Intent 분류     │    │
│  │ - 추천 표시       │    │ - 필터버블 해소   │    │
│  │ - 상품 연동       │    │ - GPT-4 호출      │    │
│  └───────────────────┘    └───────────────────┘    │
│                                                      │
│  Auto Scaling (2~10 Tasks per service)             │
└─────────────────────────────────────────────────────┘
                  ↓
    ┌─────────────┴─────────────┐
    ↓                           ↓
┌─────────────────┐    ┌─────────────────┐
│ AWS RDS         │    │ ElastiCache     │
│ (PostgreSQL)    │    │ (Redis)         │
│                 │    │                 │
│ - users         │    │ - JWT 세션      │
│ - products      │    │ - 챗봇 컨텍스트 │
│ - orders        │    │ - 캐시          │
│ - conversations │    └─────────────────┘
│ - messages      │
│ - recommendations│
│                 │
│ Multi-AZ        │
└─────────────────┘
    ↓
┌─────────────────┐
│ S3 Buckets      │
│ - 상품 이미지   │
│ - 로그 저장     │
│ - 백업 파일     │
└─────────────────┘
    ↓
┌─────────────────┐
│ External APIs   │
│ - OpenAI GPT-4  │
│ - Pinecone      │
│ - 결제 게이트웨이│
└─────────────────┘
```

### 2.2 사용자 플로우

#### 2.2.1 일반 사용자 플로우

```
1. 쇼핑몰 메인 페이지 접속
   ↓
2. (선택) 회원가입 또는 로그인
   ├─ 비로그인: 쇼핑 가능, 챗봇 이용 제한적
   └─ 로그인: 전체 기능 이용 가능
   ↓
3. 상품 브라우징
   ├─ 카테고리별 탐색
   ├─ 검색
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
2. 관리자 대시보드 접근
   ├─ 상품 관리
   │  ├─ 상품 등록/수정/삭제
   │  ├─ 재고 관리
   │  └─ 카테고리 관리
   │
   ├─ 사용자 관리
   │  ├─ 사용자 목록
   │  └─ 권한 변경
   │
   ├─ 주문 관리
   │  ├─ 주문 내역 조회
   │  └─ 배송 상태 업데이트
   │
   └─ 챗봇 분석 대시보드
      ├─ 대화 로그 조회 (DBeaver 연동)
      ├─ Intent 분포
      ├─ 추천 성과 (CTR, 전환율)
      └─ 재추천 케이스 확인
```

### 2.3 챗봇 위젯 임베디드 구조

```html
<!-- 쇼핑몰 페이지 -->
<html>
  <body>
    <!-- 쇼핑몰 콘텐츠 -->
    <main>
      <ProductList />
    </main>
    
    <!-- 우측 하단 플로팅 챗봇 -->
    <div id="chatbot-container" style="position: fixed; bottom: 20px; right: 20px;">
      <!-- 챗봇 아이콘 -->
      <button id="chatbot-toggle">
        <ChatBotIcon />
      </button>
      
      <!-- 챗봇 위젯 (클릭 시 표시) -->
      <div id="chatbot-widget" style="display: none;">
        <ChatbotIframe src="/chatbot" />
        <!-- 또는 직접 컴포넌트 렌더링 -->
      </div>
    </div>
  </body>
</html>
```

#### 챗봇 UI 스펙

```
크기: 400px (width) × 600px (height)
위치: 우측 하단 (bottom: 80px, right: 20px)
애니메이션: Slide up (열릴 때), Slide down (닫힐 때)

구성:
┌─────────────────────────┐
│ 헤더                    │
│ AI 스타일리스트 💬      │
│                   [X]   │
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
│ 입력창                  │
│ [메시지 입력...] [전송] │
└─────────────────────────┘
```

### 2.4 Docker 컨테이너 구조 (수정)

```
프로젝트 루트/
├── docker-compose.yml           # 로컬 개발 환경
├── docker-compose.prod.yml      # 프로덕션 참고용
│
├── shop-frontend/               # 쇼핑몰 웹사이트
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   ├── next.config.js
│   └── .dockerignore
│
├── chatbot-widget/              # 챗봇 위젯 (별도 빌드)
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── .dockerignore
│
├── backend/
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   ├── pyproject.toml
│   └── .dockerignore
│
└── docs/
    └── aws-deployment.md
```

### 2.5 데이터 흐름 (상세)

```
1. 사용자가 쇼핑몰 접속
   ↓ [HTTPS]
2. CloudFront → ALB → Shop Frontend (Next.js)
   ↓
3. 상품 데이터 요청
   ↓ [REST API]
4. Backend FastAPI → PostgreSQL
   ↓
5. 상품 목록 반환 → 화면 렌더링
   ↓
6. 사용자가 챗봇 아이콘 클릭
   ↓
7. 챗봇 위젯 로드 (iframe 또는 직접 렌더링)
   ↓
8. "10만 원대 자켓 추천해줘" 입력
   ↓ [WebSocket or REST]
9. Backend: Intent 분류 (100ms)
   ↓
10. Redis에서 세션 확인 (사용자 로그인 여부)
   ↓
11. PostgreSQL에서 사용자 히스토리 조회
    ├─ 최근 추천 이력
    ├─ 구매 이력
    └─ 선호도 프로필
   ↓
12. 필터버블 해소 로직 실행
    ├─ Pinecone Vector DB에서 유사 상품 검색
    ├─ 재추천 방지 필터링
    └─ 신규 70% + 기존 30% 선정
   ↓
13. GPT-4 프롬프트 생성 및 호출
   ↓
14. 추천 결과 반환
    ├─ 챗봇 UI에 표시
    └─ PostgreSQL에 추천 이력 저장
   ↓
15. 사용자가 추천 상품 클릭
    ↓
16. 상품 상세 페이지로 이동 (쇼핑몰 내)
    └─ 클릭 이벤트 기록 (PostgreSQL)
```

---

## 3. 데이터베이스 설계

### 3.1 ERD

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │    products     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ email           │       │ name            │
│ username        │       │ brand           │
│ password_hash   │       │ price           │
│ role (enum)     │       │ original_price  │
│ is_active       │       │ discount_rate   │
│ created_at      │       │ category_id(FK) │
│ updated_at      │       │ style_tags[]    │
│ last_login      │       │ description     │
│ style_profile   │       │ main_image_url  │
└─────────────────┘       │ images[]        │
        │                 │ stock           │
        │                 │ is_active       │
        │                 │ created_at      │
        │                 └─────────────────┘
        │                         │
        ├─────────────────────────┤
        │                         │
        │                 ┌───────▼─────────┐
        │                 │   categories    │
        │                 ├─────────────────┤
        │                 │ id (PK)         │
        │                 │ name            │
        │                 │ parent_id (FK)  │
        │                 │ slug            │
        │                 │ display_order   │
        │                 └─────────────────┘
        │
┌───────▼─────────┐       ┌─────────────────┐
│     orders      │       │   order_items   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │
│ user_id (FK)    │       │ order_id (FK)   │
│ status (enum)   │       │ product_id (FK) │
│ total_amount    │       │ quantity        │
│ payment_method  │       │ price           │
│ shipping_addr   │       │ subtotal        │
│ created_at      │       └─────────────────┘
│ updated_at      │
└─────────────────┘
        │
┌───────▼─────────┐
│ conversations   │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ started_at      │
│ ended_at        │
│ session_id      │
└─────────────────┘
        │
        ├─────────────────────────┐
        │                         │
┌───────▼─────────┐       ┌───────▼─────────┐
│    messages     │       │ recommendations │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ conversation_id │       │ conversation_id │
│ role (user/ai)  │       │ product_id (FK) │
│ content         │       │ rank_position   │
│ intent_type     │       │ is_new_discover │
│ created_at      │       │ recommended_at  │
└─────────────────┘       │ clicked         │
                          │ clicked_at      │
                          │ purchased       │
                          │ purchased_at    │
                          └─────────────────┘
                                  │
                          ┌───────▼─────────┐
                          │ user_feedback   │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ recommendation  │
                          │ rating (1-5)    │
                          │ feedback_type   │
                          │ comment         │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│     carts       │       │   cart_items    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │
│ user_id (FK)    │       │ cart_id (FK)    │
│ created_at      │       │ product_id (FK) │
│ updated_at      │       │ quantity        │
└─────────────────┘       │ added_at        │
                          └─────────────────┘

┌─────────────────┐
│   wishlists     │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ product_id (FK) │
│ added_at        │
└─────────────────┘
```

### 3.2 주요 테이블 상세

#### users (수정: 인증 및 권한 추가)

```sql
CREATE TYPE user_role AS ENUM ('admin', 'user');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    style_profile JSONB DEFAULT '{}'::jsonb,
    -- style_profile 구조:
    -- {
    --   "preferred_styles": ["minimal", "street"],
    --   "price_range": [50000, 150000],
    --   "body_type": "average",
    --   "height": 175
    -- }
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
```

#### categories (신규)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    slug VARCHAR(100) UNIQUE NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);

-- 초기 카테고리 데이터
INSERT INTO categories (name, slug, display_order) VALUES
('아우터', 'outer', 1),
('상의', 'top', 2),
('하의', 'bottom', 3),
('신발', 'shoes', 4),
('악세서리', 'accessory', 5);

-- 서브 카테고리
INSERT INTO categories (name, parent_id, slug, display_order) VALUES
('자켓', 1, 'jacket', 1),
('코트', 1, 'coat', 2),
('셔츠', 2, 'shirt', 1),
('니트', 2, 'knit', 2),
('슬랙스', 3, 'slacks', 1),
('진', 3, 'jeans', 2);
```

#### products (수정: 쇼핑몰 정보 추가)

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    original_price INTEGER,
    discount_rate INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES categories(id),
    style_tags TEXT[] DEFAULT '{}',
    description TEXT,
    main_image_url VARCHAR(500),
    images TEXT[] DEFAULT '{}',  -- 추가 이미지들
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    embedding VECTOR(1536), -- OpenAI embedding
    
    CONSTRAINT positive_price CHECK (price > 0),
    CONSTRAINT valid_discount CHECK (discount_rate BETWEEN 0 AND 100)
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_style ON products USING GIN(style_tags);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_embedding ON products USING ivfflat(embedding);
```

#### orders (신규)

```sql
CREATE TYPE order_status AS ENUM (
    'pending',      -- 결제 대기
    'paid',         -- 결제 완료
    'preparing',    -- 배송 준비
    'shipped',      -- 배송 중
    'delivered',    -- 배송 완료
    'cancelled',    -- 취소
    'refunded'      -- 환불
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status order_status DEFAULT 'pending',
    total_amount INTEGER NOT NULL,
    payment_method VARCHAR(50),
    shipping_address JSONB NOT NULL,
    -- shipping_address 구조:
    -- {
    --   "recipient": "홍길동",
    --   "phone": "010-1234-5678",
    --   "zip_code": "12345",
    --   "address": "서울시 강남구...",
    --   "detail": "101동 1001호"
    -- }
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

#### order_items (신규)

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,  -- 주문 당시 가격
    subtotal INTEGER NOT NULL,
    
    CONSTRAINT positive_quantity CHECK (quantity > 0)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

#### carts (신규)

```sql
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_carts_user ON carts(user_id);
```

#### cart_items (신규)

```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(cart_id, product_id),
    CONSTRAINT positive_quantity CHECK (quantity > 0)
);

CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
```

#### wishlists (신규)

```sql
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_wishlists_user ON wishlists(user_id);
CREATE INDEX idx_wishlists_product ON wishlists(product_id);
```

#### conversations

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    session_id UUID UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_conv_user_started ON conversations(user_id, started_at DESC);
```

#### messages

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    intent_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_msg_conversation ON messages(conversation_id, created_at);
```

#### recommendations

```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    product_id INTEGER REFERENCES products(id),
    rank_position INTEGER NOT NULL,
    is_new_discovery BOOLEAN DEFAULT FALSE,
    recommended_at TIMESTAMP DEFAULT NOW(),
    clicked BOOLEAN DEFAULT FALSE,
    clicked_at TIMESTAMP,
    purchased BOOLEAN DEFAULT FALSE,
    purchased_at TIMESTAMP,
    UNIQUE(conversation_id, product_id)
);

CREATE INDEX idx_rec_conversation ON recommendations(conversation_id);
CREATE INDEX idx_rec_product ON recommendations(product_id);
CREATE INDEX idx_rec_clicked ON recommendations(clicked, recommended_at);
```

#### user_feedback

```sql
CREATE TABLE user_feedback (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_type VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.3 더미 데이터 생성 스크립트

#### scripts/seed_data.py

```python
"""
쇼핑몰 더미 데이터 생성 스크립트
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from app.models import Category, Product, User
from app.core.security import get_password_hash

fake = Faker(['ko_KR'])

# 브랜드 목록
BRANDS = [
    "무신사 스탠다드", "앤더슨벨", "마르디 메크르디", 
    "커버낫", "디스이즈네버댓", "아더에러",
    "아크네 스튜디오", "폴로 랄프 로렌", "타미 힐피거",
    "유니클로", "자라", "COS"
]

# 스타일 태그
STYLE_TAGS = {
    "minimal": ["미니멀", "심플", "베이직"],
    "street": ["스트릿", "캐주얼", "힙합"],
    "classic": ["클래식", "정통", "포멀"],
    "modern": ["모던", "세련", "도시적"],
    "vintage": ["빈티지", "레트로", "올드스쿨"]
}

def generate_products(db: Session, count: int = 100):
    """상품 더미 데이터 생성"""
    
    categories = db.query(Category).all()
    
    products = []
    for i in range(count):
        category = random.choice(categories)
        style_type = random.choice(list(STYLE_TAGS.keys()))
        tags = random.sample(STYLE_TAGS[style_type], k=2)
        
        original_price = random.randint(30, 500) * 1000
        discount_rate = random.choice([0, 10, 20, 30])
        price = int(original_price * (100 - discount_rate) / 100)
        
        product = Product(
            name=f"{random.choice(BRANDS)} {category.name} {i+1:03d}",
            brand=random.choice(BRANDS),
            price=price,
            original_price=original_price,
            discount_rate=discount_rate,
            category_id=category.id,
            style_tags=tags,
            description=fake.text(max_nb_chars=200),
            main_image_url=f"https://picsum.photos/seed/{i}/400/600",
            images=[
                f"https://picsum.photos/seed/{i}-{j}/400/600" 
                for j in range(1, 4)
            ],
            stock=random.randint(0, 100),
            is_active=True
        )
        products.append(product)
    
    db.bulk_save_objects(products)
    db.commit()
    print(f"✅ {count}개 상품 생성 완료")

def generate_users(db: Session, count: int = 50):
    """사용자 더미 데이터 생성"""
    
    # 관리자 계정
    admin = User(
        email="admin@fashion-ai.com",
        username="admin",
        password_hash=get_password_hash("admin123!"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    
    # 일반 사용자
    users = []
    for i in range(count):
        user = User(
            email=fake.email(),
            username=f"user{i+1:03d}",
            password_hash=get_password_hash("password123"),
            role="user",
            is_active=True,
            style_profile={
                "preferred_styles": random.sample(
                    list(STYLE_TAGS.keys()), k=2
                ),
                "price_range": [
                    random.randint(30, 100) * 1000,
                    random.randint(100, 500) * 1000
                ],
                "height": random.randint(160, 190)
            }
        )
        users.append(user)
    
    db.bulk_save_objects(users)
    db.commit()
    print(f"✅ 관리자 1명 + 일반 사용자 {count}명 생성 완료")

if __name__ == "__main__":
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        print("🌱 더미 데이터 생성 시작...")
        generate_users(db, count=50)
        generate_products(db, count=100)
        print("✅ 모든 더미 데이터 생성 완료!")
    finally:
        db.close()
```

#### 실행 방법

```bash
# Docker 컨테이너 내부에서
docker-compose exec backend python scripts/seed_data.py

# 또는 로컬에서
cd backend
poetry run python scripts/seed_data.py
```

---

## 4. DBeaver를 활용한 데이터베이스 관리 및 분석

### 4.1 DBeaver 연결 설정

#### AWS RDS PostgreSQL 연결

```
Connection Settings:
- Host: fashion-ai-db.xxxxx.ap-northeast-2.rds.amazonaws.com
- Port: 5432
- Database: fashion_ai_prod
- Username: admin
- Password: [AWS Secrets Manager에서 관리]

SSH Tunnel (보안 강화):
- Use SSH Tunnel: Yes
- Host: bastion.your-domain.com
- Port: 22
- Username: ec2-user
- Auth Method: Public Key
```

#### 연결 풀 설정 (DBeaver)

```
Driver Properties:
- maximumPoolSize: 10
- minimumIdle: 2
- connectionTimeout: 30000
- idleTimeout: 600000
```

### 4.2 채팅 로그 분석 쿼리

#### 4.2.1 대화 흐름 분석

```sql
-- 전체 대화 흐름 조회 (최근 100개 대화)
SELECT 
    c.id AS conversation_id,
    c.session_id,
    c.started_at,
    c.ended_at,
    EXTRACT(EPOCH FROM (c.ended_at - c.started_at)) / 60 AS duration_minutes,
    COUNT(m.id) AS message_count,
    u.username
FROM conversations c
JOIN users u ON c.user_id = u.id
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.started_at >= NOW() - INTERVAL '7 days'
GROUP BY c.id, u.username
ORDER BY c.started_at DESC
LIMIT 100;
```

#### 4.2.2 Intent 분포 분석

```sql
-- Intent별 메시지 분포
SELECT 
    intent_type,
    COUNT(*) AS message_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM messages
WHERE 
    role = 'user' 
    AND created_at >= NOW() - INTERVAL '30 days'
    AND intent_type IS NOT NULL
GROUP BY intent_type
ORDER BY message_count DESC;
```

#### 4.2.3 추천 성과 분석

```sql
-- 추천 클릭률 및 구매 전환율 분석
SELECT 
    DATE(r.recommended_at) AS date,
    COUNT(*) AS total_recommendations,
    SUM(CASE WHEN r.clicked THEN 1 ELSE 0 END) AS clicks,
    SUM(CASE WHEN r.purchased THEN 1 ELSE 0 END) AS purchases,
    ROUND(SUM(CASE WHEN r.clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ctr_percent,
    ROUND(SUM(CASE WHEN r.purchased THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS conversion_rate
FROM recommendations r
WHERE r.recommended_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(r.recommended_at)
ORDER BY date DESC;
```

#### 4.2.4 필터버블 해소 효과 분석

```sql
-- 신규 발견 vs 기존 취향 클릭률 비교
SELECT 
    CASE 
        WHEN is_new_discovery THEN '신규 발견 (70%)'
        ELSE '기존 취향 (30%)'
    END AS recommendation_type,
    COUNT(*) AS total_count,
    SUM(CASE WHEN clicked THEN 1 ELSE 0 END) AS click_count,
    ROUND(SUM(CASE WHEN clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS ctr_percent
FROM recommendations
WHERE recommended_at >= NOW() - INTERVAL '30 days'
GROUP BY is_new_discovery;
```

#### 4.2.5 재추천 상품 탐지

```sql
-- 동일 상품이 재추천된 케이스 찾기 (버그 검증)
WITH recommendation_counts AS (
    SELECT 
        c.user_id,
        r.product_id,
        p.name AS product_name,
        COUNT(*) AS recommendation_count,
        MIN(r.recommended_at) AS first_recommended,
        MAX(r.recommended_at) AS last_recommended
    FROM recommendations r
    JOIN conversations c ON r.conversation_id = c.id
    JOIN products p ON r.product_id = p.id
    WHERE r.recommended_at >= NOW() - INTERVAL '30 days'
    GROUP BY c.user_id, r.product_id, p.name
    HAVING COUNT(*) > 1
)
SELECT *
FROM recommendation_counts
ORDER BY recommendation_count DESC, user_id
LIMIT 50;
```

#### 4.2.6 사용자별 대화 패턴 분석

```sql
-- 활성 사용자 Top 20 + 대화 패턴
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT c.id) AS total_conversations,
    COUNT(m.id) AS total_messages,
    ROUND(AVG(
        EXTRACT(EPOCH FROM (c.ended_at - c.started_at)) / 60
    ), 2) AS avg_conversation_minutes,
    MAX(c.started_at) AS last_conversation_date
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.started_at >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.username
HAVING COUNT(DISTINCT c.id) > 0
ORDER BY total_conversations DESC
LIMIT 20;
```

#### 4.2.7 응답 시간 분석

```sql
-- 메시지별 응답 시간 분석
WITH message_pairs AS (
    SELECT 
        m1.id AS user_message_id,
        m1.created_at AS user_time,
        m2.created_at AS assistant_time,
        EXTRACT(EPOCH FROM (m2.created_at - m1.created_at)) AS response_time_seconds,
        m1.intent_type
    FROM messages m1
    JOIN messages m2 ON m1.conversation_id = m2.conversation_id
    WHERE 
        m1.role = 'user'
        AND m2.role = 'assistant'
        AND m2.id = (
            SELECT MIN(id) 
            FROM messages 
            WHERE conversation_id = m1.conversation_id 
            AND role = 'assistant' 
            AND created_at > m1.created_at
        )
        AND m1.created_at >= NOW() - INTERVAL '7 days'
)
SELECT 
    intent_type,
    COUNT(*) AS message_count,
    ROUND(AVG(response_time_seconds), 2) AS avg_response_time,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_seconds), 2) AS median_response_time,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_seconds), 2) AS p95_response_time,
    MAX(response_time_seconds) AS max_response_time
FROM message_pairs
GROUP BY intent_type
ORDER BY avg_response_time DESC;
```

### 4.3 DBeaver 커스텀 대시보드 설정

#### 즐겨찾기 쿼리 등록

```
DBeaver > SQL Scripts > Create Folder "Fashion AI 분석"

저장할 쿼리:
1. daily_metrics.sql - 일일 주요 지표
2. intent_distribution.sql - Intent 분포
3. recommendation_performance.sql - 추천 성과
4. filter_bubble_check.sql - 필터버블 효과
5. slow_responses.sql - 느린 응답 탐지
```

### 4.4 채팅 로그 기반 기능 고도화 전략

#### 4.4.1 Phase 1: 로그 분석 (Week 1-2)

```python
# scripts/analyze_logs.py
"""
DBeaver에서 추출한 데이터를 기반으로 분석
"""

import pandas as pd
import matplotlib.pyplot as plt

# DBeaver에서 CSV로 내보낸 데이터 로드
def analyze_intent_distribution(csv_path):
    """Intent 분포 시각화"""
    df = pd.read_csv(csv_path)
    
    plt.figure(figsize=(10, 6))
    plt.bar(df['intent_type'], df['message_count'])
    plt.title('Intent Distribution (Last 30 Days)')
    plt.xlabel('Intent Type')
    plt.ylabel('Message Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/intent_distribution.png')

def analyze_recommendation_performance(csv_path):
    """추천 성과 분석"""
    df = pd.read_csv(csv_path)
    
    # 클릭률 트렌드
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['ctr_percent'], marker='o', label='CTR')
    plt.plot(df['date'], df['conversion_rate'], marker='s', label='Conversion')
    plt.title('Recommendation Performance Trend')
    plt.xlabel('Date')
    plt.ylabel('Percentage (%)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reports/recommendation_performance.png')

if __name__ == "__main__":
    analyze_intent_distribution('data/intent_dist.csv')
    analyze_recommendation_performance('data/rec_performance.csv')
```

#### 4.4.2 Phase 2: 알고리즘 개선 (Week 3-4)

**개선 항목**:

1. **Intent 분류 정확도 향상**
    
    - DBeaver에서 잘못 분류된 케이스 추출
    - 키워드 사전 업데이트
    - 머신러닝 모델 도입 검토
2. **추천 품질 개선**
    
    - 클릭률 낮은 상품 패턴 분석
    - 필터버블 해소 비율 조정 (70:30 → 60:40 테스트)
    - 브랜드 다양성 규칙 강화
3. **응답 시간 최적화**
    
    - 느린 쿼리 식별 및 인덱스 추가
    - Redis 캐싱 전략 강화
    - GPT-4 프롬프트 최적화

#### 4.4.3 Phase 3: A/B 테스트 (Week 5-6)

```sql
-- A/B 테스트 그룹 생성
ALTER TABLE users ADD COLUMN ab_test_group VARCHAR(10);

UPDATE users
SET ab_test_group = CASE 
    WHEN id % 2 = 0 THEN 'control'
    ELSE 'experiment'
END;

-- A/B 테스트 결과 분석
SELECT 
    u.ab_test_group,
    COUNT(DISTINCT c.id) AS conversations,
    AVG(
        CASE WHEN r.clicked THEN 1.0 ELSE 0.0 END
    ) AS avg_ctr,
    AVG(
        CASE WHEN r.purchased THEN 1.0 ELSE 0.0 END
    ) AS avg_conversion
FROM users u
JOIN conversations c ON u.id = c.user_id
JOIN recommendations r ON c.id = r.conversation_id
WHERE c.started_at >= NOW() - INTERVAL '7 days'
GROUP BY u.ab_test_group;
```

### 4.5 DBeaver ER 다이어그램 활용

```
DBeaver > Database Navigator > 
우클릭 > Tools > Generate ER Diagram

생성할 다이어그램:
1. 전체 스키마 (모든 테이블)
2. 추천 흐름 (users → conversations → recommendations → products)
3. 분석용 (recommendations + feedback)

저장 위치: docs/diagrams/
```

### 4.6 정기 점검 체크리스트 (DBeaver 활용)

```markdown
## 주간 점검 (매주 월요일)

☐ 지난 주 대화량 확인
☐ Intent 분포 변화 확인
☐ 추천 클릭률/전환율 확인
☐ 재추천 케이스 확인 (버그 체크)
☐ 느린 쿼리 탐지 (EXPLAIN ANALYZE)
☐ 디스크 사용량 확인

## 월간 점검 (매월 1일)

☐ 월간 성과 리포트 생성
☐ 데이터베이스 인덱스 최적화
☐ 테이블 VACUUM 실행
☐ 백업 무결성 검증
☐ 사용자 피드백 종합 분석
```

---

## 5. 핵심 알고리즘

### 4.1 Intent 분류 시스템

```python
from enum import Enum
from typing import List, Dict
import re

class IntentType(Enum):
    PRICE_VALUE = "가격·가성비"
    STYLE_MOOD = "감성·스타일"
    SEASON_WEATHER = "시즌·날씨"
    BODY_FIT = "체형·핏"
    SITUATION_COORD = "코디·상황"
    UNKNOWN = "unknown"

class IntentClassifier:
    """의도 분류기"""
    
    INTENT_KEYWORDS = {
        IntentType.PRICE_VALUE: [
            "가격", "가성비", "저렴", "부담 없는", "학생", 
            "예산", "만원", "원대", "첫", "하나만"
        ],
        IntentType.STYLE_MOOD: [
            "미니멀", "스트릿", "무드", "감성", "트렌디", 
            "깔끔", "29CM", "무신사", "느낌", "스타일"
        ],
        IntentType.SEASON_WEATHER: [
            "봄", "여름", "가을", "겨울", "장마", 
            "더위", "추위", "날씨", "비", "바람", "일교차"
        ],
        IntentType.BODY_FIT: [
            "키", "체형", "핏", "마른", "배", 
            "어깨", "다리", "cm", "허벅지", "상체"
        ],
        IntentType.SITUATION_COORD: [
            "출근", "데이트", "소개팅", "여행", "회식", 
            "면접", "주말", "회사", "첫 출근", "사진"
        ]
    }
    
    def classify(self, user_query: str) -> IntentType:
        """
        사용자 질문을 분석하여 Intent 분류
        
        Args:
            user_query: 사용자 입력 텍스트
            
        Returns:
            IntentType: 분류된 의도
        """
        query_lower = user_query.lower()
        
        # 각 Intent별 키워드 매칭 점수 계산
        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[intent] = score
        
        # 최고 점수 Intent 반환
        max_intent = max(scores, key=scores.get)
        
        if scores[max_intent] == 0:
            return IntentType.UNKNOWN
            
        return max_intent
    
    def extract_context(self, user_query: str, intent: IntentType) -> Dict:
        """
        Intent별 추가 컨텍스트 추출
        
        Returns:
            Dict: 추출된 컨텍스트 정보
        """
        context = {}
        
        if intent == IntentType.PRICE_VALUE:
            # 가격 정보 추출
            price_match = re.search(r'(\d+)만\s*원', user_query)
            if price_match:
                context['max_price'] = int(price_match.group(1)) * 10000
        
        elif intent == IntentType.BODY_FIT:
            # 신체 정보 추출
            height_match = re.search(r'(\d{3})cm', user_query)
            if height_match:
                context['height'] = int(height_match.group(1))
        
        elif intent == IntentType.SEASON_WEATHER:
            # 계절 정보 추출
            seasons = ["봄", "여름", "가을", "겨울"]
            for season in seasons:
                if season in user_query:
                    context['season'] = season
                    break
        
        return context
```

### 4.2 필터버블 해소 엔진

```python
from typing import List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    brand: str
    price: int
    style_tags: List[str]
    relevance_score: float = 0.0

@dataclass
class RecommendationHistory:
    product_id: int
    recommended_at: datetime
    clicked: bool
    purchased: bool

class FilterBubbleBuster:
    """필터버블 해소 추천 엔진"""
    
    NEW_DISCOVERY_RATIO = 0.7  # 새로운 발견 70%
    EXISTING_PREFERENCE_RATIO = 0.3  # 기존 취향 30%
    RECENT_HISTORY_COUNT = 5  # 최근 5회 추천 이력
    SAME_BRAND_LIMIT = 2  # 동일 브랜드 최대 2개
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_recommendations(
        self, 
        user_id: int, 
        candidate_products: List[Product],
        total_count: int = 5
    ) -> Tuple[List[Product], List[Product]]:
        """
        필터버블을 해소한 추천 상품 리스트 생성
        
        Args:
            user_id: 사용자 ID
            candidate_products: 후보 상품 리스트 (이미 관련성 점수 계산됨)
            total_count: 총 추천 개수
            
        Returns:
            (새로운 발견 상품 리스트, 기존 취향 상품 리스트)
        """
        # 1. 최근 추천 이력 조회
        recent_history = self._get_recent_history(user_id)
        
        # 2. 재추천 방지 필터링
        filtered_products = self._filter_recently_recommended(
            candidate_products, 
            recent_history
        )
        
        # 3. 사용자 선호도 기반 분류
        new_discoveries, existing_prefs = self._split_by_preference(
            user_id,
            filtered_products
        )
        
        # 4. 비율에 맞게 선정
        new_count = int(total_count * self.NEW_DISCOVERY_RATIO)
        existing_count = total_count - new_count
        
        # 5. 브랜드 다양성 체크
        final_new = self._ensure_brand_diversity(
            new_discoveries[:new_count * 2]  # 여유있게 가져와서 필터링
        )[:new_count]
        
        final_existing = self._ensure_brand_diversity(
            existing_prefs[:existing_count * 2]
        )[:existing_count]
        
        return final_new, final_existing
    
    def _get_recent_history(self, user_id: int) -> List[RecommendationHistory]:
        """최근 N회 추천 이력 조회"""
        query = """
            SELECT DISTINCT ON (r.product_id)
                r.product_id,
                r.recommended_at,
                r.clicked,
                r.purchased
            FROM recommendations r
            JOIN conversations c ON r.conversation_id = c.id
            WHERE c.user_id = %s
            ORDER BY r.product_id, r.recommended_at DESC
            LIMIT %s
        """
        
        results = self.db.execute(
            query, 
            (user_id, self.RECENT_HISTORY_COUNT * 10)
        ).fetchall()
        
        return [
            RecommendationHistory(
                product_id=row[0],
                recommended_at=row[1],
                clicked=row[2],
                purchased=row[3]
            )
            for row in results
        ]
    
    def _filter_recently_recommended(
        self,
        products: List[Product],
        history: List[RecommendationHistory]
    ) -> List[Product]:
        """
        재추천 방지 필터
        - 최근 추천했으나 클릭 안 한 상품 제외
        - 최근 추천한 상품은 우선순위 낮춤
        """
        recent_product_ids = {h.product_id for h in history}
        not_clicked_ids = {
            h.product_id for h in history 
            if not h.clicked and not h.purchased
        }
        
        # 클릭 안 한 상품 완전 제외
        filtered = [
            p for p in products 
            if p.id not in not_clicked_ids
        ]
        
        # 최근 추천 상품은 관련성 점수 50% 페널티
        for product in filtered:
            if product.id in recent_product_ids:
                product.relevance_score *= 0.5
        
        return sorted(
            filtered, 
            key=lambda x: x.relevance_score, 
            reverse=True
        )
    
    def _split_by_preference(
        self,
        user_id: int,
        products: List[Product]
    ) -> Tuple[List[Product], List[Product]]:
        """
        사용자 선호도 기반으로 신규/기존 분류
        """
        # 사용자 프로필 조회
        user_profile = self._get_user_style_profile(user_id)
        preferred_styles = set(user_profile.get('preferred_styles', []))
        
        new_discoveries = []
        existing_prefs = []
        
        for product in products:
            product_styles = set(product.style_tags)
            
            # 교집합이 있으면 기존 취향, 없으면 새로운 발견
            if product_styles & preferred_styles:
                existing_prefs.append(product)
            else:
                new_discoveries.append(product)
        
        return new_discoveries, existing_prefs
    
    def _ensure_brand_diversity(
        self,
        products: List[Product]
    ) -> List[Product]:
        """
        브랜드 다양성 보장 (동일 브랜드 최대 2개)
        """
        brand_count = {}
        result = []
        
        for product in products:
            current_count = brand_count.get(product.brand, 0)
            
            if current_count < self.SAME_BRAND_LIMIT:
                result.append(product)
                brand_count[product.brand] = current_count + 1
        
        return result
    
    def _get_user_style_profile(self, user_id: int) -> dict:
        """사용자 스타일 프로필 조회"""
        query = "SELECT style_profile FROM users WHERE id = %s"
        result = self.db.execute(query, (user_id,)).fetchone()
        return result[0] if result else {}
```

### 4.3 프롬프트 생성 시스템

```python
from typing import List, Dict
from jinja2 import Template

class PromptBuilder:
    """GPT-4용 프롬프트 생성기"""
    
    SYSTEM_PROMPT_TEMPLATE = """
당신은 패션 이커머스 플랫폼의 **AI 스타일리스트**입니다.

## 핵심 원칙
1. 필터버블 해소: 매번 비슷한 상품만 추천하지 않습니다
2. 추천 비율: 새로운 발견 70% + 기존 취향 30%
3. 재추천 방지: 최근 5회 대화에서 추천한 상품 제외
4. 브랜드 다양성: 동일 브랜드 최대 2개

## 응답 구조
1단계: 공감 + 의도 확인
2단계: 💡 새로운 발견 (70%)
3단계: 🏠 내 취향 (30%)
4단계: 꼬리질문 (최대 2개)

## 톤앤매너
- 친근하고 자연스러운 대화체
- 존댓말 사용
- 이모지 적절히 사용
- 추천 이유 필수 포함
"""
    
    USER_PROMPT_TEMPLATE = """
## 사용자 정보
- Intent: {{ intent }}
- 질문: {{ query }}
{% if context %}
- 추가 컨텍스트: {{ context }}
{% endif %}

## 추천 상품

### 💡 새로운 발견 ({{ new_products|length }}개)
{% for product in new_products %}
{{ loop.index }}. **{{ product.name }}** - {{ product.brand }}
   - 가격: {{ "{:,}".format(product.price) }}원
   - 스타일: {{ product.style_tags|join(', ') }}
   - 설명: {{ product.description }}
   {% if product.why_new %}
   - 새로운 이유: {{ product.why_new }}
   {% endif %}
{% endfor %}

### 🏠 내 취향 ({{ existing_products|length }}개)
{% for product in existing_products %}
{{ loop.index }}. **{{ product.name }}** - {{ product.brand }}
   - 가격: {{ "{:,}".format(product.price) }}원
   - 스타일: {{ product.style_tags|join(', ') }}
   - 설명: {{ product.description }}
{% endfor %}

## 최근 추천 이력 (참고용 - 재추천 금지)
{% for item in recent_history %}
- {{ item.product_name }} ({{ item.recommended_at }})
  {% if not item.clicked %}- 클릭 안 함{% endif %}
{% endfor %}

위 정보를 바탕으로 사용자에게 추천 응답을 작성하세요.
"""
    
    def build_prompt(
        self,
        intent: IntentType,
        user_query: str,
        new_products: List[Product],
        existing_products: List[Product],
        context: Dict = None,
        recent_history: List[Dict] = None
    ) -> Tuple[str, str]:
        """
        GPT-4 프롬프트 생성
        
        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.strip()
        
        # 상품에 "새로운 이유" 추가
        for product in new_products:
            product.why_new = self._generate_why_new(product, context)
        
        user_template = Template(self.USER_PROMPT_TEMPLATE)
        user_prompt = user_template.render(
            intent=intent.value,
            query=user_query,
            context=context or {},
            new_products=new_products,
            existing_products=existing_products,
            recent_history=recent_history or []
        )
        
        return system_prompt, user_prompt
    
    def _generate_why_new(self, product: Product, context: Dict) -> str:
        """상품이 '새로운 발견'인 이유 생성"""
        reasons = []
        
        if context and 'preferred_styles' in context:
            preferred = set(context['preferred_styles'])
            product_styles = set(product.style_tags)
            
            if not (product_styles & preferred):
                reasons.append("평소와 다른 스타일")
        
        # 추가적인 새로운 이유들
        # - 새로운 브랜드
        # - 가격대 다양화
        # - 트렌드 반영 등
        
        return ", ".join(reasons) if reasons else "새로운 스타일"
```

---

## 6. API 설계

### 6.1 엔드포인트 목록

```
# 인증 (Authentication)
POST   /api/v1/auth/register         # 회원가입
POST   /api/v1/auth/login            # 로그인
POST   /api/v1/auth/logout           # 로그아웃
POST   /api/v1/auth/refresh          # 토큰 갱신
GET    /api/v1/auth/me               # 현재 사용자 정보

# 상품 (Products)
GET    /api/v1/products              # 상품 목록
GET    /api/v1/products/:id          # 상품 상세
GET    /api/v1/products/search       # 상품 검색
GET    /api/v1/categories            # 카테고리 목록

# 장바구니 (Cart)
GET    /api/v1/cart                  # 장바구니 조회
POST   /api/v1/cart/items            # 상품 추가
PUT    /api/v1/cart/items/:id        # 수량 변경
DELETE /api/v1/cart/items/:id        # 상품 삭제

# 주문 (Orders)
POST   /api/v1/orders                # 주문 생성
GET    /api/v1/orders                # 주문 내역
GET    /api/v1/orders/:id            # 주문 상세

# 찜 (Wishlist)
GET    /api/v1/wishlist              # 찜 목록
POST   /api/v1/wishlist              # 찜 추가
DELETE /api/v1/wishlist/:product_id  # 찜 삭제

# 챗봇 (Chatbot)
POST   /api/v1/chat/message          # 메시지 전송
GET    /api/v1/chat/conversations    # 대화 이력
GET    /api/v1/chat/conversation/:id # 특정 대화 상세
POST   /api/v1/feedback              # 피드백 제출

# 사용자 (User)
GET    /api/v1/user/profile          # 프로필 조회
PUT    /api/v1/user/profile          # 프로필 수정
PUT    /api/v1/user/password         # 비밀번호 변경

# 관리자 - 상품 관리 (Admin - Products)
POST   /api/v1/admin/products        # 상품 등록
PUT    /api/v1/admin/products/:id    # 상품 수정
DELETE /api/v1/admin/products/:id    # 상품 삭제
PUT    /api/v1/admin/products/:id/stock  # 재고 업데이트

# 관리자 - 주문 관리 (Admin - Orders)
GET    /api/v1/admin/orders          # 전체 주문 조회
PUT    /api/v1/admin/orders/:id/status  # 주문 상태 변경

# 관리자 - 사용자 관리 (Admin - Users)
GET    /api/v1/admin/users           # 사용자 목록
PUT    /api/v1/admin/users/:id/role  # 권한 변경
PUT    /api/v1/admin/users/:id/active  # 계정 활성화/비활성화

# 관리자 - 대시보드 (Admin - Dashboard)
GET    /api/v1/admin/dashboard/stats      # 전체 통계
GET    /api/v1/admin/dashboard/chatbot    # 챗봇 분석
GET    /api/v1/admin/dashboard/sales      # 매출 분석
```

### 6.2 인증 API 상세

#### POST /api/v1/auth/register

```python
# Request
{
    "email": "user@example.com",
    "username": "user123",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!"
}

# Response (201 Created)
{
    "id": 123,
    "email": "user@example.com",
    "username": "user123",
    "role": "user",
    "created_at": "2026-01-02T10:00:00Z"
}

# Error Response (400 Bad Request)
{
    "error": {
        "code": "EMAIL_ALREADY_EXISTS",
        "message": "이미 등록된 이메일입니다",
        "details": {"email": "user@example.com"}
    }
}
```

#### POST /api/v1/auth/login

```python
# Request
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}

# Response (200 OK)
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": 123,
        "email": "user@example.com",
        "username": "user123",
        "role": "user"
    }
}

# Error Response (401 Unauthorized)
{
    "error": {
        "code": "INVALID_CREDENTIALS",
        "message": "이메일 또는 비밀번호가 올바르지 않습니다"
    }
}
```

### 6.3 상품 API 상세

#### GET /api/v1/products

```python
# Request Query Parameters
{
    "category_id": 1,           # optional
    "brand": "무신사 스탠다드",   # optional
    "min_price": 50000,         # optional
    "max_price": 200000,        # optional
    "style_tags": ["미니멀"],   # optional
    "sort": "price_asc",        # price_asc, price_desc, newest, popular
    "page": 1,
    "per_page": 20
}

# Response (200 OK)
{
    "items": [
        {
            "id": 1,
            "name": "무신사 스탠다드 싱글 자켓",
            "brand": "무신사 스탠다드",
            "price": 89000,
            "original_price": 99000,
            "discount_rate": 10,
            "category": {
                "id": 1,
                "name": "아우터",
                "slug": "outer"
            },
            "style_tags": ["미니멀", "베이직"],
            "main_image_url": "https://...",
            "stock": 50,
            "is_active": true
        }
    ],
    "total": 156,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
}
```

### 6.4 챗봇 API 상세

#### POST /api/v1/chat/message

```python
# Request Header
Authorization: Bearer <access_token>

# Request Body
{
    "session_id": "uuid-string",  # optional, 새 대화면 생성
    "message": "10만 원대 자켓 추천해줘",
    "context": {
        "current_product_id": 123  # optional, 현재 보고 있는 상품
    }
}

# Response (200 OK)
{
    "message_id": 789,
    "conversation_id": 101,
    "session_id": "uuid-string",
    "response": {
        "text": "가성비 좋은 자켓을 찾고 계시는군요! 👔\n\n💡 새로운 발견...",
        "intent": "가격·가성비",
        "recommendations": [
            {
                "product_id": 1001,
                "name": "코튼 워크 재킷",
                "brand": "브랜드A",
                "price": 89000,
                "main_image_url": "https://...",
                "category": "new_discovery",  # new_discovery or existing_preference
                "rank": 1,
                "recommendation_id": 5001
            }
        ]
    },
    "metadata": {
        "processing_time_ms": 1234,
        "model_version": "gpt-4-turbo",
        "confidence_score": 0.92
    }
}
```

### 6.5 관리자 API 상세

#### GET /api/v1/admin/dashboard/stats

```python
# Request Header
Authorization: Bearer <admin_access_token>

# Response (200 OK)
{
    "overview": {
        "total_users": 1250,
        "active_users_today": 89,
        "total_products": 500,
        "total_orders": 3420,
        "total_revenue": 85600000
    },
    "chatbot": {
        "total_conversations": 5432,
        "avg_messages_per_conversation": 6.5,
        "recommendations_made": 15234,
        "click_through_rate": 18.5,
        "conversion_rate": 4.2
    },
    "time_range": {
        "start": "2026-01-01T00:00:00Z",
        "end": "2026-01-02T23:59:59Z"
    }
}

# Error Response (403 Forbidden)
{
    "error": {
        "code": "ADMIN_REQUIRED",
        "message": "관리자 권한이 필요합니다"
    }
}
```

#### POST /api/v1/admin/products

```python
# Request Header
Authorization: Bearer <admin_access_token>

# Request Body (multipart/form-data)
{
    "name": "새로운 자켓",
    "brand": "무신사 스탠다드",
    "price": 150000,
    "original_price": 180000,
    "category_id": 1,
    "style_tags": ["미니멀", "베이직"],
    "description": "심플한 디자인의 자켓...",
    "stock": 100,
    "main_image": <File>,
    "images": [<File>, <File>]
}

# Response (201 Created)
{
    "id": 501,
    "name": "새로운 자켓",
    "brand": "무신사 스탠다드",
    "price": 150000,
    "main_image_url": "https://s3.../501-main.jpg",
    "images": [
        "https://s3.../501-1.jpg",
        "https://s3.../501-2.jpg"
    ],
    "created_at": "2026-01-02T15:30:00Z"
}
```

### 6.6 권한 체계 (RBAC)

```python
# backend/app/core/permissions.py

from enum import Enum
from functools import wraps
from fastapi import HTTPException, Depends
from app.core.auth import get_current_user
from app.models import User

class Role(Enum):
    ADMIN = "admin"
    USER = "user"

class Permission(Enum):
    # 상품 관리
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    
    # 주문 관리
    ORDER_MANAGE = "order:manage"
    
    # 사용자 관리
    USER_MANAGE = "user:manage"
    
    # 대시보드 접근
    DASHBOARD_VIEW = "dashboard:view"
    CHATBOT_ANALYTICS = "chatbot:analytics"

# 역할별 권한 매핑
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,
        Permission.ORDER_MANAGE,
        Permission.USER_MANAGE,
        Permission.DASHBOARD_VIEW,
        Permission.CHATBOT_ANALYTICS,
    ],
    Role.USER: []  # 일반 사용자는 특별 권한 없음
}

def require_permission(permission: Permission):
    """권한 체크 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(Role(current_user.role), [])
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "PERMISSION_DENIED",
                        "message": f"{permission.value} 권한이 필요합니다"
                    }
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 사용 예시
from app.core.permissions import require_permission, Permission

@router.post("/products")
@require_permission(Permission.PRODUCT_CREATE)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    # 상품 생성 로직
    pass
```

---

## 6. 성능 요구사항

### 6.1 응답 시간

|항목|목표|최대|
|---|---|---|
|Intent 분류|100ms|300ms|
|상품 검색|200ms|500ms|
|GPT-4 응답|2초|5초|
|전체 응답|3초|7초|

### 6.2 처리량

- 동시 사용자: 1,000명
- 일일 대화: 50,000건
- 초당 메시지: 50 TPS

### 6.3 가용성

- 서비스 가동률: 99.9% (월 43분 다운타임 허용)
- 데이터베이스 백업: 일 1회 + 실시간 복제
- 장애 복구 시간(RTO): 1시간
- 데이터 복구 지점(RPO): 15분

---

## 7. 보안 및 개인정보

### 7.1 인증/인가

```python
# JWT 기반 인증
{
    "user_id": 123,
    "session_id": "uuid",
    "exp": 1704067200,  # 만료 시간
    "iat": 1704063600,  # 발급 시간
    "scopes": ["chat", "profile"]
}

# API 요청 헤더
Authorization: Bearer <JWT_TOKEN>
```

### 7.2 데이터 암호화

- 전송 중: TLS 1.3
- 저장 시: AES-256 (민감 정보)
- 비밀번호: bcrypt (cost factor 12)

### 7.3 개인정보 처리

|데이터|보존기간|암호화|비고|
|---|---|---|---|
|대화 내용|1년|X|익명화 후 학습 데이터 활용 가능|
|추천 이력|1년|X|-|
|결제 정보|5년|O|법적 의무|
|로그|3개월|X|-|

---

## 8. 모니터링 및 로깅

### 8.1 주요 메트릭

```python
# Application Metrics
- chat.message.count (Counter)
- chat.response.time (Histogram)
- chat.intent.distribution (Gauge)
- recommendation.click_rate (Gauge)
- recommendation.purchase_rate (Gauge)
- filter_bubble.diversity_score (Gauge)

# System Metrics
- api.request.count
- api.response.time
- db.query.time
- db.connection.pool
- redis.hit_rate
- gpt4.api.latency
- gpt4.api.token_usage
```

### 8.2 로깅 전략

```python
# 구조화된 로그 (JSON)
{
    "timestamp": "2026-01-02T10:30:00.123Z",
    "level": "INFO",
    "service": "chat-api",
    "trace_id": "abc-123-def",
    "user_id": 123,
    "event": "message_processed",
    "data": {
        "intent": "가격·가성비",
        "response_time_ms": 2345,
        "recommendation_count": 5
    }
}
```

### 8.3 알림 규칙

|조건|심각도|액션|
|---|---|---|
|응답 시간 > 7초 (5분 지속)|WARNING|Slack 알림|
|에러율 > 5% (1분 지속)|CRITICAL|PagerDuty + Slack|
|GPT-4 API 장애|CRITICAL|즉시 대응|
|DB 연결 실패|CRITICAL|자동 재시작 + 알림|

---

## 9. AWS 배포 전략 (Docker 기반)

### 9.1 로컬 개발 환경 (Docker Compose)

#### docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - fashion-ai-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/fashion_ai_dev
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    networks:
      - fashion-ai-network
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fashion_ai_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    networks:
      - fashion-ai-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - fashion-ai-network

  # DBeaver 연결용 - 로컬 DB에 직접 접근
  # Host: localhost, Port: 5432

volumes:
  postgres_data:

networks:
  fashion-ai-network:
    driver: bridge
```

#### 로컬 실행 방법

```bash
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
EOF

# 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend

# 중지
docker-compose down

# 전체 삭제 (볼륨 포함)
docker-compose down -v
```

### 9.2 AWS 인프라 구성

#### 9.2.1 VPC 및 네트워크 설정

```
VPC: 10.0.0.0/16

Public Subnets (ALB용):
- ap-northeast-2a: 10.0.1.0/24
- ap-northeast-2c: 10.0.2.0/24

Private Subnets (ECS Tasks용):
- ap-northeast-2a: 10.0.11.0/24
- ap-northeast-2c: 10.0.12.0/24

Database Subnets:
- ap-northeast-2a: 10.0.21.0/24
- ap-northeast-2c: 10.0.22.0/24

NAT Gateway:
- ap-northeast-2a (Primary)
- ap-northeast-2c (Backup)
```

#### 9.2.2 보안 그룹 설정

```
ALB Security Group:
- Inbound: 443 (HTTPS) from 0.0.0.0/0
- Inbound: 80 (HTTP) from 0.0.0.0/0 → 443 리다이렉트
- Outbound: All

ECS Tasks Security Group:
- Inbound: 8000 from ALB Security Group
- Inbound: 3000 from ALB Security Group
- Outbound: All

RDS Security Group:
- Inbound: 5432 from ECS Tasks Security Group
- Inbound: 5432 from Bastion Security Group (DBeaver 접근용)
- Outbound: None

ElastiCache Security Group:
- Inbound: 6379 from ECS Tasks Security Group
- Outbound: None

Bastion Security Group (DBeaver 접근용):
- Inbound: 22 from [Your IP]
- Outbound: 5432 to RDS Security Group
```

### 9.3 CI/CD 파이프라인 (GitHub Actions)

#### .github/workflows/deploy.yml

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: ap-northeast-2
  ECR_REGISTRY: 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com
  ECR_REPOSITORY_BACKEND: fashion-ai-backend
  ECR_REPOSITORY_FRONTEND: fashion-ai-frontend
  ECS_CLUSTER: fashion-ai-cluster
  ECS_SERVICE_BACKEND: fashion-ai-backend-service
  ECS_SERVICE_FRONTEND: fashion-ai-frontend-service

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      
      - name: Run linters
        run: |
          cd backend
          poetry run black --check .
          poetry run flake8 .
          poetry run mypy .
      
      - name: Run tests
        run: |
          cd backend
          poetry run pytest tests/ -v --cov

  build-and-push:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Backend image
        id: build-backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -f Dockerfile.prod -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG" >> $GITHUB_OUTPUT
      
      - name: Build and push Frontend image
        id: build-frontend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd frontend
          docker build -f Dockerfile.prod -t $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG" >> $GITHUB_OUTPUT

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy Backend to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE_BACKEND }} \
            --force-new-deployment
      
      - name: Deploy Frontend to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE_FRONTEND }} \
            --force-new-deployment
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE_BACKEND }} ${{ env.ECS_SERVICE_FRONTEND }}
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 9.4 ECS Task Definition

#### backend-task-definition.json

```json
{
  "family": "fashion-ai-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/fashion-ai-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:fashion-ai/db-url"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:fashion-ai/openai-key"
        },
        {
          "name": "REDIS_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:fashion-ai/redis-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fashion-ai-backend",
          "awslogs-region": "ap-northeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 9.5 Auto Scaling 설정

```bash
# ECS Service Auto Scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/fashion-ai-cluster/fashion-ai-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# CPU 기반 스케일링 정책
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/fashion-ai-cluster/fashion-ai-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### 9.6 배포 단계별 체크리스트

#### Phase 1: 인프라 구축 (Week 1)

```markdown
☐ AWS 계정 설정 및 IAM 사용자 생성
☐ VPC 및 서브넷 생성
☐ 보안 그룹 설정
☐ RDS PostgreSQL 인스턴스 생성 (Multi-AZ)
☐ ElastiCache Redis 클러스터 생성
☐ S3 버킷 생성 (정적 파일, 로그)
☐ ECR 리포지토리 생성 (backend, frontend)
☐ Secrets Manager에 민감 정보 저장
☐ CloudWatch 로그 그룹 생성
```

#### Phase 2: 컨테이너화 (Week 2)

```markdown
☐ Backend Dockerfile 작성
☐ Frontend Dockerfile 작성
☐ docker-compose.yml 작성 (로컬 개발)
☐ 로컬 환경에서 테스트
☐ 이미지 빌드 최적화 (멀티 스테이지)
☐ .dockerignore 설정
☐ 헬스체크 엔드포인트 구현 (/health)
```

#### Phase 3: ECS 설정 (Week 2)

```markdown
☐ ECS 클러스터 생성 (Fargate)
☐ Task Definition 작성
☐ ECS Service 생성
☐ Application Load Balancer 설정
☐ Target Group 설정
☐ Auto Scaling 설정
☐ CloudWatch Alarms 설정
```

#### Phase 4: CI/CD 구축 (Week 3)

```markdown
☐ GitHub Actions 워크플로우 작성
☐ AWS 자격증명 설정 (Secrets)
☐ ECR 푸시 자동화
☐ ECS 배포 자동화
☐ 테스트 자동화 (Lint, Unit Test)
☐ Slack 알림 연동
☐ 롤백 전략 수립
```

#### Phase 5: 모니터링 및 최적화 (Week 4)

```markdown
☐ CloudWatch 대시보드 구성
☐ 로그 수집 및 분석 설정
☐ 비용 모니터링 설정
☐ 성능 테스트 (부하 테스트)
☐ DBeaver로 RDS 연결 확인
☐ 백업 및 복구 테스트
☐ 문서화 완료
```

### 9.7 비용 최적화 전략

```
예상 월 비용 (초기):

1. ECS Fargate
   - Backend: 2 Tasks × 0.5 vCPU × 1GB = $30/월
   - Frontend: 2 Tasks × 0.25 vCPU × 0.5GB = $15/월

2. RDS PostgreSQL (db.t3.medium, Multi-AZ)
   - 인스턴스: $120/월
   - 스토리지 (100GB): $23/월

3. ElastiCache Redis (cache.t3.micro)
   - 인스턴스: $25/월

4. ALB
   - 시간당 요금: $20/월
   - LCU: $10/월

5. Data Transfer
   - CloudFront: $50/월
   - NAT Gateway: $45/월

6. 기타 (S3, CloudWatch 로그)
   - $20/월

총 예상 비용: ~$358/월

최적화 방안:
- Reserved Instances (RDS 1년 약정 시 30% 절감)
- Spot Instances (비프로덕션 환경)
- S3 Lifecycle 정책 (로그 자동 삭제)
- CloudWatch 로그 보존 기간 제한
```

### 9.8 재해 복구 (DR) 계획

```
RTO (Recovery Time Objective): 1시간
RPO (Recovery Point Objective): 15분

백업 전략:
1. RDS 자동 백업 (매일 03:00 KST)
2. RDS 스냅샷 (주간, 보존 기간 30일)
3. S3 버전 관리 활성화
4. ECS Task Definition 버전 관리

복구 절차:
1. RDS 스냅샷에서 복원 (30분)
2. ECS Service 재배포 (10분)
3. DNS 업데이트 (5분)
4. 헬스체크 및 검증 (15분)
```

---

## 10. 테스트 전략

### 10.1 테스트 피라미드

```
       ┌─────────┐
       │   E2E   │  10%
       │  Tests  │
    ┌──┴─────────┴──┐
    │  Integration  │  30%
    │     Tests     │
 ┌──┴───────────────┴──┐
 │    Unit Tests       │  60%
 └─────────────────────┘
```

### 10.2 주요 테스트 케이스

#### Unit Tests

```python
# test_intent_classifier.py
def test_price_value_intent():
    classifier = IntentClassifier()
    assert classifier.classify("10만 원대 자켓") == IntentType.PRICE_VALUE

def test_style_mood_intent():
    classifier = IntentClassifier()
    assert classifier.classify("미니멀한 셔츠") == IntentType.STYLE_MOOD

# test_filter_bubble_buster.py
def test_exclude_not_clicked_products():
    """클릭 안 한 상품 제외 테스트"""
    # ...

def test_brand_diversity():
    """브랜드 다양성 보장 테스트"""
    # ...
```

#### Integration Tests

```python
# test_recommendation_flow.py
@pytest.mark.asyncio
async def test_full_recommendation_flow():
    """전체 추천 플로우 통합 테스트"""
    # 1. 사용자 질문
    # 2. Intent 분류
    # 3. 상품 검색
    # 4. 필터버블 해소
    # 5. 프롬프트 생성
    # 6. GPT-4 호출
    # 7. 응답 검증
```

#### E2E Tests

```python
# test_chat_scenario.py
def test_multiple_turn_conversation():
    """다중 턴 대화 시나리오 테스트"""
    # 1. 첫 질문
    # 2. 추천 받기
    # 3. 피드백
    # 4. 후속 질문
    # 5. 재추천 방지 확인
```

---

## 11. 개발 일정

### 11.1 Phase 1: MVP 개발 및 로컬 환경 구축 (4주)

```
Week 1: 기반 구축
- DB 스키마 설계 및 구축
- Docker Compose 로컬 환경 세팅
- 기본 API 프레임워크 (FastAPI)
- Intent 분류 시스템 구현
- DBeaver 연결 및 기본 쿼리 작성

Week 2: 추천 엔진 개발
- 필터버블 해소 알고리즘 구현
- 상품 검색 로직 개발
- 프롬프트 생성기 구현
- PostgreSQL 인덱스 최적화
- 로컬 환경 통합 테스트

Week 3: GPT-4 통합
- OpenAI API 연동
- 프롬프트 최적화
- 응답 포맷팅 및 검증
- Redis 캐싱 적용
- 에러 핸들링 구현

Week 4: 로컬 테스트 및 문서화
- 통합 테스트 작성
- API 문서 작성 (Swagger)
- 성능 테스트 (로컬)
- Docker 이미지 최적화
- 코드 리뷰 및 리팩토링
```

### 11.2 Phase 2: AWS 배포 및 인프라 구축 (4주)

```
Week 5: AWS 인프라 설정
- AWS 계정 및 VPC 구성
- RDS PostgreSQL 생성 (Multi-AZ)
- ElastiCache Redis 클러스터 생성
- S3 버킷 및 CloudFront 설정
- Secrets Manager 설정
- DBeaver로 RDS 연결 확인

Week 6: 컨테이너화 및 ECR 설정
- Dockerfile.prod 작성 (멀티 스테이지)
- ECR 리포지토리 생성
- 이미지 빌드 및 푸시 자동화
- 헬스체크 엔드포인트 구현
- 로그 구조화 (JSON 포맷)

Week 7: ECS 배포 및 CI/CD
- ECS 클러스터 및 Task Definition 작성
- ALB 및 Target Group 설정
- GitHub Actions 워크플로우 구축
- Auto Scaling 설정
- CloudWatch Alarms 설정
- Staging 환경 배포

Week 8: Production 배포 및 검증
- Production 환경 배포
- DNS 설정 (Route 53)
- SSL 인증서 적용
- 부하 테스트 (1000 동시 사용자)
- 재해 복구 테스트
- 배포 문서 작성
```

### 11.3 Phase 3: 데이터 분석 및 고도화 (4주)

```
Week 9: DBeaver 기반 로그 분석
☐ 채팅 로그 분석 쿼리 작성
  - Intent 분포 분석
  - 추천 성과 분석 (CTR, 전환율)
  - 재추천 케이스 탐지
  - 응답 시간 분석
☐ 커스텀 대시보드 구성
☐ 주간/월간 리포트 자동화
☐ 데이터 시각화 (Python + Matplotlib)
☐ 문제 패턴 식별

Week 10: 알고리즘 개선
☐ Intent 분류 개선
  - 잘못 분류된 케이스 수집
  - 키워드 사전 업데이트
  - 분류 정확도 측정
☐ 필터버블 해소 비율 조정
  - A/B 테스트 설계 (70:30 vs 60:40)
  - 클릭률 비교 분석
☐ 추천 품질 향상
  - 저성과 상품 패턴 분석
  - 브랜드 다양성 규칙 강화
☐ 쿼리 최적화
  - 느린 쿼리 식별 (EXPLAIN ANALYZE)
  - 인덱스 추가
  - 쿼리 리팩토링

Week 11: A/B 테스트 및 사용자 피드백
☐ A/B 테스트 구현
  - 사용자 그룹 분할
  - 실험군 / 대조군 설정
  - 메트릭 수집
☐ A/B 테스트 실행 (7일)
☐ 결과 분석 (DBeaver 쿼리)
☐ 승자 알고리즘 선정
☐ 프로덕션 반영

Week 12: 고도화 및 문서화
☐ 협업 필터링 추가 검토
☐ 사용자 프로필 학습 강화
☐ 프롬프트 템플릿 최적화
☐ GPT-4 토큰 사용량 최적화
☐ 최종 성능 테스트
☐ 기술 문서 업데이트
☐ 운영 매뉴얼 작성
```

### 11.4 Phase 4: 운영 안정화 및 모니터링 강화 (4주)

```
Week 13-14: 모니터링 및 알림 체계 구축
☐ CloudWatch 대시보드 고도화
  - 비즈니스 메트릭 (CTR, 전환율)
  - 시스템 메트릭 (CPU, 메모리, 응답 시간)
  - 비용 메트릭
☐ PagerDuty 연동
☐ Slack 알림 세분화
☐ 주간 리포트 자동 생성
☐ SLA 정의 및 모니터링

Week 15-16: 비용 최적화 및 스케일링
☐ Reserved Instances 검토
☐ Spot Instances 활용 (개발/테스트 환경)
☐ S3 Lifecycle 정책 적용
☐ CloudWatch 로그 보존 기간 최적화
☐ 캐싱 전략 강화
☐ DB 커넥션 풀 튜닝
☐ 최종 비용 분석 리포트
```

### 11.5 마일스톤 및 성공 지표

|Week|마일스톤|성공 지표|
|---|---|---|
|4|MVP 완성 (로컬)|- 전체 API 엔드포인트 구현<br>- 테스트 커버리지 > 80%<br>- 응답 시간 < 3초|
|8|Production 배포|- 무중단 배포 성공<br>- 가용성 > 99%<br>- 실사용자 트래픽 처리|
|12|고도화 완료|- Intent 분류 정확도 > 90%<br>- CTR > 15%<br>- 전환율 > 3%|
|16|운영 안정화|- 월 비용 < $500<br>- 평균 응답 시간 < 2초<br>- 에러율 < 0.1%|

### 11.6 위험 요소 및 대응 계획

|위험|발생 가능성|영향도|대응 계획|
|---|---|---|---|
|GPT-4 API 비용 초과|높음|중|- 토큰 제한 설정<br>- 캐싱 강화<br>- 프롬프트 최적화|
|AWS 비용 초과|중|중|- 예산 알림 설정<br>- 리소스 모니터링<br>- Auto Scaling 조정|
|데이터베이스 성능 저하|중|높음|- Read Replica 추가<br>- 인덱스 최적화<br>- 쿼리 튜닝|
|추천 품질 저하|중|높음|- A/B 테스트<br>- 지속적 모니터링<br>- 빠른 롤백|
|일정 지연|중|중|- 주간 스프린트 리뷰<br>- 우선순위 조정<br>- MVP 범위 축소|

---

## 12. 위험 관리

### 12.1 기술적 위험

|위험|확률|영향도|대응 방안|
|---|---|---|---|
|GPT-4 API 장애|중|상|Fallback 응답 시스템 구축|
|응답 시간 초과|중|중|타임아웃 설정 + 사용자 피드백|
|DB 부하 증가|높음|중|Read Replica + 캐싱|
|Vector DB 성능|중|중|하이브리드 검색 (키워드+벡터)|

### 12.2 비즈니스 위험

|위험|확률|영향도|대응 방안|
|---|---|---|---|
|추천 품질 저하|중|상|A/B 테스트 + 지속적 모니터링|
|사용자 이탈|중|상|피드백 루프 + 빠른 개선|
|운영 비용 증가|높음|중|GPT-4 토큰 최적화|

---

## 13. 부록

### 13.1 환경 변수

#### 로컬 개발 환경 (.env)

```bash
# Application
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database (Docker Compose)
DATABASE_URL=postgresql://user:password@db:5432/fashion_ai_dev
DATABASE_POOL_SIZE=10

# Redis (Docker Compose)
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Vector DB
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=fashion-ai-dev

# Application Settings
API_RATE_LIMIT=100  # per minute
SESSION_TIMEOUT=3600  # seconds
```

#### Production 환경 (AWS Secrets Manager)

```bash
# 이 값들은 AWS Secrets Manager에 저장되며,
# ECS Task Definition에서 참조됩니다.

# Database (RDS)
DATABASE_URL=postgresql://admin:${SECRET}@fashion-ai-db.xxxxx.ap-northeast-2.rds.amazonaws.com:5432/fashion_ai_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (ElastiCache)
REDIS_URL=redis://fashion-ai-redis.xxxxx.cache.amazonaws.com:6379/0
REDIS_MAX_CONNECTIONS=50

# OpenAI
OPENAI_API_KEY=sk-prod-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30

# Vector DB
PINECONE_API_KEY=prod-pinecone-key
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=fashion-ai-prod

# AWS
AWS_REGION=ap-northeast-2
AWS_S3_BUCKET=fashion-ai-assets
AWS_CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net

# Application
ENV=production
DEBUG=false
LOG_LEVEL=INFO
API_RATE_LIMIT=1000  # per minute
SESSION_TIMEOUT=7200  # seconds

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
CLOUDWATCH_LOG_GROUP=/ecs/fashion-ai-backend
```

### 13.2 Docker 관련 명령어 모음

```bash
# 로컬 개발 환경 시작
docker-compose up -d

# 특정 서비스만 재시작
docker-compose restart backend

# 로그 실시간 확인
docker-compose logs -f backend

# 컨테이너 내부 접속
docker-compose exec backend bash
docker-compose exec db psql -U user -d fashion_ai_dev

# 이미지 빌드 (캐시 무시)
docker-compose build --no-cache backend

# 볼륨 포함 전체 삭제
docker-compose down -v

# Production 이미지 빌드 및 테스트
docker build -f backend/Dockerfile.prod -t fashion-ai-backend:test backend/
docker run -p 8000:8000 --env-file .env.prod fashion-ai-backend:test

# ECR 푸시
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag fashion-ai-backend:latest 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/fashion-ai-backend:latest
docker push 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/fashion-ai-backend:latest

# 이미지 용량 확인
docker images | grep fashion-ai

# 불필요한 이미지/컨테이너 정리
docker system prune -a
```

### 13.3 AWS CLI 명령어 모음

```bash
# ECS 서비스 상태 확인
aws ecs describe-services \
  --cluster fashion-ai-cluster \
  --services fashion-ai-backend-service

# ECS 태스크 목록 조회
aws ecs list-tasks \
  --cluster fashion-ai-cluster \
  --service-name fashion-ai-backend-service

# CloudWatch 로그 실시간 조회
aws logs tail /ecs/fashion-ai-backend --follow

# RDS 스냅샷 생성
aws rds create-db-snapshot \
  --db-instance-identifier fashion-ai-db \
  --db-snapshot-identifier fashion-ai-manual-snapshot-$(date +%Y%m%d-%H%M%S)

# Secrets Manager 시크릿 조회
aws secretsmanager get-secret-value \
  --secret-id fashion-ai/db-url \
  --query SecretString \
  --output text

# S3 버킷 동기화
aws s3 sync ./logs/ s3://fashion-ai-logs/$(date +%Y%m%d)/

# CloudWatch 메트릭 조회
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=fashion-ai-backend-service \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### 13.4 DBeaver 유용한 설정

```
1. 자동 커밋 비활성화
   Window > Preferences > Database > Transactions
   ☐ Auto-commit by default

2. SQL 포맷터 설정
   Window > Preferences > Database > SQL Editor > Formatting
   - Keyword case: UPPER
   - Identifier case: lower
   - Indent size: 4

3. 쿼리 결과 최대 행 수 설정
   Window > Preferences > Database > Data Editor
   Max rows: 1000 (기본값 200에서 변경)

4. 단축키 설정
   Ctrl+Enter: Execute SQL Statement
   Ctrl+Shift+Enter: Execute SQL Script
   F5: Refresh
   Ctrl+Alt+Shift+X: Format SQL

5. 데이터 내보내기 기본값
   Database > Data Transfer
   Format: CSV
   Delimiter: ,
   Encoding: UTF-8
   Include column headers: Yes
```

### 13.5 유용한 SQL 스니펫 (DBeaver에 저장)

```sql
-- 1. 테이블 크기 확인
SELECT 
    schemaname AS schema,
    tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. 인덱스 사용률 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 3. 느린 쿼리 찾기 (pg_stat_statements 필요)
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- 4. 활성 세션 확인
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- 5. 데이터베이스 통계
SELECT 
    datname,
    numbackends AS connections,
    xact_commit AS commits,
    xact_rollback AS rollbacks,
    blks_read AS disk_reads,
    blks_hit AS cache_hits,
    tup_returned AS rows_returned,
    tup_fetched AS rows_fetched,
    tup_inserted AS rows_inserted,
    tup_updated AS rows_updated,
    tup_deleted AS rows_deleted
FROM pg_stat_database
WHERE datname = 'fashion_ai_prod';
```

### 13.6 참고 문서

#### 공식 문서

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Docker Documentation](https://docs.docker.com/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [DBeaver Documentation](https://dbeaver.com/docs/)

#### AWS 참고 자료

- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [RDS PostgreSQL Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [ElastiCache Redis Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

#### 개발 도구

- [Poetry Documentation](https://python-poetry.org/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Sentry Documentation](https://docs.sentry.io/)

#### 블로그 및 튜토리얼

- [Deploying FastAPI on AWS ECS](https://www.google.com/search?q=fastapi+ecs+deployment)
- [Docker Multi-Stage Builds Best Practices](https://docs.docker.com/develop/develop-images/multistage-build/)
- [PostgreSQL Indexing Strategies](https://www.postgresql.org/docs/current/indexes.html)

### 13.7 프로젝트 구조

```
fashion-ai-recommendation/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       ├── test.yml
│       └── lint.yml
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py
│   │   │   │   ├── feedback.py
│   │   │   │   └── products.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── product.py
│   │   │   └── recommendation.py
│   │   ├── services/
│   │   │   ├── intent_classifier.py
│   │   │   ├── filter_bubble_buster.py
│   │   │   ├── prompt_builder.py
│   │   │   └── llm_service.py
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   ├── product.py
│   │   │   └── recommendation.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── migrations/
│   ├── scripts/
│   │   ├── analyze_logs.py
│   │   └── seed_data.py
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   ├── pyproject.toml
│   └── poetry.lock
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   ├── nginx.conf
│   └── package.json
│
├── infrastructure/
│   ├── terraform/
│   │   ├── vpc.tf
│   │   ├── ecs.tf
│   │   ├── rds.tf
│   │   ├── elasticache.tf
│   │   └── outputs.tf
│   └── cloudformation/
│
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── deployment/
│   │   ├── aws-setup.md
│   │   └── docker-guide.md
│   ├── dbeaver/
│   │   └── query-collection.md
│   └── diagrams/
│
├── scripts/
│   ├── setup-local.sh
│   ├── deploy-prod.sh
│   └── backup-db.sh
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

---

**문서 버전**: 1.2  
**최종 수정일**: 2026-01-02  
**작성자**: 현결 (IT-Goblin)

## v1.2 핵심 변경사항 요약

### 1. 시스템 구조 변경

- **AS-IS (v1.1)**: 독립형 AI 챗봇 서비스
- **TO-BE (v1.2)**: 쇼핑몰 웹사이트 + 임베디드 챗봇 위젯 통합

### 2. 주요 추가 사항

#### 2.1 쇼핑몰 기능

- 상품 목록/상세/검색
- 장바구니 및 주문/결제
- 카테고리 기반 브라우징
- 찜 기능

#### 2.2 사용자 인증 시스템

- JWT 기반 인증 (Access Token + Refresh Token)
- 역할 기반 접근 제어 (Admin / User)
- 회원가입 / 로그인 / 로그아웃

#### 2.3 권한별 기능 차등화

**관리자 (Admin):**

- 상품 CRUD 관리
- 사용자 관리 (권한 변경, 계정 활성화)
- 주문 관리 (상태 변경)
- 챗봇 분석 대시보드 (DBeaver 연동)
- 전체 통계 및 매출 분석

**일반 사용자 (User):**

- 쇼핑몰 브라우징 및 구매
- 챗봇을 통한 상품 추천
- 마이페이지 (주문 내역, 찜 목록)

#### 2.4 챗봇 위젯 구현

- 우측 하단 플로팅 아이콘
- 400px × 600px 크기
- Slide up/down 애니메이션
- 추천 상품 클릭 시 쇼핑몰 상품 페이지 연동

#### 2.5 더미 데이터 구축

- 더미 상품 100개 자동 생성
- 카테고리 및 서브카테고리
- 더미 사용자 50명
- 관리자 계정 1개
- 브랜드, 스타일 태그, 이미지 URL

### 3. 데이터베이스 변경

**신규 테이블:**

- `categories`: 상품 카테고리
- `orders`: 주문
- `order_items`: 주문 상품
- `carts`: 장바구니
- `cart_items`: 장바구니 상품
- `wishlists`: 찜 목록

**수정 테이블:**

- `users`: role, password_hash, is_active 추가
- `products`: category_id, original_price, discount_rate, images[] 추가

### 4. API 엔드포인트 추가

- 인증 API (5개)
- 상품 API (4개)
- 장바구니 API (4개)
- 주문 API (3개)
- 찜 API (3개)
- 관리자 API (10개)

### 5. 프론트엔드 구조 변경

```
기존 (v1.1):
- frontend/ (React 단일 앱)

변경 (v1.2):
- shop-frontend/ (Next.js 쇼핑몰)
- chatbot-widget/ (React 챗봇 위젯)
```

### 6. 개발 일정 영향

- Week 1-2: 쇼핑몰 기본 기능 구현 추가
- Week 2-3: 인증 시스템 구현
- Week 3-4: 챗봇 위젯 임베디드
- Week 4: 관리자 대시보드 기본 기능

### 7. 차기 버전 계획 (v1.3)

- 소셜 로그인 (Google, Kakao)
- 실시간 채팅 (WebSocket)
- 상품 리뷰 시스템
- 이미지 검색 기능
- 모바일 앱 (React Native)

---

## 프로젝트 구조 (v1.2)

```
fashion-ai-shop/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       ├── test.yml
│       └── lint.yml
│
├── shop-frontend/              # 쇼핑몰 웹사이트 (Next.js)
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── products/
│   │   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   ├── cart/
│   │   │   ├── orders/
│   │   │   └── admin/
│   │   │       ├── dashboard/
│   │   │       ├── products/
│   │   │       └── users/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── product/
│   │   │   ├── cart/
│   │   │   └── chatbot-trigger/  # 챗봇 아이콘
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── styles/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── chatbot-widget/             # 챗봇 위젯 (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow/
│   │   │   ├── MessageList/
│   │   │   ├── InputBox/
│   │   │   └── ProductCard/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py         # 인증
│   │   │   │   ├── products.py     # 상품
│   │   │   │   ├── cart.py         # 장바구니
│   │   │   │   ├── orders.py       # 주문
│   │   │   │   ├── chat.py         # 챗봇
│   │   │   │   └── admin.py        # 관리자
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── auth.py             # JWT 인증
│   │   │   ├── permissions.py       # 권한 관리
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── cart.py
│   │   │   └── conversation.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       ├── product_service.py
│   │       └── chatbot_service.py
│   ├── scripts/
│   │   ├── seed_data.py            # 더미 데이터 생성
│   │   └── create_admin.py         # 관리자 계정 생성
│   └── Dockerfile
│
├── docs/
│   ├── api/
│   │   ├── authentication.md
│   │   ├── products.md
│   │   └── admin.md
│   ├── deployment/
│   └── user-guide/
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## 빠른 시작 가이드

### 1. 로컬 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-org/fashion-ai-shop.git
cd fashion-ai-shop

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (OPENAI_API_KEY 등)

# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 더미 데이터 생성
docker-compose exec backend python scripts/seed_data.py

# 관리자 계정 생성
docker-compose exec backend python scripts/create_admin.py
```

### 2. 접속 정보

```
쇼핑몰: http://localhost:3000
관리자 대시보드: http://localhost:3000/admin
API 문서: http://localhost:8000/docs

관리자 계정:
- Email: admin@fashion-ai.com
- Password: admin123!

일반 사용자 (더미):
- Email: user001@example.com
- Password: password123
```

### 3. 챗봇 테스트

1. 쇼핑몰 접속
2. 우측 하단 챗봇 아이콘 클릭
3. "10만 원대 자켓 추천해줘" 입력
4. AI 추천 확인 및 상품 클릭

---

**다음 단계**:

- [AWS 배포 가이드](https://claude.ai/chat/docs/deployment/aws-setup.md)
- [API 문서](http://localhost:8000/docs)
- [DBeaver 분석 쿼리](https://claude.ai/chat/docs/dbeaver/query-collection.md)