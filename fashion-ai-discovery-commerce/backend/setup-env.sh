#!/bin/bash

# .env 파일 자동 설정 스크립트
# T3.small 배포용 환경 변수 파일 생성

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 .env 파일 설정 시작..."

# .env.example이 있으면 복사, 없으면 생성
if [ ! -f .env.example ]; then
    echo "📝 .env.example 파일 생성 중..."
    cat > .env.example << 'EOF'
# ============================================
# Fashion AI Discovery Commerce - 환경 변수 예제
# ============================================
# 사용법: cp .env.example .env 후 실제 값으로 변경하세요

# ============================================
# 애플리케이션 설정
# ============================================
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# ============================================
# 보안 설정
# ============================================
SECRET_KEY=dev-secret-key-change-in-production-please-generate-random-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# 데이터베이스 설정 (SQLite - T3.small 최적화)
# ============================================
DATABASE_URL=sqlite:///./fashion_ai.db

# ============================================
# Redis 설정 (Docker Compose용)
# ============================================
REDIS_URL=redis://redis:6379
REDIS_SESSION_TTL=3600

# ============================================
# OpenAI API 설정
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072

# ============================================
# CORS 설정
# ============================================
ALLOWED_HOSTS=["*"]

# ============================================
# 로깅 설정
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ============================================
# MMR 알고리즘 설정
# ============================================
MMR_LAMBDA=0.7
EXPLORATION_RATIO=0.7
EXPLOITATION_RATIO=0.3

# ============================================
# 추천 시스템 설정
# ============================================
MAX_RECOMMENDATIONS=10
MIN_SIMILARITY_THRESHOLD=0.3
MAX_SIMILARITY_THRESHOLD=0.9
RECENT_HISTORY_LIMIT=5

# ============================================
# 의도 분석 설정
# ============================================
INTENT_CONFIDENCE_THRESHOLD=0.8
MAX_FOLLOW_UP_QUESTIONS=2

# ============================================
# 응답 생성 설정
# ============================================
RESPONSE_TEMPLATE_PATH=ml/response_generator/templates
MAX_RESPONSE_LENGTH=1000
USE_EMOJIS=True

# ============================================
# 성능 설정
# ============================================
CACHE_TTL=3600
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30

# ============================================
# 모니터링 설정
# ============================================
ENABLE_METRICS=True
METRICS_PORT=9090

# ============================================
# 기능 플래그
# ============================================
ENABLE_IMAGE_SEARCH=False
ENABLE_VOICE_INTERFACE=False
ENABLE_MULTIMODAL=False
ENABLE_AB_TESTING=True
EOF
fi

# .env 파일이 없으면 .env.example에서 복사
if [ ! -f .env ]; then
    echo "📋 .env.example을 .env로 복사 중..."
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다."
else
    echo "ℹ️  .env 파일이 이미 존재합니다."
    read -p "기존 .env 파일을 덮어쓰시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env 파일이 덮어쓰기되었습니다."
    else
        echo "⏭️  기존 .env 파일을 유지합니다."
    fi
fi

# SECRET_KEY 생성
if [ -f .env ]; then
    if grep -q "SECRET_KEY=dev-secret-key-change" .env || grep -q "SECRET_KEY=CHANGE-THIS" .env; then
        echo "🔑 SECRET_KEY 생성 중..."
        if command -v openssl &> /dev/null; then
            NEW_SECRET_KEY=$(openssl rand -hex 32)
            # macOS와 Linux 호환
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
            else
                sed -i "s|SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
            fi
            echo "✅ SECRET_KEY가 자동으로 생성되었습니다."
        else
            echo "⚠️  openssl이 없어 SECRET_KEY를 자동 생성할 수 없습니다."
            echo "   수동으로 openssl rand -hex 32 명령어로 생성하세요."
        fi
    else
        echo "ℹ️  SECRET_KEY가 이미 설정되어 있습니다."
    fi
fi

echo ""
echo "📝 다음 단계:"
echo "   1. .env 파일을 열어 OPENAI_API_KEY를 실제 값으로 변경하세요"
echo "   2. 필요시 다른 설정값들을 조정하세요"
echo "   3. 파일 확인: cat .env | grep -E '(SECRET_KEY|OPENAI_API_KEY|DATABASE_URL|REDIS_URL)'"
echo ""
echo "✅ 환경 변수 설정 완료!"

