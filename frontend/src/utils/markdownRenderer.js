/**
 * 마크다운 텍스트를 HTML로 변환하는 유틸리티 함수
 * 주요 마크다운 문법을 지원합니다.
 */

/**
 * 마크다운 텍스트를 HTML 문자열로 변환
 * 
 * @param {string} text - 마크다운 형식의 텍스트
 * @param {Array} recommendations - 추천 상품 배열 (선택사항)
 * @returns {string} HTML 문자열
 */
export function markdownToHtml(text, recommendations = []) {
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
      html += '<li>' + processInlineMarkdown(listContent, recommendations) + '</li>';
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
    
    html += processInlineMarkdown(lines[i], recommendations);
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
 * 인라인 마크다운 처리 (볼드, 이탤릭, 상품 링크 등)
 * 
 * @param {string} text - 텍스트
 * @param {Array} recommendations - 추천 상품 배열 (선택사항)
 * @returns {string} 처리된 HTML 문자열
 */
function processInlineMarkdown(text, recommendations = []) {
  if (!text) return '';
  
  let html = text;
  
  // 볼드 텍스트 변환 (**텍스트** 또는 __텍스트__)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
  
  // 상품명을 링크로 변환 (추천 상품 목록이 있을 때만)
  // 볼드 처리 후에 상품명 링크를 적용
  if (recommendations && recommendations.length > 0) {
    // 상품명 길이 순으로 정렬 (긴 이름부터 처리하여 부분 일치 방지)
    const sortedRecs = [...recommendations].sort((a, b) => {
      const nameA = a.name || '';
      const nameB = b.name || '';
      return nameB.length - nameA.length;
    });
    
    sortedRecs.forEach(rec => {
      if (rec.name && rec.product_url) {
        const productName = rec.name;
        
        // 공백 정규화: 상품명과 텍스트 모두 공백을 제거한 버전으로 비교
        // "오피스룩"과 "오피스 룩"을 동일하게 처리
        const normalizedProductName = productName.replace(/\s+/g, '');
        
        // 정규표현식 이스케이프
        const escapedName = productName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        
        // 공백 차이를 허용하는 패턴 생성
        // 상품명의 각 문자 사이에 공백 0개 이상을 허용하는 패턴
        // "오피스룩" -> "오\\s*피\\s*스\\s*룩"
        // "오피스 룩" -> "오\\s*피\\s*스\\s*\\s*룩" (기존 공백도 유지)
        const chars = productName.split('');
        const flexiblePattern = chars.map(char => {
          if (/\s/.test(char)) {
            return '\\s*';
          }
          return char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*';
        }).join('').replace(/\\s\*\\s\*/g, '\\s*'); // 연속된 \s* 정리
        
        // <strong> 태그 내부의 상품명도 링크로 변환
        html = html.replace(new RegExp(`(<strong>)([^<]*?)(${flexiblePattern})([^<]*?)(</strong>)`, 'gi'), 
          (match, openTag, prefix, productNameText, suffix, closeTag) => {
            // 매칭된 텍스트에서 공백을 제거한 버전과 상품명의 정규화된 버전 비교
            const matchedText = (prefix + productNameText + suffix).trim().replace(/\s+/g, '');
            if (matchedText.includes(normalizedProductName)) {
              const fullText = prefix + productNameText + suffix;
              return `${openTag}<a href="${rec.product_url}" class="chat-product-link" data-product-url="${rec.product_url}">${fullText.trim()}</a>${closeTag}`;
            }
            return match;
          });
        
        // 일반 텍스트에서 상품명을 링크로 변환 (이미 링크나 태그 내부가 아닌 경우)
        html = html.replace(new RegExp(`(?!<a[^>]*>)(?<!</a>)(?<!<strong>)(?<!</strong>)(${flexiblePattern})(?![^<]*</a>)(?![^<]*</strong>)`, 'gi'), 
          (match) => {
            // 매칭된 텍스트에서 공백을 제거한 버전과 상품명의 정규화된 버전 비교
            const matchedText = match.trim().replace(/\s+/g, '');
            if (matchedText === normalizedProductName || matchedText.includes(normalizedProductName)) {
              return `<a href="${rec.product_url}" class="chat-product-link" data-product-url="${rec.product_url}">${match.trim()}</a>`;
            }
            return match;
          });
      }
    });
  }
  
  // 남은 볼드 마커 제거 (** 또는 __)
  html = html.replace(/\*\*/g, '');
  html = html.replace(/__/g, '');
  
  // 이탤릭 텍스트 변환은 볼드보다 우선순위가 낮으므로 제외
  // (볼드와 충돌 방지)
  
  return html;
}

/**
 * 마크다운 텍스트를 React 요소로 변환 (dangerouslySetInnerHTML 사용)
 * 
 * @param {string} text - 마크다운 형식의 텍스트
 * @param {Array} recommendations - 추천 상품 배열 (선택사항)
 * @returns {Object} dangerouslySetInnerHTML에 사용할 객체
 */
export function markdownToReactHtml(text, recommendations = []) {
  return { __html: markdownToHtml(text, recommendations) };
}

