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

### 1. 환경 설정 (최초 1회만)

#### 저장소 클론 및 환경 변수 설정
```bash
# 저장소 클론
git clone <repository-url>
cd fashion-ai-discovery-commerce

# 백엔드 환경 변수 설정
cd backend
cp .env  # .env.example이 없다면 직접 생성

# .env 파일을 열어서 OpenAI API Key 설정
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 가상환경 설정 및 의존성 설치 (최초 1회만)

**백엔드 가상환경 설정:**
```bash
# 프로젝트 루트에서 시작
cd fashion-ai-discovery-commerce

# 가상환경 생성 (아직 없다면)
# 가상환경은 프로젝트 루트에 생성됩니다
python3 -m venv venv

# 가상환경 활성화 (프로젝트 루트에서 실행)
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 가상환경이 활성화되면 터미널 프롬프트 앞에 (venv)가 표시됩니다
# 예: (venv) matthew_studio@Matthew-MacStudio fashion-ai-discovery-commerce %

# 의존성 설치 (가상환경 활성화 상태에서)
cd backend
pip install -r requirements.txt
```

**프론트엔드 의존성 설치:**
```bash
# 프로젝트 루트에서
cd frontend

# 의존성 설치
npm install
```

---

### 2. 프로그램 실행 (매일 또는 재시작 시)

프로그램을 껐다 켰을 때는 **의존성 설치 없이 바로 실행**하면 됩니다.

#### 방법 1: 로컬 환경에서 실행 (개발용)

**백엔드 실행:**
```bash
# ⚠️ 중요: 가상환경은 프로젝트 루트에 있습니다!

# 현재 디렉토리 확인 (선택사항)
pwd  # 현재 위치 확인

# 방법 1: 프로젝트 루트에서 가상환경 활성화 후 백엔드로 이동 (권장)
# 프로젝트 루트로 이동 (필요한 경우)
cd ~/Documents/GitHub/fashion-ai-discovery-commerce
# 또는 상대 경로로: cd /Users/matthew_studio/Documents/GitHub/fashion-ai-discovery-commerce

source venv/bin/activate  # 가상환경 활성화 (macOS/Linux)
# 또는 Windows: venv\Scripts\activate

# 가상환경 활성화 확인: 터미널 프롬프트 앞에 (venv)가 보여야 합니다
# 예: (venv) matthew_studio@Matthew-MacStudio fashion-ai-discovery-commerce %

cd backend  # 백엔드 디렉토리로 이동
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: 백엔드 디렉토리에서 상대 경로로 활성화
# 이미 backend 디렉토리에 있다면:
source ../venv/bin/activate  # 상위 디렉토리의 venv 활성화
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드가 정상적으로 실행되면:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**프론트엔드 실행 (새 터미널 창에서):**
```bash
# 프로젝트 루트에서
cd frontend

# 프론트엔드 개발 서버 실행 (포트: 3000)
npm start
```

프론트엔드가 정상적으로 실행되면:
- 웹 애플리케이션: http://localhost:3000
- 브라우저가 자동으로 열립니다

**실행 순서:**
1. 포트 충돌 확인 및 해결 (필요한 경우)
   ```bash
   # 포트 8000이 사용 중이면 종료
   lsof -ti :8000 | xargs kill -9
   ```
2. 가상환경 활성화 및 백엔드 실행 (포트 8000)
3. 새 터미널에서 프론트엔드 실행 (포트 3000)
4. 두 서버가 모두 실행되면 브라우저에서 http://localhost:3000 접속

**빠른 참조 (한 줄 요약):**
```bash
# 백엔드 실행
cd ~/Documents/GitHub/fashion-ai-discovery-commerce && source venv/bin/activate && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 포트 충돌 해결
lsof -ti :8000 | xargs kill -9
```

#### 방법 2: Docker로 실행 (권장, 프로덕션 환경)

```bash
# 프로젝트 루트에서
docker-compose up -d

# 실행 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 서비스 중지 및 볼륨 삭제 (데이터 초기화)
docker-compose down -v
```

