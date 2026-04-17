import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import './PipelineScroller.css';

gsap.registerPlugin(ScrollTrigger);

export default function PipelineScroller() {
  const containerRef  = useRef<HTMLDivElement>(null);
  const trackRef      = useRef<HTMLDivElement>(null);
  const nervePathRef  = useRef<HTMLDivElement>(null);
  const lineRef       = useRef<HTMLDivElement>(null);

  useEffect(() => {
    requestAnimationFrame(() => {
      document.body.style.overflow = '';
      document.body.style.height   = '';
      document.documentElement.style.overflow = '';
    });

    const ctx = gsap.context(() => {
      const sections = gsap.utils.toArray<HTMLElement>('.pipeline-step');
      const td        = () => window.innerWidth * 2.1;
      const trackEnd  = () => td() + 600;
      const vw        = window.innerWidth;
      const t         = td();

      // Pre-compute thresholds and snap points so we have them for the ScrollTrigger configs.
      // - threshold: when nerve light hits card center.
      // - snapPoint: when card center hits viewport center (vw/2).
      const cardData = sections.map((section) => {
        const card = section.querySelector<HTMLElement>('.step-card')!;
        const node = section.querySelector<HTMLElement>('.step-node')!;
        const initialLeft = card.getBoundingClientRect().left;
        const cardWidth   = card.offsetWidth;
        const cardCenter  = initialLeft + cardWidth / 2;
        
        // Threshold for ignition (p * vw = cardCenter - p * t)
        const threshold = cardCenter / (vw + t);
        
        // Snap point for centering (cardCenter - p * t = vw / 2)
        const snapPoint = (cardCenter - vw / 2) / t;
        
        return { card, node, threshold, snapPoint };
      });

      const snapPoints = cardData.map(d => d.snapPoint);

      // 1. Horizontal track scroll (pinned) + AGGRESSIVE COMMIT SNAPPING
      gsap.to(trackRef.current, {
        x: () => -td(),
        ease: 'none',
        scrollTrigger: {
          trigger : containerRef.current,
          pin     : true,
          scrub   : 0.5, // Reduced lag for more direct "Stepping" feel
          start   : 'top top',
          anticipatePin: 1,
          end     : () => '+=' + trackEnd(),
          snap: {
            snapTo: snapPoints,
            directional: true, // 방향 감지 즉시 다음/이전 단계로 확정(Commit)
            delay: 0,
            duration: { min: 0.4, max: 0.7 },
            ease: 'power4.out', // 프리미엄 감속 커브
          },
        },
      });

      // 2. Nerve-path counter-animation
      gsap.to(nervePathRef.current, {
        x: () => td(),
        ease: 'none',
        scrollTrigger: {
          trigger : containerRef.current,
          start   : 'top top',
          end     : () => '+=' + trackEnd(),
          scrub   : 0.5, // Sync scrub with track
        },
      });

      // 3. Nerve-progress (Light) Animation
      gsap.fromTo(
        lineRef.current,
        { width: '0%' },
        {
          width: '100%',
          ease : 'none',
          scrollTrigger: {
            trigger  : containerRef.current,
            start    : 'top top',
            end      : () => '+=' + trackEnd(),
            scrub    : 0.5, // Sync scrub
            onUpdate : (self) => {
              const p = self.progress;
              cardData.forEach(({ card, threshold }) => {
                // node reference removed from loop to avoid errors since it's display:none
                if (p >= threshold) {
                  card.classList.add('active-glow');
                } else {
                  card.classList.remove('active-glow');
                }
              });
            },
          },
        }
      );

      requestAnimationFrame(() => ScrollTrigger.refresh());
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <section className="pipeline-wrapper" ref={containerRef}>
      <div className="pipeline-header">
        <h2 className="text-hero">Data Foundry Pipeline</h2>
        <p className="text-subtitle">수집된 문서를 승인된 플레이북 자산으로 제련하는 제품 파이프라인.</p>
      </div>

      <div className="pipeline-track-container">
        <div className="pipeline-track" ref={trackRef}>

          {/* Nerve line lives INSIDE the track so it shares the same stacking
              context as the cards. z-index:0 here is unambiguously below the
              cards' z-index:5 — no cross-context GPU compositing involved. */}
          <div className="nerve-path" ref={nervePathRef}>
            <div className="nerve-progress" ref={lineRef}></div>
          </div>

          <div className="pipeline-steps-inner">
            <div className="pipeline-step">
              <div className="step-node"></div>
              <div className="step-card">
                <span className="step-number text-dim">01.</span>
                <h3 className="step-title">Multi-Source Capture</h3>
                <p className="step-desc">공식 문서, 업로드 파일, 선택한 레포지토리 문서를 수집하고 원본과 출처를 함께 고정합니다.</p>
              </div>
            </div>

            <div className="pipeline-step">
              <div className="step-node"></div>
              <div className="step-card">
                <span className="step-number text-dim">02.</span>
                <h3 className="step-title">Canonical Normalization</h3>
                <p className="step-desc">HTML, PDF, DOCX, PPTX, XLSX를 정규 섹션으로 바꾸고 명령어, 표, 절차, 앵커와 lineage를 추출합니다.</p>
              </div>
            </div>

            <div className="pipeline-step">
              <div className="step-node"></div>
              <div className="step-card">
                <span className="step-number text-dim">03.</span>
                <h3 className="step-title">Approval & Materialization</h3>
                <p className="step-desc">품질 게이트를 통과한 문서만 Approved Runtime Book으로 승격하고 뷰어와 라이브러리 자산으로 반영합니다.</p>
              </div>
            </div>

            <div className="pipeline-step">
              <div className="step-node"></div>
              <div className="step-card highlight-card">
                <span className="step-number gradient-text">04.</span>
                <h3 className="step-title">Derived Playbook Foundry</h3>
                <p className="step-desc">승격된 북을 Topic, Operation, Troubleshooting, Policy, Synthesized Playbook으로 파생해 실행형 지식 자산으로 배포합니다.</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
