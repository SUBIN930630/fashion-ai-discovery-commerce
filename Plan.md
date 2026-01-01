# 코드 수정 플랜 (데모 + SQL)

## 범위
- 데모 환경 전용.
- 데이터는 SQL(DB)로 저장 (SQLite/Postgres). Redis는 사용하지 않음.
- 프론트 데모 인증은 유지(필요 시 추후 개선).

## 목표
- 백엔드가 import 오류 없이 정상 부팅되도록 함.
- 세션/히스토리/좋아요/장바구니/추천 기록을 SQL에 영속화.
- MMR 추천 정확도 개선(실제 임베딩 사용).
- 게스트 채팅 사용자 식별자 안정화.

## 작업 항목
1) 누락된 백엔드 모델/스키마 추가
   - `backend/app/models/chat.py` 생성: `ChatSession`, `ChatMessage`, `MessageRole`.
   - `backend/app/models/db_models.py` 생성: `Product`, `UserFavorite`, `UserCart`, `ChatHistory`.
   - `backend/migrations/init_db.sql`을 모델과 맞추거나 Alembic 도입.

2) 채팅 히스토리/세션 영속화
   - `ChatHistoryService.save_conversation`에서 `metadata` 인자 오류 수정.
   - `GET /chat/history/{session_id}`가 `ChatHistoryService`(DB)에서 읽도록 변경.
   - `SessionService`를 SQL 기반으로 전환(테이블로 세션 저장).

3) 추천/피드백 영속화
   - 추천 히스토리와 피드백을 SQL 테이블에 저장.
   - `/history`, `/analytics`가 메모리 대신 SQL을 읽도록 수정.

4) MMR 임베딩 실제 사용
   - `SQLVectorStore.search`에서 임베딩을 반환하거나,
     `SearchEngine._convert_to_candidate`에서 임베딩을 조회하도록 변경.
   - 0벡터 placeholder 제거.

5) OpenAI 호출 비동기/블로킹 방지
   - `ml/intent_analyzer/intent_classifier.py`
   - `ml/response_generator/response_generator.py`
   - (스레드 실행기 또는 async SDK 사용)

6) 프론트 데이터 일관성
   - 게스트 `user_id`를 localStorage나 `useRef`로 고정.
   - 데모 계정 자동생성은 데모 플래그로 제어(실수 방지).
   - 로컬스토리지 인증은 데모 범위에서 유지.

7) 설정 정리
   - `backend/.env.example`에 필요한 환경변수 문서화.
   - (선택) 데모 호스트만 허용하도록 CORS 축소.

8) 테스트
   - 모델/서비스 단위 테스트 추가(히스토리, 세션, 좋아요, 장바구니).
   - 최소 통합 테스트(채팅 + 히스토리 + 추천).

## 추천 작업 순서
1. 모델/스키마 추가
2. 채팅/세션 저장 수정
3. 추천/피드백 저장
4. MMR 임베딩 개선
5. OpenAI 호출 비동기화
6. 프론트 게스트/데모 정리
7. 설정/테스트 정리
