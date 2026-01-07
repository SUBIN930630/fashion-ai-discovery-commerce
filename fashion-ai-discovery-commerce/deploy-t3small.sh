#!/bin/bash

# T3.small 배포 스크립트
# AWS EC2에서 실행하는 배포 자동화 스크립트

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 Fashion AI Discovery Commerce - T3.small 배포 시작"

# 1. Docker 및 Docker Compose 확인
echo "📦 Docker 및 Docker Compose 확인 중..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "다음 명령으로 설치하세요:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 2. 환경 변수 파일 확인
echo "🔍 환경 변수 파일 확인 중..."
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env 파일이 없습니다."
    echo "backend/.env.example을 복사하여 .env 파일을 생성하세요."
    exit 1
fi

# 3. Frontend 빌드 확인
echo "🔨 Frontend 빌드 확인 중..."
if [ ! -d "frontend/build" ]; then
    echo "⚠️  Frontend가 빌드되지 않았습니다. 빌드 중..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 4. Nginx 설정 파일 확인
echo "⚙️  Nginx 설정 파일 확인 중..."
if [ ! -f "nginx/nginx.conf" ]; then
    echo "❌ nginx/nginx.conf 파일이 없습니다."
    exit 1
fi

if [ ! -d "nginx/conf.d" ]; then
    echo "❌ nginx/conf.d 디렉토리가 없습니다."
    exit 1
fi

# 5. 로그 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p logs
mkdir -p backend/fashion_ai.db.dir 2>/dev/null || true

# 6. 기존 컨테이너 중지 및 제거 (선택사항)
read -p "기존 컨테이너를 중지하고 제거하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 기존 컨테이너 중지 중..."
    docker-compose -f docker-compose.t3small.yml down || true
fi

# 7. Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.t3small.yml build --no-cache

# 8. 서비스 시작
echo "🚀 서비스 시작 중..."
docker-compose -f docker-compose.t3small.yml up -d

# 9. 서비스 상태 확인
echo "⏳ 서비스 시작 대기 중 (30초)..."
sleep 30

# 10. 상태 확인
echo "📊 서비스 상태 확인 중..."
docker-compose -f docker-compose.t3small.yml ps

# 11. 로그 확인 (선택사항)
read -p "최근 로그를 확인하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.t3small.yml logs --tail=50
fi

# 12. 메모리 사용량 확인
echo "💾 메모리 사용량 확인:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 13. Health check
echo "🏥 Health check 수행 중..."
sleep 5  # 추가 대기 시간

# curl 또는 wget 사용 가능 여부 확인
if command -v curl &> /dev/null; then
    HEALTH_CHECK_CMD="curl -f http://localhost/health"
    IP_CHECK_CMD="curl -s http://169.254.169.254/latest/meta-data/public-ipv4"
elif command -v wget &> /dev/null; then
    HEALTH_CHECK_CMD="wget -q -O- http://localhost/health"
    IP_CHECK_CMD="wget -q -O- http://169.254.169.254/latest/meta-data/public-ipv4"
else
    HEALTH_CHECK_CMD=""
    IP_CHECK_CMD=""
fi

if [ -n "$HEALTH_CHECK_CMD" ]; then
    if $HEALTH_CHECK_CMD > /dev/null 2>&1; then
        echo "✅ 배포 성공! 서비스가 정상적으로 실행 중입니다."
        if [ -n "$IP_CHECK_CMD" ]; then
            SERVER_IP=$($IP_CHECK_CMD 2>/dev/null || echo "your-server-ip")
            echo "🌐 접속 URL: http://${SERVER_IP}"
        fi
    else
        echo "⚠️  Health check 실패. 로그를 확인하세요:"
        echo "   docker-compose -f docker-compose.t3small.yml logs"
    fi
else
    echo "⚠️  curl 또는 wget이 없어 Health check를 수행할 수 없습니다."
    echo "   수동으로 확인하세요: docker-compose -f docker-compose.t3small.yml ps"
fi

echo ""
echo "📚 유용한 명령어:"
echo "   로그 확인: docker-compose -f docker-compose.t3small.yml logs -f"
echo "   서비스 중지: docker-compose -f docker-compose.t3small.yml down"
echo "   서비스 재시작: docker-compose -f docker-compose.t3small.yml restart"
echo "   메모리 사용량: docker stats"

