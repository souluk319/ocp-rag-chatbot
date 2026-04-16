import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Book, ShieldCheck, Layers, PlaySquare } from 'lucide-react';
import gsap from 'gsap';
import './ProjectDetailsPage.css';

export default function ProjectDetailsPage() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Basic entrance animation for the page
    gsap.fromTo(containerRef.current,
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: 1, ease: 'power3.out' }
    );
  }, []);

  return (
    <div className="details-page-wrapper" ref={containerRef}>
      
      {/* Sidebar Navigation */}
      <nav className="details-sidebar glass-panel">
        <div className="sidebar-header">
          <Link to="/" className="back-link">
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </Link>
          <h2 className="sidebar-title gradient-text">Project Contracts</h2>
        </div>
        
        <ul className="sidebar-menu">
          <li><a href="#core-charter"><Book size={16}/> Core Charter</a></li>
          <li><a href="#asset-derived"><Layers size={16}/> Playbook Outputs</a></li>
          <li><a href="#traceability"><ShieldCheck size={16}/> Zero Hallucination</a></li>
          <li><a href="#enterprise"><PlaySquare size={16}/> Enterprise Overlay</a></li>
        </ul>
      </nav>

      {/* Main Content Area */}
      <main className="details-content">
        
        <section id="core-charter" className="detail-section">
          <h1>Product Core Charter</h1>
          <p className="lead-text">
            Play Book Studio는 문서를 요약해주는 흔한 지식 챗봇이 아닙니다. 이 플랫폼의 본질은 방대한 기업 문서, 운영 절차, 제조사 기술 문서를 <strong>검증 가능하고 실행할 수 있는 플레이북 형태</strong>로 제련하는 데이터 파이프라인(Data Foundry)입니다.
          </p>
          <div className="status-banner">
            <span className="status-label">Current Truth:</span>
            <span className="status-value gradient-text">paid_poc_candidate</span>
            <span className="status-label ms-auto">Primary Pack:</span>
            <span className="status-value text-white">OpenShift 4.20</span>
          </div>
        </section>

        <section id="asset-derived" className="detail-section">
          <h2>1. Beyond Chat: The Playbook Output</h2>
          <p>
            우리는 단순히 검색 증강 생성(RAG)을 통해 "요약과 링크"를 던져주는 것에 머물지 않습니다.
            원문(Raw Manual) 하나를 섭취하면, 운영자의 질문 맥락에 맞추어 다음과 같은 파생 자산(Derived Assets)을 찍어냅니다.
          </p>
          <div className="asset-grid">
            <div className="asset-card glass-panel">
              <h3>Topic Playbook</h3>
              <p>사전조건 → 절차 → 코드 → 검증 → 실패 신호 → 출처의 완벽한 구조를 갖춘 실행형 매뉴얼.</p>
            </div>
            <div className="asset-card glass-panel">
              <h3>Troubleshooting Book</h3>
              <p>에러 신호와 원인을 분석하고 즉각적으로 대응할 수 있는 트러블슈팅 행동 강령.</p>
            </div>
            <div className="asset-card glass-panel">
              <h3>Policy Overlay Book</h3>
              <p>표준 벤더 문서 위에 고객사 특유의 폐쇄망 환경이나 사내 정책을 안전하게 덧씌운 오버레이 문서.</p>
            </div>
          </div>
        </section>

        <section id="traceability" className="detail-section">
          <h2>2. Absolute Traceability (Zero Hallucination)</h2>
          <p>
            단 하나의 답변도 근거 없이는 나가지 않습니다. 답변을 생성한 내부 메커니즘은 <strong>Answer → Source → Version → Anchor</strong> 라인을 정확히 유지해야 합니다. 사용자(운영자 및 설계자)는 답변에 달린 Citation 뱃지를 클릭하는 즉시, 답변의 뼈대가 된 소스 원문 문서의 정확한 섹션으로 점프(`Manualbook Viewer`)할 수 있습니다.
          </p>
          <div className="trace-path">
            <span>Query</span>
            <div className="arrow">→</div>
            <span className="glow-cyan">AST Extraction</span>
            <div className="arrow">→</div>
            <span className="glow-purple">Vector/Graph DB</span>
            <div className="arrow">→</div>
            <span className="glow-white">Citation Attached</span>
          </div>
        </section>

        <section id="enterprise" className="detail-section">
          <h2>3. Enterprise Policy Overlay (PoC Ready)</h2>
          <p>
             아무리 뛰어난 AI 챗봇이라도 외부 벤더의 공식 문서만으로는 기업의 내부 사정을 해결할 수 없습니다. Play Book Studio는 `Source Authority Policy` 매트릭스에 따라 권위를 분리합니다.
          </p>
          <ul className="feature-list">
            <li><strong>Vendor Official Source</strong> : 절대적인 사실 기반 (e.g. Red Hat OCP)</li>
            <li><strong>Internal Runbook</strong> : 고객사의 운영 룰 (최우선 순위로 오버레이 됨)</li>
            <li><strong>Verified Evidence</strong> : 장애 처리 티켓 등 과거의 해결 증거</li>
          </ul>
          <p>이러한 권위 게층을 통해 "공식 문서에는 이렇게 나와있지만, 귀사의 사내 보안 정책에 따라 포트를 변경하여 실행해야 합니다" 와 같은 기업 맞춤형 답변을 도출합니다.</p>
        </section>

      </main>

    </div>
  );
}
