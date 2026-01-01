"""
더미 상품 데이터 생성 유틸리티
남성/여성 의류 200개를 생성합니다.
"""

def generate_additional_products():
    """추가 상품 데이터 200개 생성 (남성 100개, 여성 100개)"""
    
    # 문서 규칙 준수: 다양한 브랜드 추가 (29CM 감성, 무신사 감성 브랜드 포함)
    brands = [
        'Street Brand', 'Denim Co', 'Minimal Style', 'Office Wear', 'Sporty', 
        'Classic', 'Basic', 'Feminine', 'Trendy', 'Casual Co', 'Urban Style', 
        'Modern Wear', 'Elite Fashion', 'Simple Life', 'Style Lab',
        '29CM Studio', '무신사 Style', 'Aesthetic Co', 'Clean Brand', 'Urban Minimal'
    ]
    colors = ['블랙', '화이트', '네이비', '그레이', '베이지', '크림', '인디고', '카키', '차콜', '라이트블루', '아이보리', '핑크', '레드', '브라운', '올리브']
    
    # 문서 규칙: 시즌 정보 추가
    seasons = ['봄', '여름', '가을', '겨울', '사계절']
    
    # 문서 규칙: 상황별 정보 추가
    situations = ['출근', '데이트', '소개팅', '여행', '회식', '면접', '데일리', '파티']
    
    # 실제 작동하는 Unsplash 의류 이미지 ID 목록 (검증된 것들만)
    clothing_image_ids = [
        "1556821840-3a63f95609a7",  # 후드티/맨투맨
        "1542272604-787c3835535d",  # 청바지/데님
        "1576566588028-4147f3842f27",  # 가디건/니트
        "1594938291221-94f18dd6d221",  # 슬랙스/팬츠
        "1551028719-00167b16eac5",  # 재킷/아우터
        "1594633313593-bab3825d0caf",  # 스커트/원피스
        "1595777457583-95e059d581b8",  # 원피스
        "1506629905862-4c94c8ebf58c",  # 팬츠
        "1539533018447-63fcce2678e3",  # 코트
        "1521572163474-6864f9cf17ab",  # 티셔츠
        "1521223890158-f9f7c3d5d504",  # 셔츠
        "1556821843-3a63f95609a7",  # 후드 집업
        "1441986300917-64674bd600d8",  # 의류
        "1445205170230-053b83016050",  # 의류
        "1434389677669-e08b4cac3105",  # 의류
        "1469334031218-e382a71b716b",  # 의류
        "1485968579580-b6d5ecdf6a9a",  # 의류
        "1515886657613-d68ecb4b59cd",  # 의류
        "1523262406531-0b0c0a8c8b8c",  # 의류
        "1562157873-868a12fecc10",  # 의류
        "1586790170083-674960dba9e4",  # 의류
        "1601925264989-8c2c2a2b3c3d",  # 의류
        "1612349317154-e723f72ccb8b",  # 의류
        "1624280433509-b29afea68da1",  # 의류
        "1631217868264-9af6bd8134b8",  # 의류
        "1642772996194-9d163f2b96c1",  # 의류
        "1651696080452-283a08d844f3",  # 의류
        "1661956602119-9b35671e78de",  # 의류
        "1477945149619-80470b6afbf4",  # 의류
        "1490489784569-37001340e4b6",  # 의류
        "1503341338988-bff7a3a0c51b",  # 의류
    ]
    
    # 남성 의류 템플릿
    male_templates = {
        '상의': ['오버핏 후드티', '맨투맨', '반팔 티셔츠', '긴팔 티셔츠', '셔츠', '데님 셔츠', '니트 스웨터', '터틀넥 니트', '후드 스웨트셔츠', '크롭 티셔츠', '린넨 셔츠', '폴로 셔츠', '헨리넥 티셔츠', '카라 티셔츠', '베이직 티셔츠'],
        '하의': ['슬림핏 청바지', '와이드 데님', '스키니 진', '카고 팬츠', '슬림핏 슬랙스', '와이드 슬랙스', '트레이닝 조거', '치노 팬츠', '코듀라 팬츠', '조거 팬츠', '스웨트 팬츠', '반바지', '카고 반바지', '치노 반바지', '데님 반바지'],
        '아우터': ['레더 재킷', '후드 집업', '코치 재킷', '후드 코트', '바람막이', '패딩 재킷', '트렌치 코트', '블루종', '야상', '항공 점퍼', '데님 재킷', '무스탕', '후리스', '플리스', '바시티 재킷']
    }
    
    # 문서 규칙 준수: 29CM 감성, 무신사 감성 스타일 태그 추가
    # 29CM 감성: 미니멀 / 차분한 컬러 / 여유 있는 핏
    # 무신사 감성: 스트릿 / 트렌디 / 오버핏
    male_styles = [
        '스트릿', '캐주얼', '미니멀', '오버핏', '슬림핏', '와이드', '스포티', 
        '클래식', '베이직', '모던', '레트로', '유니크', '심플', '트렌디', '시크',
        '29CM 감성', '무신사 감성', '아메카지', '워크웨어'
    ]
    
    # 여성 의류 템플릿
    female_templates = {
        '상의': ['크롭 가디건', '니트 스웨터', '터틀넥 니트', '크롭 티셔츠', '린넨 셔츠', '블라우스', '크롭 블라우스', '셔츠 블라우스', '베이직 티셔츠', '크롭 후드티', '맨투맨', '후드 스웨트셔츠', '터틀넥 스웨터', '카디건', '크롭 니트'],
        '하의': ['플리츠 스커트', '부츠컷 팬츠', '치마 바지', '플레어 스커트', '미니 스커트', '롱 스커트', '와이드 팬츠', '슬림핏 팬츠', '부츠컷 팬츠', '하이웨이스트 팬츠', '크롭 팬츠', '레깅스', '조거 팬츠', '스커트 팬츠', '플리츠 팬츠'],
        '원피스': ['셔츠 원피스', '플리츠 원피스', '미디 원피스', '롱 원피스', '크롭 원피스', '니트 원피스', '린넨 원피스', '플레어 원피스', 'A라인 원피스', 'H라인 원피스', '맥시 원피스', '미니 원피스', '셔츠 원피스', '니트 원피스', '린넨 원피스'],
        '아우터': ['트렌치 코트', '패딩 재킷', '후드 코트', '바람막이', '코치 재킷', '데님 재킷', '블루종', '야상', '후리스', '플리스', '무스탕', '크롭 재킷', '크롭 코트', '롱 코트', '숏 코트']
    }
    
    # 문서 규칙 준수: 29CM 감성 스타일 태그 추가
    female_styles = [
        '페미닌', '미니멀', '캐주얼', '크롭', '플리츠', '부츠컷', '플레어', 
        '오피스', '로맨틱', '모던', '심플', '트렌디', '시크', '우아', '레트로',
        '29CM 감성', '무신사 감성', '아메카지', '워크웨어'
    ]
    
    products = []
    product_id = 31
    
    # 남성 의류 100개 생성
    for i in range(100):
        categories = list(male_templates.keys())
        category = categories[i % len(categories)]
        templates = male_templates[category]
        name_template = templates[i % len(templates)]
        
        # 스타일 태그 선택 (3개) - 문서 규칙: 3개 이상의 다른 스타일 포함
        style_start = i % len(male_styles)
        style_tags = []
        for j in range(3):
            style_tags.append(male_styles[(style_start + j) % len(male_styles)])
        
        # 문서 규칙: 시즌 정보 추가
        season = seasons[i % len(seasons)]
        
        # 문서 규칙: 상황별 정보 추가
        situation = situations[i % len(situations)]
        
        # 문서 규칙: 학생용 저렴한 가격대 포함 (10만원대)
        # 가격대 다양화: 3만원~22만원 (학생용 저렴한 가격대 포함)
        price = 30000 + (i % 20) * 10000
        # 일부 상품은 학생용 저렴한 가격대로 설정 (10만원대)
        if i % 5 == 0:
            price = 50000 + (i % 10) * 5000  # 5만원~10만원대
        
        products.append({
            "id": f"prod_{product_id:03d}",
            "name": name_template,
            "brand": brands[i % len(brands)],
            "category": category,
            "gender": "남성",
            "style_tags": style_tags,
            "color": colors[i % len(colors)],
            "price": price,
            "popularity_score": round(0.7 + (i % 30) * 0.01, 2),
            "image_url": f"https://images.unsplash.com/photo-{clothing_image_ids[i % len(clothing_image_ids)]}?w=600&h=800&fit=crop",
            "description": f"{name_template}입니다. {season}에 입기 좋은 {situation}룩으로 활용하기 좋은 남성용 {category}입니다.",
            "season": season,  # 문서 규칙: 시즌 정보
            "situation": situation  # 문서 규칙: 상황별 정보
        })
        product_id += 1
    
    # 여성 의류 100개 생성
    for i in range(100):
        categories = list(female_templates.keys())
        category = categories[i % len(categories)]
        templates = female_templates[category]
        name_template = templates[i % len(templates)]
        
        # 스타일 태그 선택 (3개) - 문서 규칙: 3개 이상의 다른 스타일 포함
        style_start = i % len(female_styles)
        style_tags = []
        for j in range(3):
            style_tags.append(female_styles[(style_start + j) % len(female_styles)])
        
        # 문서 규칙: 시즌 정보 추가
        season = seasons[i % len(seasons)]
        
        # 문서 규칙: 상황별 정보 추가
        situation = situations[i % len(situations)]
        
        # 문서 규칙: 학생용 저렴한 가격대 포함 (10만원대)
        # 가격대 다양화: 3만원~22만원 (학생용 저렴한 가격대 포함)
        price = 30000 + (i % 20) * 10000
        # 일부 상품은 학생용 저렴한 가격대로 설정 (10만원대)
        if i % 5 == 0:
            price = 50000 + (i % 10) * 5000  # 5만원~10만원대
        
        products.append({
            "id": f"prod_{product_id:03d}",
            "name": name_template,
            "brand": brands[i % len(brands)],
            "category": category,
            "gender": "여성",
            "style_tags": style_tags,
            "color": colors[i % len(colors)],
            "price": price,
            "popularity_score": round(0.7 + (i % 30) * 0.01, 2),
            "image_url": f"https://images.unsplash.com/photo-{clothing_image_ids[i % len(clothing_image_ids)]}?w=600&h=800&fit=crop",
            "description": f"{name_template}입니다. {season}에 입기 좋은 {situation}룩으로 활용하기 좋은 여성용 {category}입니다.",
            "season": season,  # 문서 규칙: 시즌 정보
            "situation": situation  # 문서 규칙: 상황별 정보
        })
        product_id += 1
    
    return products

