# AWS EC2 T3.small 배포 가이드

## 📋 배포 전 준비사항

### 필수 준비물
- ✅ AWS 계정
- ✅ EC2 인스턴스 (T3.small 권장)
- ✅ 프로젝트 코드 (GitHub 저장소 또는 로컬)
- ✅ OpenAI API 키
- ✅ 도메인 (선택사항, IP로도 접속 가능)

---

## 🚀 단계별 배포 가이드

### 1단계: EC2 인스턴스 생성

#### 1-1. EC2 인스턴스 시작

1. **AWS 콘솔 접속**
   - https://console.aws.amazon.com 접속
   - EC2 서비스 선택

2. **인스턴스 시작**
   - "인스턴스 시작" 클릭
   - 이름: `fashion-ai-commerce` (원하는 이름)

3. **AMI 선택**
   - **Ubuntu 22.04 LTS** 권장 (가장 안정적)
   - 또는 Amazon Linux 2023

4. **인스턴스 유형**
   - **t3.small** 선택
   - vCPU: 2, RAM: 2GB

5. **키 페어 생성/선택**
   - 새 키 페어 생성 또는 기존 키 사용
   - 키 페어 이름: `fashion-ai-key` (예시)
   - 키 페어 유형: RSA
   - 프라이빗 키 파일 형식: `.pem`
   - **⚠️ 중요**: 키 파일을 안전한 곳에 저장! (다운로드)

6. **네트워크 설정**
   - 보안 그룹: 새 보안 그룹 생성
   - 인바운드 규칙 추가:
     ```
     SSH (22): 내 IP 또는 0.0.0.0/0 (임시)
     HTTP (80): 0.0.0.0/0
     HTTPS (443): 0.0.0.0/0 (SSL 인증서 적용 시)
     ```

7. **스토리지**
   - 기본 8GB (gp3) 또는 20GB 권장
   - T3.small에는 충분함

8. **인스턴스 시작**
   - "인스턴스 시작" 클릭

#### 1-2. Elastic IP 할당 (선택사항, 권장)

**Elastic IP란?**
- 인스턴스의 공인 IP를 고정 IP로 만드는 기능
- 인스턴스를 중지/재시작해도 IP 주소가 변경되지 않음
- DNS 설정이나 방화벽 규칙 관리에 유용

**AWS 콘솔에서 Elastic IP 할당하기:**

1. **AWS 콘솔 접속**
   - https://console.aws.amazon.com 접속
   - 상단 검색창에서 "EC2" 검색 후 선택

2. **Elastic IP 메뉴로 이동**
   - 왼쪽 사이드바에서 **"네트워크 및 보안"** 클릭
   - 하위 메뉴에서 **"탄력적 IP"** 클릭
   - (영문 콘솔: "Network & Security" → "Elastic IPs")

3. **Elastic IP 주소 할당**
   - 오른쪽 상단의 **"탄력적 IP 주소 할당"** 버튼 클릭
   - (영문: "Allocate Elastic IP address")
   - 네트워크 경계 그룹: 기본값 유지 (자동)
   - 퍼블릭 IPv4 주소 풀: "Amazon의 IPv4 주소 풀" 선택 (기본값)
   - **"재연결"** 섹션:
     - ✅ **"이 탄력적 IP 주소를 재연결하도록 허용"** 체크 (권장)
     - 이 옵션을 체크하면 향후 다른 인스턴스로 Elastic IP를 재연결할 수 있어 유연성이 높아집니다
   - 하단의 **"할당"** 버튼 클릭

4. **Elastic IP를 인스턴스에 연결**
   - 할당된 Elastic IP를 클릭하여 선택
   - 상단의 **"작업"** 드롭다운 메뉴 클릭
   - **"탄력적 IP 주소 연결"** 선택
   - (영문: "Actions" → "Associate Elastic IP address")
   - **인스턴스**: 드롭다운에서 생성한 인스턴스 선택
   - **프라이빗 IP 주소**: 기본값 유지 (자동 선택)
   - **연결** 버튼 클릭

5. **연결 확인**
   - EC2 콘솔 → 인스턴스 페이지로 이동
   - 인스턴스를 선택하면 상세 정보에서 "퍼블릭 IPv4 주소"가 Elastic IP로 변경된 것을 확인 가능

**참고사항:**
- Elastic IP는 인스턴스에 연결되어 있으면 무료
- 인스턴스에 연결되지 않은 Elastic IP는 시간당 비용 발생
- 인스턴스를 종료하면 Elastic IP 연결이 해제되므로 주의

