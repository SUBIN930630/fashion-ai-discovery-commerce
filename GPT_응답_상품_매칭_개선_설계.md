# GPT 응답에서 상품명 추출 및 DB 매칭 개선 설계

## 문제 상황

### 현재 문제점
1. **GPT가 상품 추천 내용을 텍스트로만 생성**
   - 예: "블레이저", "화이트 셔츠", "슬랙스" 등을 텍스트로 언급
   - 하지만 `recommendations` 배열이 비어있어서 하단 버튼이 표시되지 않음
   - 텍스트 내에도 하이퍼링크가 생성되지 않음

2. **상품 추천 완료 신호는 있지만 실제 상품이 없음**
   - GPT 응답: "혹시 더 궁금한 점이나 다른 스타일에 대한 요청이 있으신가요?"
   - 이는 상품 추천이 완료되었다는 신호이지만, 실제 DB 상품이 연결되지 않음

3. **현재 프로세스의 한계**
   - `_should_show_recommendations`가 False이면 recommendations 배열이 비어있음
   - GPT가 `no_recommendations` 템플릿을 사용하거나 자유롭게 응답 생성
   - GPT 응답 생성 후 상품명을 추출하여 DB와 매칭하는 로직이 없음

## 원인 분석

### 현재 코드 흐름
```
1. 사용자 메시지 입력
2. _should_show_recommendations() 판단
   - False → recommendations = []
   - True → _generate_recommendations() 실행 → DB 검색 → recommendations 배열 생성
3. GPT 응답 생성 (recommendations 배열 전달)
4. recommendations 배열 그대로 반환
```

### 문제 발생 시나리오

**시나리오 1: _should_show_recommendations가 False인 경우**
- "오피스 룩이라고" (8자, confidence 낮을 수 있음)
- recommendations = [] (빈 배열)
- GPT가 `no_recommendations` 템플릿 사용
- 하지만 GPT가 자유롭게 응답을 생성하여 상품명을 언급할 수 있음
- 결과: 상품명은 언급되었지만 recommendations 배열이 비어있음

**시나리오 2: GPT가 템플릿 없이 자유롭게 응답 생성**
- recommendations 배열이 비어있지만 GPT가 상품 추천 내용을 생성
- 예: "블레이저", "화이트 셔츠" 등을 텍스트로 언급
- 실제 DB 상품과 매칭되지 않음

## 개선 방안

### 방안 1: GPT 응답 후처리에서 상품명 추출 및 DB 검색 (추천)

**개요:**
- GPT 응답 생성 후, 응답 텍스트에서 상품명을 추출
- 추출한 상품명으로 DB 검색
- 검색된 상품을 recommendations 배열에 추가

**장점:**
- GPT가 어떤 방식으로 응답하든 상품 매칭 가능
- 기존 로직과 독립적으로 동작
- 유연하고 확장 가능

**단점:**
- GPT 응답을 파싱해야 함
- 상품명 추출 정확도 의존

**구현 방법:**

1. **상품명 추출 로직**
   ```python
   def _extract_product_names_from_response(self, response: str) -> List[str]:
       """
       GPT 응답에서 상품명 후보 추출
       - 패턴 매칭 (예: "블레이저", "셔츠", "슬랙스" 등)
       - 키워드 기반 추출
       """
       product_keywords = [
           "블레이저", "셔츠", "슬랙스", "바지", "티셔츠", 
           "자켓", "코트", "원피스", "스커트", ...
       ]
       # 응답 텍스트에서 키워드 추출
   ```

2. **DB 검색 및 매칭**
   ```python
   async def _match_products_from_response(
       self, 
       response: str, 
       user_message: str,
       intent_result: Any
   ) -> List[Dict]:
       """
       GPT 응답에서 상품명 추출 후 DB 검색
       """
       # 1. 상품명 후보 추출
       product_names = self._extract_product_names_from_response(response)
       
       # 2. 각 상품명으로 DB 검색
       matched_products = []
       for name in product_names:
           products = await self.search_engine.search_products(
               query=name,
               ...
           )
           matched_products.extend(products)
       
       # 3. 중복 제거 및 유사도 기준 정렬
       # 4. 상위 N개 선택
       return matched_products[:settings.MAX_RECOMMENDATIONS]
   ```

