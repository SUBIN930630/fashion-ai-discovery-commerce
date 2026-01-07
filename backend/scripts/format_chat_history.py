#!/usr/bin/env python3
"""
챗봇 대화 히스토리를 읽기 쉬운 형식으로 변환하는 스크립트
JSON의 content 필드에 있는 \n을 실제 줄바꿈으로 변환하여 가독성 향상
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def format_chat_history(input_file: str, output_file: str = None):
    """
    채팅 히스토리를 읽기 쉬운 형식으로 변환
    
    Args:
        input_file: 입력 JSON 파일 경로
        output_file: 출력 파일 경로 (None이면 입력 파일명에 _formatted 추가)
    """
    
    # 입력 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # content 필드의 \n을 실제 줄바꿈으로 변환
    def process_content(content):
        """content 문자열의 \n을 실제 줄바꿈으로 변환"""
        if isinstance(content, str):
            return content.replace('\\n', '\n')
        return content
    
    # conversations 배열 처리
    for conv in data.get('conversations', []):
        if 'user_message' in conv:
            conv['user_message'] = process_content(conv['user_message'])
        if 'assistant_message' in conv:
            conv['assistant_message'] = process_content(conv['assistant_message'])
    
    # sessions 배열 처리
    for session in data.get('sessions', []):
        for msg in session.get('messages', []):
            if 'content' in msg:
                msg['content'] = process_content(msg['content'])
    
    # 출력 파일명 결정
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_formatted{input_path.suffix}")
    
    # JSON으로 저장 (indent를 크게 하여 가독성 향상)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 포맷팅 완료!")
    print(f"📁 입력 파일: {input_file}")
    print(f"📁 출력 파일: {output_file}")
    print(f"📊 통계:")
    print(f"   - 총 세션 수: {data['statistics']['total_sessions']}")
    print(f"   - 총 대화 수: {data['statistics']['total_conversations']}")
    print(f"   - 총 메시지 수: {data['statistics']['total_messages']}")
    
    return output_file


def create_readable_text_version(input_file: str, output_file: str = None):
    """
    채팅 히스토리를 읽기 쉬운 텍스트 형식으로 변환
    
    Args:
        input_file: 입력 JSON 파일 경로
        output_file: 출력 텍스트 파일 경로
    """
    
    # 입력 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 출력 파일명 결정
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_readable.txt")
    
    # 텍스트 형식으로 변환
    lines = []
    lines.append("=" * 80)
    lines.append("챗봇 대화 히스토리")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"내보낸 날짜: {data['export_info']['export_date']}")
    lines.append(f"총 세션 수: {data['statistics']['total_sessions']}")
    lines.append(f"총 대화 수: {data['statistics']['total_conversations']}")
    lines.append(f"총 메시지 수: {data['statistics']['total_messages']}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    # 대화 내용 출력
    for idx, conv in enumerate(data.get('conversations', []), 1):
        lines.append(f"\n{'=' * 80}")
        lines.append(f"대화 #{idx}")
        lines.append(f"{'=' * 80}")
        lines.append(f"\n[세션 ID] {conv['session_id']}")
        lines.append(f"[사용자 ID] {conv['user_id']}")
        lines.append(f"[시간] {conv['timestamp']}")
        lines.append(f"[의도] {conv.get('intent', 'N/A')}")
        lines.append(f"[신뢰도] {conv.get('confidence', 'N/A')}")
        lines.append(f"[탐색 의도] {conv.get('exploration_intent', False)}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("👤 사용자:")
        lines.append("-" * 80)
        # \n을 실제 줄바꿈으로 변환
        user_msg = conv['user_message'].replace('\\n', '\n')
        lines.append(user_msg)
        lines.append("")
        lines.append("-" * 80)
        lines.append("🤖 챗봇:")
        lines.append("-" * 80)
        # \n을 실제 줄바꿈으로 변환
        assistant_msg = conv['assistant_message'].replace('\\n', '\n')
        lines.append(assistant_msg)
        lines.append("")
        
        # 추천 상품 정보
        if conv.get('recommendations'):
            lines.append("-" * 80)
            lines.append("🛍️ 추천 상품:")
            lines.append("-" * 80)
            for rec in conv['recommendations']:
                lines.append(f"  - {rec.get('name', 'N/A')} ({rec.get('brand', 'N/A')}) - {rec.get('price', 0):,}원")
            lines.append("")
    
    # 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 읽기 쉬운 텍스트 파일 생성 완료!")
    print(f"📁 출력 파일: {output_file}")
    
    return output_file


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='챗봇 대화 히스토리를 읽기 쉬운 형식으로 변환')
    parser.add_argument('input_file', help='입력 JSON 파일 경로')
    parser.add_argument('--output-json', type=str, help='출력 JSON 파일 경로')
    parser.add_argument('--output-text', type=str, help='출력 텍스트 파일 경로')
    parser.add_argument('--text-only', action='store_true', help='텍스트 형식만 생성')
    
    args = parser.parse_args()
    
    try:
        if not args.text_only:
            # JSON 포맷팅
            format_chat_history(args.input_file, args.output_json)
            print()
        
        # 텍스트 형식 생성
        create_readable_text_version(args.input_file, args.output_text)
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

