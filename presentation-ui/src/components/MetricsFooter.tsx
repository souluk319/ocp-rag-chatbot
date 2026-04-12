import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import gsap from 'gsap';
import './MetricsFooter.css';

export default function MetricsFooter() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Counter animation logic
      const counters = gsap.utils.toArray('.metric-number');
      
      counters.forEach((counter: any) => {
        const targetValue = parseInt(counter.getAttribute('data-target') || '0', 10);
        
        gsap.to(counter, {
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 80%",
            once: true
          },
          innerHTML: targetValue,
          duration: 2,
          ease: "power2.out",
          snap: { innerHTML: 1 },
          onUpdate: function() {
            counter.innerHTML = Math.round(this.targets()[0].innerHTML);
          }
        });
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <footer className="metrics-footer" ref={containerRef}>
      <div className="metrics-content">
        <h2>지금 바로 플랫폼에 검증된 지식</h2>
        
        <div className="metrics-grid">
          <div className="metric-item">
            <span className="metric-number gradient-text" data-target="23">0</span>
            <span className="metric-label">Approved Runtime Books</span>
          </div>
          <div className="metric-item">
            <span className="metric-number gradient-text" data-target="4">0</span>
            <span className="metric-label">Review Pending Drafts</span>
          </div>
          <div className="metric-item">
            <span className="metric-number gradient-text" data-target="1500">0</span>
            <span className="metric-label">Gold Corpus Chunks (est.)</span>
          </div>
        </div>

        <div className="footer-cta">
          <a href="http://127.0.0.1:8765/workspace" className="btn-primary" target="_blank" rel="noreferrer">
            Workspace 시작하기
          </a>
          <Link to="/details" className="btn-secondary">
            프로젝트 상세 보기
          </Link>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>Play Book Studio Enterprise — Red Hat OpenShift 4.20 / Designed by Cywell</p>
      </div>
    </footer>
  );
}
