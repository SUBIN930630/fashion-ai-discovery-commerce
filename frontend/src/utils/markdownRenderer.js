/**
 * 마크다운 텍스트를 HTML로 변환하는 유틸리티 함수
 * 주요 마크다운 문법을 지원합니다.
 */

/**
 * 마크다운 텍스트를 HTML 문자열로 변환
 * 
 * @param {string} text - 마크다운 형식의 텍스트
 * @returns {string} HTML 문자열
 */
export function markdownToHtml(text) {
  if (!text) return '';
  
  // 줄 단위로 분리
  const lines = text.split('\n');
  let html = '';
  let inList = false;
  let inParagraph = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 헤딩 처리 (###, ##, #)
    if (line.match(/^### (.+)$/)) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      html += '<h3>' + line.replace(/^### /, '') + '</h3>';
      continue;
    }
    
    if (line.match(/^## (.+)$/)) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      html += '<h2>' + line.replace(/^## /, '') + '</h2>';
      continue;
    }
    
    if (line.match(/^# (.+)$/)) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      html += '<h1>' + line.replace(/^# /, '') + '</h1>';
      continue;
    }
    
    // 리스트 항목 처리 (- 또는 *)
    if (line.match(/^[-*] (.+)$/)) {
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      if (!inList) {
        html += '<ul>';
        inList = true;
      }
      const listContent = line.replace(/^[-*] /, '');
      html += '<li>' + processInlineMarkdown(listContent) + '</li>';
      continue;
    }
    
    // 빈 줄 처리
    if (line === '') {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      continue;
    }
    
    // 일반 텍스트 (단락)
    if (inList) {
      html += '</ul>';
      inList = false;
    }
    
    if (!inParagraph) {
      html += '<p>';
      inParagraph = true;
    } else {
      html += '<br />';
    }
    
    html += processInlineMarkdown(lines[i]);
  }
  
  // 닫히지 않은 태그 정리
  if (inList) {
    html += '</ul>';
  }
  if (inParagraph) {
    html += '</p>';
  }
  
  return html;
}

/**
 * 인라인 마크다운 처리 (볼드, 이탤릭 등)
 * 
 * @param {string} text - 텍스트
 * @returns {string} 처리된 HTML 문자열
 */
function processInlineMarkdown(text) {
  if (!text) return '';
  
  let html = text;
  
  // 볼드 텍스트 변환 (**텍스트** 또는 __텍스트__)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
  
  // 이탤릭 텍스트 변환은 볼드보다 우선순위가 낮으므로 제외
  // (볼드와 충돌 방지)
  
  return html;
}

/**
 * 마크다운 텍스트를 React 요소로 변환 (dangerouslySetInnerHTML 사용)
 * 
 * @param {string} text - 마크다운 형식의 텍스트
 * @returns {Object} dangerouslySetInnerHTML에 사용할 객체
 */
export function markdownToReactHtml(text) {
  return { __html: markdownToHtml(text) };
}

