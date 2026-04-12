import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import './PipelineScroller.css';

export default function PipelineScroller() {
  const containerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const lineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // ULTIMATE RECOVERY: Force clear ANY scroll locks across the global document
    const unlockBody = () => {
      document.body.style.overflow = '';
      document.body.style.height = '';
      document.documentElement.style.overflow = '';
    };

    requestAnimationFrame(unlockBody);

    const ctx = gsap.context(() => {
      const sections = gsap.utils.toArray('.pipeline-step');

      const travelDistance = () => window.innerWidth * 2.1;

      const scrollTween = gsap.to(trackRef.current, {
        x: () => -travelDistance(),
        ease: "none",
        scrollTrigger: {
          trigger: containerRef.current,
          pin: true,
          scrub: 1,
          start: "top top",
          anticipatePin: 1, // Prevent wheel lag/jittering
          end: () => "+=" + (travelDistance() + 600) // Clear, finite end point
        }
      });

      // 2. Nerve Line Progress Flow (Synchronized with track move)
      gsap.fromTo(lineRef.current,
        { width: "0%" },
        {
          width: "100%",
          ease: "none",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top top",
            end: () => "+=" + travelDistance(),
            scrub: 1,
          }
        }
      );

      // 3. Sequential Ignition for Each Card
      sections.forEach((section: any) => {
        const card = section.querySelector('.step-card');
        const node = section.querySelector('.step-node');

        gsap.to(card, {
          scrollTrigger: {
            trigger: section,
            containerAnimation: scrollTween,
            start: "left center+=10%",
            end: "right center-=10%",
            toggleClass: { targets: [card, node], className: "active-glow node-active" },
            scrub: false,
          }
        });
      });

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
        {/* The glowing nerve flow line in the background */}
        <div className="nerve-path">
          <div className="nerve-progress" ref={lineRef}></div>
        </div>

        <div className="pipeline-track" ref={trackRef}>

          <div className="pipeline-step">
            <div className="step-node"></div>
            <div className="step-card glass-panel">
              <span className="step-number text-dim">01.</span>
              <h3 className="step-title">Multi-Source Capture</h3>
              <p className="step-desc">공식 문서, 업로드 파일, 선택한 레포지토리 문서를 수집하고 원본과 출처를 함께 고정합니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node"></div>
            <div className="step-card glass-panel">
              <span className="step-number text-dim">02.</span>
              <h3 className="step-title">Canonical Normalization</h3>
              <p className="step-desc">HTML, PDF, DOCX, PPTX, XLSX를 정규 섹션으로 바꾸고 명령어, 표, 절차, 앵커와 lineage를 추출합니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node"></div>
            <div className="step-card glass-panel">
              <span className="step-number text-dim">03.</span>
              <h3 className="step-title">Approval & Materialization</h3>
              <p className="step-desc">품질 게이트를 통과한 문서만 Approved Runtime Book으로 승격하고 뷰어와 라이브러리 자산으로 반영합니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node node-active"></div>
            <div className="step-card glass-panel highlight-card">
              <span className="step-number gradient-text">04.</span>
              <h3 className="step-title">Derived Playbook Foundry</h3>
              <p className="step-desc">승격된 북을 Topic, Operation, Troubleshooting, Policy, Synthesized Playbook으로 파생해 실행형 지식 자산으로 배포합니다.</p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