3. **process_message 수정**
   ```python
   # 5. AI 응답 생성
   ai_response = await self.response_generator.generate_response(...)
   
   # 6. GPT 응답에서 상품명 추출 및 DB 매칭 (새로운 단계)
   if not recommendations or len(recommendations) == 0:
       # GPT 응답이 상품 추천 내용을 포함하는지 확인
       if self._is_product_recommendation_response(ai_response):
           extracted_recommendations = await self._match_products_from_response(
               ai_response, user_message, intent_result
           )
           if extracted_recommendations:
               recommendations = extracted_recommendations
   ```

### 방안 2: 상품 추천 완료 신호 감지 로직 추가

**개요:**
- GPT 응답에서 상품 추천 완료 신호 감지
- 감지되면 사용자 메시지와 대화 히스토리 기반으로 DB 검색

**상품 추천 완료 신호:**
- "혹시 더 궁금한 점", "다른 스타일에 대한 요청" 등
- 상품명이 2개 이상 언급됨
- "추천", "제안", "추천드립니다" 등의 키워드 포함

**구현:**
```python
def _is_product_recommendation_response(self, response: str) -> bool:
    """
    GPT 응답이 상품 추천 완료 신호를 포함하는지 확인
    """
    completion_signals = [
        "혹시 더 궁금한 점",
        "다른 스타일에 대한 요청",
        "추천해드릴게요",
        "제안",
        ...
    ]
    
    product_keywords_count = sum(
        1 for keyword in PRODUCT_KEYWORDS 
        if keyword in response
    )
    
    # 신호가 있거나 상품 키워드가 2개 이상이면 추천 완료로 간주
    has_signal = any(signal in response for signal in completion_signals)
    has_products = product_keywords_count >= 2
    
    return has_signal or has_products
```

### 방안 3: 하이브리드 접근 (최종 추천)

**1단계: GPT 응답에서 상품 추천 완료 신호 감지**
- `_is_product_recommendation_response()` 사용

**2단계: 상품명 추출**
- GPT 응답에서 상품명 키워드 추출
- 또는 사용자 메시지 + 대화 히스토리 기반 검색

**3단계: DB 검색 및 매칭**
- 추출한 키워드로 DB 검색
- 또는 사용자 메시지를 쿼리로 사용

**4단계: recommendations 배열 업데이트**
- 검색된 상품을 recommendations 배열에 추가
- 최대 개수 제한 (MAX_RECOMMENDATIONS)

## 구현 상세 설계

### 1. 상품명 추출 함수

```python
def _extract_product_keywords_from_response(self, response: str) -> List[str]:
    """
    GPT 응답에서 상품 관련 키워드 추출
    
    Returns:
        List[str]: 추출된 상품 키워드 리스트
    """
    # 패션 상품 키워드 사전
    product_keywords = [
        "블레이저", "셔츠", "슬랙스", "바지", "티셔츠", "후드티",
        "자켓", "코트", "원피스", "스커트", "치마", "청바지",
        "니트", "가디건", "블라우스", "와이드팬츠", "조거팬츠",
        "오버핏", "카디건", "베스트", "패딩", "무스탕", ...
    ]
    
    found_keywords = []
    for keyword in product_keywords:
        if keyword in response:
            found_keywords.append(keyword)
    
    return found_keywords
```

### 2. 상품 추천 완료 신호 감지

```python
def _is_product_recommendation_response(self, response: str) -> bool:
    """
    GPT 응답이 상품 추천 완료 신호를 포함하는지 확인
    
    Returns:
        bool: 상품 추천 완료 신호가 있으면 True
    """
    # 완료 신호 키워드
    completion_signals = [
        "혹시 더 궁금한 점",
        "다른 스타일에 대한 요청",
        "다른 스타일에 대한",
        "추천해드릴게요",
        "추천드릴게요",
        "제안",
        "어떤 스타일",
        "다른 스타일",
    ]
    
    # 상품 키워드 개수 확인
    product_keywords = self._extract_product_keywords_from_response(response)
    
    # 신호가 있거나 상품 키워드가 2개 이상이면 추천 완료로 간주
    has_completion_signal = any(
        signal in response for signal in completion_signals
    )
    has_multiple_products = len(product_keywords) >= 2
    
    return has_completion_signal or has_multiple_products
```

### 3. DB 검색 및 매칭

