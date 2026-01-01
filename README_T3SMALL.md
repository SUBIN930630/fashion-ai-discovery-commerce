# T3.small 배포 빠른 시작 가이드

## 📋 요약

이 프로젝트는 **AWS EC2 T3.small 인스턴스 (2GB RAM)**에서 실행 가능하도록 최적화되어 있습니다.

## ✅ 배포 가능성

**가능합니다!** 최적화된 구성을 사용하면 충분히 운영 가능합니다.

### 예상 메모리 사용량
- Backend: ~200MB
- SQLite: ~50MB
- Redis: ~50MB
- Nginx: ~30MB
- 시스템: ~350MB
- **총합: ~680MB / 여유: ~1.3GB**

## 🚀 빠른 배포 (5분)

### 1. EC2 인스턴스 준비

```bash
# Ubuntu 22.04 LTS AMI 사용
# 보안 그룹: SSH (22), HTTP (80), HTTPS (443)
```

### 2. 필수 패키지 설치

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 프로젝트 클론

```bash
git clone <your-repo-url> fashion-ai
cd fashion-ai
```

### 4. 환경 변수 설정

```bash
# backend/.env 파일 생성
cd backend
cat > .env << EOF
# API 설정
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# 보안
SECRET_KEY=$(openssl rand -hex 32)

# 데이터베이스 (SQLite)
DATABASE_URL=sqlite:///./fashion_ai.db

# Redis
REDIS_URL=redis://redis:6379

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072

# CORS
ALLOWED_HOSTS=["*"]
EOF
cd ..
```

### 5. Frontend 빌드

```bash
cd frontend
npm install
npm run build
cd ..
```

### 6. 배포 실행

```bash
# 배포 스크립트 실행 (권장)
chmod +x deploy-t3small.sh
./deploy-t3small.sh

# 또는 수동 실행
docker-compose -f docker-compose.t3small.yml up -d --build
```

### 7. 확인

```bash
# 서비스 상태
docker-compose -f docker-compose.t3small.yml ps

# 로그 확인
docker-compose -f docker-compose.t3small.yml logs -f

# Health check
curl http://localhost/health

# 메모리 사용량
docker stats
```

## 📁 주요 파일

- `docker-compose.t3small.yml` - T3.small 최적화된 Docker Compose 설정
- `nginx/nginx.conf` - Nginx 메인 설정
- `nginx/conf.d/default.conf` - Nginx 가상 호스트 설정
- `deploy-t3small.sh` - 자동 배포 스크립트
- `Document/T3.small_배포_가이드.md` - 상세 배포 가이드

## ⚠️ 중요 사항

### 메모리 최적화
- SQLite 사용 (PostgreSQL 대신)
- Redis 메모리 제한: 80MB
- 각 서비스별 메모리 제한 설정

### 제한사항
- 동시 접속자: 50-100명 권장
- CPU 버스트 성능 주의 (T3 인스턴스 특성)

### 모니터링

```bash
# 실시간 모니터링
docker stats

# 시스템 리소스
htop

# 서비스 로그
docker-compose -f docker-compose.t3small.yml logs -f backend
```

## 🔧 문제 해결

### 메모리 부족 시

```bash
# 스왑 메모리 추가 (1GB)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 서비스 재시작

```bash
docker-compose -f docker-compose.t3small.yml restart
```

### 전체 재배포

```bash
docker-compose -f docker-compose.t3small.yml down
docker-compose -f docker-compose.t3small.yml up -d --build
```

## 📚 상세 문서

자세한 내용은 `Document/T3.small_배포_가이드.md`를 참고하세요.

---

**작성일**: 2024년  
**버전**: 1.0