Docker로 실행 시 접속 주소:
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

### 3. 실행 확인 및 문제 해결

#### 백엔드 실행 확인
```bash
# 터미널에서 확인
curl http://localhost:8000/health

# 또는 브라우저에서 접속
# http://localhost:8000/health
```

정상 응답 예시:
```json
{"status": "healthy"}
```

#### 프론트엔드 실행 확인
- 브라우저에서 http://localhost:3000 접속
- 페이지가 정상적으로 로드되는지 확인

#### 자주 발생하는 문제

**문제 1: "command not found: uvicorn" 오류**
```bash
# 원인: 가상환경이 활성화되지 않음

# 해결 방법:
# 가상환경은 프로젝트 루트에 있습니다!
cd fashion-ai-discovery-commerce  # 프로젝트 루트로 이동
source venv/bin/activate  # macOS/Linux
# 또는 Windows: venv\Scripts\activate

# 가상환경 활성화 확인
which uvicorn  # 경로가 venv 안에 있어야 함
# 예: /Users/.../fashion-ai-discovery-commerce/venv/bin/uvicorn

# 가상환경이 없다면 생성 (프로젝트 루트에서)
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

**문제 1-1: "no such file or directory: venv/bin/activate" 오류**
```bash
# 원인: 가상환경이 프로젝트 루트에 있는데 백엔드 디렉토리에서 활성화 시도

# 해결 방법 1: 프로젝트 루트에서 활성화 (권장)
cd fashion-ai-discovery-commerce  # 프로젝트 루트로 이동
source venv/bin/activate
cd backend

# 해결 방법 2: 백엔드 디렉토리에서 상대 경로로 활성화
cd fashion-ai-discovery-commerce/backend
source ../venv/bin/activate  # 상위 디렉토리의 venv 활성화

# 가상환경 위치 확인
ls -la ../venv/bin/activate  # 파일이 존재하는지 확인
```

**문제 2: 포트가 이미 사용 중입니다 (Address already in use)**
```bash
# 포트 8000이 이미 사용 중인 경우 해결 방법

# 1단계: 포트를 사용 중인 프로세스 확인
lsof -i :8000  # 백엔드 포트 확인
# 출력 예시:
# COMMAND   PID           USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# Python  12345  matthew_studio   5u  IPv4  ...      0t0  TCP *:8000 (LISTEN)

# 2단계: 프로세스 종료
# 방법 A: PID 번호를 직접 사용
kill -9 <PID>  # 위에서 확인한 PID 번호 입력
# 예: kill -9 12345

# 방법 B: 한 번에 종료 (권장)
lsof -ti :8000 | xargs kill -9

# 방법 C: uvicorn 프로세스 모두 종료
pkill -f uvicorn

# 3단계: 포트가 해제되었는지 확인
lsof -i :8000  # 아무것도 출력되지 않으면 성공

# 4단계: 다시 서버 실행
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 참고: 프론트엔드 포트(3000)도 같은 방법으로 해결 가능
lsof -ti :3000 | xargs kill -9
```

**문제 2: 백엔드가 프론트엔드 요청을 받지 못함**
- `backend/app/core/config.py`의 `ALLOWED_HOSTS`에 `"*"` 또는 `"http://localhost:3000"` 포함 확인
- CORS 설정 확인

**문제 3: 환경 변수가 적용되지 않음**
- `.env` 파일이 `backend/` 디렉토리에 있는지 확인
- `.env` 파일의 변수명이 정확한지 확인 (대소문자 구분)
- 서버 재시작 필요

**문제 4: 데이터베이스 연결 오류**
- SQLite 사용 시: `backend/fashion_ai.db` 파일 존재 확인
- PostgreSQL 사용 시: 데이터베이스 서버 실행 상태 확인

**문제 5: 챗봇이 상품을 찾지 못함 ("현재 조건에 맞는 상품을 찾지 못했어요")**
```bash
# 원인: 데이터베이스에 상품 데이터가 없거나 임베딩이 생성되지 않음