**이유**: 인스턴스 재시작 시 IP가 변경되지 않도록 고정 (도메인 연결, 방화벽 설정 등에 유용)

---

### 2단계: EC2 인스턴스 접속 및 초기 설정

#### 2-1. SSH 접속

**macOS/Linux:**
```bash
# 키 파일 권한 설정 (처음 한 번만)
# 키 파일이 ~/.ssh/aws-keys/ 디렉토리에 있는 경우:
chmod 400 ~/.ssh/aws-keys/fashion-ai-key.pem
# 또는 실제 키 파일 이름으로 변경:
# chmod 400 ~/.ssh/aws-keys/<실제-키-파일명>.pem

# SSH 접속
ssh -i ~/.ssh/aws-keys/fashion-ai-key.pem ubuntu@<EC2-PUBLIC-IP>
# 또는 실제 키 파일 이름으로:
# ssh -i ~/.ssh/aws-keys/<실제-키-파일명>.pem ubuntu@<EC2-PUBLIC-IP>

# 예시:
# ssh -i ~/.ssh/aws-keys/fashion-ai-key.pem ubuntu@3.34.123.45
```

**Windows (PowerShell):**
```powershell
# SSH 접속 (키 파일 경로를 실제 위치로 변경)
ssh -i C:\Users\YourName\.ssh\aws-keys\fashion-ai-key.pem ubuntu@<EC2-PUBLIC-IP>
```

**접속 성공 확인:**
```bash
# 터미널 프롬프트가 다음과 같이 변경됨:
ubuntu@ip-172-31-xx-xx:~$
```

#### 2-2. 시스템 업데이트

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y curl wget git vim htop
```

**⚠️ 시스템 업데이트 중 나타나는 메시지:**

1. **커널 업데이트 메시지 ("Newer kernel available"):**
   - 지금 당장 재시작할 필요 없음 (배포 완료 후 재시작 가능)
   - 재시작 없이 계속 진행해도 기능상 문제 없음
   - 재시작하려면: `sudo reboot` (배포 완료 후 권장)

2. **데몬 재시작 선택 메시지 ("Daemons using outdated libraries"):**
   - **7번 (none of the above)** 선택 권장
   - 배포 과정에서는 데몬을 지금 재시작할 필요 없음
   - 시스템 재시작 시 자동으로 새 라이브러리 사용
   - 키보드로 **7** 입력 후 **Enter**

#### 2-3. Docker 설치

```bash
# Docker 설치 스크립트 다운로드 및 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 그룹 변경사항 적용 (재로그인 또는)
newgrp docker

# Docker 설치 확인
docker --version
# 예상 출력: Docker version 24.x.x 이상
```

#### 2-4. Docker Compose 설치

```bash
# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 실행 권한 부여
sudo chmod +x /usr/local/bin/docker-compose

# Docker Compose 설치 확인
docker-compose --version
# 예상 출력: Docker Compose version v2.x.x
```

#### 2-5. 스왑 메모리 설정 (권장)

T3.small의 2GB RAM에 여유를 주기 위해 스왑 메모리를 추가합니다.

```bash
# 1GB 스왑 파일 생성
sudo fallocate -l 1G /swapfile

# 권한 설정
sudo chmod 600 /swapfile

# 스왑 파일 포맷
sudo mkswap /swapfile

# 스왑 활성화
sudo swapon /swapfile

# 영구적으로 활성화 (재부팅 후에도 유지)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 스왑 확인
free -h
# Swap 행에 1G가 표시되어야 함
```

---

### 3단계: 프로젝트 코드 배포

#### 3-1. 프로젝트 클론 또는 업로드

**방법 1: Git 저장소에서 클론 (권장)**

```bash
# 홈 디렉토리로 이동
cd ~

# Git 저장소 클론
git clone <your-repository-url>
cd fashion-ai-discovery-commerce

# 예시:
# git clone https://github.com/your-username/fashion-ai-discovery-commerce.git
# cd fashion-ai-discovery-commerce
```

**방법 2: 로컬에서 SCP로 업로드**

```bash
# 로컬 터미널에서 실행 (EC2가 아닌 로컬 컴퓨터)
cd ~/Documents/GitHub/fashion-ai-discovery-commerce

# 프로젝트 압축 (선택사항)
tar -czf fashion-ai.tar.gz --exclude='node_modules' --exclude='venv' --exclude='.git' .