```python
async def _match_products_from_response(
    self,
    response: str,
    user_message: str,
    intent_result: Any,
    user_profile: Optional[Dict],
    session: ChatSession
) -> List[Dict]:
    """
    GPT 응답에서 상품명을 추출하여 DB에서 매칭
    
    Args:
        response: GPT 응답 텍스트
        user_message: 사용자 메시지
        intent_result: 의도 분석 결과
        user_profile: 사용자 프로필
        session: 채팅 세션
    
    Returns:
        List[Dict]: 매칭된 상품 리스트
    """
    # 1. 상품 키워드 추출
    product_keywords = self._extract_product_keywords_from_response(response)
    
    # 2. 검색 쿼리 생성 (키워드 또는 사용자 메시지 사용)
    search_query = user_message
    if product_keywords:
        # 키워드를 조합하여 검색 쿼리 생성
        search_query = " ".join(product_keywords[:3])  # 상위 3개 키워드
    
    # 3. DB 검색
    search_results = await self.search_engine.search_products(
        query=search_query,
        user_profile=user_profile,
        intent=intent_result.intent,
        limit=50
    )
    
    if not search_results:
        return []
    
    # 4. MMR 알고리즘으로 다양성 있는 추천 선택
    mmr_result = await self.mmr_scorer.select_recommendations(
        query_embedding=None,
        candidates=search_results,
        target_count=settings.MAX_RECOMMENDATIONS,
        strategy=intent_result.recommendation_strategy,
        excluded_ids=await self._get_excluded_products(session.user_id),
        user_history=await self._get_user_history(session.user_id)
    )
    
    # 5. 응답 형식으로 변환
    recommendations = []
    for product in mmr_result.selected_products:
        product_id = product.id
        product_url = f"/product/{product_id}"
        
        recommendations.append({
            "id": product_id,
            "name": product.metadata.get("name", ""),
            "brand": product.metadata.get("brand", ""),
            "price": product.metadata.get("price", 0),
            "image_url": product.metadata.get("image_url", ""),
            "product_url": product_url,
            "similarity_score": product.similarity_score,
            "recommendation_type": product.recommendation_type.value,
        })
    
    return recommendations
```

### 4. process_message 수정

```python
async def process_message(...):
    # ... 기존 코드 ...
    
    # 5. AI 응답 생성
    ai_response = await self.response_generator.generate_response(
        user_message=user_message,
        intent_result=intent_result,
        recommendations=recommendations,
        user_profile=user_profile,
        chat_history=chat_history
    )
    
    # 6. GPT 응답에서 상품명 추출 및 DB 매칭 (새로운 단계)
    # recommendations가 비어있고, GPT 응답이 상품 추천 내용을 포함하는 경우
    if (not recommendations or len(recommendations) == 0) and \
       self._is_product_recommendation_response(ai_response):
        logger.info("Extracting products from GPT response",
                   response_length=len(ai_response))
        extracted_recommendations = await self._match_products_from_response(
            ai_response=ai_response,
            user_message=user_message,
            intent_result=intent_result,
            user_profile=user_profile,
            session=session
        )
        if extracted_recommendations:
            recommendations = extracted_recommendations
            logger.info("Products extracted from response",
                       count=len(recommendations))
    
    # 7. 메시지 저장
    await self._save_messages(session, user_message, ai_response, intent_result)
    
    return {
        "response": ai_response,
        "recommendations": recommendations,  # 업데이트된 recommendations
        ...
    }
```

## 예상 효과

1. **GPT가 텍스트로만 상품을 언급해도 실제 DB 상품과 연결**
2. **하단 추천 상품 버튼 표시**
3. **텍스트 내 하이퍼링크 생성** (markdownRenderer.js가 recommendations 배열 사용)
4. **사용자 경험 개선**: 실제 상품으로 바로 이동 가능

## 고려사항

1. **성능**: GPT 응답 생성 후 추가 DB 검색으로 인한 지연
   - 해결: 비동기 처리 또는 캐싱

2. **정확도**: 상품명 추출 정확도
   - 해결: 키워드 사전 확장, ML 기반 추출 (추후)

3. **중복 검색**: 이미 recommendations가 있는 경우
   - 해결: 조건문으로 중복 방지

4. **키워드 사전 관리**: 새로운 상품 카테고리 추가 시
   - 해결: DB에서 자동 추출 또는 설정 파일로 관리