# 해결 방법 1: 관리자 API로 상품 초기화 (권장)
curl -X POST http://localhost:8000/api/v1/admin/products/init

# 또는 브라우저에서 접속
# http://localhost:8000/api/v1/admin/products/init (POST 요청)

# 해결 방법 2: Python 스크립트로 직접 실행
cd backend
source ../venv/bin/activate  # 가상환경 활성화
python scripts/init_products.py

# 성공 시 응답 예시:
# {
#   "message": "상품 데이터 초기화 완료",
#   "total_products": 200,
#   "indexed_products": 200,
#   "success": true
# }

# 확인: 데이터베이스에 상품이 있는지 확인
# SQLite의 경우:
sqlite3 backend/fashion_ai.db "SELECT COUNT(*) FROM products WHERE embedding IS NOT NULL;"
```

---

### 4. 개발 팁

#### 백엔드 개발 모드
```bash
# 자동 리로드 활성화 (코드 변경 시 자동 재시작)
uvicorn app.main:app --reload

# 특정 포트로 실행
uvicorn app.main:app --reload --port 8001
```

#### 프론트엔드 개발 모드
```bash
# 개발 서버 실행 (기본적으로 자동 리로드)
npm start

# 특정 포트로 실행
PORT=3001 npm start
```

#### 로그 확인

**백엔드 로그 확인:**
```bash
# 방법 1: 애플리케이션 로그 파일 확인
tail -f backend/logs/app.log

# 방법 2: 실시간 로그 확인 (최근 50줄)
tail -50 backend/logs/app.log

# 방법 3: 특정 키워드 검색
grep -i "error" backend/logs/app.log
grep -i "warning" backend/logs/app.log
grep -i "chat" backend/logs/app.log

# 방법 4: 백엔드 서버를 백그라운드로 실행한 경우
# 서버 실행 시 로그 파일로 리다이렉트한 경우:
tail -f /tmp/backend_server.log

# 방법 5: uvicorn 콘솔 로그 (서버 실행 중인 터미널에서 직접 확인)
# 서버를 포그라운드로 실행하면 실시간 로그가 표시됨
```

**프론트엔드 로그 확인:**
```bash
# React 개발 서버는 브라우저 콘솔에서 확인
# Chrome/Edge: F12 → Console 탭
# Firefox: F12 → 콘솔 탭

# 또는 터미널에서 확인 (npm start 실행 중인 터미널)
# React 개발 서버의 로그가 실시간으로 표시됨
```

**Docker 로그 확인:**
```bash
# 모든 서비스 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis

# 최근 100줄만 확인
docker-compose logs --tail=100 backend

# 특정 시간 이후 로그만 확인
docker-compose logs --since 10m backend  # 최근 10분
docker-compose logs --since 2024-01-02T10:00:00 backend  # 특정 시간 이후
```

**로그 레벨별 확인:**
```bash
# 에러만 확인
grep -i "ERROR" backend/logs/app.log | tail -20

# 경고만 확인
grep -i "WARNING" backend/logs/app.log | tail -20

# 정보 로그 확인
grep -i "INFO" backend/logs/app.log | tail -20

# 디버그 로그 확인 (DEBUG 레벨이 활성화된 경우)
grep -i "DEBUG" backend/logs/app.log | tail -20
```

**챗봇 관련 로그 확인:**
```bash
# 챗봇 메시지 처리 로그
grep "chat" backend/logs/app.log | tail -20

# 상품 검색 로그
grep "search" backend/logs/app.log | tail -20

# 추천 생성 로그
grep "recommendation" backend/logs/app.log | tail -20

# 의도 분석 로그
grep "intent" backend/logs/app.log | tail -20
```

**로그 파일 위치:**
- 백엔드 애플리케이션 로그: `backend/logs/app.log`
- 백그라운드 실행 시: `/tmp/backend_server.log` (또는 지정한 경로)
- Docker 로그: `docker-compose logs` 명령어로 확인

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