# SCP로 업로드 (키 파일 경로를 실제 위치로 변경)
scp -i ~/.ssh/aws-keys/fashion-ai-key.pem fashion-ai.tar.gz ubuntu@<EC2-PUBLIC-IP>:~/

# EC2에서 압축 해제
ssh -i ~/.ssh/aws-keys/fashion-ai-key.pem ubuntu@<EC2-PUBLIC-IP>
cd ~
tar -xzf fashion-ai.tar.gz
cd fashion-ai-discovery-commerce
```

#### 3-2. 환경 변수 설정

```bash
# backend 디렉토리로 이동
cd backend

# .env 파일 생성
nano .env
# 또는
vim .env
```

**.env 파일 내용 (복사하여 붙여넣기):**

```env
# ============================================
# 애플리케이션 설정
# ============================================
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# ============================================
# 보안 설정
# ============================================
SECRET_KEY=<openssl rand -hex 32로 생성한 키>
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
OPENAI_API_KEY=<실제 OpenAI API 키>
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
```

**SECRET_KEY 생성:**
```bash
# SECRET_KEY 생성
openssl rand -hex 32

# 생성된 키를 .env 파일의 SECRET_KEY에 입력
```

**파일 저장:**
- nano: `Ctrl + X`, `Y`, `Enter`
- vim: `Esc`, `:wq`, `Enter`

#### 3-3. Frontend 빌드 (로컬에서 실행)

**⚠️ 중요**: Frontend는 로컬에서 빌드한 후 업로드하는 것이 더 빠릅니다.

**로컬 컴퓨터에서:**
```bash
cd frontend
npm install
npm run build
```

**빌드 파일 업로드:**
```bash
# 로컬 터미널에서 (키 파일 경로를 실제 위치로 변경)
scp -i ~/.ssh/aws-keys/fashion-ai-key.pem -r frontend/build ubuntu@<EC2-PUBLIC-IP>:~/fashion-ai-discovery-commerce/frontend/
```

**또는 EC2에서 직접 빌드:**
```bash
# EC2에서 Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Frontend 빌드
cd ~/fashion-ai-discovery-commerce/frontend
npm install
npm run build
```

---

### 4단계: 배포 실행

#### 4-1. 프로젝트 디렉토리 확인

```bash
# 프로젝트 루트로 이동
cd ~/fashion-ai-discovery-commerce

# 필수 파일 확인
ls -la docker-compose.t3small.yml
ls -la nginx/nginx.conf
ls -la frontend/build
```

#### 4-2. Docker Compose로 배포

```bash
# 프로젝트 루트에서
cd ~/fashion-ai-discovery-commerce

# Docker 이미지 빌드 및 서비스 시작
docker-compose -f docker-compose.t3small.yml up -d --build

# 서비스 상태 확인
docker-compose -f docker-compose.t3small.yml ps

# 로그 확인
docker-compose -f docker-compose.t3small.yml logs -f
```

#### 4-3. 배포 확인

```bash
# Health check
curl http://localhost/health

# 예상 응답: {"status":"healthy"}

# 서비스 상태 확인
docker-compose -f docker-compose.t3small.yml ps

# 메모리 사용량 확인
docker stats --no-stream
```

---

### 5단계: 접속 확인

#### 5-1. 브라우저에서 접속

1. **EC2 Public IP 확인**
   ```bash
   # EC2 콘솔에서 확인하거나
   curl http://169.254.169.254/latest/meta-data/public-ipv4
   ```

2. **브라우저에서 접속**
   - Frontend: `http://<EC2-PUBLIC-IP>`
   - Health Check: `http://<EC2-PUBLIC-IP>/health`
   - API: `http://<EC2-PUBLIC-IP>/api/v1/`

#### 5-2. 문제 해결

**접속이 안 될 때:**

1. **보안 그룹 확인**
   - EC2 콘솔 → 인스턴스 → 보안 그룹
   - 인바운드 규칙에 HTTP (80) 포트가 열려있는지 확인

2. **서비스 상태 확인**
   ```bash
   docker-compose -f docker-compose.t3small.yml ps
   ```

3. **로그 확인**
   ```bash
   docker-compose -f docker-compose.t3small.yml logs
   ```

---

## 🔧 유용한 명령어

### 서비스 관리

