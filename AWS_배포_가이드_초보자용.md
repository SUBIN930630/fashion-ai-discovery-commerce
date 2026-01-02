# 🎯 AWS EC2 배포 가이드 - 초보자 완전 정복편

> **이 가이드는 처음 배포하는 분도 쉽게 따라할 수 있도록 만들었습니다!**  
> 각 단계마다 "왜 이렇게 하는지" 설명하고, 실수하기 쉬운 부분을 강조했습니다.

---

## 📚 목차

1. [배포 전 준비사항](#1-배포-전-준비사항-체크리스트)
2. [1단계: EC2 서버 접속하기](#1단계-ec2-서버-접속하기)
3. [2단계: 서버에 필요한 도구 설치하기](#2단계-서버에-필요한-도구-설치하기)
4. [3단계: 프로젝트 코드 가져오기](#3단계-프로젝트-코드-가져오기)
5. [4단계: 환경 변수 설정하기](#4단계-환경-변수-설정하기)
6. [5단계: Frontend 빌드하기](#5단계-frontend-빌드하기)
7. [6단계: 배포 실행하기](#6단계-배포-실행하기)
8. [7단계: 접속 확인하기](#7단계-접속-확인하기)
9. [문제 해결 가이드](#문제-해결-가이드)

---

## 1. 배포 전 준비사항 체크리스트

### ✅ 필수 준비물 (반드시 준비해야 할 것들)

배포를 시작하기 전에 아래 항목들이 모두 준비되어 있는지 확인하세요!

| 항목 | 설명 | 확인 방법 |
|------|------|----------|
| **AWS 계정** | AWS에 로그인할 수 있는 계정 | AWS 콘솔 접속 가능한지 확인 |
| **EC2 인스턴스** | 이미 생성되어 있어야 함 | AWS 콘솔 → EC2 → 인스턴스 목록 확인 |
| **EC2 Public IP** | 서버의 주소 (예: 3.34.123.45) | EC2 인스턴스 상세 정보에서 확인 |
| **SSH 키 파일 (.pem)** | 서버에 접속하기 위한 열쇠 | 로컬 컴퓨터에 저장되어 있는지 확인 |
| **OpenAI API 키** | AI 기능을 사용하기 위한 키 | OpenAI 계정에서 발급받은 키 |
| **프로젝트 코드** | 배포할 코드 (로컬 또는 GitHub) | 로컬에 있거나 GitHub 저장소 URL |

### 💡 비유로 이해하기

- **EC2 인스턴스**: 인터넷에 있는 우리만의 컴퓨터 (서버)
- **Public IP**: 서버의 주소 (집 주소 같은 것)
- **SSH 키 파일**: 서버 문을 여는 열쇠
- **OpenAI API 키**: AI 기능을 사용하기 위한 열쇠

---

## 1단계: EC2 서버 접속하기

### 🎯 이 단계에서 하는 일

**목표**: 로컬 컴퓨터에서 AWS 서버로 접속하기

**왜 필요한가요?**
- 집에서 멀리 있는 서버를 조작하려면 먼저 접속해야 합니다
- SSH는 서버에 안전하게 접속하는 방법입니다

### 📝 단계별 가이드

#### 1-1. SSH 키 파일 위치 확인

**macOS/Linux 사용자:**

```bash
# 키 파일이 보통 ~/.ssh/ 디렉토리에 있습니다
ls -la ~/.ssh/

# 또는 aws-keys 디렉토리에 있을 수 있습니다
ls -la ~/.ssh/aws-keys/
```

**Windows 사용자:**
- 보통 `C:\Users\YourName\.ssh\` 또는 `C:\Users\YourName\.ssh\aws-keys\` 에 있습니다
- 파일 탐색기에서 확인하세요

#### 1-2. 키 파일 권한 설정 (macOS/Linux만)

**왜 필요한가요?**
- SSH는 보안상 키 파일의 권한이 너무 열려있으면 접속을 거부합니다
- 마치 "열쇠를 누구나 볼 수 있게 두면 안 된다"는 것과 같습니다

```bash
# 키 파일 경로를 실제 위치로 변경하세요
chmod 400 ~/.ssh/aws-keys/fashion-ai-key.pem

# 예시:
# chmod 400 ~/.ssh/aws-keys/my-key.pem
```

**확인 방법:**
```bash
# 권한이 제대로 설정되었는지 확인
ls -l ~/.ssh/aws-keys/fashion-ai-key.pem

# 예상 출력: -r-------- (읽기 전용)
```

#### 1-3. EC2 Public IP 확인

**AWS 콘솔에서 확인:**
1. AWS 콘솔 접속: https://console.aws.amazon.com
2. EC2 서비스 선택
3. 인스턴스 목록에서 생성한 인스턴스 클릭
4. "퍼블릭 IPv4 주소" 또는 "Public IPv4 address" 확인
   - 예: `3.34.123.45`

**또는 터미널에서 확인 (이미 접속된 경우):**
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

#### 1-4. SSH 접속 실행

**macOS/Linux:**

```bash
# 기본 형식
ssh -i <키-파일-경로> ubuntu@<EC2-PUBLIC-IP>

# 실제 예시 (키 파일 경로와 IP를 실제 값으로 변경!)
ssh -i ~/.ssh/aws-keys/fashion-ai-key.pem ubuntu@3.34.123.45
```

**Windows (PowerShell):**

```powershell
# 기본 형식
ssh -i <키-파일-경로> ubuntu@<EC2-PUBLIC-IP>

# 실제 예시
ssh -i C:\Users\YourName\.ssh\aws-keys\fashion-ai-key.pem ubuntu@3.34.123.45
```

**⚠️ 주의사항:**
- 키 파일 경로에 공백이 있으면 따옴표로 감싸세요: `"C:\Users\My Name\.ssh\key.pem"`
- Windows에서 경로는 백슬래시(`\`) 또는 슬래시(`/`) 둘 다 사용 가능합니다

#### 1-5. 접속 성공 확인

**성공하면 다음과 같이 표시됩니다:**

```bash
# 접속 전 (로컬 컴퓨터)
yourname@yourcomputer:~/Documents$

# 접속 후 (EC2 서버)
ubuntu@ip-172-31-xx-xx:~$
```

**확인 포인트:**
- ✅ 프롬프트가 `ubuntu@ip-...`로 변경됨
- ✅ "Welcome to Ubuntu" 같은 메시지가 보임
- ✅ 에러 메시지가 없음

**❌ 접속 실패 시:**
- 키 파일 경로가 맞는지 확인
- EC2 Public IP가 맞는지 확인
- 보안 그룹에서 SSH (22번 포트)가 열려있는지 확인

---

## 2단계: 서버에 필요한 도구 설치하기

### 🎯 이 단계에서 하는 일

**목표**: 서버에 Docker와 Docker Compose 설치하기

**왜 필요한가요?**
- Docker는 애플리케이션을 쉽게 실행할 수 있게 해주는 도구입니다
- 마치 "레고 블록처럼 프로그램을 조립해서 실행"하는 것과 같습니다
- Docker Compose는 여러 프로그램을 한 번에 관리하는 도구입니다

### 📝 단계별 가이드

#### 2-1. 시스템 업데이트

**왜 필요한가요?**
- 서버를 처음 만들면 오래된 프로그램들이 설치되어 있을 수 있습니다
- 최신 보안 패치와 버그 수정을 받기 위해 업데이트합니다

```bash
# 시스템 업데이트 (시간이 조금 걸릴 수 있습니다)
sudo apt update && sudo apt upgrade -y
```

**⏱️ 예상 소요 시간:** 5-10분

**⚠️ 업데이트 중 나타나는 메시지 처리:**

1. **커널 업데이트 메시지가 나타나면:**
   - 지금 재시작할 필요 없습니다
   - 배포 완료 후 재시작하면 됩니다
   - 그냥 Enter를 눌러 계속 진행하세요

2. **데몬 재시작 선택 메시지가 나타나면:**
   - 키보드로 **7** 입력 후 **Enter**
   - (none of the above 선택)

#### 2-2. 필수 패키지 설치

**왜 필요한가요?**
- `curl`, `wget`: 파일 다운로드용
- `git`: 코드 가져오기용
- `vim`: 파일 편집용
- `htop`: 시스템 모니터링용

```bash
# 필수 패키지 설치
sudo apt install -y curl wget git vim htop
```

**확인:**
```bash
# 각 도구가 설치되었는지 확인
curl --version
git --version
```

#### 2-3. Docker 설치

**왜 필요한가요?**
- 우리 애플리케이션을 실행하기 위해 필요합니다
- 마치 "프로그램 실행 환경을 만들어주는 도구"입니다

```bash
# Docker 설치 스크립트 다운로드
curl -fsSL https://get.docker.com -o get-docker.sh

# Docker 설치 실행
sudo sh get-docker.sh
```

**⏱️ 예상 소요 시간:** 3-5분

**설치 후 설정:**
```bash
# 현재 사용자를 docker 그룹에 추가
# (이렇게 하면 sudo 없이도 docker 명령어를 사용할 수 있습니다)
sudo usermod -aG docker $USER

# 그룹 변경사항 적용 (재로그인 대신)
newgrp docker
```

**확인:**
```bash
# Docker가 제대로 설치되었는지 확인
docker --version

# 예상 출력: Docker version 24.x.x 또는 그 이상
```

**❌ 에러가 나면:**
- `docker: command not found` → 설치가 완료되지 않았습니다. 위 명령어를 다시 실행하세요.

#### 2-4. Docker Compose 설치

**왜 필요한가요?**
- 여러 서비스(Backend, Redis, Nginx)를 한 번에 관리하기 위해 필요합니다
- 마치 "여러 앱을 한 번에 실행하는 리모컨"과 같습니다"

```bash
# Docker Compose 다운로드 및 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 실행 권한 부여
sudo chmod +x /usr/local/bin/docker-compose
```

**확인:**
```bash
# Docker Compose가 제대로 설치되었는지 확인
docker-compose --version

# 예상 출력: Docker Compose version v2.x.x
```

#### 2-5. 스왑 메모리 설정 (권장)

**왜 필요한가요?**
- T3.small은 2GB RAM만 있습니다
- 메모리가 부족할 때를 대비해 "임시 저장 공간"을 만듭니다
- 마치 "작은 책상에 서랍을 추가하는 것"과 같습니다

```bash
# 1GB 스왑 파일 생성
sudo fallocate -l 1G /swapfile

# 권한 설정 (보안을 위해)
sudo chmod 600 /swapfile

# 스왑 파일 포맷
sudo mkswap /swapfile

# 스왑 활성화
sudo swapon /swapfile

# 영구적으로 활성화 (재부팅 후에도 유지)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**확인:**
```bash
# 스왑이 제대로 설정되었는지 확인
free -h

# 예상 출력에서 Swap 행에 1G가 표시되어야 함
# 예시:
#               total        used        free      shared  buff/cache   available
# Mem:           1.9Gi       200Mi       1.2Gi        10Mi       500Mi       1.6Gi
# Swap:          1.0Gi          0B       1.0Gi    ← 이 줄이 있어야 함!
```

---

## 3단계: 프로젝트 코드 가져오기

### 🎯 이 단계에서 하는 일

**목표**: 배포할 코드를 서버에 가져오기

**왜 필요한가요?**
- 서버는 비어있는 상태입니다
- 우리가 만든 코드를 서버에 올려야 실행할 수 있습니다

### 📝 방법 선택

**두 가지 방법이 있습니다:**

1. **방법 1: Git으로 클론** (GitHub에 코드가 있는 경우, 권장)
2. **방법 2: 로컬에서 SCP로 업로드** (로컬에 코드가 있는 경우)

---

### 방법 1: Git으로 클론하기 (권장)

**왜 이 방법이 좋은가요?**
- 간단하고 빠릅니다
- 나중에 업데이트할 때 `git pull`만 하면 됩니다

#### 3-1-1. 프로젝트 클론

```bash
# 홈 디렉토리로 이동
cd ~

# Git 저장소 클론 (저장소 URL을 실제 값으로 변경!)
git clone https://github.com/itgoblin-develop/fashion-ai-discovery-commerce.git

# 프로젝트 디렉토리로 이동
cd fashion-ai-discovery-commerce
```

**⚠️ "already exists and is not an empty directory" 오류 발생 시:**

이 오류는 이미 같은 이름의 디렉토리가 있을 때 발생합니다.

**해결 방법 1: 기존 디렉토리 삭제 후 클론 (권장)**
```bash
cd ~
rm -rf fashion-ai-discovery-commerce
git clone https://github.com/itgoblin-develop/fashion-ai-discovery-commerce.git
cd fashion-ai-discovery-commerce
```

**해결 방법 2: 다른 이름으로 클론**
```bash
cd ~
git clone https://github.com/itgoblin-develop/fashion-ai-discovery-commerce.git fashion-ai
cd fashion-ai
```

**⚠️ "Authentication failed" 오류 발생 시:**

비공개 저장소이거나 인증이 필요한 경우 발생합니다.  
→ **방법 2 (SCP 업로드)**를 사용하세요.

#### 3-1-2. 클론 확인

```bash
# 프로젝트 파일들이 제대로 있는지 확인
ls -la

# 필수 파일 확인
ls -la docker-compose.t3small.yml
ls -la backend/
ls -la frontend/
```

---

### 방법 2: 로컬에서 SCP로 업로드하기

**왜 이 방법을 사용하나요?**
- 로컬에 코드가 있거나
- Git 인증이 복잡할 때

#### 3-2-1. 로컬 컴퓨터에서 준비

**⚠️ 중요: 이 명령어는 EC2 서버가 아닌 로컬 컴퓨터에서 실행하세요!**

```bash
# 로컬 컴퓨터에서 프로젝트 디렉토리로 이동
cd ~/Documents/GitHub/fashion-ai-discovery-commerce

# 프로젝트 압축 (node_modules, venv 등은 제외)
tar -czf fashion-ai.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.db' \
  --exclude='*.log' \
  .
```

#### 3-2-2. 압축 파일 업로드

**macOS/Linux:**
```bash
# SCP로 업로드 (키 파일 경로와 IP를 실제 값으로 변경!)
scp -i ~/.ssh/aws-keys/fashion-ai-key.pem \
  fashion-ai.tar.gz \
  ubuntu@<EC2-PUBLIC-IP>:~/

# 예시:
# scp -i ~/.ssh/aws-keys/fashion-ai-key.pem fashion-ai.tar.gz ubuntu@3.34.123.45:~/
```

**Windows (PowerShell):**
```powershell
# SCP로 업로드
scp -i C:\Users\YourName\.ssh\aws-keys\fashion-ai-key.pem `
  fashion-ai.tar.gz `
  ubuntu@<EC2-PUBLIC-IP>:~/
```

#### 3-2-3. EC2 서버에서 압축 해제

**이제 다시 EC2 서버로 돌아와서:**

```bash
# EC2 서버에 SSH 접속 (아직 접속 안 했다면)
ssh -i ~/.ssh/aws-keys/fashion-ai-key.pem ubuntu@<EC2-PUBLIC-IP>

# 홈 디렉토리로 이동
cd ~

# 압축 해제
tar -xzf fashion-ai.tar.gz

# 프로젝트 디렉토리로 이동
cd fashion-ai-discovery-commerce

# 압축 파일 삭제 (선택사항)
rm fashion-ai.tar.gz
```

#### 3-2-4. 업로드 확인

```bash
# 프로젝트 파일들이 제대로 있는지 확인
ls -la

# 필수 파일 확인
ls -la docker-compose.t3small.yml
ls -la backend/
ls -la frontend/
```

---

## 4단계: 환경 변수 설정하기

### 🎯 이 단계에서 하는 일

**목표**: 애플리케이션이 실행되기 위해 필요한 설정값들을 입력하기

**왜 필요한가요?**
- 애플리케이션은 데이터베이스 주소, API 키 같은 정보가 필요합니다
- 마치 "앱을 실행하려면 아이디와 비밀번호를 입력해야 하는 것"과 같습니다
- 이 정보들을 `.env` 파일에 저장합니다

### 📝 단계별 가이드

#### 4-1. backend 디렉토리로 이동

```bash
# 프로젝트 루트에서
cd ~/fashion-ai-discovery-commerce/backend
```

#### 4-2. .env 파일 생성

**방법 1: 자동 생성 스크립트 사용 (가장 간단, 권장)**

```bash
# setup-env.sh 스크립트 실행
bash setup-env.sh
```

이 스크립트가 자동으로:
- `.env.example` 파일 생성 (없는 경우)
- `.env` 파일 생성
- `SECRET_KEY` 자동 생성

**방법 2: 수동으로 생성**

```bash
# .env.example이 있으면 복사
cp .env.example .env

# 또는 새로 생성
nano .env
```

#### 4-3. .env 파일 편집

```bash
# nano 에디터로 파일 열기
nano .env
```

**파일 내용 (아래 내용을 복사하여 붙여넣기):**

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
SECRET_KEY=<아래 명령어로 생성한 키를 여기에 입력>
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
OPENAI_API_KEY=<실제 OpenAI API 키를 여기에 입력>
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

#### 4-4. SECRET_KEY 생성

**새 터미널 창을 열어서 (또는 nano를 저장하고 나와서):**

```bash
# SECRET_KEY 생성
openssl rand -hex 32

# 예상 출력 예시:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**생성된 키를 복사한 후:**
1. nano 에디터로 돌아가기 (`nano .env`)
2. `SECRET_KEY=<생성한-키>` 부분에 붙여넣기

#### 4-5. OpenAI API 키 입력

**nano 에디터에서:**
1. `OPENAI_API_KEY=<실제 OpenAI API 키를 여기에 입력>` 부분 찾기
2. `<실제 OpenAI API 키를 여기에 입력>` 부분을 실제 API 키로 교체
   - 예: `OPENAI_API_KEY=sk-proj-abc123...`

**⚠️ 주의:**
- API 키는 `sk-`로 시작하는 긴 문자열입니다
- OpenAI 웹사이트에서 발급받은 키를 정확히 입력하세요

#### 4-6. 파일 저장

**nano 에디터에서:**
1. `Ctrl + X` (저장하고 나가기)
2. `Y` (저장 확인)
3. `Enter` (파일명 확인)

**vim 에디터를 사용한 경우:**
1. `Esc` (명령 모드로 전환)
2. `:wq` (저장하고 나가기)
3. `Enter`

#### 4-7. 설정 확인

```bash
# .env 파일이 제대로 생성되었는지 확인
ls -la .env

# 중요 설정값 확인 (비밀번호는 가려서 표시)
cat .env | grep -E '(SECRET_KEY|OPENAI_API_KEY|DATABASE_URL|REDIS_URL)'

# SECRET_KEY와 OPENAI_API_KEY가 실제 값으로 설정되었는지 확인
# (CHANGE-THIS 같은 기본값이 아닌지 확인)
```

**✅ 확인 포인트:**
- ✅ `.env` 파일이 존재함
- ✅ `SECRET_KEY`가 긴 랜덤 문자열로 설정됨
- ✅ `OPENAI_API_KEY`가 실제 API 키로 설정됨 (sk-로 시작)
- ✅ `DATABASE_URL`이 `sqlite:///./fashion_ai.db`로 설정됨

---

## 5단계: Frontend 빌드하기

### 🎯 이 단계에서 하는 일

**목표**: React 앱을 브라우저에서 실행할 수 있는 파일로 변환하기

**왜 필요한가요?**
- React는 개발용 코드입니다
- 브라우저에서 실행하려면 "빌드"라는 과정을 거쳐야 합니다
- 마치 "요리 재료를 요리해서 먹을 수 있는 음식으로 만드는 것"과 같습니다

### 📝 방법 선택

**두 가지 방법이 있습니다:**

1. **방법 1: 로컬에서 빌드 후 업로드** (권장, 더 빠름)
2. **방법 2: EC2에서 직접 빌드** (EC2에 Node.js 설치 필요)

---

### 방법 1: 로컬에서 빌드 후 업로드 (권장)

**왜 이 방법이 좋은가요?**
- 로컬 컴퓨터가 더 빠릅니다
- EC2 서버의 리소스를 절약할 수 있습니다

#### 5-1-1. 로컬 컴퓨터에서 빌드

**⚠️ 중요: 이 명령어는 EC2 서버가 아닌 로컬 컴퓨터에서 실행하세요!**

```bash
# 로컬 컴퓨터에서 프로젝트 디렉토리로 이동
cd ~/Documents/GitHub/fashion-ai-discovery-commerce/frontend

# 의존성 설치 (처음 한 번만)
npm install

# 빌드 실행
npm run build
```

**⏱️ 예상 소요 시간:** 2-5분

**확인:**
```bash
# build 디렉토리가 생성되었는지 확인
ls -la build/

# index.html 파일이 있는지 확인
ls -la build/index.html
```

#### 5-1-2. 빌드 파일 업로드

**macOS/Linux:**
```bash
# 로컬 컴퓨터에서 실행
scp -i ~/.ssh/aws-keys/fashion-ai-key.pem \
  -r frontend/build \
  ubuntu@<EC2-PUBLIC-IP>:~/fashion-ai-discovery-commerce/frontend/
```

**Windows (PowerShell):**
```powershell
# 로컬 컴퓨터에서 실행
scp -i C:\Users\YourName\.ssh\aws-keys\fashion-ai-key.pem `
  -r frontend/build `
  ubuntu@<EC2-PUBLIC-IP>:~/fashion-ai-discovery-commerce/frontend/
```

#### 5-1-3. EC2에서 확인

**EC2 서버로 돌아와서:**

```bash
# 프로젝트 디렉토리로 이동
cd ~/fashion-ai-discovery-commerce

# build 디렉토리가 있는지 확인
ls -la frontend/build/

# index.html 파일 확인
ls -la frontend/build/index.html
```

---

### 방법 2: EC2에서 직접 빌드

**왜 이 방법을 사용하나요?**
- 로컬 컴퓨터에 Node.js가 없을 때
- 또는 로컬 빌드가 실패할 때

#### 5-2-1. Node.js 설치

```bash
# Node.js 설치 스크립트 다운로드 및 실행
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Node.js 설치
sudo apt-get install -y nodejs
```

**확인:**
```bash
# Node.js 버전 확인
node --version
# 예상 출력: v20.x.x

# npm 버전 확인
npm --version
# 예상 출력: 10.x.x
```

#### 5-2-2. Frontend 빌드

```bash
# 프로젝트 디렉토리로 이동
cd ~/fashion-ai-discovery-commerce/frontend

# 의존성 설치
npm install

# 빌드 실행
npm run build
```

**⏱️ 예상 소요 시간:** 5-10분 (EC2가 느릴 수 있음)

**확인:**
```bash
# build 디렉토리가 생성되었는지 확인
ls -la build/

# index.html 파일 확인
ls -la build/index.html
```

---

## 6단계: 배포 실행하기

### 🎯 이 단계에서 하는 일

**목표**: 모든 서비스를 실행하여 애플리케이션을 배포하기

**왜 필요한가요?**
- 지금까지 준비한 것들을 실제로 실행해야 합니다
- Docker Compose가 Backend, Redis, Nginx를 모두 실행합니다

### 📝 단계별 가이드

#### 6-1. 프로젝트 디렉토리 확인

```bash
# 프로젝트 루트로 이동
cd ~/fashion-ai-discovery-commerce

# 필수 파일 확인
ls -la docker-compose.t3small.yml
ls -la nginx/nginx.conf
ls -la frontend/build
ls -la backend/.env
```

**✅ 확인 포인트:**
- ✅ `docker-compose.t3small.yml` 파일 존재
- ✅ `nginx/nginx.conf` 파일 존재
- ✅ `frontend/build` 디렉토리 존재
- ✅ `backend/.env` 파일 존재

#### 6-2. Docker Compose로 배포 실행

```bash
# 프로젝트 루트에서 실행
cd ~/fashion-ai-discovery-commerce

# Docker 이미지 빌드 및 서비스 시작
docker-compose -f docker-compose.t3small.yml up -d --build
```

**⏱️ 예상 소요 시간:** 5-15분 (처음 빌드 시)

**이 명령어가 하는 일:**
- `-f docker-compose.t3small.yml`: 사용할 설정 파일 지정
- `up`: 서비스 시작
- `-d`: 백그라운드에서 실행 (detached mode)
- `--build`: 이미지를 새로 빌드

**⚠️ 주의:**
- 처음 실행 시 시간이 오래 걸릴 수 있습니다
- 에러가 나면 로그를 확인하세요 (아래 참고)

#### 6-3. 서비스 상태 확인

```bash
# 모든 서비스 상태 확인
docker-compose -f docker-compose.t3small.yml ps
```

**예상 출력:**
```
NAME                    STATUS              PORTS
fashion-ai-backend     Up 30 seconds       8000/tcp
fashion-ai-redis       Up 30 seconds       6379/tcp
fashion-ai-nginx       Up 30 seconds       0.0.0.0:80->80/tcp
```

**✅ 확인 포인트:**
- ✅ 모든 서비스가 "Up" 상태
- ✅ nginx의 PORTS에 `0.0.0.0:80->80/tcp` 표시됨

**❌ 문제가 있을 때:**
- 상태가 "Exited" 또는 "Restarting"이면 로그를 확인하세요

#### 6-4. 로그 확인

```bash
# 모든 서비스 로그 확인 (실시간)
docker-compose -f docker-compose.t3small.yml logs -f

# 특정 서비스 로그만 확인
docker-compose -f docker-compose.t3small.yml logs -f backend
docker-compose -f docker-compose.t3small.yml logs -f nginx

# 최근 100줄만 확인
docker-compose -f docker-compose.t3small.yml logs --tail=100
```

**로그에서 확인할 것:**
- ✅ Backend: "Application startup complete" 같은 메시지
- ✅ Nginx: 에러 메시지가 없어야 함
- ❌ 에러 메시지가 있으면 문제 해결 가이드 참고

**로그 보기 종료:**
- `Ctrl + C` 누르기

#### 6-5. Health Check

```bash
# Health check 실행
curl http://localhost/health
```

**예상 응답:**
```json
{"status":"healthy"}
```

**✅ 성공:**
- `{"status":"healthy"}` 응답이 오면 성공!

**❌ 실패:**
- 연결이 안 되거나 에러가 나면 로그를 확인하세요

#### 6-6. 메모리 사용량 확인

```bash
# 메모리 사용량 확인 (한 번만)
docker stats --no-stream

# 실시간 모니터링 (종료하려면 Ctrl+C)
docker stats
```

**확인 포인트:**
- 총 메모리 사용량이 2GB 이하인지 확인
- 각 서비스의 메모리 사용량 확인

---

## 7단계: 접속 확인하기

### 🎯 이 단계에서 하는 일

**목표**: 브라우저에서 웹사이트가 제대로 작동하는지 확인하기

### 📝 단계별 가이드

#### 7-1. EC2 Public IP 확인

**EC2 서버에서:**
```bash
# Public IP 확인
curl http://169.254.169.254/latest/meta-data/public-ipv4

# 예상 출력: 3.34.123.45 (실제 IP 주소)
```

**또는 AWS 콘솔에서:**
1. EC2 콘솔 접속
2. 인스턴스 선택
3. "퍼블릭 IPv4 주소" 확인

#### 7-2. 브라우저에서 접속

**웹 브라우저를 열고 다음 주소로 접속:**

1. **Frontend (메인 페이지):**
   ```
   http://<EC2-PUBLIC-IP>
   ```
   예: `http://3.34.123.45`

2. **Health Check:**
   ```
   http://<EC2-PUBLIC-IP>/health
   ```
   예: `http://3.34.123.45/health`

3. **API:**
   ```
   http://<EC2-PUBLIC-IP>/api/v1/
   ```
   예: `http://3.34.123.45/api/v1/`

**✅ 성공 확인:**
- ✅ Frontend 페이지가 정상적으로 로드됨
- ✅ Health Check에서 `{"status":"healthy"}` 응답
- ✅ API가 정상 작동함

**❌ 접속이 안 될 때:**
- 아래 "문제 해결 가이드" 참고

#### 7-3. 보안 그룹 확인

**접속이 안 되면 보안 그룹을 확인하세요:**

1. AWS 콘솔 → EC2 → 인스턴스 선택
2. "보안" 탭 클릭
3. 보안 그룹 이름 클릭
4. "인바운드 규칙" 확인

**필수 규칙:**
- ✅ SSH (22): 본인 IP 또는 0.0.0.0/0
- ✅ HTTP (80): 0.0.0.0/0
- ✅ HTTPS (443): 0.0.0.0/0 (선택사항)

**규칙이 없으면 추가:**
1. "인바운드 규칙 편집" 클릭
2. "규칙 추가" 클릭
3. 유형: HTTP, 포트: 80, 소스: 0.0.0.0/0
4. "규칙 저장" 클릭

---

## 문제 해결 가이드

### 🔍 자주 발생하는 문제들

#### 문제 1: SSH 접속이 안 됨

**증상:**
```
Permission denied (publickey)
```

**원인 분석:**
이 에러는 여러 가지 원인이 있을 수 있습니다:
1. 잘못된 키 파일을 사용했거나
2. 키 파일 권한이 잘못되었거나
3. EC2 인스턴스에 연결된 키 페어가 다르거나
4. 키 파일 경로가 잘못되었거나

**해결 방법 (단계별):**

**1단계: 키 파일 위치 확인**

```bash
# macOS/Linux에서 키 파일 찾기
ls -la ~/.ssh/
ls -la ~/.ssh/aws-keys/

# Windows에서 키 파일 찾기
# 파일 탐색기에서 C:\Users\YourName\.ssh\ 확인
```

**2단계: 키 파일 권한 확인 및 수정 (macOS/Linux만)**

```bash
# 키 파일 권한 확인
ls -l ~/.ssh/aws-keys/*.pem

# 권한이 400이 아니면 수정
chmod 400 ~/.ssh/aws-keys/fashion-ai-key.pem

# 또는 실제 키 파일 이름으로
chmod 400 ~/.ssh/aws-keys/<실제-키-파일명>.pem

# 권한 확인 (예상 출력: -r--------)
ls -l ~/.ssh/aws-keys/fashion-ai-key.pem
```

**3단계: AWS 콘솔에서 키 페어 확인**

1. AWS 콘솔 접속: https://console.aws.amazon.com
2. EC2 서비스 선택
3. 인스턴스 선택
4. "보안" 탭 → "키 페어 이름" 확인
   - 예: `fashion-ai-key` 또는 `my-key-pair`
5. 이 이름과 로컬 키 파일 이름이 일치하는지 확인

**4단계: 올바른 키 파일로 접속 시도**

```bash
# macOS/Linux
ssh -i ~/.ssh/aws-keys/<실제-키-파일명>.pem ubuntu@43.201.87.79

# Windows (PowerShell)
ssh -i C:\Users\YourName\.ssh\aws-keys\<실제-키-파일명>.pem ubuntu@43.201.87.79
```

**5단계: 보안 그룹 확인**

1. AWS 콘솔 → EC2 → 인스턴스 선택
2. "보안" 탭 → 보안 그룹 이름 클릭
3. "인바운드 규칙" 확인
4. SSH (22) 포트가 열려있는지 확인
   - 유형: SSH
   - 포트: 22
   - 소스: 본인 IP 또는 0.0.0.0/0
5. 없으면 "인바운드 규칙 편집" → "규칙 추가" → SSH (22) 추가

**6단계: 상세 디버그 정보로 접속 시도**

```bash
# -v 옵션으로 상세 정보 확인
ssh -v -i ~/.ssh/aws-keys/<키-파일명>.pem ubuntu@43.201.87.79

# 더 상세한 정보가 필요하면 -vv 또는 -vvv 사용
ssh -vv -i ~/.ssh/aws-keys/<키-파일명>.pem ubuntu@43.201.87.79
```

**7단계: 다른 키 파일 시도**

만약 여러 키 파일이 있다면, 각각 시도해보세요:

```bash
# 키 파일 목록 확인
ls -la ~/.ssh/aws-keys/

# 각 키 파일로 접속 시도
ssh -i ~/.ssh/aws-keys/key1.pem ubuntu@43.201.87.79
ssh -i ~/.ssh/aws-keys/key2.pem ubuntu@43.201.87.79
```

**8단계: 이미 접속된 세션이 있는지 확인**

터미널에 `ubuntu@ip-172-31-xx-xx:~$` 같은 프롬프트가 보이면 이미 접속된 상태일 수 있습니다.

```bash
# 현재 호스트 확인
hostname

# Public IP 확인
curl http://169.254.169.254/latest/meta-data/public-ipv4

# 이미 접속되어 있다면 그대로 사용하세요!
```

**⚠️ 여전히 안 되면:**

1. **AWS 콘솔에서 새 키 페어 생성:**
   - EC2 → 키 페어 → 키 페어 생성
   - 새 키 파일 다운로드
   - 인스턴스에 새 키 페어 연결 (인스턴스 재시작 필요할 수 있음)

2. **EC2 Instance Connect 사용 (임시 해결책):**
   - AWS 콘솔 → EC2 → 인스턴스 선택
   - "연결" 버튼 클릭
   - "EC2 Instance Connect" 탭 선택
   - "연결" 클릭
   - 브라우저에서 터미널이 열립니다

---

#### 문제 2: Docker 명령어가 작동하지 않음

**증상:**
```
docker: command not found
```

**해결 방법:**
```bash
# Docker 재설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 확인
docker --version
```

---

#### 문제 3: 서비스가 시작되지 않음

**증상:**
```
docker-compose ps
# 상태가 "Exited" 또는 "Restarting"
```

**해결 방법:**
```bash
# 로그 확인
docker-compose -f docker-compose.t3small.yml logs

# 특정 서비스 로그 확인
docker-compose -f docker-compose.t3small.yml logs backend

# 재시작
docker-compose -f docker-compose.t3small.yml restart

# 완전히 재시작 (컨테이너 삭제 후 재생성)
docker-compose -f docker-compose.t3small.yml down
docker-compose -f docker-compose.t3small.yml up -d --build
```

---

#### 문제 4: 메모리 부족

**증상:**
```
OOM (Out of Memory) 에러
```

**해결 방법:**
```bash
# 스왑 메모리 확인
free -h

# 스왑이 없으면 추가 (2단계 2-5 참고)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

#### 문제 5: 브라우저에서 접속이 안 됨

**증상:**
- 브라우저에서 "연결할 수 없음" 또는 타임아웃

**해결 방법:**

1. **보안 그룹 확인:**
   - HTTP (80) 포트가 열려있는지 확인
   - 소스가 0.0.0.0/0인지 확인

2. **서비스 상태 확인:**
   ```bash
   docker-compose -f docker-compose.t3small.yml ps
   ```
   - 모든 서비스가 "Up" 상태인지 확인

3. **로그 확인:**
   ```bash
   docker-compose -f docker-compose.t3small.yml logs nginx
   ```

4. **EC2에서 직접 테스트:**
   ```bash
   curl http://localhost/health
   ```
   - 이게 작동하면 서비스는 정상, 보안 그룹 문제일 가능성 높음

---

#### 문제 6: .env 파일 관련 에러

**증상:**
```
OPENAI_API_KEY not found
SECRET_KEY not found
```

**해결 방법:**
```bash
# .env 파일 확인
cd ~/fashion-ai-discovery-commerce/backend
ls -la .env

# 파일이 없으면 생성
bash setup-env.sh

# 파일 내용 확인
cat .env | grep -E '(OPENAI_API_KEY|SECRET_KEY)'

# 값이 제대로 설정되었는지 확인
```

---

## 🔧 유용한 명령어 모음

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

## 🎉 배포 완료!

축하합니다! 배포가 완료되었습니다!

### 다음 단계

1. **도메인 연결** (선택사항)
   - Route 53이나 다른 DNS 서비스 사용
   - 도메인을 EC2 Public IP에 연결

2. **SSL 인증서 설정** (선택사항)
   - Let's Encrypt 사용
   - HTTPS 활성화

3. **모니터링 설정**
   - CloudWatch 알람 설정
   - 로그 모니터링

4. **백업 설정**
   - 정기적인 데이터베이스 백업
   - 스냅샷 생성

---

## 📚 추가 자료

- [T3.small 배포 가이드](./Document/T3.small_배포_가이드.md)
- [README_T3SMALL.md](./README_T3SMALL.md)
- [AWS EC2 문서](https://docs.aws.amazon.com/ec2/)

---

**작성일**: 2024년  
**버전**: 2.0 (초보자용)  
**대상**: 처음 배포하는 분들을 위한 완전 정복 가이드

