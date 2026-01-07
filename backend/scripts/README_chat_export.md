# 챗봇 대화 히스토리 내보내기 가이드

## 개요
AWS 배포 서버의 데이터베이스에서 실제 사용자와 챗봇의 대화 내용을 JSON 형식으로 내보내는 스크립트입니다.

## 사용 방법

### 1. AWS 서버에 접속
```bash
ssh -i your-key.pem ubuntu@your-aws-server-ip
```

### 2. 프로젝트 디렉토리로 이동
```bash
cd /path/to/fashion-ai-discovery-commerce
```

### 3. 가상환경 활성화 (필요시)
```bash
source venv/bin/activate
```

### 4. 스크립트 실행

#### 전체 데이터 내보내기
```bash
cd backend
python scripts/export_chat_history.py
```

#### 최근 100개 대화만 내보내기
```bash
python scripts/export_chat_history.py --limit 100
```

#### 특정 기간 데이터 내보내기
```bash
# 2025년 1월 데이터만
python scripts/export_chat_history.py --start-date 2025-01-01 --end-date 2025-01-31
```

#### 출력 파일명 지정
```bash
python scripts/export_chat_history.py --output my_chat_data.json
```

## 출력 파일 구조

```json
{
  "export_info": {
    "export_date": "2025-01-02T12:00:00",
    "total_sessions": 50,
    "total_conversations": 150,
    "total_messages": 300,
    "date_range": {
      "start": "2025-01-01T00:00:00",
      "end": "2025-01-31T23:59:59"
    }
  },
  "statistics": {
    "total_sessions": 50,
    "total_conversations": 150,
    "total_messages": 300,
    "user_messages": 150,
    "assistant_messages": 150
  },
  "conversations": [
    {
      "session_id": "session_123",
      "user_id": "user_456",
      "timestamp": "2025-01-02T10:30:00",
      "user_message": "미니멀 셔츠 추천해줘",
      "assistant_message": "미니멀 스타일의 셔츠를 추천해드릴게요! ...",
      "intent": "감성·스타일",
      "confidence": 0.95,
      "exploration_intent": false,
      "recommendations": [
        {
          "id": "prod001",
          "name": "미니멀 코튼 셔츠",
          "brand": "브랜드A",
          "price": 59000
        }
      ],
      "recommendations_count": 1
    }
  ],
  "sessions": [
    {
      "session_id": "session_123",
      "user_id": "user_456",
      "created_at": "2025-01-02T10:00:00",
      "messages": [...]
    }
  ]
}
```

## 주의사항

1. **데이터베이스 연결 확인**: 스크립트 실행 전에 `.env` 파일의 `DATABASE_URL`이 올바른지 확인하세요.

2. **대용량 데이터**: 전체 데이터를 내보낼 경우 시간이 오래 걸릴 수 있습니다. 필요시 `--limit` 옵션을 사용하세요.

3. **파일 크기**: 대화가 많을 경우 JSON 파일이 매우 커질 수 있습니다. 필요시 날짜 범위를 지정하세요.

4. **권한**: 데이터베이스 읽기 권한이 필요합니다.

## 로컬에서 실행하는 경우

로컬에서 AWS 데이터베이스에 직접 연결하려면:

1. `.env` 파일에 AWS 데이터베이스 연결 정보 설정
2. 스크립트 실행

```bash
# .env 파일 예시
DATABASE_URL=postgresql://user:password@aws-db-host:5432/dbname
```

## 데이터 분석 예시

내보낸 JSON 파일을 Python으로 분석:

```python
import json

with open('chat_history_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 가장 많이 나온 질문 유형
intents = [c['intent'] for c in data['conversations'] if c['intent']]
from collections import Counter
print(Counter(intents))

# 평균 추천 개수
avg_recommendations = sum(c['recommendations_count'] for c in data['conversations']) / len(data['conversations'])
print(f"평균 추천 개수: {avg_recommendations}")
```

