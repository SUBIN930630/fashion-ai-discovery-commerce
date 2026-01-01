# ✅ 환경 변수 설정 완료

## 📋 완료된 작업

1. ✅ `.env.example` 파일 생성 - 환경 변수 템플릿
2. ✅ `.env` 파일 확인 - 실제 환경 변수 파일
3. ✅ `setup-env.sh` 스크립트 생성 - 자동 설정 스크립트

## 🔍 현재 상태 확인

`.env` 파일이 이미 존재합니다. 다음 명령어로 주요 설정을 확인하세요:

```bash
cd backend
cat .env | grep -E "(SECRET_KEY|OPENAI_API_KEY|DATABASE_URL|REDIS_URL|DEBUG)"
```

## ⚠️ 필수 설정 항목 확인

다음 항목들이 올바르게 설정되어 있는지 확인하세요:

### 1. SECRET_KEY (보안 키)
```bash
# 확인 방법
grep SECRET_KEY backend/.env

# 올바른 형식: 64자리 16진수 문자열
# 예: d9ae98a5af570797a63f58b34dde6d5498462e30c9ca5660a9b781aea30cc7d5
```

**⚠️ 중요**: SECRET_KEY가 기본값(`dev-secret-key-change...` 또는 `CHANGE-THIS...`)으로 되어 있다면 반드시 변경하세요!

```bash
# 새로운 SECRET_KEY 생성
openssl rand -hex 32

# .env 파일에 업데이트 (macOS)
sed -i '' 's|SECRET_KEY=.*|SECRET_KEY=새로생성된키|' backend/.env

# .env 파일에 업데이트 (Linux)
sed -i 's|SECRET_KEY=.*|SECRET_KEY=새로생성된키|' backend/.env
```

### 2. OPENAI_API_KEY (OpenAI API 키)
```bash
# 확인 방법
grep OPENAI_API_KEY backend/.env
```

**⚠️ 중요**: 실제 OpenAI API 키로 변경해야 합니다!
- 기본값: `sk-your-openai-api-key-here` (작동하지 않음)
- 실제 OpenAI API 키로 변경 필요

### 3. DATABASE_URL (데이터베이스)
```bash
# 확인 방법
grep DATABASE_URL backend/.env
```

**T3.small 최적화 설정:**
```
DATABASE_URL=sqlite:///./fashion_ai.db
```

### 4. REDIS_URL (Redis)
```bash
# 확인 방법
grep REDIS_URL backend/.env
```

**Docker Compose 사용 시:**
```
REDIS_URL=redis://redis:6379
```

## 🔧 설정 업데이트 방법

### 방법 1: setup-env.sh 스크립트 사용 (권장)

```bash
cd backend
./setup-env.sh
```

이 스크립트는:
- `.env.example`이 없으면 생성
- `.env` 파일이 없으면 `.env.example`에서 복사
- SECRET_KEY가 기본값이면 자동 생성

### 방법 2: 수동 설정

```bash
cd backend

# .env.example이 있으면 복사
cp .env.example .env

# SECRET_KEY 생성 및 업데이트
SECRET_KEY=$(openssl rand -hex 32)
# macOS
sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
# Linux
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env

# .env 파일 편집 (OPENAI_API_KEY 등 수정)
nano .env  # 또는 vi, vim, code 등
```

## 📝 .env 파일 예시 (T3.small 최적화)

```env
# 애플리케이션 설정
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# 보안 설정
SECRET_KEY=d9ae98a5af570797a63f58b34dde6d5498462e30c9ca5660a9b781aea30cc7d5
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 데이터베이스 (SQLite - T3.small 최적화)
DATABASE_URL=sqlite:///./fashion_ai.db

# Redis (Docker Compose용)
REDIS_URL=redis://redis:6379
REDIS_SESSION_TTL=3600

# OpenAI API (반드시 실제 키로 변경!)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072

# CORS
ALLOWED_HOSTS=["*"]

# 로깅
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## ✅ 다음 단계

환경 변수 설정이 완료되었으므로 다음 단계로 진행하세요:

1. ✅ **환경 변수 설정 완료** (현재 단계)
2. ⏭️ **Frontend 빌드** (`npm run build`)
3. ⏭️ **배포 실행** (`./deploy-t3small.sh` 또는 `docker-compose -f docker-compose.t3small.yml up -d --build`)

## 🔒 보안 주의사항

1. **절대 `.env` 파일을 Git에 커밋하지 마세요!**
   - `.gitignore`에 `.env`가 포함되어 있는지 확인
   
2. **SECRET_KEY는 강력한 랜덤 문자열이어야 합니다**
   - 최소 32자 이상
   - `openssl rand -hex 32`로 생성 권장

3. **OPENAI_API_KEY는 실제 유효한 키여야 합니다**
   - OpenAI 계정에서 API 키 생성
   - 키가 노출되지 않도록 주의

4. **프로덕션 환경에서는 ALLOWED_HOSTS를 제한하세요**
   - 현재: `ALLOWED_HOSTS=["*"]` (모두 허용)
   - 권장: `ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]`

## 📚 관련 파일

- `backend/.env` - 실제 환경 변수 파일 (Git에 포함되지 않음)
- `backend/.env.example` - 환경 변수 템플릿 (Git에 포함됨)
- `backend/setup-env.sh` - 자동 설정 스크립트
- `Document/T3.small_배포_가이드.md` - 상세 배포 가이드

---

**작성일**: 2024년  
**버전**: 1.0

