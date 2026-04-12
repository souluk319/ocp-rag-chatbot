import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import './Hero.css';

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const maskRef = useRef<HTMLDivElement>(null);
  const textGroupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Cinematic Entrance: Scale down from 1.1 + fade in
      gsap.fromTo(textGroupRef.current, 
        { autoAlpha: 0, scale: 1.1, translateY: 30 },
        { autoAlpha: 1, scale: 1, translateY: 0, duration: 2.2, ease: "power4.out", delay: 0.1 }
      );

      // Removed scrubbing intro text fade out at user request
      // Background mask reveal effect on scroll
      gsap.to(maskRef.current, {
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: "bottom top",
          scrub: 1,
        },
        clipPath: "circle(100% at 50% 50%)"
      });
      
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <section className="hero-container" ref={containerRef}>
      <div className="hero-bokeh bokeh-cyan"></div>
      <div className="hero-bokeh bokeh-purple"></div>
      
      {/* Background Masking Layer */}
      <div className="hero-bg-mask" ref={maskRef}></div>

      <div className="hero-content" ref={textGroupRef}>
        <h1 className="text-giant hero-title">
          Play Book<br/>
          <span className="gradient-text">Studio.</span>
        </h1>
        <p className="text-subtitle hero-subtitle">
          공식 문서를 실행형 플레이북으로.<br/>
          근거와 챗봇을 연결하는 지능형 데이터 제련소.
        </p>
      </div>

      <div className="hero-scroll-indicator">
        <div className="mouse-icon">
          <div className="mouse-wheel"></div>
        </div>
        <span>Explore the knowledge</span>
      </div>
    </section>
  );
}
