import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import './PipelineScroller.css';

export default function PipelineScroller() {
  const containerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const lineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const sections = gsap.utils.toArray('.pipeline-step');
      
      gsap.to(sections, {
        xPercent: -100 * (sections.length - 1),
        ease: "none",
        scrollTrigger: {
          trigger: containerRef.current,
          pin: true,
          scrub: 1,
          end: () => "+=" + trackRef.current?.offsetWidth
        }
      });

      // Animate the internal "nerve line" width syncing with scroll
      gsap.fromTo(lineRef.current, 
        { width: "0%" },
        { 
          width: "100%", 
          ease: "none",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top top",
            end: () => "+=" + trackRef.current?.offsetWidth,
            scrub: 1,
          }
        }
      );
      
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <section className="pipeline-wrapper" ref={containerRef}>
      <div className="pipeline-header">
        <h2 className="text-hero">Data Foundry Pipeline</h2>
        <p className="text-subtitle">챗봇의 한계를 넘는 고순도 데이터 제련소.</p>
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
              <h3 className="step-title">Bronze Ingestion</h3>
              <p className="step-desc">공식 문서 HTML, 커뮤니티 이슈, 실제 운영 증거를 원본 그대로 수집합니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node"></div>
            <div className="step-card glass-panel">
              <span className="step-number text-dim">02.</span>
              <h3 className="step-title">Silver Normalization</h3>
              <p className="step-desc">텍스트를 구조화된 그래프로 변환합니다. 명령어, 에러 로그, 쿠버네티스 객체를 추출합니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node"></div>
            <div className="step-card glass-panel">
              <span className="step-number text-dim">03.</span>
              <h3 className="step-title">Silver-KO Fallback</h3>
              <p className="step-desc">한국어 품질을 보장하기 위해, 누락된 번역은 영문을 바탕으로 Draft를 생성하여 대기열에 올립니다.</p>
            </div>
          </div>

          <div className="pipeline-step">
            <div className="step-node node-active"></div>
            <div className="step-card glass-panel highlight-card">
              <span className="step-number gradient-text">04.</span>
              <h3 className="step-title">Gold Corpus & Manual</h3>
              <p className="step-desc">모든 검수를 마친 데이터는 RAG 코퍼스와 사람이 읽는 매뉴얼북 양쪽으로 동시에 배포됩니다.</p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
