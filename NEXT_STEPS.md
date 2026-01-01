# 다음 단계 가이드

## 📋 현재 상태

✅ **1단계 완료**: 환경 변수 설정 (`.env` 파일)
- 모든 필수 설정 완료
- T3.small 배포 최적화 설정 적용

---

## 🚀 다음 단계: Frontend 빌드

### 2단계: Frontend 빌드

Frontend React 애플리케이션을 프로덕션용으로 빌드해야 합니다.

#### 명령어

```bash
cd frontend

# 1. 의존성 설치 (처음 한 번만 또는 package.json 변경 시)
npm install

# 2. 프로덕션 빌드
npm run build
```

#### 빌드 결과

빌드가 완료되면 `frontend/build` 디렉토리에 정적 파일들이 생성됩니다.
이 파일들은 Nginx가 서빙할 파일입니다.

#### 예상 소요 시간
- `npm install`: 2-5분 (의존성 설치)
- `npm run build`: 1-3분 (빌드)

---

## 📦 그 다음: 배포 실행

### 3단계: 배포 실행

Frontend 빌드가 완료되면 Docker Compose로 배포를 실행합니다.

#### 방법 1: 배포 스크립트 사용 (권장)

```bash
cd ..  # 프로젝트 루트로 이동
./deploy-t3small.sh
```

#### 방법 2: 수동 배포

```bash
# Docker Compose로 서비스 시작
docker-compose -f docker-compose.t3small.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.t3small.yml logs -f

# 상태 확인
docker-compose -f docker-compose.t3small.yml ps
```

---

## ✅ 체크리스트

배포 전 확인사항:

- [x] `.env` 파일 설정 완료
- [ ] Frontend 빌드 완료 (`npm run build`)
- [ ] Docker 및 Docker Compose 설치 확인
- [ ] `docker-compose.t3small.yml` 파일 존재 확인
- [ ] `nginx/nginx.conf` 파일 존재 확인

---

## 🔍 문제 해결

### npm install 오류 시

```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 빌드 실패 시

```bash
# 캐시 삭제 후 재빌드
npm run build -- --no-cache
```

### Docker 관련 문제

```bash
# Docker 상태 확인
docker --version
docker-compose --version

# Docker 서비스 상태 확인
docker ps
```

---

## 📚 관련 파일

- `frontend/package.json` - Frontend 의존성
- `docker-compose.t3small.yml` - T3.small 최적화 배포 설정
- `deploy-t3small.sh` - 자동 배포 스크립트
- `Document/T3.small_배포_가이드.md` - 상세 배포 가이드

---

**다음 단계**: `cd frontend && npm install && npm run build`

