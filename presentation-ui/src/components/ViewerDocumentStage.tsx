import { useEffect, useRef } from 'react';

export interface ViewerDocumentPayload {
  html: string;
  inlineStyles: string[];
  bodyClassName: string;
  interactionPolicy?: {
    codeCopy?: boolean;
    codeWrapToggle?: boolean;
    recentPositionTracking?: boolean;
    anchorNavigation?: boolean;
  };
}

const VIEWER_READER_POLISH = `
  :host {
    display: block;
    color: #0f172a;
    min-width: 0;
    max-width: 100%;
  }

  .viewer-root {
    min-height: 100%;
    background: transparent;
    padding-bottom: 40px;
    min-width: 0;
    max-width: 100%;
  }

  /* 
   * Allow the native styling from viewer_page.py to take over entirely.
   * Hide the reader-sidebar as requested by user ("목록들은 껍데기같은데 싹 지우면 안돼?").
   */
  .viewer-root .reader-sidebar {
    display: none !important;
  }

  .viewer-root .reader-layout {
    grid-template-columns: 1fr !important;
    min-width: 0 !important;
    max-width: 100% !important;
  }

  /* Constrain the main width similar to a typical book/documentation layout */
  .viewer-root main {
    width: min(900px, 100%) !important;
    max-width: 900px !important;
    margin: 0 auto !important;
    padding: 32px 48px !important;
    min-width: 0 !important;
  }

  .viewer-root .study-document,
  .viewer-root .hero,
  .viewer-root .hero-grid,
  .viewer-root .hero-main,
  .viewer-root .section-list,
  .viewer-root .section-card,
  .viewer-root .section-body,
  .viewer-root .code-block,
  .viewer-root .table-wrap {
    min-width: 0 !important;
    max-width: 100% !important;
  }

  @media (max-width: 1100px) {
    .viewer-root main {
      padding: 32px 24px !important;
    }
  }
`;

function isViewerHref(href: string): boolean {
  try {
    const parsed = new URL(href, window.location.origin);
    return (
      parsed.pathname.startsWith('/playbooks/')
      || parsed.pathname.startsWith('/docs/ocp/')
      || parsed.pathname.startsWith('/wiki/entities/')
      || parsed.pathname.startsWith('/wiki/figures/')
    );
  } catch {
    return false;
  }
}

export default function ViewerDocumentStage({
  viewerDocument,
  onNavigateViewerPath,
  className,
}: {
  viewerDocument: ViewerDocumentPayload;
  onNavigateViewerPath?: (viewerPath: string) => void;
  className?: string;
}) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) {
      return;
    }
    const root = host.shadowRoot ?? host.attachShadow({ mode: 'open' });
    root.replaceChildren();

    viewerDocument.inlineStyles.forEach((styleText) => {
      const style = document.createElement('style');
      style.textContent = styleText;
      root.appendChild(style);
    });

    const polishStyle = document.createElement('style');
    polishStyle.textContent = VIEWER_READER_POLISH;
    root.appendChild(polishStyle);

    const wrapper = document.createElement('div');
    wrapper.className = ['viewer-root', 'is-embedded', viewerDocument.bodyClassName].filter(Boolean).join(' ');
    wrapper.innerHTML = viewerDocument.html;
    root.appendChild(wrapper);

    root.querySelectorAll('a[href]').forEach((node) => {
      const anchor = node as HTMLAnchorElement;
      const href = anchor.getAttribute('href') ?? '';
      if (!href || href.startsWith('#') || isViewerHref(href)) {
        return;
      }
      if (!anchor.hasAttribute('target')) {
        anchor.setAttribute('target', '_blank');
      }
      anchor.setAttribute('rel', 'noreferrer');
    });

    const handleClick = async (event: Event): Promise<void> => {
      const target = event.target as HTMLElement | null;
      const anchor = target?.closest('a[href]') as HTMLAnchorElement | null;
      if (anchor) {
        const href = anchor.getAttribute('href') ?? '';
        if (href.startsWith('#')) {
          event.preventDefault();
          const targetId = href.slice(1);
          const targetNode = root.getElementById(targetId) ?? root.querySelector(`[id="${CSS.escape(targetId)}"]`);
          if (targetNode instanceof HTMLElement) {
            // scrollIntoView on shadow DOM nodes scrolls ALL light-DOM ancestors including the
            // panel scroll container, which snaps the whole panel to scrollTop=0 before trying
            // to reveal the element. Instead, find the nearest scrollable ancestor of the shadow
            // host in the light DOM and scroll it manually using viewport-relative coordinates.
            const shadowHost = host;
            let scrollContainer: Element | null = shadowHost.parentElement;
            while (scrollContainer && scrollContainer !== document.documentElement) {
              const style = window.getComputedStyle(scrollContainer);
              if (style.overflowY === 'auto' || style.overflowY === 'scroll') break;
              scrollContainer = scrollContainer.parentElement;
            }
            if (scrollContainer && scrollContainer !== document.documentElement) {
              const containerRect = scrollContainer.getBoundingClientRect();
              const nodeRect = targetNode.getBoundingClientRect();
              const targetScrollTop = scrollContainer.scrollTop + (nodeRect.top - containerRect.top) - 16;
              scrollContainer.scrollTo({ top: targetScrollTop, behavior: 'smooth' });
            } else {
              targetNode.scrollIntoView({ block: 'start', behavior: 'smooth' });
            }
          }
          return;
        }
        if (href && isViewerHref(href) && onNavigateViewerPath) {
          event.preventDefault();
          const parsed = new URL(href, window.location.origin);
          onNavigateViewerPath(`${parsed.pathname}${parsed.search}${parsed.hash}`);
          return;
        }
      }

      const button = target?.closest('button');
      if (!button) {
        return;
      }
      if (button.classList.contains('copy-button')) {
        const copyPayload = button.getAttribute('data-copy') ?? '""';
        const defaultLabel = button.getAttribute('data-label-default') ?? '복사';
        try {
          const text = JSON.parse(copyPayload) as string;
          if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
          }
          button.textContent = '복사됨';
          button.classList.add('is-copied');
          window.setTimeout(() => {
            button.textContent = defaultLabel;
            button.classList.remove('is-copied');
          }, 1400);
        } catch {
          button.textContent = '실패';
          window.setTimeout(() => {
            button.textContent = defaultLabel;
          }, 1400);
        }
        return;
      }
      if (button.classList.contains('icon-button')) {
        const codeBlock = button.closest('.code-block');
        if (!codeBlock) {
          return;
        }
        codeBlock.classList.toggle('is-wrapped');
        const wrapped = codeBlock.classList.contains('is-wrapped');
        button.setAttribute('aria-pressed', wrapped ? 'true' : 'false');
        button.textContent = wrapped
          ? button.getAttribute('data-label-active') ?? '줄바꿈 해제'
          : button.getAttribute('data-label-default') ?? '줄바꿈';
      }
    };

    root.addEventListener('click', handleClick);
    return () => {
      root.removeEventListener('click', handleClick);
    };
  }, [onNavigateViewerPath, viewerDocument]);

  return <div className={className} ref={hostRef} />;
}