```bash
# 서비스 시작
docker-compose -f docker-compose.t3small.yml up -d

# 서비스 중지
docker-compose -f docker-compose.t3small.yml down

# 서비스 재시작
docker-compose -f docker-compose.t3small.yml restart

# 특정 서비스만 재시작
docker-compose -f docker-compose.t3small.yml restart backend
```

### 로그 확인

```bash
# 모든 서비스 로그 (실시간)
docker-compose -f docker-compose.t3small.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.t3small.yml logs -f backend
docker-compose -f docker-compose.t3small.yml logs -f nginx

# 최근 100줄만
docker-compose -f docker-compose.t3small.yml logs --tail=100
```

### 모니터링

```bash
# 메모리 사용량 (실시간)
docker stats

# 시스템 리소스
htop

# 디스크 사용량
df -h
```

### 업데이트 및 재배포

```bash
# 코드 업데이트 후 재배포
cd ~/fashion-ai-discovery-commerce
git pull  # 또는 새 코드 업로드
docker-compose -f docker-compose.t3small.yml up -d --build

# Frontend만 재빌드
cd frontend
npm run build
cd ..
docker-compose -f docker-compose.t3small.yml restart nginx
```

---

## 🔒 보안 권장사항

### 1. SSH 키 보안

```bash
# SSH 키 파일 권한 확인 (키 파일 경로를 실제 위치로 변경)
chmod 400 ~/.ssh/aws-keys/fashion-ai-key.pem

# 키 파일을 안전한 곳에 백업 (이미 ~/.ssh/aws-keys/에 있으므로 백업 완료)
```

### 2. 보안 그룹 최적화

- SSH (22): 본인 IP만 허용 (0.0.0.0/0 제거)
- HTTP (80): 0.0.0.0/0 (필요시)
- HTTPS (443): 0.0.0.0/0 (SSL 인증서 적용 시)

### 3. 환경 변수 보안

- `.env` 파일은 절대 Git에 커밋하지 않기
- SECRET_KEY는 강력한 랜덤 문자열 사용
- OpenAI API 키 노출 주의

### 4. 방화벽 설정 (선택사항)

```bash
# UFW 방화벽 활성화
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 모니터링

### CloudWatch 설정

1. **EC2 콘솔 → 모니터링**
2. **CloudWatch 알람 생성**
   - CPU 사용률 80% 이상
   - 메모리 사용률 90% 이상
   - 디스크 사용률 80% 이상

### 로그 모니터링

```bash
# 애플리케이션 로그 확인
tail -f backend/logs/app.log

# Docker 로그 확인
docker-compose -f docker-compose.t3small.yml logs -f
```

---

## 🔄 자동 재시작 설정 (선택사항)

### systemd 서비스 생성

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/fashion-ai.service
```

**파일 내용:**
```ini
[Unit]
Description=Fashion AI Discovery Commerce
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/fashion-ai-discovery-commerce
ExecStart=/usr/local/bin/docker-compose -f docker-compose.t3small.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.t3small.yml down
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
```

**서비스 활성화:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fashion-ai.service
sudo systemctl start fashion-ai.service
```

---

## 💰 비용 최적화

### T3.small 예상 비용 (서울 리전 기준)

- 인스턴스: 약 $0.02/시간 (~$15/월)
- Elastic IP: 무료 (인스턴스에 연결된 경우)
- 데이터 전송: 1GB 무료, 이후 $0.09/GB

**월 예상 비용: 약 $15-20**

### 비용 절감 팁

1. **불필요한 인스턴스 중지**
2. **스냅샷 후 인스턴스 종료** (개발 중단 시)
3. **Reserved Instance 사용** (장기 운영 시)

---

## 🆘 문제 해결

### 메모리 부족

```bash
# 스왑 메모리 확인
free -h

# 스왑이 없으면 추가 (위의 2-5 단계 참고)
```

### 디스크 공간 부족

```bash
# 디스크 사용량 확인
df -h

# Docker 이미지 정리
docker system prune -a

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

### 서비스가 시작되지 않음

```bash
# 로그 확인
docker-compose -f docker-compose.t3small.yml logs

# 컨테이너 상태 확인
docker ps -a

# 재시작
docker-compose -f docker-compose.t3small.yml restart
```

---

## 📚 추가 자료

- [T3.small 배포 가이드](./Document/T3.small_배포_가이드.md)
- [README_T3SMALL.md](./README_T3SMALL.md)
- [AWS EC2 문서](https://docs.aws.amazon.com/ec2/)

---

**작성일**: 2024년  
**버전**: 1.0

